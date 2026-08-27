#!/usr/bin/env python3
"""PLAN en GLOBAL van `deck-check`: lees de deck, schrijf niets, plan alles.

Usage:
    python plan.py <deck.pptx>
    python plan.py <deck.pptx> --json plan.json      # het plan ook wegschrijven
    python plan.py <deck.pptx> --taal nl             # de deckmeerderheid overrulen

Dit script leest een bestaande .pptx en levert één plan op: per alinea de tekst zoals
hij is, de tekst zoals hij wordt, de regels die dat verklaren, en daarnaast alle
vlaggen die geen tekstwijziging zijn. Het schrijft **niets** in de deck. Dat doet
`toepassen.py`, en die neemt dit plan als enige input.

Waarom die scheiding er is: een fixer die tijdens het lezen al schrijft, ziet de
deckbrede uitkomsten (de meerderheidstaal, de uitlijning per rol, de terminologie) pas
nadat hij de eerste tien slides al heeft aangepast. Dan gelden er twee regimes in één
bestand. Dus: PLAN leest per slide, GLOBAL beslist wat alleen over de hele deck te
beslissen is, en pas APPLY schrijft.

Wat dit script NIET doet, omdat het al bestaat:

* restplaceholders, `{{MARKER}}`, sjabloonprompts, Calibri, harde hex, autofit, een
  titel in onderkast, de drager buiten zijn band — `scripts/qa_text.py`
* maten per rol, twee letterfamilies in één alinea, de hoge punt, bandfrequentie,
  exhibits bij cijfers, woorden per slide — `scripts/qa_tellingen.py`
* of de titel met het echte Gotham Bold past — `scripts/fit_title.py --check`
* wat er op de slides staat en welke vormen hoe heten — `scripts/inspect_deck.py`

De vorm van de uitvoer:

    {"deck", "slides", "taal", "notities": [1, 4],
     "opmerkingen": {"totaal", "open", "opgelost", "lijst": [...]},
     "plan": [{"adres": {...}, "slide", "rol", "origineel", "nieuw",
               "regels": [...], "runs": [{"i", "nieuw"}]}],
     "vlaggen": [{"slide", "vlag", "tekst", "detail"}],
     "tellingen": {...}}

Een vlag is nooit een tekstwijziging en blokkeert nooit. Het oordeel over vorm komt van
de render (`scripts/render.py`, `scripts/thumbnail.py`) en van `deck-visual-reviewer`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _deck import (  # noqa: E402
    EMU_PER_INCH,
    NS,
    _ppr_chain,
    emit,
    open_deck,
    resolve_paragraph,
    resolve_run,
    role_of,
    shape_type_name,
)
from shapes import hoogte_van  # noqa: E402
from tekstregels import (  # noqa: E402
    niet_lopende_zin,
    schoon_run,
    taal_van,
)

# Uitlijningstolerantie tussen een placeholder op de slide en dezelfde placeholder in
# de layout. 0,08 in is ongeveer 2 mm: daaronder ziet niemand het, daarboven staat de
# titelrij van de deck niet meer op één lijn.
POSITIE_TOLERANTIE_IN = 0.08

# Regelafstand buiten deze band komt uit een kopieerslag en niet uit een besluit; de
# norm zelf staat in `reference/vormentaal.md` §9. De waarde is een verhouding, zoals
# `resolve_paragraph()` hem geeft: 1,12 is 112 procent.
REGELAFSTAND_MIN, REGELAFSTAND_MAX = 0.90, 1.50
ALINEARUIMTE_MAX_PT = 24.0

# Insets die PowerPoint gebruikt als het tekstvak ze niet zelf zet.
DEFAULT_INSETS_IN = (0.1, 0.1, 0.05, 0.05)

CONTENT_LAYOUTS = {19, 20, 21, 22}

# Een `{{MARKER}}` of een sjabloonprompt is geen tekst om op te schonen maar een
# restplaceholder, en `scripts/qa_text.py` meldt hem als `critical`. De tekstregels gaan
# er dus niet over heen: kapitaliseren van `{{SUBTITEL}}` levert een bevinding op over
# tekst die er hoort te verdwijnen.
RESTPLACEHOLDER = re.compile(r"\{\{[A-Z0-9 _-]{2,40}\}\}")

HANDMATIG_NUMMER = re.compile(r"^\s*(\d{1,2}[.)]|[a-z][.)])\s+")
HANDMATIGE_BULLET = re.compile(r"^\s*[-•*▪·]\s+")

FORMAAT_CHECKS = (
    ("formaat-euroteken", re.compile(r"\bEUR\b"),
     "reference/voice.md: het euroteken, niet EUR"),
    ("formaat-procent", re.compile(r"\d\s+%"),
     "reference/voice.md: het procentteken direct achter het getal"),
    ("formaat-decimaal", re.compile(r"\b\d+\.\d{1,2}\b(?!\.\d)"),
     "reference/voice.md: decimalen met een komma, duizendtallen met een punt"),
    ("formaat-duizendtal", re.compile(r"(?<![\d.,])\d{5,}(?![\d.,])"),
     "reference/voice.md: duizendtallen met een punt"),
)

WOORD = re.compile(r"[^\W\d_]{4,}", re.UNICODE)


# ---------------------------------------------------------------------------
# Deckniveau: notities en opmerkingen
# ---------------------------------------------------------------------------

def notities(presentation) -> list[int]:
    gevonden = []
    for nummer, slide in enumerate(presentation.slides, start=1):
        try:
            if slide.has_notes_slide and slide.notes_slide.notes_text_frame.text.strip():
                gevonden.append(nummer)
        except (AttributeError, KeyError):
            continue
    return gevonden


def opmerkingen(presentation) -> dict:
    """Open en opgeloste opmerkingen per slide, uit de commentaardelen van het pakket.

    PowerPoint kent twee vormen: de klassieke `ppt/comments/comment*.xml` en de
    moderne `modernComment`-delen. Beide hangen als relationship aan de slide, dus de
    slide is bekend zonder het pakket af te struinen. Een opmerking is opgelost zodra
    het element `status="resolved"` of `resolved="1"` draagt; de klassieke vorm kent
    dat niet en is dus altijd open.
    """
    from lxml import etree

    lijst: list[dict] = []
    for nummer, slide in enumerate(presentation.slides, start=1):
        for rel in slide.part.rels.values():
            naam = str(getattr(rel.target_part, "partname", ""))
            if "comment" not in naam.lower():
                continue
            try:
                boom = etree.fromstring(rel.target_part.blob)
            except (etree.XMLSyntaxError, AttributeError):
                continue
            for element in boom.iter():
                tag = etree.QName(element).localname
                if tag not in {"cm", "comment"}:
                    continue
                status = (element.get("status") or "").lower()
                opgelost = status == "resolved" or element.get("resolved") in {"1", "true"}
                tekst = " ".join(
                    (t.text or "") for t in element.iter()
                    if etree.QName(t).localname in {"t", "text"}
                ).strip()
                if not tekst:
                    tekst = (element.findtext("./{*}text") or "").strip()
                lijst.append({
                    "slide": nummer,
                    "auteur": element.get("authorId") or element.get("author") or "",
                    "tekst": tekst[:300],
                    "opgelost": opgelost,
                })
    return {
        "totaal": len(lijst),
        "open": sum(1 for c in lijst if not c["opgelost"]),
        "opgelost": sum(1 for c in lijst if c["opgelost"]),
        "lijst": lijst,
    }


# ---------------------------------------------------------------------------
# Vormen doorlopen, met een adres dat `toepassen.py` terugvindt
# ---------------------------------------------------------------------------

def vormen_van(slide) -> list[tuple[object, list[int]]]:
    """Alle vormen met tekst, plat, met het pad van vorm-id's erbij."""
    uit: list[tuple[object, list[int]]] = []

    def loop(container, pad):
        for shape in container:
            eigen = pad + [int(getattr(shape, "shape_id", 0) or 0)]
            if shape_type_name(shape).startswith("GROUP"):
                loop(shape.shapes, eigen)
                continue
            uit.append((shape, eigen))

    loop(slide.shapes, [])
    return uit


