#!/usr/bin/env python3
"""APPLY van `deck-check`: voer het plan uit en lever de twee bestanden op.

Usage:
    python toepassen.py <deck.pptx> --plan plan.json --uit opgeschoond.pptx \
        --logboek wijzigingen.csv
    python toepassen.py <deck.pptx> --plan plan.json --uit x.pptx --logboek x.csv \
        --alleen-logboek        # niets schrijven in de deck, wel het logboek

Dit is de enige stap die schrijft, en hij schrijft alleen wat in het plan van
`plan.py` staat. Geen eigen regels, geen tweede ronde detectie: wat hier gebeurt is
per adres de tekst van één run vervangen. Vet, cursief, onderstreping, maat, kleur en
font blijven staan omdat de run zelf blijft staan — er wordt geen alinea opnieuw
opgebouwd.

Twee opleveringen, altijd beide:

1. het opgeschoonde `.pptx`
2. het wijzigingslogboek als CSV, met de kolommen
   `slide, origineel, nieuw, regel, toelichting`

De vijfde kolom staat er omdat een vlag zonder toelichting de lezer niets zegt: "deze
regel eindigt mét punt en de zeven andere zonder" is de bevinding, en `regel` is alleen
het label. De eerste vier kolommen zijn de kolommen van de bron.

Het logboek komt er ook als er niets veranderd is. Een lege run is een uitkomst: dan
is de deck schoon en dat is precies wat de gebruiker wil weten. Een vlag zonder
wijziging staat er met `origineel == nieuw` en de vlagnaam in `regel`, dus het logboek
is compleet en niet alleen een lijst van bewerkingen.

Na het opslaan worden de grafieken en tabellen geteld en vergeleken met het plan.
`python-pptx` herschrijft het pakket bij opslaan, en dat is de plek waar in deze repo
eerder grafieken verdwenen (`reference/sjabloon.md`, de procesval onderaan). Verdwijnt
er een, dan zegt de JSON dat en is de uitkomst niet leverbaar.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _deck import emit, open_deck, shape_type_name  # noqa: E402

KOLOMMEN = ("slide", "origineel", "nieuw", "regel", "toelichting")


def vorm_op_pad(slide, vormpad: list[int]):
    """De vorm terugvinden op het pad van vorm-id's dat `plan.py` schreef."""
    container = slide.shapes
    shape = None
    for wil in vormpad:
        shape = None
        for kandidaat in container:
            if int(getattr(kandidaat, "shape_id", 0) or 0) == wil:
                shape = kandidaat
                break
        if shape is None:
            return None
        if shape_type_name(shape).startswith("GROUP"):
            container = shape.shapes
    return shape


def kader_van(shape, cel):
    if cel is None:
        return shape.text_frame if getattr(shape, "has_text_frame", False) else None
    if not (getattr(shape, "has_table", False) and shape.has_table):
        return None
    rij, kolom = cel
    return shape.table.rows[rij].cells[kolom].text_frame


def tel_beeld(presentation) -> dict:
    grafieken = tabellen = 0
    for slide in presentation.slides:
        for shape in slide.shapes:
            if getattr(shape, "has_chart", False) and shape.has_chart:
                grafieken += 1
            if getattr(shape, "has_table", False) and shape.has_table:
                tabellen += 1
    return {"grafieken": grafieken, "tabellen": tabellen}


