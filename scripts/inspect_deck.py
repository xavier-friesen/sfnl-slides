"""Read an existing deck in one call: layouts, compositions and reuse candidates.

Usage:
    python inspect_deck.py <deck.pptx>
    python inspect_deck.py <deck.pptx> --slides 4,5      # volledige vormdetails
    python inspect_deck.py <deck.pptx> --slides 4 --text # mét de tekst per vorm

Waarom dit script bestaat
-------------------------
Slides toevoegen aan een deck die er al staat is een ander probleem dan een deck bouwen.
De layoutkeuze en de compositie liggen al vast — in de deck zelf — en de nieuwe slides
moeten daar naast kunnen staan zonder dat iemand ziet dat ze later zijn aangeschoven. Dat
betekent dat de eerste vraag niet "welke layout past hierbij" is, maar "wat doet deze deck
al". Dat uit de slide-XML lezen kost een handvol Read-aanroepen per slide en levert
duizenden regels op waarvan je er tien nodig had.

Twee niveaus, want dat is de manier waarop je een deck leest:

* **Overzicht** (zonder `--slides`) — één regel per slide: positie, bestandsnaam, layout
  met verdict, master, titel, welke placeholders gevuld zijn, hoeveel eigen vormen er
  staan, en een signatuur van de compositie (`kaartenrij(3)`, `tweeluik`,
  `tekstplaceholders`). Daarnaast op deckniveau: welke layouts het pakket überhaupt nog
  bevat, de fonts en tinten die op de slides staan, en de taal.
* **Detail** (`--slides 4,5`) — per vorm de geometrie in inch, de vulling, de lijn, het
  font van de eerste run en (met `--text`) de tekst. Dat is precies wat je nodig hebt om
  dezelfde compositie nog een keer neer te zetten, of om te besluiten dat
  `duplicate_slide.py` sneller is dan hem natekenen.

`layouts_available` is geen sier. Een opgeleverde deck is vaak geslankt met
`clean.py --drop-unused-layouts` (5,79 → 1,66 MB op een deck met vier fotodividers), en dan
zijn de layouts die de deck niet gebruikt uit het pakket verdwenen.
`add_slide.py <unpacked> slideLayout19.xml` faalt daar,
en de melding gaat over een ontbrekend bestand in plaats van over de oorzaak. Staat de
layout die je wilt niet in de lijst, dan is de route: een bestaande slide dupliceren en
opnieuw vullen, of de deck vanuit het sjabloon aanvullen.

De signatuur is een heuristiek en zegt dat ook: hij clustert eigen vormen op hun bovenkant
en kijkt naar vulling en tekst. Hij is bedoeld om je naar de juiste voorbeeldslide te
sturen, niet om een compositie te classificeren. `reuse_candidates` geeft per signatuur
één exemplaar, zodat je één detailaanroep doet in plaats van vijf.

Er wordt niets geschreven. Output is compacte JSON, zoals de andere scripts.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from pathlib import Path

from _deck import (
    AGENDA_LAYOUT_NAMES,
    BLANK_CANVAS_NAME,
    CONTENT_LAYOUT_NAMES,
    EMU_PER_INCH,
    LAYOUT_NAMES,
    LAYOUT_POLICY,
    NEUTRAL_HEX,
    NS,
    UNKNOWN_VERDICT,
    emit,
    forbidden_reason,
    layout_name_of,
    layout_number_of,
    open_deck,
    verdict_for_name,
)

# De contentzone begint hier: alles erboven is geërfde header (titel, dash, logo).
CONTENT_ZONE_TOP_IN = 1.93

# Layoutnamen waarop een eigen compositie mag staan — zie het layoutbeleid (B11). Op naam,
# want dit script leest juist de decks die NIET uit ons sjabloon komen.
COMPOSABLE_LAYOUT_NAMES = CONTENT_LAYOUT_NAMES | {BLANK_CANVAS_NAME}

TRUNCATE = 90


def inches(value) -> float | None:
    if value is None:
        return None
    return round(value / EMU_PER_INCH, 2)


def shorten(text: str, limit: int = TRUNCATE) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def type_name(shape) -> str:
    """`shape_type` als string, ook als python-pptx het niet kan bepalen.

    Dit script leest decks die het zelf niet gebouwd heeft. Een `<p:sp>` zonder
    `prstGeom` of `custGeom` — generatoren maken die, PowerPoint niet — laat
    `shape.shape_type` een NotImplementedError gooien. Dat mag geen inspectie stukmaken:
    het antwoord is "onbekend vormtype", en de rest van de slide is nog steeds te lezen.
    """
    try:
        return str(shape.shape_type or "")
    except NotImplementedError:
        return ""


def shape_kind(shape) -> str:
    """Eén woord per vorm, in de termen waarin de skills erover praten."""
    if getattr(shape, "has_chart", False) and shape.has_chart:
        return "chart"
    if getattr(shape, "has_table", False) and shape.has_table:
        return "table"
    kind = type_name(shape)
    if kind.startswith("GROUP"):
        return "group"
    if kind.startswith("PICTURE"):
        return "picture"
    if kind.startswith("LINE") or kind.startswith("FREEFORM"):
        return "line"
    if shape.is_placeholder:
        return "placeholder"
    if getattr(shape, "has_text_frame", False) and shape.text_frame.text.strip():
        return "textbox"
    return "shape"


# De vier tinten met een naam en een rol (brand.md §Het tintenpalet), plus het recept
# dat daar expliciet is afgekeurd. Sleutel is de descriptor die `colour_of` opbouwt.
NAMED_FILLS = {
    "dk2 lum10/90": "navy-tint #E2E1F6",
    "accent1 sat25 lum25/75": "warmgrijs #EDE6E3",
    "accent1 lum20/80": "oranje-tint #FEE5DC",
    "accent3 lum20/80": "royal-tint #D7DFF3",
    "accent4 lum20/80": "sky-tint",
    "accent5 lum20/80": "emerald-tint",
    "accent2 lum20/80": "grapefruit-tint",
    "dk2 lum20/80": "lavendel #C6C3ED (AFGEKEURD recept, zie xml-editing.md)",
    "dk2": "navy vol",
    "accent1": "oranje vol",
    "lt2": "wit",
}

DEPRECATED_FILL = "dk2 lum20/80"


def colour_of(element) -> str | None:
    """De vulling van een `<p:spPr>` of `<a:ln>` als recept, niet als losse hex.

    Een tint in dit sjabloon is een `schemeClr` met `lumMod`/`lumOff` erop, en dat is ook
    de vorm waarin de bouwer hem opnieuw moet schrijven. `fore_color.rgb` gooit daar
    AttributeError op ("no .rgb property on color type '_SchemeColor'"), dus een
    hex-alleen-lezing zag precies de vullingen niet die dit sjabloon gebruikt: een
    kaartenrij in navy-tint kwam eruit als een slide zonder kleur.

    Terug komt bijvoorbeeld `dk2 lum10/90`, `srgb:1B2A5B`, `gradient` of `picture`.
    """
    if element is None:
        return None
    for child in element:
        tag = child.tag.split("}")[-1]
        if tag == "noFill":
            return None
        if tag == "gradFill":
            return "gradient"
        if tag == "blipFill":
            return "picture"
        if tag == "pattFill":
            return "pattern"
        if tag != "solidFill":
            continue
        for colour in child:
            ctag = colour.tag.split("}")[-1]
            value = colour.get("val")
            if ctag == "srgbClr":
                return f"srgb:{(value or '').upper()}"
            if ctag != "schemeClr":
                return ctag
            parts = [value or "?"]
            transforms = {
                mod.tag.split("}")[-1]: mod.get("val") for mod in colour
            }
            if "satMod" in transforms:
                parts.append(f"sat{int(transforms['satMod']) // 1000}")
            if "lumMod" in transforms or "lumOff" in transforms:
                mod = int(transforms.get("lumMod", 100000)) // 1000
                off = int(transforms.get("lumOff", 0)) // 1000
                parts.append(f"lum{mod}/{off}")
            if "alpha" in transforms:
                parts.append(f"alpha{int(transforms['alpha']) // 1000}")
            return " ".join(parts)
    return None


def fill_of(shape) -> str | None:
    """De vulling van de vorm zelf. None betekent: geen eigen vulling."""
    sp_pr = shape._element.find(f"{{{NS['p']}}}spPr")
    if sp_pr is None:
        sp_pr = shape._element.find(f"{{{NS['a']}}}spPr")
    return colour_of(sp_pr)


def line_of(shape) -> str | None:
    sp_pr = shape._element.find(f"{{{NS['p']}}}spPr")
    if sp_pr is None:
        return None
    return colour_of(sp_pr.find(f"{{{NS['a']}}}ln"))


def describe_fill(descriptor: str | None) -> str | None:
    """De descriptor met de palet-naam erachter, waar die er is."""
    if descriptor is None:
        return None
    name = NAMED_FILLS.get(descriptor)
    return f"{descriptor} = {name}" if name else descriptor


def is_tint(descriptor: str | None) -> bool:
    """Een echte eigen vlakvulling — geen wit, geen beeld, geen verloop."""
    if not descriptor:
        return False
    if descriptor in {"gradient", "picture", "pattern", "lt2", "bg1"}:
        return False
    if descriptor.startswith("srgb:"):
        return descriptor.split(":", 1)[1] not in NEUTRAL_HEX
    return True


def first_run_font(shape) -> tuple[str | None, float | None, bool]:
    """Font, grootte en bold van de eerste run met tekst. None = geërfd."""
    if not getattr(shape, "has_text_frame", False):
        return None, None, False
    for paragraph in shape.text_frame.paragraphs:
        for run in paragraph.runs:
            if not run.text.strip():
                continue
            size = run.font.size.pt if run.font.size is not None else None
            return run.font.name, size, bool(run.font.bold)
    return None, None, False


def shape_text(shape) -> str:
    if getattr(shape, "has_table", False) and shape.has_table:
        rows = [
            " | ".join(cell.text.strip() for cell in row.cells)
            for row in shape.table.rows
        ]
        return " / ".join(rows)
    if not getattr(shape, "has_text_frame", False):
        return ""
    return shape.text_frame.text


def walk(shape, depth: int = 0):
    """Yield (shape, depth) voor elke vorm, groepen ingaand."""
    yield shape, depth
    if type_name(shape).startswith("GROUP"):
        for child in shape.shapes:
            yield from walk(child, depth + 1)


def cluster_rows(tops: list[float], tolerance: float = 0.25) -> list[list[float]]:
    """Groepeer bovenkanten die op dezelfde regel staan."""
    rows: list[list[float]] = []
    for top in sorted(tops):
        if rows and abs(top - rows[-1][0]) <= tolerance:
            rows[-1].append(top)
        else:
            rows.append([top])
    return rows


def signature(slide, layout_name: str | None) -> str:
    """Een korte naam voor wat er in de contentzone staat. Heuristiek, geen oordeel."""
    own = []
    placeholders_with_text = 0
    for shape in slide.shapes:
        if shape.is_placeholder:
            if getattr(shape, "has_text_frame", False) and shape.text_frame.text.strip():
                placeholders_with_text += 1
            continue
        top = inches(shape.top)
        if top is None or top < CONTENT_ZONE_TOP_IN - 0.05:
            # Header-zone: op 17 kan dat een bewuste compositie zijn, elders is het
            # geërfde chrome of iets nagetekend. Niet meetellen in de signatuur.
            continue
        own.append(shape)

    kinds = Counter(shape_kind(shape) for shape in own)
    if kinds["chart"]:
        return f"grafiek({kinds['chart']})"
    if kinds["table"]:
        return f"tabel({kinds['table']})"

    filled = [
        shape
        for shape in own
        if shape_kind(shape) in {"shape", "textbox", "group"} and is_tint(fill_of(shape))
    ]
    if filled:
        rows = cluster_rows([inches(shape.top) for shape in filled])
        widest = max(rows, key=len)
        if len(widest) >= 2:
            return f"kaartenrij({len(widest)})"
        if len(filled) == 2:
            return "tweeluik"
        return f"vlak({len(filled)})"
    if kinds["group"]:
        return f"groepen({kinds['group']})"
    if kinds["picture"]:
        return f"beeld({kinds['picture']})"
    if kinds["textbox"] or kinds["shape"]:
        return f"eigen tekst({kinds['textbox'] + kinds['shape']})"
    if placeholders_with_text:
        return "tekstplaceholders"
    if layout_name in AGENDA_LAYOUT_NAMES:
        return "agendalijst"
    return "leeg"


def master_number(slide) -> int | None:
    try:
        name = str(slide.slide_layout.slide_master.part.partname)
    except AttributeError:
        return None
    match = re.search(r"slideMaster(\d+)\.xml", name)
    return int(match.group(1)) if match else None


def package_layouts(presentation) -> dict[int, str]:
    """{19: 'Titel, subtitel'} voor elke layout die nog in het pakket zit."""
    found: dict[int, str] = {}
    for master in presentation.slide_masters:
        for layout in master.slide_layouts:
            match = re.search(r"slideLayout(\d+)\.xml", str(layout.part.partname))
            if match:
                found[int(match.group(1))] = layout.name
    return dict(sorted(found.items()))


def expected_layout_names() -> dict[int, str]:
    """{19: 'Titel, subtitel'} — welke naam bij welk nummer hoort in ÓNS sjabloon.

    Komt uit `_deck.LAYOUT_NAMES`, dus uit de gegenereerde sidecar. Tot W2b parste deze
    functie de beslistabel uit `reference/layouts.md` met een reguliere expressie — een
    derde plek waar de layoutfeiten leefden, en een die stil leeg opleverde zodra de
    tabelopmaak veranderde.

    Waar het voor is: een deck waarvan de namen niet bij de nummers passen komt niet uit
    het huidige SFNL-sjabloon. Dat is de goedkoopste detectie die er is, en het is de reden
    dat het beleid op naam keyt en niet op nummer.
    """
    return dict(LAYOUT_NAMES)


def language_ids(slide) -> Counter:
    counts: Counter = Counter()
    for element in slide.element.iter(f"{{{NS['a']}}}rPr"):
        lang = element.get("lang")
        if lang:
            counts[lang] += 1
    return counts


def overview(presentation, expected: dict[int, str]) -> tuple[list[dict], dict]:
    slides = []
    fonts: Counter = Counter()
    tints: Counter = Counter()
    languages: Counter = Counter()
    mismatches = []

    for position, slide in enumerate(presentation.slides, start=1):
        layout = layout_number_of(slide)
        layout_name = layout_name_of(slide)
        if layout in expected and expected[layout] != layout_name:
            mismatches.append(
                {"layout": layout, "in_deck": layout_name, "in_template": expected[layout]}
            )

        filled_idx = []
        title = None
        subtitle = None
        first_text = None
        chars = 0
        kinds: Counter = Counter()
        for shape, depth in (pair for top in slide.shapes for pair in walk(top)):
            kind = shape_kind(shape)
            if depth == 0:
                kinds[kind] += 1
            text = shape_text(shape)
            chars += len(text.strip())
            if shape.is_placeholder and text.strip():
                idx = shape.placeholder_format.idx
                filled_idx.append(idx)
                if first_text is None:
                    first_text = shorten(text)
                if idx == 0:
                    title = shorten(text)
                elif idx == 1:
                    subtitle = shorten(text)
            own_fill = fill_of(shape)
            if is_tint(own_fill):
                tints[own_fill] += 1
            name, _size, _bold = first_run_font(shape)
            if name:
                fonts[name] += 1

        languages.update(language_ids(slide))

        if title is None and first_text:
            # Covers en dividers hebben geen idx 0: op layout 4 draagt idx 10 de dektitel,
            # op de dividers idx 13 of 14. De eerste gevulde placeholder is daar de kop, en
            # die wil je in het overzicht zien staan — anders leest de deck als titelloos.
            title = first_text

        record = {
            "pos": position,
            "file": Path(str(slide.part.partname)).name,
            "layout": layout,
            "layout_name": layout_name,
            "verdict": verdict_for_name(layout_name),
            "master": master_number(slide),
            "title": title,
            "signature": signature(slide, layout_name),
            "filled_idx": sorted(set(filled_idx)),
            "own_shapes": kinds["shape"] + kinds["textbox"] + kinds["group"] + kinds["line"],
            "chars": chars,
        }
        if subtitle:
            record["subtitle"] = subtitle
        for key in ("chart", "table", "picture"):
            if kinds[key]:
                record[key + "s"] = kinds[key]
        slides.append(record)

    deck_level = {
        "fonts_on_slides": dict(fonts.most_common()),
        "fills_on_slides": {
            describe_fill(descriptor): count for descriptor, count in tints.most_common(12)
        },
        "languages": dict(languages.most_common(4)),
        "layout_name_mismatches": mismatches,
    }
    return slides, deck_level


def reuse_candidates(slides: list[dict]) -> list[dict]:
    """Per signatuur één voorbeeldslide, zodat één detailaanroep genoeg is."""
    best: dict[str, dict] = {}
    for record in slides:
        if record["layout_name"] not in COMPOSABLE_LAYOUT_NAMES:
            continue
        if record["signature"] in {"leeg", "tekstplaceholders"} and not record["own_shapes"]:
            continue
        current = best.get(record["signature"])
        if current is None or record["chars"] > current["chars"]:
            best[record["signature"]] = record
    return [
        {
            "pos": record["pos"],
            "file": record["file"],
            "layout": record["layout"],
            "signature": record["signature"],
        }
        for record in sorted(best.values(), key=lambda item: item["pos"])
    ]


def detail(presentation, wanted: set[int], with_text: bool) -> list[dict]:
    out = []
    for position, slide in enumerate(presentation.slides, start=1):
        if position not in wanted:
            continue
        shapes = []
        for top_shape in slide.shapes:
            for shape, depth in walk(top_shape):
                font, size, bold = first_run_font(shape)
                item = {
                    "depth": depth,
                    "kind": shape_kind(shape),
                    "name": shape.name,
                    "box": [
                        inches(shape.left),
                        inches(shape.top),
                        inches(shape.width),
                        inches(shape.height),
                    ],
                }
                if shape.is_placeholder:
                    item["idx"] = shape.placeholder_format.idx
                fill = describe_fill(fill_of(shape))
                if fill:
                    item["fill"] = fill
                stroke = describe_fill(line_of(shape))
                if stroke:
                    item["line"] = stroke
                if font:
                    item["font"] = font
                if size:
                    item["size_pt"] = size
                if bold:
                    item["bold"] = True
                text = shape_text(shape).strip()
                if text:
                    item["text"] = text if with_text else shorten(text, 40)
                    item["chars"] = len(text)
                shapes.append(item)
        out.append(
            {
                "pos": position,
                "file": Path(str(slide.part.partname)).name,
                "layout": layout_number_of(slide),
                "shapes": shapes,
            }
        )
    return out


def notes_for(
    slides: list[dict],
    available: dict[int, str],
    mismatches: list[dict],
    fills: dict[str, int],
) -> list[str]:
    notes = []
    # Verboden layouts, op NAAM. Op nummer melde dit elke slide van een vreemd deck op
    # `slideLayout23.xml` als verboden, ook als die layout daar 'Titel, subtitel' heet en
    # dus juist onze norm-contentslide is.
    forbidden = defaultdict(list)
    for record in slides:
        if forbidden_reason(record["layout_name"]) is not None:
            forbidden[record["layout_name"]].append(record["pos"])
    for name, positions in sorted(forbidden.items()):
        what, advice = forbidden_reason(name)
        places = ", ".join(str(p) for p in positions)
        notes.append(
            f"slide {places} staat op de verboden layout ‘{name}’ ({what}). {advice}. "
            "Bouw nieuwe slides hier NOOIT op na; meld het en bouw op 19."
        )

    onbekend = sorted(
        {
            record["layout_name"]
            for record in slides
            if record["layout_name"] and record["layout_name"] not in LAYOUT_POLICY
        }
    )
    if onbekend:
        notes.append(
            "deze layoutnamen staan in geen enkele beleidsregel: "
            + ", ".join(f"‘{name}’" for name in onbekend)
            + f" — verdict `{UNKNOWN_VERDICT}`. Die slides komen niet uit het "
            "SFNL-sjabloon, dus er is geen verdict om aan te houden en de layoutnummers "
            "uit layouts.md wijzen hier iets anders aan. Beoordeel ze op wat er staat en "
            "bouw nieuwe slides op de norm-contentlayout ‘Titel, subtitel’."
        )

    missing = sorted(
        number for number in (17, 19, 20, 21, 22) if number not in available
    )
    if missing:
        notes.append(
            "layouts "
            + ", ".join(str(n) for n in missing)
            + " zitten niet meer in het pakket (deck geslankt met clean.py "
            "--drop-unused-layouts). add_slide.py kan die layout niet instantiëren: "
            "dupliceer een bestaande slide met duplicate_slide.py, of vul aan uit het "
            "sjabloon."
        )
    if mismatches:
        notes.append(
            f"{len(mismatches)} layoutnaam wijkt af van de catalogus — deze deck komt "
            "waarschijnlijk niet uit het huidige SFNL-sjabloon. Controleer voordat je "
            "layoutnummers uit layouts.md gebruikt."
        )
    if any(descriptor.startswith(DEPRECATED_FILL) for descriptor in fills):
        notes.append(
            f"de deck vult vlakken met `{DEPRECATED_FILL}` (#C6C3ED lavendel), het recept "
            "dat xml-editing.md afkeurt. Voor aansluiting bij de bestaande slides mag je "
            "het aanhouden — zeg dan tegen de gebruiker dat de deck op dat punt afwijkt "
            "van het palet en bied navy-tint (dk2 lum10/90) aan als alternatief."
        )
    return notes


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("deck")
    parser.add_argument(
        "--slides",
        help="komma-gescheiden deckposities: geef per vorm geometrie, vulling en font",
    )
    parser.add_argument(
        "--text",
        action="store_true",
        help="in de detailweergave de volledige tekst per vorm, niet afgekapt",
    )
    args = parser.parse_args()

    path = Path(args.deck)
    if not path.exists():
        raise SystemExit(f"bestaat niet: {path}")

    presentation = open_deck(path)
    expected = expected_layout_names()
    available = package_layouts(presentation)
    slides, deck_level = overview(presentation, expected)

    payload = {
        "deck": str(path),
        "slide_count": len(slides),
        "slide_size_in": [
            inches(presentation.slide_width),
            inches(presentation.slide_height),
        ],
        "layouts_available": sorted(available),
        "layouts_used": sorted({record["layout"] for record in slides if record["layout"]}),
        **deck_level,
        "slides": slides,
        "reuse_candidates": reuse_candidates(slides),
        "notes": notes_for(
            slides,
            available,
            deck_level["layout_name_mismatches"],
            deck_level["fills_on_slides"],
        ),
    }

    if args.slides:
        wanted = {int(part) for part in args.slides.replace(" ", "").split(",") if part}
        unknown = sorted(number for number in wanted if number > len(slides) or number < 1)
        if unknown:
            raise SystemExit(
                f"deze deck heeft {len(slides)} slides; gevraagd: "
                + ", ".join(str(n) for n in unknown)
            )
        payload["detail"] = detail(presentation, wanted, args.text)

    emit(payload)


if __name__ == "__main__":
    main()