def doos_in_inch(shape) -> tuple[float, float, float, float] | None:
    try:
        if None in (shape.left, shape.top, shape.width, shape.height):
            return None
        return (shape.left / EMU_PER_INCH, shape.top / EMU_PER_INCH,
                shape.width / EMU_PER_INCH, shape.height / EMU_PER_INCH)
    except (AttributeError, TypeError):
        return None


def layoutnummer(slide) -> int | None:
    match = re.search(r"slideLayout(\d+)\.xml", str(slide.slide_layout.part.partname))
    return int(match.group(1)) if match else None


def rollen(slide) -> dict[int, str]:
    """Rol per vorm-id: `title`, `subtitle`, `body`.

    Twee passes, zoals de bron ze had. Pass A wijst titel en subtitel aan: eerst op
    placeholdertype, en alleen als er geen subtitelplaceholder is op de heuristiek —
    een korte, brede regel onder de titel in de bovenste 35 procent van de slide.
    Pass B is daarna kort: alles wat geen titel en geen subtitel is, is body — de
    positiegrens uit de bron doet daar geen werk meer, want er is geen vierde rol om
    naartoe te wijken. In dit sjabloon is idx 1 de subtitel, dus de heuristiek slaat
    vrijwel nooit aan; hij staat er voor decks die niet uit het sjabloon komen.
    """
    hoogte = 7.5
    try:
        hoogte = slide.part.package.presentation_part.presentation.slide_height / EMU_PER_INCH
    except (AttributeError, TypeError):
        pass

    uit: dict[int, str] = {}
    titel_onder = None
    for shape, pad in vormen_van(slide):
        rol = role_of(shape)
        if rol in {"title", "subtitle"}:
            uit[pad[-1]] = rol
            doos = doos_in_inch(shape)
            if doos and rol == "title":
                titel_onder = doos[1] + doos[3]

    if "subtitle" not in uit.values():
        for shape, pad in vormen_van(slide):
            if pad[-1] in uit or not getattr(shape, "has_text_frame", False):
                continue
            tekst = shape.text_frame.text.strip()
            doos = doos_in_inch(shape)
            if not tekst or not doos:
                continue
            if "subtitel" in tekst.lower() or "subtitle" in tekst.lower():
                uit[pad[-1]] = "subtitle"
                break
            onder_titel = titel_onder is not None and doos[1] >= titel_onder - 0.05
            bovenzone = doos[1] < hoogte * 0.35
            kort = len(tekst) <= 120 and tekst.count("\n") <= 1
            breed = doos[2] > 4.0
            if onder_titel and bovenzone and kort and breed:
                uit[pad[-1]] = "subtitle"
                break

    for shape, pad in vormen_van(slide):
        if pad[-1] not in uit:
            uit[pad[-1]] = "body"
    return uit


