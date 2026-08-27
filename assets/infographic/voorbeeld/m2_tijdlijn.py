#!/usr/bin/env python3
"""Maatstaf 2 — een tijdlijn waarop afstand informatie draagt. Register: bijna helemaal wit.

Elke x komt uit `op_schaal()`. De twee stiltes in het verhaal -- twaalf maanden wachten op de
meting en eenentwintig maanden tot de afrekening -- zijn zichtbaar omdat ze op schaal staan,
en zij zijn de reden dat er een investeerder nodig is. Dat is de bewering, en die staat in de
maatbalk onderaan.
"""
import sys
from pathlib import Path

HIER = Path(__file__).resolve()
sys.path.insert(0, str(HIER.parents[3] / "scripts" / "infographic"))
from svg import (CANVAS, Maten, blok, bron, cirkel, drager, kop, label,  # noqa: E402
                 lijn, op_schaal, pad, schrijf, tekst)

c = CANVAS["breed"]
m = Maten(body=13, kop=18, drager=40, voetnoot=10)

MARGE = 30
AS_Y = 150
T0, T1 = 0, (2027 - 2024) * 12 + 11       # jan 2024 t/m dec 2027, in maanden


def maand(j, mm):
    return (j - 2024) * 12 + (mm - 1)


MOMENTEN = [
    (maand(2024, 1),  "boven", "Contract",   "€ 1,2 mln ingelegd",       7, "oranje"),
    (maand(2024, 3),  "onder", "Start",      "eerste 40 deelnemers",     4, "navy"),
    (maand(2024, 9),  "boven", "Cohort vol", "120 deelnemers",           5, "navy"),
    (maand(2025, 9),  "onder", "Meting",     "71 van 120 aan het werk",  6, "navy"),
    (maand(2026, 3),  "boven", "Betaling",   "€ 0,9 mln",                7, "oranje"),
    (maand(2027, 12), "onder", "Afrekening", "restbetaling",             5, "navy"),
]

X = lambda t: op_schaal(t, T0, T1, MARGE, c.w - 2 * MARGE)  # noqa: E731

vormen = [
    blok("Aanhef", MARGE, 24, 420,
         [label("VIER JAAR TUSSEN INLEG EN AFREKENING", 10, "navy", dekking=0.55)]),
    # De drager staat rechtsboven en niet in de tijdlijn: alles tussen de as en de maatbalk
    # is bezet, en een drager die daar tussen valt gaat over de labels heen. Dat gebeurde.
    blok("Drager", c.w - MARGE - 330, 18, 330,
         [drager("33 maanden", m.drager, "oranje", algn="end"),
          tekst("tussen inleg en de eerste euro terug", m.body, "navy", dekking=0.65,
                algn="end", ruimte_voor=4)]),
    lijn("As", MARGE, AS_Y, c.w - MARGE, AS_Y, kleur="navy", dikte=0.75, dekking=0.25),
]

# jaarmarkeringen op schaal, stil op de achtergrond
for jaar in (2025, 2026, 2027):
    x = X(maand(jaar, 1))
    vormen += [
        lijn(f"Jaar {jaar} tik", x, AS_Y - 5, x, AS_Y + 5, kleur="navy", dikte=0.75,
             dekking=0.25),
        blok(f"Jaar {jaar}", x - 20, AS_Y + 12, 40,
             [label(str(jaar), 9, "navy", dekking=0.40, algn="middle")]),
    ]

for i, (t, kant, titel, regel, r, hue) in enumerate(MOMENTEN):
    x = X(t)
    boven = kant == "boven"
    steel = 34
    y_punt = AS_Y - steel if boven else AS_Y + steel
    # de aanwijzer, en dan pas de tekst -- de stip zit op de as, niet bij het label
    vormen += [
        lijn(f"Steel {i}", x, AS_Y, x, y_punt, kleur=hue, dikte=1.0,
             dekking=1.0 if hue == "oranje" else 0.35),
        cirkel(f"Stip {i}", x, AS_Y, r, vulling=hue if hue == "oranje" else (hue, 0.18),
               lijn_=(hue, 1.2)),
    ]
    # links uitlijnen, behalve het laatste moment: dat lijnt rechts uit tegen de rand
    laatste = i == len(MOMENTEN) - 1
    bx, algn, bw = (x - 150, "end", 150) if laatste else (x - 4, "start", 190)
    ty = y_punt - 40 if boven else y_punt + 6
    vormen.append(blok(f"Moment {i}", bx, ty, bw, [
        kop(titel, m.kop, "oranje" if hue == "oranje" else "navy",
            algn=algn),
        tekst(regel, m.body, "navy", dekking=0.70, algn=algn, ruimte_voor=3),
    ]))

# ---- de maatbalk: de twee stiltes, op schaal, als drager
BALK_Y = 252
stiltes = [(maand(2024, 9), maand(2025, 9), "12 maanden wachten op de meting"),
           (maand(2026, 3), maand(2027, 12), "21 maanden tot de afrekening")]
for i, (a, b, txt) in enumerate(stiltes):
    xa, xb = X(a), X(b)
    vormen += [
        pad(f"Stilte {i}", f"M {xa} {BALK_Y} L {xb} {BALK_Y}", lijn_=("navy", 3.0)),
        lijn(f"Stilte {i} links", xa, BALK_Y - 5, xa, BALK_Y + 5, kleur="navy", dikte=1),
        lijn(f"Stilte {i} rechts", xb, BALK_Y - 5, xb, BALK_Y + 5, kleur="navy", dikte=1),
        blok(f"Stilte {i} label", xa, BALK_Y + 12, xb - xa,
             [tekst(txt, m.body, "navy", dekking=0.70)]),
    ]

vormen += [
    blok("Bron", MARGE, c.h - 14, c.w - 2 * MARGE,
         [bron("Monitoring Zaanstad, peildatum 1 juli 2026. Bedragen in prijspeil 2024.",
               m.voetnoot)]),
]

if __name__ == "__main__":
    uit = HIER.parents[1] / "maatstaf"
    schrijf(uit / "m2-tijdlijn.svg", c, vormen,
            beschrijving="Zes momenten in een Social Impact Bond, op schaal over vier jaar, "
                         "met de twee wachtperiodes als maatbalk.")
    print("laatste x:", X(maand(2027, 12)), "van", c.w)
