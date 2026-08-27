#!/usr/bin/env python3
"""Maakt een SFNL-layout écht blanco: geen logo, geen paginanummer, wit vlak.

Waarom dit bestaat
------------------
`slideLayout17.xml` is zelf leeg -- 969 bytes, nul vormen. Het SFNL-logo en het paginanummer
komen uit `slideMaster2.xml`, waar ze als `Picture 4` en `Slide Number Placeholder 5` staan.
Een slide op layout 17 erft ze dus allebei, en dat is op de render te zien en niet in de XML
van de slide.

`add_slide.py --no-page-number` uit de sfnl-design plugin zet precies de vlag die je hier
nodig hebt (`showMasterSp="0"` op de layout), maar weigert op layout 17: die vlag haalt álle
mastervormen weg, dus ook het logo, en voor een deck is dat vrijwel nooit de bedoeling. Voor
een losse infographic ís het de bedoeling.

Wat dit script doet is dus één ding, en het is expres een apart script met een expliciete
naam: `showMasterSp="0"` op de genoemde layout. Alles wat de master tekent verdwijnt van elke
slide die op die layout staat. In een bestand met één slide is dat precies wat je wil.

**Gebruik dit niet op een deck.** Draai je het op een layout waar meerdere slides op staan,
dan verliezen die allemaal hun logo en hun paginanummer. Het script waarschuwt als het er meer
dan één ziet.

    python blanco.py unpacked slideLayout17.xml
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def blanco(unpacked: str | Path, layout: str = "slideLayout17.xml") -> dict:
    unpacked = Path(unpacked)
    pad = unpacked / "ppt" / "slideLayouts" / layout
    if not pad.is_file():
        raise SystemExit(f"niet gevonden: {pad}")
    s = pad.read_text(encoding="utf-8")

    if 'showMasterSp="0"' in s:
        stand = "stond al uit"
    else:
        nieuw, n = re.subn(r"(<p:sldLayout\b[^>]*?)(/?>)",
                           lambda m: m.group(1) + ' showMasterSp="0"' + m.group(2), s, count=1)
        if not n:
            raise SystemExit("geen <p:sldLayout> gevonden; is dit wel een layout?")
        s = re.sub(r'showMasterSp="0"\s+showMasterSp="0"', 'showMasterSp="0"', nieuw)
        pad.write_text(s, encoding="utf-8")
        stand = "uitgezet"

    # tellen hoeveel slides op deze layout staan -- meer dan één is bijna altijd een vergissing
    doel = layout.replace(".xml", "")
    gebruikers = []
    for rels in sorted((unpacked / "ppt" / "slides" / "_rels").glob("*.rels")):
        if doel + ".xml" in rels.read_text(encoding="utf-8"):
            gebruikers.append(rels.name.replace(".rels", ""))

    uit = {"layout": layout, "mastervormen": stand, "slides_op_deze_layout": gebruikers}
    if len(gebruikers) > 1:
        uit["waarschuwing"] = (
            f"{len(gebruikers)} slides staan op {layout}; die verliezen nu allemaal hun logo "
            "en paginanummer. Bedoeld?")
    print(uit)
    return uit


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    blanco(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "slideLayout17.xml")