# ---------------------------------------------------------------------------
# Alinea's: lijstitem, bullets, nummering
# ---------------------------------------------------------------------------

def bullet_van(shape, paragraph) -> tuple[str | None, bool]:
    """(bulletteken of `auto`/`geen`, of de alinea een lijstitem is).

    De vraag "is dit een lijstitem" moet uit de erfketen komen en niet uit een aanname
    over idx: de tekstplaceholders van de cover (idx 13 en 14) dragen `buNone` uit de
    layout en zijn dus geen lijst, terwijl de contentzone van layout 20 wél een bullet
    erft. `_ppr_chain()` uit `_deck.py` is precies die keten, nearest first, dus het
    eerste bullet-element dat je tegenkomt is het element dat PowerPoint gebruikt.
    """
    keten = _ppr_chain(shape, paragraph, paragraph.level or 0)
    for node in keten:
        if node.find("a:buNone", NS) is not None:
            return "geen", False
        if node.find("a:buAutoNum", NS) is not None:
            return "auto", True
        char = node.find("a:buChar", NS)
        if char is not None:
            return char.get("char") or "?", True
    return None, False


def insets_in(shape) -> tuple[float, float, float, float]:
    frame = shape.text_frame
    waarden = []
    for attr, standaard in zip(
        ("margin_left", "margin_right", "margin_top", "margin_bottom"),
        DEFAULT_INSETS_IN,
    ):
        emu = getattr(frame, attr, None)
        waarden.append(emu / EMU_PER_INCH if emu is not None else standaard)
    return tuple(waarden)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# PLAN