def toepassen(deck: Path, plan: dict, uit: Path | None) -> dict:
    presentation = open_deck(deck)
    slides = list(presentation.slides)
    toegepast = 0
    mislukt: list[dict] = []

    for regel in plan.get("plan", []):
        if not regel.get("runs"):
            continue
        adres = regel["adres"]
        nummer = adres["slide"]
        if not 1 <= nummer <= len(slides):
            mislukt.append({"adres": adres, "waarom": "slide bestaat niet"})
            continue
        shape = vorm_op_pad(slides[nummer - 1], adres["vormpad"])
        kader = kader_van(shape, adres["cel"]) if shape is not None else None
        if kader is None:
            mislukt.append({"adres": adres, "waarom": "vorm niet gevonden"})
            continue
        try:
            paragraph = kader.paragraphs[adres["alinea"]]
            runs = list(paragraph.runs)
        except IndexError:
            mislukt.append({"adres": adres, "waarom": "alinea niet gevonden"})
            continue
        if "".join(r.text or "" for r in runs) != regel["origineel"]:
            mislukt.append({"adres": adres, "waarom": "tekst is inmiddels anders"})
            continue
        for wijziging in regel["runs"]:
            runs[wijziging["i"]].text = wijziging["nieuw"]
        toegepast += 1

    beeld = tel_beeld(presentation)
    if uit is not None:
        uit.parent.mkdir(parents=True, exist_ok=True)
        presentation.save(str(uit))
        na = tel_beeld(open_deck(uit))
        if na != beeld:
            mislukt.append({"adres": None,
                            "waarom": f"beeld verloren bij opslaan: {beeld} -> {na}"})
        beeld = na

    return {"toegepast": toegepast, "mislukt": mislukt, "beeld": beeld}


def logboek(plan: dict, doel: Path) -> int:
    """Schrijf de CSV. Altijd, ook als er niets veranderd is."""
    rijen: list[tuple] = []

    for regel in plan.get("plan", []):
        gewijzigd = bool(regel.get("runs"))
        rijen.append((
            regel["slide"],
            regel["origineel"],
            regel["nieuw"] if gewijzigd else regel["origineel"],
            ";".join(regel["regels"]) or "geen-regel",
            "" if gewijzigd else "gemeld, niet gewijzigd",
        ))

    for vlag in plan.get("vlaggen", []):
        tekst = vlag.get("tekst", "")
        rijen.append((vlag["slide"], tekst, tekst, vlag["vlag"],
                      vlag.get("detail", "")))

    for opmerking in plan.get("opmerkingen", {}).get("lijst", []):
        if opmerking["opgelost"]:
            continue
        rijen.append((opmerking["slide"], opmerking["tekst"], opmerking["tekst"],
                      "open-opmerking", "onopgeloste opmerking in het bestand"))

    for nummer in plan.get("notities", []):
        rijen.append((nummer, "", "", "presentatienotitie-aanwezig",
                      "deze slide draagt een presentatienotitie"))

    tellingen = plan.get("tellingen", {})
    if tellingen.get("tabellen"):
        rijen.append((0, "", "", "tabeltekst-gecontroleerd",
                      f"{tellingen['tabellen']} tabel(len) meegenomen"))
    if tellingen.get("grafieken"):
        rijen.append((0, "", "", "grafiektekst-gecontroleerd",
                      f"{tellingen['grafieken']} grafiek(en) meegenomen"))

    doel.parent.mkdir(parents=True, exist_ok=True)
    with doel.open("w", newline="", encoding="utf-8-sig") as bestand:
        schrijver = csv.writer(bestand, delimiter=";")
        schrijver.writerow(KOLOMMEN)
        for rij in sorted(rijen, key=lambda r: (r[0], r[3])):
            schrijver.writerow(rij)
    return len(rijen)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck")
    parser.add_argument("--plan", required=True, help="de JSON van plan.py")
    parser.add_argument("--uit", help="pad van het opgeschoonde .pptx")
    parser.add_argument("--logboek", required=True, help="pad van de CSV")
    parser.add_argument("--alleen-logboek", action="store_true",
                        help="niets in de deck schrijven")
    args = parser.parse_args()

    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    uit = None if args.alleen_logboek else Path(args.uit) if args.uit else None
    if uit is None and not args.alleen_logboek:
        parser.error("geef --uit, of --alleen-logboek")

    resultaat = toepassen(Path(args.deck), plan, uit)
    aantal = logboek(plan, Path(args.logboek))

    emit({
        "deck": args.deck,
        "uit": str(uit) if uit else None,
        "logboek": args.logboek,
        "rijen": aantal,
        **resultaat,
    })
    return 1 if resultaat["mislukt"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
