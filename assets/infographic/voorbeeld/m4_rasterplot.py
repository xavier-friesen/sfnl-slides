#!/usr/bin/env python3
"""Maatstaf 4 — één verhouding, zo groot mogelijk. Vorm: rasterplot. Canvas: vierkant.

Honderdtwintig vierkantjes, eenenzeventig gevuld. Dat is de hele infographic. Geen kader, geen
kaart, geen band: het raster zelf is de vorm en de witruimte eromheen doet het werk.

Dit is de maatstaf voor "zo min mogelijk". Wie hier iets aan toevoegt maakt hem slechter.
"""
import sys
from pathlib import Path

HIER = Path(__file__).resolve()
sys.path.insert(0, str(HIER.parents[3] / "scripts" / "infographic"))
from svg import (CANVAS, Maten, blok, bron, drager, kop, label, lijn,  # noqa: E402
                 schrijf, tekst, vlak)

c = CANVAS["vierkant"]                    # 560 x 560pt
m = Maten(body=13, kop=16, drager=40, voetnoot=10)

MARGE = 34
KOL, RIJ = 12, 10                         # 120 deelnemers
GEVULD = 71
CEL = 26
BLOK = 18                                 # het vierkantje zelf; de rest is lucht
RASTER_Y = 202

vormen = [
    blok("Aanhef", MARGE, 40, c.w - 2 * MARGE,
         [label("VAN DE 120 DEELNEMERS", 10, "navy", dekking=0.55)]),
    blok("Drager", MARGE, 62, c.w - 2 * MARGE,
         [drager("71 aan het werk", m.drager, "oranje"),
          tekst("twaalf maanden na start, onafhankelijk vastgesteld", m.body, "navy",
                dekking=0.65, ruimte_voor=8)]),
    lijn("Streep", MARGE, RASTER_Y - 34, c.w - MARGE, RASTER_Y - 34,
         kleur="navy", dikte=0.75, dekking=0.20),
]

for i in range(KOL * RIJ):
    r, k = divmod(i, KOL)
    aan = i < GEVULD
    vormen.append(vlak(
        f"Deelnemer {i+1}", MARGE + k * CEL, RASTER_Y + r * CEL, BLOK, BLOK,
        vulling="oranje" if aan else ("navy", 0.12), lijn_=None))

onder = RASTER_Y + RIJ * CEL - (CEL - BLOK)

vormen += [
    blok("Legenda aan", MARGE, onder + 20, 200,
         [tekst("71 aan het werk", m.body, "navy", dekking=0.75)]),
    blok("Legenda uit", MARGE + 200, onder + 20, 200,
         [tekst("49 niet", m.body, "navy", dekking=0.45)]),
    blok("Sluitregel", MARGE, onder + 46, c.w - 2 * MARGE,
         [tekst("De gemeente betaalt per deelnemer die werkt, en niets voor de rest.",
                m.body, "navy", aanhef=("De gemeente betaalt", "Montserrat SemiBold"))]),
    blok("Bron", MARGE, c.h - 14, c.w - 2 * MARGE,
         [bron("Meting cohort 1, Zaanstad, september 2025.", m.voetnoot)]),
]

if __name__ == "__main__":
    uit = HIER.parents[1] / "maatstaf"
    schrijf(uit / "m4-rasterplot.svg", c, vormen,
            beschrijving="Honderdtwintig vierkantjes waarvan eenenzeventig gevuld: het "
                         "aandeel deelnemers dat na twaalf maanden werkt.")
    print("raster tot", onder, "van", c.h)
