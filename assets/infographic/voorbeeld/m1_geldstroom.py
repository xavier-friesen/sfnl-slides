#!/usr/bin/env python3
"""Maatstaf 1 — waar het geld heen gaat. Vorm: sankey. Register: bijna helemaal wit.

Eén accent naast navy, geen enkele containervulling, en de stroom zelf is de vorm. Dit is de
compositie waar SFNL-werk het sterkst in staat en die het minst gemaakt wordt.
"""
import sys
from pathlib import Path

HIER = Path(__file__).resolve()
sys.path.insert(0, str(HIER.parents[3] / "scripts" / "infographic"))
from svg import (CANVAS, Maten, blok, bron, drager, hoogte_van, kop, label,  # noqa: E402
                 lijn, pad, schrijf, tekst, vlak)

c = CANVAS["breed"]                       # 960 x 320pt
m = Maten(body=13, kop=16, drager=40, voetnoot=10)

MARGE = 30                                # optische marge; alleen volvlakken bloeden af
TOP = 96                                  # bovenkant van het stroomvlak
STROOM_H = 148
X_IN, X_UIT = MARGE + 200, c.w - MARGE - 232
BALK = 9

BRON = ("Investering", "€ 1,2 mln", "voorgeschoten door de investeerder")
POSTEN = [
    ("Begeleiding op de werkvloer", 0.52, "oranje"),
    ("Taal en basisvaardigheden", 0.26, "navy"),
    ("Coördinatie en meting", 0.14, "navy"),
    ("Terug naar de investeerder", 0.08, "navy"),
]

vormen = []

# ---- de bewering, links, als drager
vormen += [
    blok("Drager", MARGE, TOP - 4, 190,
         [drager("€ 1,2 mln", m.drager, "oranje"),
          tekst("werkkapitaal, drie jaar", m.body, "navy", dekking=0.65, ruimte_voor=8)]),
    lijn("Aanhef streep", MARGE, TOP - 26, MARGE + 190, TOP - 26,
         kleur="oranje", dikte=2),
    blok("Aanhef", MARGE, TOP - 48, 300, [label("WAAR HET GELD HEEN GAAT", 10, "navy",
                                                dekking=0.55)]),
]

# ---- de bronbalk
vormen.append(vlak("Bronbalk", X_IN, TOP, BALK, STROOM_H, vulling="oranje", lijn_=None))

# ---- de stromen: dikte is het aandeel, en dus de informatie
y_in = TOP
y_uit = TOP
GAT = 18
totaal_gat = GAT * (len(POSTEN) - 1)
for i, (naam, aandeel, hue) in enumerate(POSTEN):
    h_in = STROOM_H * aandeel
    h_uit = (STROOM_H - totaal_gat) * aandeel
    x1, x2 = X_IN + BALK, X_UIT
    cx = (x1 + x2) / 2
    vormen.append(pad(
        f"Stroom {i+1}",
        f"M {x1} {y_in:.1f} "
        f"C {cx} {y_in:.1f} {cx} {y_uit:.1f} {x2} {y_uit:.1f} "
        f"L {x2} {y_uit + h_uit:.1f} "
        f"C {cx} {y_uit + h_uit:.1f} {cx} {y_in + h_in:.1f} {x1} {y_in + h_in:.1f} Z",
        vulling=(hue, 0.30 if hue == "oranje" else 0.16)))
    vormen.append(vlak(f"Uitbalk {i+1}", x2, y_uit, BALK, h_uit,
                       vulling=hue, lijn_=None))
    # direct gelabeld, geen legenda
    vormen += [
        blok(f"Post {i+1} naam", x2 + BALK + 12, y_uit + h_uit / 2 - 1, 208,
             [kop(naam, m.kop if i == 0 else m.body,
                  "oranje" if i == 0 and m.kop >= 18 else "navy")], anchor="c"),
        blok(f"Post {i+1} deel", x2 - 46, y_uit + h_uit / 2 - 1, 38,
             [kop(f"{aandeel * 100:.0f}%", m.body, "navy", algn="end")], anchor="c"),
    ]
    y_in += h_in
    y_uit += h_uit + GAT

onder = max(y_in, y_uit - GAT)

vormen += [
    lijn("Slotstreep", MARGE, onder + 30, c.w - MARGE, onder + 30,
         kleur="navy", dikte=0.75, dekking=0.20),
    blok("Sluitregel", MARGE, onder + 44, c.w - 2 * MARGE - 260,
         [tekst("Ruim de helft gaat naar begeleiding op de werkvloer, want daar wordt het "
                "resultaat gehaald.", m.body, "navy",
                aanhef=("Ruim de helft", "Montserrat SemiBold"))]),
    blok("Bron", c.w - MARGE - 250, onder + 44, 250,
         [bron("Begroting Social Finance NL, 2026. Prijspeil 2026.", m.voetnoot)]),
]

if __name__ == "__main__":
    uit = HIER.parents[1] / "maatstaf"
    schrijf(uit / "m1-geldstroom.svg", c, vormen,
            beschrijving="Waar 1,2 miljoen euro werkkapitaal naartoe gaat: vier posten, "
                         "elk met zijn aandeel, als stroom getekend.")
    print("stroom tot", round(onder, 1), "van", c.h)
