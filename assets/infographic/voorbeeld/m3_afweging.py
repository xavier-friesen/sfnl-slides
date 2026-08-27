#!/usr/bin/env python3
"""Maatstaf 3 — kost tegenover baat. Vorm: divergerende staaf. Register: bijna helemaal wit.

Twee hues, en ze coderen: grapefruit is kost, emerald is baat. Alles hangt aan één nullijn in
het midden, dus de lezer ziet in één oogopslag welke kant zwaarder weegt. Geen legenda: de twee
kopjes boven de kolommen doen dat werk, in hun eigen hue.
"""
import sys
from pathlib import Path

HIER = Path(__file__).resolve()
sys.path.insert(0, str(HIER.parents[3] / "scripts" / "infographic"))
from svg import (CANVAS, Maten, blok, bron, drager, kop, label, lijn,  # noqa: E402
                 schrijf, tekst, vlak)

c = CANVAS["breed"]
m = Maten(body=13, kop=16, drager=36, voetnoot=10)

MARGE = 30
MID = c.w * 0.50                          # de nullijn, iets rechts van het midden
HALF = 290                                # maximale staaflengte per kant
STAAF = 13
RIJ = 30
TOP = 106
# Eén schaal voor alle staven, ook de totaalrij: de grootste waarde op het beeld is het
# hoogste totaal, en die vult de halve breedte. Een aparte schaal voor de totaalrij zou
# korter ogen maar is een leugen -- dat was de eerste versie, en de balken liepen het
# canvas uit.
SCHAAL = 1180.0

KOST = [("Begeleiding op de werkvloer", 624),
        ("Taal en basisvaardigheden", 312),
        ("Coördinatie en meting", 168)]
BAAT = [("Uitkeringen die wegvallen", 700),
        ("Minder zorgkosten", 296),
        ("Belasting en premies", 184)]
# 1.104 tegen 1.180, dus een saldo van + 76k. De drager is uitgerekend en niet verzonnen:
# in de eerste versie stond er "+ € 0,04 mln" terwijl de posten optelden tot een tekort.

vormen = [
    blok("Aanhef", MARGE, 24, 460,
         [label("WAT HET KOST, EN WAT HET OPLEVERT", 10, "navy", dekking=0.55)]),
    blok("Kop kost", MID - HALF, 58, HALF - 14,
         [kop("KOSTEN", 18, "grapefruit")]),
    blok("Kop baat", MID + 14, 58, HALF - 14,
         [kop("OPBRENGSTEN", 18, "emerald")]),
]

for i, ((kn, kv), (bn, bv)) in enumerate(zip(KOST, BAAT)):
    y = TOP + i * RIJ
    kl, bl = kv / SCHAAL * HALF, bv / SCHAAL * HALF
    vormen += [
        vlak(f"Kost {i} staaf", MID - kl, y, kl, STAAF, vulling="grapefruit", lijn_=None),
        vlak(f"Baat {i} staaf", MID, y, bl, STAAF, vulling="emerald", lijn_=None),
        blok(f"Kost {i} naam", MID - HALF, y - 15, HALF - 12,
             [tekst(kn, m.body, "navy", dekking=0.75, algn="end")]),
        blok(f"Baat {i} naam", MID + 12, y - 15, HALF - 12,
             [tekst(bn, m.body, "navy", dekking=0.75)]),
        blok(f"Kost {i} getal", MID - kl - 90, y - 1, 82,
             [kop(f"€ {kv / 1000:.2f}".replace(".", ",") + " mln", m.body, "navy",
                  algn="end")], anchor="t"),
        blok(f"Baat {i} getal", MID + bl + 8, y - 1, 82,
             [kop(f"€ {bv / 1000:.2f}".replace(".", ",") + " mln", m.body, "navy")],
             anchor="t"),
    ]

# ---- de totaalrij, en die is er niet voor de volledigheid maar omdat het saldo anders een
# bewering is die je op je woord moet geloven. Nu staat het verschil er als lengte.
tot_k, tot_b = sum(v for _, v in KOST), sum(v for _, v in BAAT)
y_tot = TOP + len(KOST) * RIJ + 16
kl, bl = tot_k / SCHAAL * HALF, tot_b / SCHAAL * HALF
vormen += [
    lijn("Totaalstreep", MID - kl - 4, y_tot - 8, MID + bl + 4, y_tot - 8,
         kleur="navy", dikte=0.75, dekking=0.30),
    vlak("Totaal kost", MID - kl, y_tot, kl, STAAF + 4, vulling="grapefruit", lijn_=None),
    vlak("Totaal baat", MID, y_tot, bl, STAAF + 4, vulling="emerald", lijn_=None),
    blok("Totaal kost label", MID - kl, y_tot - 17, 200,
         [label("TOTAAL", 9, "navy", dekking=0.45)]),
    blok("Totaal baat label", MID + bl - 200, y_tot - 17, 200,
         [label("TOTAAL", 9, "navy", dekking=0.45, algn="end")]),
    blok("Totaal kost getal", MID - kl - 96, y_tot + 1, 88,
         [kop(f"€ {tot_k / 1000:.2f}".replace(".", ",") + " mln", m.kop, "navy",
              algn="end")]),
    blok("Totaal baat getal", MID + bl + 8, y_tot + 1, 88,
         [kop(f"€ {tot_b / 1000:.2f}".replace(".", ",") + " mln", m.kop, "navy")]),
]

onder = y_tot + STAAF + 4

vormen += [
    lijn("Nullijn", MID, 88, MID, onder + 2, kleur="navy", dikte=1.0, dekking=0.45),
    lijn("Slotstreep", MARGE, onder + 16, c.w - MARGE, onder + 16,
         kleur="navy", dikte=0.75, dekking=0.20),
    blok("Drager", MARGE, onder + 26, 340,
         [drager("+ € 0,08 mln", m.drager, "emerald"),
          tekst("saldo over drie jaar, per cohort van 120", m.body, "navy",
                dekking=0.65, ruimte_voor=6)]),
    blok("Sluitregel", MARGE + 300, onder + 32, c.w - MARGE - 300 - 250,
         [tekst("De opbrengst valt bij de gemeente, de kosten bij de uitvoerder. "
                "Resultaatfinanciering brengt die twee bij elkaar.", m.body, "navy",
                aanhef=("De opbrengst valt bij de gemeente", "Montserrat SemiBold"))]),
    blok("Bron", c.w - MARGE - 240, onder + 32, 240,
         [bron("Doorrekening SFNL, 2026. Prijspeil 2026.", m.voetnoot)]),
]

if __name__ == "__main__":
    uit = HIER.parents[1] / "maatstaf"
    schrijf(uit / "m3-afweging.svg", c, vormen,
            beschrijving="Drie kostenposten tegenover drie opbrengstposten aan weerszijden "
                         "van één nullijn, met het saldo als drager.")
    print("staven tot", onder, "van", c.h)