# ---------------------------------------------------------------------------

def analyse(pad: Path, taal_override: str | None = None) -> dict:
    presentation = open_deck(pad)
    plan: list[dict] = []
    vlaggen: list[dict] = []
    taalstemmen: Counter = Counter()
    per_slide_taal: dict[int, Counter] = defaultdict(Counter)
    uitlijning: dict[str, Counter] = defaultdict(Counter)
    uitlijning_plek: list[tuple[str, str, int, dict]] = []
    bulletglyphs: Counter = Counter()
    termen: dict[str, Counter] = defaultdict(Counter)
    tabellen = grafieken = 0

    def vlag(slide: int, naam: str, tekst: str = "", detail: str = "") -> None:
        vlaggen.append({"slide": slide, "vlag": naam, "tekst": tekst[:200],
                        "detail": detail})

    # ---------- pass 1: lezen en per element plannen ----------
    ruwe_elementen: list[dict] = []

    for nummer, slide in enumerate(presentation.slides, start=1):
        layout = layoutnummer(slide)
        rol_per_id = rollen(slide)
        layout_dozen = {}
        for ph in slide.slide_layout.placeholders:
            try:
                layout_dozen[ph.placeholder_format.idx] = doos_in_inch(ph)
            except (AttributeError, ValueError):
                continue

        heeft_titel = False
        for shape in slide.shapes:
            if getattr(shape, "has_table", False) and shape.has_table:
                tabellen += 1
            if getattr(shape, "has_chart", False) and shape.has_chart:
                grafieken += 1
                chart = shape.chart
                if not (chart.has_title and chart.chart_title.text_frame.text.strip()):
                    vlag(nummer, "grafiektekst-niet-bewerkbaar",
                         getattr(shape, "name", "?"),
                         "de grafiek draagt geen titel die via het tekstmodel te "
                         "bereiken is; wat in het beeld staat is niet te controleren")

        for shape, vormpad in vormen_van(slide):
            rol = rol_per_id.get(vormpad[-1], "body")
            if rol == "title":
                heeft_titel = True

            # Placeholder die verschoven is ten opzichte van zijn eigen layout.
            if getattr(shape, "is_placeholder", False):
                try:
                    idx = shape.placeholder_format.idx
                except (AttributeError, ValueError):
                    idx = None
                doos, layoutdoos = doos_in_inch(shape), layout_dozen.get(idx)
                if doos and layoutdoos:
                    dx, dy = abs(doos[0] - layoutdoos[0]), abs(doos[1] - layoutdoos[1])
                    if max(dx, dy) > POSITIE_TOLERANTIE_IN:
                        vlag(nummer, f"positie-afwijkend-{rol}",
                             getattr(shape, "name", "?"),
                             f"staat {dx:.2f} in naar rechts en {dy:.2f} in lager dan "
                             "dezelfde placeholder in de layout "
                             "(`reference/sjabloon.md`, De placeholders per layout)")

            if not getattr(shape, "has_text_frame", False) and not (
                getattr(shape, "has_table", False) and shape.has_table
            ):
                continue

            for frame, cel in tekstkaders(shape):
                for a_index, paragraph in enumerate(frame.paragraphs):
                    runs = list(paragraph.runs)
                    if not runs:
                        continue
                    glyph, lijstitem = bullet_van(shape, paragraph)
                    if glyph and glyph not in {"geen", "geerfd", "auto"}:
                        bulletglyphs[glyph] += 1
                    origineel = "".join(r.text or "" for r in runs)
                    if RESTPLACEHOLDER.search(origineel):
                        vlag(nummer, "restplaceholder", origineel[:80],
                             "een niet-gevulde placeholder uit de bouw. De tekstregels "
                             "gaan hier niet over heen; `scripts/qa_text.py` meldt hem "
                             "als critical en de reparatie is vullen of verwijderen "
                             "(`scripts/clean.py`).")
                        continue
                    ruwe_elementen.append({
                        "slide": nummer, "layout": layout, "rol": rol,
                        "shape": shape, "vormpad": vormpad, "cel": cel,
                        "frame": frame, "alinea": a_index, "paragraph": paragraph,
                        "runs": runs, "origineel": origineel, "lijstitem": lijstitem,
                        "glyph": glyph,
                    })
                    stem = taal_van(origineel)
                    if stem:
                        taalstemmen[stem] += 1
                        per_slide_taal[nummer][stem] += len(origineel.split())
                    # Termen alleen uit de body: een titel en een kapitaallabel staan
                    # per regel in kapitalen (`reference/voice.md`), dus `NIET` naast
                    # `niet` is geen inconsistente term maar de zetting.
                    if rol == "body":
                        for woord in WOORD.findall(origineel):
                            if not woord.isupper():
                                termen[sleutel(woord)][woord] += 1
                    # Uitlijning in een TABEL is per kolom een ontwerpbesluit — de
                    # labelkolom links, de getallen rechts — dus die telt hier niet mee.
                    if paragraph.alignment is not None and cel is None:
                        naam = str(paragraph.alignment).split()[0]
                        uitlijning[rol][naam] += 1
                        uitlijning_plek.append((rol, naam, nummer, {
                            "vorm": getattr(shape, "name", "?"),
                            "tekst": origineel[:80],
                        }))

            if getattr(shape, "has_text_frame", False):
                controleer_zetting(shape, nummer, vlag)
                if rol == "body" and layout in CONTENT_LAYOUTS | {17}:
                    controleer_overloop(shape, nummer, vlag)

        if layout in CONTENT_LAYOUTS and not heeft_titel:
            vlag(nummer, "geen-titel", "",
                 "een contentslide zonder titel: de bewering van de slide staat "
                 "nergens (`reference/voice.md`, Titels). Een ontbrekende SUBTITEL is "
                 "nooit een bevinding.")

    # ---------- GLOBAL ----------
    deck_taal = taal_override or (
        taalstemmen.most_common(1)[0][0] if taalstemmen else "nl"
    )

    for slide_nr, telling in per_slide_taal.items():
        totaal = sum(telling.values())
        if totaal >= 8 and len(telling) == 2:
            klein = min(telling.values())
            if klein / totaal >= 0.25:
                vlag(slide_nr, "gemengde-taal", "",
                     f"{telling['nl']} woorden Nederlands en {telling['en']} woorden "
                     "Engels op één slide")

    for rol, telling in uitlijning.items():
        if len(telling) < 2:
            continue
        meest = telling.most_common(1)[0][0]
        for r, naam, slide_nr, detail in uitlijning_plek:
            if r == rol and naam != meest:
                vlag(slide_nr, f"uitlijning-afwijkend-{rol}", detail["tekst"],
                     f'"{detail["vorm"]}" staat op {naam.lower()} terwijl {rol} in de '
                     f"rest van de deck {meest.lower()} is. Niet gecorrigeerd: "
                     "uitlijning is een compositiebesluit "
                     "(`reference/vormentaal.md` §7).")

    if len(bulletglyphs) > 1:
        vlag(0, "bullet-glyph-inconsistent", "",
             "de deck gebruikt meer dan één bulletteken: "
             + ", ".join(f"{k} ({v}x)" for k, v in bulletglyphs.most_common())
             + ". Niet gecorrigeerd: een bulletteken op de slide overschrijft de "
               "layout, en dat is layout-first opgeven voor een teken.")

    for varianten in termen.values():
        vormen = [v for v, n in varianten.items() if n >= 1]
        if len(vormen) < 2:
            continue
        if len({v[1:] for v in vormen}) == 1:
            continue  # alleen een beginhoofdletter: gewone zinsopbouw
        totaal = sum(varianten.values())
        if totaal < 3:
            continue
        vlag(0, "termconsistentie", " / ".join(sorted(vormen)),
             "dezelfde term staat er in meer dan één schrijfwijze "
             + ", ".join(f"{v} ({n}x)" for v, n in varianten.most_common()))

    # Eindinterpunctie op een losse regel is een CONSISTENTIEvraag en geen merkregel.
    # Voor de titel en de subtitel staat de regel in `reference/voice.md` en voor een
    # lijstitem in `reference/vormentaal.md` §9; voor een losse regel in een blok zonder
    # bullets staat hij nergens, en dan is de enige toets of de deck het overal
    # hetzelfde doet. Dus: tellen, en de minderheid melden zonder iets te veranderen.
    alineas_per_element: Counter = Counter()
    for item in ruwe_elementen:
        alineas_per_element[(item["slide"], tuple(item["vormpad"]), str(item["cel"]))] += 1

    losse: dict[bool, list[dict]] = {True: [], False: []}
    for item in ruwe_elementen:
        sleutel_el = (item["slide"], tuple(item["vormpad"]), str(item["cel"]))
        kaal = item["origineel"].strip()
        losstaand = alineas_per_element[sleutel_el] >= 2 or item["cel"] is not None
        if (item["rol"] != "body" or item["lijstitem"] or not kaal
                or not losstaand or len(kaal) > 80
                or re.search(r"[.!?]\s+\S", kaal)):
            continue
        losse[kaal.endswith(".")].append(item)
    if losse[True] and losse[False]:
        minderheid = min(losse.values(), key=len)
        if len(minderheid) / (len(losse[True]) + len(losse[False])) <= 0.4:
            hoe = "mét" if minderheid is losse[True] else "zónder"
            for item in minderheid:
                vlag(item["slide"], "eindinterpunctie-inconsistent",
                     item["origineel"][:80],
                     f"deze losse regel eindigt {hoe} punt en de "
                     f"{len(losse[True]) + len(losse[False]) - len(minderheid)} andere "
                     "losse regels in de deck doen het omgekeerd. Niet gecorrigeerd: "
                     "welke van de twee de deck aanhoudt, is een keuze — maar één van "
                     "de twee.")

    # ---------- pass 2: de tekst per run, met de deckbrede taal erbij ----------
    formaten: dict[str, list[int]] = defaultdict(list)

    for item in ruwe_elementen:
        taal = taal_van(item["origineel"]) or deck_taal
        nieuwe_runs: list[dict] = []
        labels: list[str] = []
        laatste_index = len(item["runs"]) - 1
        for i, run in enumerate(item["runs"]):
            nieuw, gevonden = schoon_run(
                run.text or "", rol=item["rol"], taal=taal,
                laatste=(i == laatste_index), lijstitem=item["lijstitem"],
            )
            for label in gevonden:
                if label not in labels:
                    labels.append(label)
            if nieuw != (run.text or ""):
                nieuwe_runs.append({"i": i, "nieuw": nieuw})

        nieuw_totaal = "".join(
            next((r["nieuw"] for r in nieuwe_runs if r["i"] == i), run.text or "")
            for i, run in enumerate(item["runs"])
        )

        if niet_lopende_zin(item["origineel"]):
            labels.append("niet-lopende-zin-gemeld")
        if HANDMATIG_NUMMER.match(item["origineel"]):
            labels.append("handmatige-nummering-gemeld")
        if HANDMATIGE_BULLET.match(item["origineel"]):
            labels.append("handmatige-bullet-gemeld")
        for naam, patroon, waarom in FORMAAT_CHECKS:
            if patroon.search(item["origineel"]):
                formaten[naam].append(item["slide"])
                labels.append(f"{naam}-gemeld")

        if nieuwe_runs or labels:
            plan.append({
                "adres": {
                    "slide": item["slide"], "vormpad": item["vormpad"],
                    "cel": item["cel"], "alinea": item["alinea"],
                },
                "slide": item["slide"], "rol": item["rol"],
                "origineel": item["origineel"], "nieuw": nieuw_totaal,
                "regels": labels, "runs": nieuwe_runs,
            })

    # Lijsten: parallellie en niveausprongen, per element.
    per_element: dict[tuple, list[dict]] = defaultdict(list)
    for item in ruwe_elementen:
        if item["lijstitem"]:
            per_element[(item["slide"], tuple(item["vormpad"]), str(item["cel"]))].append(item)
    for (slide_nr, _, _), items in per_element.items():
        if len(items) == 1:
            vlag(slide_nr, "enkel-lijstitem", items[0]["origineel"][:80],
                 "een lijst van één item is geen lijst")
            continue
        eerste_letters = {
            item["origineel"].strip()[:1].isupper() for item in items
            if item["origineel"].strip()
        }
        if len(eerste_letters) > 1:
            vlag(slide_nr, "bullet-parallellie", "",
                 "de items van deze lijst beginnen deels met een hoofdletter en deels "
                 "met een kleine letter")
        niveaus = [item["paragraph"].level or 0 for item in items]
        for vorige, volgende in zip(niveaus, niveaus[1:]):  # noqa: RUF007
            if volgende - vorige > 1:
                vlag(slide_nr, "bullet-niveau-sprong", "",
                     f"de lijst springt van niveau {vorige} naar {volgende}")
                break

    for naam, slides in formaten.items():
        waarom = next(w for n, _, w in FORMAAT_CHECKS if n == naam)
        vlag(0, naam, "", f"{waarom} — op slide(s) {sorted(set(slides))}")

    resultaat = {
        "deck": str(pad),
        "slides": len(presentation.slides._sldIdLst),
        "taal": deck_taal,
        "taalstemmen": dict(taalstemmen),
        "notities": notities(presentation),
        "opmerkingen": opmerkingen(presentation),
        "plan": plan,
        "vlaggen": vlaggen,
        "tellingen": {
            "elementen": len(ruwe_elementen),
            "wijzigingen": sum(1 for p in plan if p["runs"]),
            "vlaggen": len(vlaggen),
            "tabellen": tabellen,
            "grafieken": grafieken,
        },
    }
    return resultaat


