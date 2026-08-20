"""Vervang de tekst in de vormen van een slide op naam, met behoud van de opmaak.

Usage:
    python retext_slide.py <slide.xml> --file nieuw.json
    python retext_slide.py <slide.xml> --json '{"title": "...", "Kaart 1 getal": "128"}'
    python retext_slide.py <slide.xml> --file nieuw.json --list

De JSON is `{doel: waarde}`. Een doel is:

    "title" / "subtitle" / "0" / "11"     een placeholder (zoals in set_text.py)
    "Kaart 1 getal"                       de NAAM van een vorm, zoals inspect_deck.py hem
                                          rapporteert (`name`)

Een waarde is dezelfde vorm als in `set_text.py` — een string, een lijst alinea's, of de
`{"runs": [...]}`-vorm voor vet binnen een regel — met één toevoeging: `null` verwijdert de
vorm. Dat laatste is voor de derde kaart in een rij van drie waar de nieuwe slide er twee
nodig heeft.

Waarom dit naast `set_text.py` staat
------------------------------------
`set_text.py` vult placeholders en schrijft daarbij bewust géén opmaak: font, grootte en
kleur komen uit de layout, en dat is de kern van layout-first. Het bouwt de alinea's dus
opnieuw op, met een kale `rPr`.

Een compositie in de contentzone werkt precies andersom. Daar staat de opmaak wél op de
run — `Montserrat SemiBold 32pt` op het getal, `Lato Light 14pt` op de toelichting — omdat
een eigen tekstvak niets te erven heeft. Wie zo'n vorm met `set_text.py` opnieuw vult,
houdt de goede geometrie over met de verkeerde typografie: het getal komt terug op 18pt
Lato en de kaart valt uit elkaar. Dit script kopieert daarom de bestaande `rPr` van de
eerste run en de `pPr` van de eerste alinea, en hangt de nieuwe tekst daaraan op.

Dat maakt de snelste route naar een nieuwe slide die naast de bestaande kan staan:
`duplicate_slide.py` kopieert een slide die de goede compositie al heeft, dit script zet er
andere inhoud in. Geen XML met de hand, geen geometrie opnieuw uitrekenen, geen
tintrecepten opzoeken — en per definitie dezelfde vormentaal als de rest van de deck.

Een doel dat niet bestaat is een fout, en de melding somt op wat er wél op de slide staat,
zodat de volgende aanroep meteen klopt. `--list` doet alleen dat, zonder te schrijven.

Output is compacte JSON. Groepen worden doorlopen, dus een vorm in een kaartgroep is met
zijn eigen naam te bereiken.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from lxml import etree

from _deck import emit
from set_text import A, ALIASES, NS, P, normalise, placeholder_idx


def shape_name(sp: etree._Element) -> str:
    node = sp.find(".//p:nvSpPr/p:cNvPr", NS)
    if node is None:
        node = sp.find(".//p:cNvPr", NS)
    return (node.get("name") if node is not None else "") or ""


def current_text(sp: etree._Element) -> str:
    return " ".join(
        "".join(t.text or "" for t in para.findall("a:r/a:t", NS))
        for para in sp.findall("./p:txBody/a:p", NS)
    ).strip()


def targets_of(sp: etree._Element) -> tuple[str, int | None]:
    return shape_name(sp), placeholder_idx(sp)


def write_preserving(sp: etree._Element, paragraphs: list[dict]) -> None:
    """Zet de alinea's in de vorm, met de opmaak die er al stond.

    Het model is de alinea op DEZELFDE plek: nieuwe alinea 1 krijgt de `pPr` en `rPr` van
    oude alinea 1, nieuwe alinea 2 die van oude alinea 2, en wie er meer schrijft dan er
    stonden erft van de laatste. Dat laatste is geen detail. In dit sjabloon draagt de
    eerste alinea van een kaartvak vaak de kop en de tweede de lopende tekst mét
    `spcBef` — kopieer je overal de eerste, dan plakken alle vervolgalinea's tegen elkaar:
    zichtbaar op de render, door geen enkel script gemeten.

    Staat er geen `rPr` (een placeholder die zijn opmaak uit de layout erft), dan wordt er
    ook geen geschreven: dan gedraagt dit script zich als `set_text.py` en blijft de
    erfenis intact.

    Vet: een run met `"b"` erin beslist zelf. Noemt één run in deze vorm `"b"` en een
    andere niet, dan is die andere expliciet niet vet — anders zou het vet van de
    modelalinea over de hele regel doorlopen, en dat is precies wat een bold label in een
    kaart zou doen met de toelichting erachter.
    """
    body = sp.find("./p:txBody", NS)
    if body is None:
        raise SystemExit(f"vorm zonder txBody: {shape_name(sp)!r}")

    existing = body.findall("a:p", NS)
    models: list[tuple[etree._Element | None, etree._Element | None]] = []
    for para in existing:
        ppr = para.find("a:pPr", NS)
        rpr = para.find("a:r/a:rPr", NS)
        models.append(
            (
                copy.deepcopy(ppr) if ppr is not None else None,
                copy.deepcopy(rpr) if rpr is not None else None,
            )
        )
    if not models:
        models = [(None, None)]

    end_rpr = None
    if existing:
        found = existing[-1].find("a:endParaRPr", NS)
        if found is not None:
            end_rpr = copy.deepcopy(found)

    for para in existing:
        body.remove(para)

    bold_mentioned = any(
        "b" in run for paragraph in paragraphs for run in paragraph["runs"]
    )

    for index, paragraph in enumerate(paragraphs):
        ppr_model, rpr_model = models[min(index, len(models) - 1)]
        node = etree.SubElement(body, f"{{{A}}}p")
        level = paragraph.get("lvl", 0)
        if ppr_model is not None:
            ppr = copy.deepcopy(ppr_model)
            node.append(ppr)
        elif level or paragraph.get("num"):
            ppr = etree.SubElement(node, f"{{{A}}}pPr")
        else:
            ppr = None
        if ppr is not None and level:
            ppr.set("lvl", str(level))
        if ppr is not None and paragraph.get("num"):
            if ppr.find("a:buAutoNum", NS) is None:
                etree.SubElement(ppr, f"{{{A}}}buAutoNum").set("type", "arabicPeriod")

        for run in paragraph["runs"]:
            r = etree.SubElement(node, f"{{{A}}}r")
            if rpr_model is not None:
                rpr = copy.deepcopy(rpr_model)
            else:
                rpr = etree.Element(f"{{{A}}}rPr")
                rpr.set("lang", run.get("lang", "nl-NL"))
                rpr.set("dirty", "0")
            if "b" in run:
                rpr.set("b", "1" if run.get("b") else "0")
            elif bold_mentioned:
                rpr.set("b", "0")
            r.append(rpr)
            t = etree.SubElement(r, f"{{{A}}}t")
            t.text = run.get("t", "")

        if end_rpr is not None and index == len(paragraphs) - 1:
            node.append(copy.deepcopy(end_rpr))


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("slide", type=Path)
    parser.add_argument("--json", dest="payload", help="JSON-object met de nieuwe inhoud")
    parser.add_argument("--file", type=Path, help="lees het JSON-object uit een bestand")
    parser.add_argument(
        "--list",
        action="store_true",
        help="alleen de vormen en hun huidige tekst tonen; niets schrijven",
    )
    parser.add_argument(
        "--keep-apostrophes",
        action="store_true",
        help="rechte apostrof laten staan (default: risico's -> risico’s)",
    )
    args = parser.parse_args()

    if not args.slide.exists():
        raise SystemExit(f"{args.slide} niet gevonden")

    tree = etree.parse(str(args.slide))
    root = tree.getroot()
    sp_tree = root.find(".//p:cSld/p:spTree", NS)
    shapes = list(sp_tree.iter(f"{{{P}}}sp"))

    if args.list:
        emit(
            {
                "slide": args.slide.name,
                "shapes": [
                    {
                        "name": shape_name(sp),
                        "idx": placeholder_idx(sp),
                        "text": current_text(sp),
                    }
                    for sp in shapes
                ],
            }
        )
        return

    if not args.payload and not args.file:
        raise SystemExit("geef --json, --file of --list")

    raw = args.file.read_text(encoding="utf-8") if args.file else args.payload
    content = json.loads(raw)

    # Doel -> waarde, met de placeholder-aliassen van set_text.py erin verwerkt.
    by_idx: dict[int, object] = {}
    by_name: dict[str, object] = {}
    for key, value in content.items():
        alias = ALIASES.get(str(key).lower())
        if alias is not None:
            by_idx[alias] = value
            continue
        try:
            by_idx[int(key)] = value
        except ValueError:
            by_name[str(key)] = value

    retexted, deleted, duplicates = [], [], []
    hit_names: set[str] = set()
    hit_idx: set[int] = set()

    for sp in shapes:
        name, idx = targets_of(sp)
        if name in by_name:
            if name in hit_names:
                duplicates.append(name)
                continue
            value = by_name[name]
            hit_names.add(name)
        elif idx is not None and idx in by_idx:
            value = by_idx[idx]
            hit_idx.add(idx)
        else:
            continue

        label = name or f"idx {idx}"
        if value is None:
            sp.getparent().remove(sp)
            deleted.append(label)
            continue

        paragraphs = normalise(value)
        if not args.keep_apostrophes:
            from _deck import normalise_apostrophes

            for paragraph in paragraphs:
                for run in paragraph["runs"]:
                    run["t"] = normalise_apostrophes(run.get("t", ""))
        write_preserving(sp, paragraphs)
        retexted.append(label)

    missing = sorted(set(by_name) - hit_names) + [
        f"idx {number}" for number in sorted(set(by_idx) - hit_idx)
    ]
    if missing:
        available = ", ".join(
            f"{shape_name(sp)!r}" + (f" (idx {placeholder_idx(sp)})" if placeholder_idx(sp) is not None else "")
            for sp in shapes
        )
        raise SystemExit(
            f"niet gevonden op {args.slide.name}: {', '.join(missing)}. "
            f"Op deze slide staan: {available}. Niets geschreven."
        )

    tree.write(str(args.slide), xml_declaration=True, encoding="UTF-8", standalone=True)
    emit(
        {
            "slide": args.slide.name,
            "retexted": retexted,
            "deleted": deleted,
            "duplicate_names_skipped": sorted(set(duplicates)),
        }
    )


if __name__ == "__main__":
    main()