def sleutel(woord: str) -> str:
    """Termen groeperen op vorm, los van accenten, koppeltekens en kapitalen."""
    kaal = unicodedata.normalize("NFKD", woord.casefold())
    kaal = "".join(c for c in kaal if not unicodedata.combining(c))
    return kaal.replace("-", "").replace("’", "").replace("'", "")


def tekstkaders(shape):
    """Yield (text_frame, cel) — cel is None of [rij, kolom] in een tabel."""
    if getattr(shape, "has_table", False) and shape.has_table:
        for r, row in enumerate(shape.table.rows):
            for c, cell in enumerate(row.cells):
                yield cell.text_frame, [r, c]
        return
    if getattr(shape, "has_text_frame", False):
        yield shape.text_frame, None


def controleer_zetting(shape, nummer: int, vlag) -> None:
    """Regelafstand en alinearuimte die uit een kopieerslag komen.

    De norm staat in `reference/vormentaal.md` §9 en wordt hier niet herhaald; wat
    hier staat is de band waarbuiten het zeker geen besluit meer is.
    """
    for paragraph in shape.text_frame.paragraphs:
        if not paragraph.runs:
            continue
        stijl = resolve_paragraph(shape, paragraph)
        pct = stijl.line_spacing_pct
        if pct is not None and not (REGELAFSTAND_MIN <= pct <= REGELAFSTAND_MAX):
            vlag(nummer, "regelafstand-extreem", paragraph.text[:80],
                 f"regelafstand {pct * 100:.0f} procent in "
                 f'"{getattr(shape, "name", "?")}" — de norm staat in '
                 "`reference/vormentaal.md` §9")
            return
        for waarde, welke in ((stijl.space_before_pt, "boven"),
                              (stijl.space_after_pt, "onder")):
            if waarde is not None and waarde > ALINEARUIMTE_MAX_PT:
                vlag(nummer, "alinearuimte-afwijkend", paragraph.text[:80],
                     f"{waarde:.0f}pt ruimte {welke} de alinea in "
                     f'"{getattr(shape, "name", "?")}"')
                return


def controleer_overloop(shape, nummer: int, vlag) -> None:
    """Schat of de tekst buiten zijn vak valt. Een vlag, nooit een blokkade.

    De meting gebruikt `hoogte_van()` uit `scripts/shapes.py` — dezelfde functie
    waarmee de bouwroute blokken op hun inhoud maat geeft, dus dezelfde regelhoogte en
    dezelfde strakheid. Die meting rekent strakker dan PowerPoint zet, en daarom staat
    de drempel op vijftien procent overschrijding: daaronder is het geen bevinding maar
    ruis.

    De titel en de subtitel gaan hier NIET langs, en de covers en dividers ook niet. De
    titelplaceholder van dit sjabloon is 0,37 in hoog en dat is smaller dan één regel
    op de titelmaat: hij hóórt te groeien, en `scripts/fit_title.py` doet dat met een
    meting op het echte Gotham Bold. Wie hem hier meeneemt, krijgt op elke slide een
    overloopvlag die geen defect is.
    """
    doos = doos_in_inch(shape)
    if not doos:
        return
    frame = shape.text_frame
    try:
        if frame.word_wrap is False:
            return
    except AttributeError:
        pass
    paras = []
    for paragraph in frame.paragraphs:
        if not paragraph.runs:
            continue
        stijl = resolve_run(shape, paragraph, paragraph.runs[0])
        paras.append((paragraph.text, stijl.size_pt, stijl.font or "Lato Light"))
    if not paras:
        return
    nodig = hoogte_van(paras, doos[2], insets=insets_in(shape))
    if nodig > doos[3] * 1.15:
        vlag(nummer, "mogelijke-overloop", paras[0][0][:80],
             f'"{getattr(shape, "name", "?")}" is {doos[3]:.2f} in hoog en de tekst '
             f"meet {nodig:.2f} in. Kijk ernaar op de render: korter schrijven of een "
             "groter vak, nooit een kleiner font "
             "(`reference/vormentaal.md` §9, noAutofit).")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck")
    parser.add_argument("--json", help="het plan ook naar dit bestand schrijven")
    parser.add_argument("--taal", choices=("nl", "en"),
                        help="de deckmeerderheid overrulen")
    args = parser.parse_args()

    resultaat = analyse(Path(args.deck), args.taal)
    if args.json:
        Path(args.json).write_text(
            json.dumps(resultaat, ensure_ascii=False, indent=1,
                       default=lambda o: str(o)),
            encoding="utf-8",
        )
        resultaat = {**resultaat, "plan": f"{len(resultaat['plan'])} regels in "
                                         f"{args.json}"}
    emit(resultaat)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
