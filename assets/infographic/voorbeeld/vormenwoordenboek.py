#!/usr/bin/env python3
"""Genereert het vormenwoordenboek: zesenveertig vormen, structureel, zonder kleur en zonder stijl.

Waarom dit bestaat en wat het NIET is
-------------------------------------
Dit is geen patroonbibliotheek en het is geen verzameling voorbeelden om na te maken. Er zit
geen kleur in, geen containervulling, geen kaarttaal en geen typografie -- alleen de meetkunde
van elke vorm en de vraag die hij beantwoordt. Je kunt er dus niets uit kopiëren; je kunt er
alleen mee kiezen.

Dat is precies de bedoeling. De zwakste stap in het maken van een infographic is niet de
opmaak maar de vormkeuze, en die keuze valt bijna altijd op de vorm die je het laatst hebt
gezien. Zesenveertig vormen naast elkaar, allemaal even kaal, maakt die keuze weer een keuze.

Herkomst
--------
De indeling volgt de negen categorieën van de Visual Vocabulary van de Financial Times
(Financial-Times/chart-doctor): afwijking, correlatie, rangschikking, verdeling, verandering
over tijd, deel van geheel, grootte, ruimte en stroom. Dat is de best ingeburgerde taxonomie
die er is en hij ordent op de vráág, niet op het uiterlijk.

De poster van de FT is auteursrechtelijk beschermd ("all rights reserved") en zit hier dus
niet in. Wat hier staat is opnieuw getekend, kaal, in de maten van deze skill, en beperkt tot
de vormen die in het werk van SFNL echt voorkomen. Ruimtelijke vormen (choropleth, cartogram)
zitten er niet in: die maak je niet met deze skill.

    python vormenwoordenboek.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HIER = Path(__file__).resolve()
sys.path.insert(0, str(HIER.parents[3] / "scripts" / "infographic"))
from svg import Canvas, blok, cirkel, kop, label, lijn, pad, schrijf, tekst, vlak  # noqa: E402

# Eén tegel. Alles kaal: navy voor de marks, navy op 30 procent voor assen en hulplijnen.
TB, TH = 232, 176                 # tegelbreedte en -hoogte
TEKEN_H = 104                     # hoogte van het tekenvlak binnen de tegel
KOLOMMEN = 6
GOOT_X, GOOT_Y = 18, 14

INKT = "navy"
DOF = 0.30
GRIJS = 0.12


def _as(x, y, w, h):
    """Een kale l-vormige as. Elke vorm die assen heeft, gebruikt dezelfde."""
    return [lijn("as-y", x, y, x, y + h, kleur=INKT, dikte=0.75, dekking=DOF),
            lijn("as-x", x, y + h, x + w, y + h, kleur=INKT, dikte=0.75, dekking=DOF)]


# ---------------------------------------------------------------- de twintig vormen
# Elke functie krijgt de linkerbovenhoek van het tekenvlak en geeft vormen terug.

def lijnvorm(x, y, w, h):
    d = [0.55, 0.42, 0.60, 0.48, 0.72, 0.66, 0.86]
    pts = [(x + i * w / (len(d) - 1), y + h - v * h) for i, v in enumerate(d)]
    p = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts)
    return _as(x, y, w, h) + [pad("lijn", p, lijn_=(INKT, 1.6))]


def kolommen_tijd(x, y, w, h):
    d = [0.40, 0.52, 0.47, 0.63, 0.58, 0.78]
    bw = w / (len(d) * 1.6)
    uit = _as(x, y, w, h)
    for i, v in enumerate(d):
        bx = x + i * w / len(d) + (w / len(d) - bw) / 2
        uit.append(vlak(f"k{i}", bx, y + h - v * h, bw, v * h, vulling=INKT, lijn_=None))
    return uit


def helling(x, y, w, h):
    paren = [(0.25, 0.70), (0.45, 0.55), (0.62, 0.30), (0.80, 0.86)]
    uit = [lijn("l", x, y, x, y + h, kleur=INKT, dikte=0.75, dekking=DOF),
           lijn("r", x + w, y, x + w, y + h, kleur=INKT, dikte=0.75, dekking=DOF)]
    for i, (a, b) in enumerate(paren):
        y1, y2 = y + h - a * h, y + h - b * h
        uit += [lijn(f"h{i}", x, y1, x + w, y2, kleur=INKT, dikte=1.2),
                cirkel(f"p{i}a", x, y1, 2.4, vulling=INKT),
                cirkel(f"p{i}b", x + w, y2, 2.4, vulling=INKT)]
    return uit


def priestley(x, y, w, h):
    balken = [(0.00, 0.46), (0.12, 0.72), (0.38, 0.94), (0.55, 0.80)]
    uit = [lijn("as", x, y + h, x + w, y + h, kleur=INKT, dikte=0.75, dekking=DOF)]
    bh = 9
    for i, (a, b) in enumerate(balken):
        uit.append(vlak(f"b{i}", x + a * w, y + i * (bh + 7), (b - a) * w, bh,
                        vulling=INKT, lijn_=None))
    return uit


def cirkeltijdlijn(x, y, w, h):
    mom = [(0.00, 7), (0.09, 4), (0.34, 9), (0.60, 5), (1.00, 6)]
    cy = y + h / 2
    uit = [lijn("as", x, cy, x + w, cy, kleur=INKT, dikte=0.75, dekking=DOF)]
    for i, (t, r) in enumerate(mom):
        uit.append(cirkel(f"m{i}", x + t * w, cy, r, vulling=(INKT, 0.18),
                          lijn_=(INKT, 1.0)))
    return uit


def geordende_staaf(x, y, w, h):
    d = [0.95, 0.74, 0.61, 0.44, 0.28]
    uit = [lijn("as", x, y, x, y + h, kleur=INKT, dikte=0.75, dekking=DOF)]
    bh = h / (len(d) * 1.5)
    for i, v in enumerate(d):
        uit.append(vlak(f"s{i}", x, y + i * h / len(d), v * w, bh, vulling=INKT, lijn_=None))
    return uit


def dot_strip(x, y, w, h):
    rijen = [[0.20, 0.34, 0.41, 0.58, 0.77], [0.28, 0.36, 0.52], [0.12, 0.44, 0.63, 0.90]]
    uit = []
    for r, punten in enumerate(rijen):
        ry = y + 12 + r * (h - 24) / (len(rijen) - 1)
        uit.append(lijn(f"r{r}", x, ry, x + w, ry, kleur=INKT, dikte=0.6, dekking=DOF))
        for i, p in enumerate(punten):
            uit.append(cirkel(f"d{r}{i}", x + p * w, ry, 3.2, vulling=(INKT, 0.55)))
    return uit


def lollipop(x, y, w, h):
    d = [0.88, 0.66, 0.52, 0.35]
    uit = [lijn("as", x, y, x, y + h, kleur=INKT, dikte=0.75, dekking=DOF)]
    for i, v in enumerate(d):
        ry = y + 14 + i * (h - 28) / (len(d) - 1)
        uit += [lijn(f"l{i}", x, ry, x + v * w, ry, kleur=INKT, dikte=1.0, dekking=0.55),
                cirkel(f"k{i}", x + v * w, ry, 4.0, vulling=INKT)]
    return uit


def gestapelde_kolom(x, y, w, h):
    kol = [[0.45, 0.30, 0.25], [0.38, 0.34, 0.28], [0.30, 0.36, 0.34]]
    bw = w / (len(kol) * 1.7)
    uit = _as(x, y, w, h)
    for i, delen in enumerate(kol):
        bx = x + i * w / len(kol) + (w / len(kol) - bw) / 2
        oy = y + h
        for j, v in enumerate(delen):
            hh = v * h * 0.92
            oy -= hh
            uit.append(vlak(f"g{i}{j}", bx, oy, bw, hh,
                            vulling=(INKT, [1.0, 0.45, 0.15][j]), lijn_=None))
    return uit


def proportionele_staaf(x, y, w, h):
    rijen = [[0.52, 0.31, 0.17], [0.38, 0.44, 0.18], [0.61, 0.22, 0.17]]
    uit = []
    bh = 16
    for i, delen in enumerate(rijen):
        ry = y + 8 + i * (h - 16) / len(rijen)
        ox = x
        for j, v in enumerate(delen):
            uit.append(vlak(f"p{i}{j}", ox, ry, v * w, bh,
                            vulling=(INKT, [1.0, 0.45, 0.15][j]), lijn_=None))
            ox += v * w
    return uit


def waterval(x, y, w, h):
    stappen = [(0.0, 0.62), (0.62, 0.78), (0.50, 0.78), (0.50, 0.34), (0.0, 0.34)]
    bw = w / (len(stappen) * 1.5)
    uit = _as(x, y, w, h)
    for i, (a, b) in enumerate(stappen):
        bx = x + i * w / len(stappen) + (w / len(stappen) - bw) / 2
        lo, hi = sorted((a, b))
        uit.append(vlak(f"w{i}", bx, y + h - hi * h, bw, (hi - lo) * h,
                        vulling=(INKT, 1.0 if i in (0, 4) else 0.45), lijn_=None))
        if i:
            vy = y + h - a * h
            uit.append(lijn(f"c{i}", bx - w / len(stappen) + bw, vy, bx, vy,
                            kleur=INKT, dikte=0.6, dekking=DOF, streep="2 2"))
    return uit


def gridplot(x, y, w, h):
    uit = []
    kol, rij = 10, 5
    s = min(w / kol, h / rij) * 0.62
    dx, dy = w / kol, h / rij
    gevuld = 31
    for r in range(rij):
        for k in range(kol):
            i = r * kol + k
            uit.append(vlak(f"c{i}", x + k * dx, y + r * dy, s, s,
                            vulling=(INKT, 1.0 if i < gevuld else 0.15), lijn_=None))
    return uit


def gepaarde_staaf(x, y, w, h):
    paren = [(0.82, 0.55), (0.64, 0.71), (0.47, 0.40), (0.33, 0.52)]
    uit = [lijn("as", x + w / 2, y, x + w / 2, y + h, kleur=INKT, dikte=0.75, dekking=DOF)]
    bh = h / (len(paren) * 1.7)
    for i, (l, r) in enumerate(paren):
        ry = y + i * h / len(paren)
        uit += [vlak(f"L{i}", x + w / 2 - l * w / 2, ry, l * w / 2, bh,
                     vulling=(INKT, 0.45), lijn_=None),
                vlak(f"R{i}", x + w / 2, ry, r * w / 2, bh, vulling=INKT, lijn_=None)]
    return uit


def proportioneel_symbool(x, y, w, h):
    r = [26, 18, 12, 7]
    uit = []
    ox = x + r[0]
    for i, rr in enumerate(r):
        uit.append(cirkel(f"s{i}", ox, y + h - rr, rr, vulling=(INKT, 0.22),
                          lijn_=(INKT, 1.0)))
        ox += rr + (r[i + 1] if i + 1 < len(r) else 0) + 12
    return uit


def divergerende_staaf(x, y, w, h):
    d = [0.62, 0.34, -0.18, -0.45, 0.21]
    mid = x + w / 2
    uit = [lijn("nul", mid, y, mid, y + h, kleur=INKT, dikte=0.75, dekking=DOF)]
    bh = h / (len(d) * 1.5)
    for i, v in enumerate(d):
        ry = y + i * h / len(d)
        bx = mid if v >= 0 else mid + v * w / 2
        uit.append(vlak(f"d{i}", bx, ry, abs(v) * w / 2, bh,
                        vulling=(INKT, 1.0 if v >= 0 else 0.40), lijn_=None))
    return uit


def surplus_tekort(x, y, w, h):
    a = [0.42, 0.55, 0.62, 0.48, 0.36, 0.44, 0.58]
    b = [0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50]
    n = len(a)
    pa = [(x + i * w / (n - 1), y + h - v * h) for i, v in enumerate(a)]
    pb = [(x + i * w / (n - 1), y + h - v * h) for i, v in enumerate(b)]
    vlakpad = ("M " + " L ".join(f"{p[0]:.1f} {p[1]:.1f}" for p in pa) +
               " L " + " L ".join(f"{p[0]:.1f} {p[1]:.1f}" for p in reversed(pb)) + " Z")
    return [pad("vlak", vlakpad, vulling=(INKT, 0.18)),
            pad("ref", "M " + " L ".join(f"{p[0]:.1f} {p[1]:.1f}" for p in pb),
                lijn_=(INKT, 0.75)),
            pad("reeks", "M " + " L ".join(f"{p[0]:.1f} {p[1]:.1f}" for p in pa),
                lijn_=(INKT, 1.6))]


def sankey(x, y, w, h):
    uit = []
    links = [(0.00, 0.46), (0.52, 0.30), (0.86, 0.14)]
    rechts = [(0.00, 0.28), (0.34, 0.24), (0.62, 0.20), (0.86, 0.14)]
    for i, (a, hh) in enumerate(links):
        uit.append(vlak(f"L{i}", x, y + a * h, 9, hh * h, vulling=INKT, lijn_=None))
    for i, (a, hh) in enumerate(rechts):
        uit.append(vlak(f"R{i}", x + w - 9, y + a * h, 9, hh * h, vulling=INKT, lijn_=None))
    stromen = [(0.00, 0.46, 0.00, 0.28), (0.00, 0.46, 0.34, 0.24),
               (0.52, 0.30, 0.62, 0.20), (0.86, 0.14, 0.86, 0.14)]
    for i, (a1, h1, a2, h2) in enumerate(stromen):
        y1, y2 = y + a1 * h, y + a2 * h
        hh = min(h1, h2) * h
        cx = x + w / 2
        uit.append(pad(f"S{i}",
                       f"M {x+9} {y1:.1f} C {cx} {y1:.1f} {cx} {y2:.1f} {x+w-9} {y2:.1f} "
                       f"L {x+w-9} {y2+hh:.1f} C {cx} {y2+hh:.1f} {cx} {y1+hh:.1f} "
                       f"{x+9} {y1+hh:.1f} Z", vulling=(INKT, 0.16)))
    return uit


def naaf(x, y, w, h):
    cx, cy = x + w / 2, y + h / 2
    R, r = 21, 11
    uit = [cirkel("naaf", cx, cy, R, vulling=(INKT, 0.12), lijn_=(INKT, 1.6))]
    for i in range(5):
        a = -math.pi / 2 + i * 2 * math.pi / 5
        px, py = cx + math.cos(a) * (w / 2 - r), cy + math.sin(a) * (h / 2 - r)
        ux, uy = math.cos(a), math.sin(a)
        uit += [lijn(f"v{i}", cx + ux * R, cy + uy * R, px - ux * r, py - uy * r,
                     kleur=INKT, dikte=1.0, dekking=0.55),
                cirkel(f"n{i}", px, py, r, vulling=None, lijn_=(INKT, 1.2))]
    return uit


def spreiding(x, y, w, h):
    pts = [(0.12, 0.22), (0.24, 0.38), (0.31, 0.30), (0.42, 0.52), (0.48, 0.44),
           (0.57, 0.63), (0.63, 0.55), (0.72, 0.76), (0.81, 0.68), (0.90, 0.88),
           (0.35, 0.68), (0.68, 0.34)]
    uit = _as(x, y, w, h)
    for i, (a, b) in enumerate(pts):
        uit.append(cirkel(f"p{i}", x + a * w, y + h - b * h, 3.0, vulling=(INKT, 0.55)))
    return uit


def histogram(x, y, w, h):
    d = [0.14, 0.30, 0.55, 0.86, 0.72, 0.44, 0.26, 0.12]
    bw = w / len(d)
    uit = _as(x, y, w, h)
    for i, v in enumerate(d):
        uit.append(vlak(f"h{i}", x + i * bw, y + h - v * h, bw - 1.5, v * h,
                        vulling=(INKT, 0.55), lijn_=None))
    return uit



# ---------------------------------------------------------------- deel twee: nog eens 22

def venn2(x, y, w, h):
    r = min(w, h) * 0.36
    cy = y + h / 2
    return [cirkel("v1", x + w / 2 - r * 0.58, cy, r, vulling=(INKT, 0.16), lijn_=(INKT, 1.2)),
            cirkel("v2", x + w / 2 + r * 0.58, cy, r, vulling=(INKT, 0.16), lijn_=(INKT, 1.2))]


def venn3(x, y, w, h):
    r = min(w, h) * 0.30
    cx, cy = x + w / 2, y + h / 2 + r * 0.18
    posities = [(cx, cy - r * 0.62), (cx - r * 0.56, cy + r * 0.34), (cx + r * 0.56, cy + r * 0.34)]
    return [cirkel(f"v{i}", px, py, r, vulling=(INKT, 0.13), lijn_=(INKT, 1.2))
            for i, (px, py) in enumerate(posities)]


def kwadrant(x, y, w, h):
    s = min(w, h)
    x0, y0 = x + (w - s) / 2, y
    punten = [(0.24, 0.72), (0.34, 0.80), (0.68, 0.30), (0.78, 0.22), (0.72, 0.66), (0.28, 0.30)]
    uit = [lijn("kx", x0, y0 + s / 2, x0 + s, y0 + s / 2, kleur=INKT, dikte=0.75, dekking=DOF),
           lijn("ky", x0 + s / 2, y0, x0 + s / 2, y0 + s, kleur=INKT, dikte=0.75, dekking=DOF)]
    for i, (a, b) in enumerate(punten):
        uit.append(cirkel(f"k{i}", x0 + a * s, y0 + b * s, 4.0,
                          vulling=(INKT, 0.55 if a > 0.5 and b < 0.5 else 0.22), lijn_=None))
    return uit


def trechter(x, y, w, h):
    breed = [1.0, 0.78, 0.52, 0.30]
    uit = []
    bh = h / len(breed) - 5
    for i, b in enumerate(breed):
        bw = w * b
        uit.append(vlak(f"t{i}", x + (w - bw) / 2, y + i * (bh + 5), bw, bh,
                        vulling=(INKT, 0.20 + i * 0.20), lijn_=None))
    return uit


def piramide(x, y, w, h):
    lagen = 4
    uit = []
    lh = h / lagen - 4
    for i in range(lagen):
        f0, f1 = i / lagen, (i + 1) / lagen
        yy = y + i * (lh + 4)
        uit.append(pad(f"p{i}",
                       f"M {x + w/2 - w/2*f0:.1f} {yy:.1f} L {x + w/2 + w/2*f0:.1f} {yy:.1f} "
                       f"L {x + w/2 + w/2*f1:.1f} {yy+lh:.1f} L {x + w/2 - w/2*f1:.1f} {yy+lh:.1f} Z",
                       vulling=(INKT, 0.75 - i * 0.17)))
    return uit


def treemap(x, y, w, h):
    vakken = [(0, 0, 0.52, 0.62), (0.52, 0, 0.48, 0.36), (0.52, 0.36, 0.28, 0.26),
              (0.80, 0.36, 0.20, 0.26), (0, 0.62, 0.34, 0.38), (0.34, 0.62, 0.30, 0.38),
              (0.64, 0.62, 0.36, 0.38)]
    return [vlak(f"tm{i}", x + a * w, y + b * h, cw * w - 2, ch * h - 2,
                 vulling=(INKT, 0.75 - i * 0.09), lijn_=None)
            for i, (a, b, cw, ch) in enumerate(vakken)]


def donut(x, y, w, h):
    import math as _m
    cx, cy = x + w / 2, y + h / 2
    R, r = min(w, h) * 0.42, min(w, h) * 0.25
    delen = [0.46, 0.28, 0.16, 0.10]
    uit, a0 = [], -_m.pi / 2
    for i, d in enumerate(delen):
        a1 = a0 + d * 2 * _m.pi
        groot = 1 if d > 0.5 else 0
        p1 = (cx + R * _m.cos(a0), cy + R * _m.sin(a0))
        p2 = (cx + R * _m.cos(a1), cy + R * _m.sin(a1))
        p3 = (cx + r * _m.cos(a1), cy + r * _m.sin(a1))
        p4 = (cx + r * _m.cos(a0), cy + r * _m.sin(a0))
        uit.append(pad(f"d{i}",
                       f"M {p1[0]:.1f} {p1[1]:.1f} A {R} {R} 0 {groot} 1 {p2[0]:.1f} {p2[1]:.1f} "
                       f"L {p3[0]:.1f} {p3[1]:.1f} A {r} {r} 0 {groot} 0 {p4[0]:.1f} {p4[1]:.1f} Z",
                       vulling=(INKT, 0.85 - i * 0.20)))
        a0 = a1
    return uit


def meter(x, y, w, h):
    import math as _m
    cx, cy = x + w / 2, y + h * 0.78
    R = min(w / 2, h * 0.72)
    def boog(f, dik, dek):
        a0, a1 = _m.pi, _m.pi + f * _m.pi
        p1 = (cx + R * _m.cos(a0), cy + R * _m.sin(a0))
        p2 = (cx + R * _m.cos(a1), cy + R * _m.sin(a1))
        return pad(f"m{f}", f"M {p1[0]:.1f} {p1[1]:.1f} A {R} {R} 0 0 1 {p2[0]:.1f} {p2[1]:.1f}",
                   lijn_=(INKT, dik))
    return [boog(1.0, 10, DOF), boog(0.68, 10, 1.0),
            lijn("naald", cx, cy, cx + R * _m.cos(_m.pi + 0.68 * _m.pi),
                 cy + R * _m.sin(_m.pi + 0.68 * _m.pi), kleur=INKT, dikte=1.0, dekking=DOF)]


def bullet(x, y, w, h):
    uit = []
    for i, (waarde, doel) in enumerate([(0.72, 0.85), (0.58, 0.50), (0.41, 0.62)]):
        ry = y + 14 + i * (h - 28) / 2
        uit += [vlak(f"spoor{i}", x, ry - 7, w, 14, vulling=(INKT, 0.10), lijn_=None),
                vlak(f"waarde{i}", x, ry - 4, w * waarde, 8, vulling=INKT, lijn_=None),
                lijn(f"doel{i}", x + w * doel, ry - 9, x + w * doel, ry + 9,
                     kleur=INKT, dikte=2.0)]
    return uit


def radar(x, y, w, h):
    import math as _m
    cx, cy = x + w / 2, y + h / 2
    R = min(w, h) * 0.44
    n = 6
    waarden = [0.86, 0.62, 0.74, 0.40, 0.55, 0.68]
    uit = []
    for ring in (0.5, 1.0):
        pts = [(cx + R * ring * _m.cos(-_m.pi / 2 + i * 2 * _m.pi / n),
                cy + R * ring * _m.sin(-_m.pi / 2 + i * 2 * _m.pi / n)) for i in range(n)]
        uit.append(pad(f"ring{ring}", "M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in pts) + " Z",
                       lijn_=(INKT, 0.6)))
    pts = [(cx + R * v * _m.cos(-_m.pi / 2 + i * 2 * _m.pi / n),
            cy + R * v * _m.sin(-_m.pi / 2 + i * 2 * _m.pi / n)) for i, v in enumerate(waarden)]
    uit.append(pad("web", "M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in pts) + " Z",
                   vulling=(INKT, 0.20), lijn_=(INKT, 1.4)))
    return uit


def marimekko(x, y, w, h):
    kol = [(0.42, [0.55, 0.30, 0.15]), (0.31, [0.38, 0.42, 0.20]), (0.27, [0.28, 0.30, 0.42])]
    uit, ox = [], x
    for i, (bw, delen) in enumerate(kol):
        oy = y
        for j, d in enumerate(delen):
            uit.append(vlak(f"mk{i}{j}", ox, oy, bw * w - 3, d * h, 
                            vulling=(INKT, 0.85 - j * 0.28), lijn_=None))
            oy += d * h
        ox += bw * w
    return uit


def chord(x, y, w, h):
    import math as _m
    cx, cy = x + w / 2, y + h / 2
    R = min(w, h) * 0.44
    hoeken = [0.3, 1.4, 2.5, 3.6, 4.7, 5.8]
    pts = [(cx + R * _m.cos(a), cy + R * _m.sin(a)) for a in hoeken]
    uit = [cirkel("rand", cx, cy, R, vulling=None, lijn_=(INKT, 0.75))]
    for i, j in [(0, 3), (1, 4), (2, 5), (0, 2)]:
        uit.append(pad(f"c{i}{j}",
                       f"M {pts[i][0]:.1f} {pts[i][1]:.1f} Q {cx} {cy} "
                       f"{pts[j][0]:.1f} {pts[j][1]:.1f}", lijn_=(INKT, 1.4)))
    for i, (px, py) in enumerate(pts):
        uit.append(cirkel(f"n{i}", px, py, 4, vulling=INKT, lijn_=None))
    return uit


def boom(x, y, w, h):
    kb, rij_h = w / 4.4, h / 3
    uit = [vlak("top", x + w / 2 - kb / 2, y, kb, 16, vulling=INKT, lijn_=None)]
    for i, f in enumerate((0.22, 0.5, 0.78)):
        uit += [vlak(f"m{i}", x + f * w - kb / 2, y + rij_h, kb, 16,
                     vulling=(INKT, 0.35), lijn_=None),
                lijn(f"v{i}", x + f * w, y + rij_h, x + f * w, y + 16 + (rij_h - 16) / 2,
                     kleur=INKT, dikte=0.75, dekking=0.6)]
    uit.append(lijn("balk", x + 0.22 * w, y + 16 + (rij_h - 16) / 2, x + 0.78 * w,
                    y + 16 + (rij_h - 16) / 2, kleur=INKT, dikte=0.75, dekking=0.6))
    uit.append(lijn("stam", x + w / 2, y + 16, x + w / 2, y + 16 + (rij_h - 16) / 2,
                    kleur=INKT, dikte=0.75, dekking=0.6))
    for i, f in enumerate((0.10, 0.34, 0.66, 0.90)):
        uit += [vlak(f"b{i}", x + f * w - kb / 2.4, y + 2 * rij_h, kb / 1.2, 14,
                     vulling=None, lijn_=(INKT, 1.0))]
    return uit


def beslisboom(x, y, w, h):
    cx = x + w * 0.30
    cy = y + h / 2
    d = 20
    uit = [pad("ruit", f"M {cx} {cy-d} L {cx+d} {cy} L {cx} {cy+d} L {cx-d} {cy} Z",
               vulling=(INKT, 0.16), lijn_=(INKT, 1.2))]
    for i, yy in enumerate((y + h * 0.18, y + h * 0.82)):
        uit += [pad(f"pijl{i}", f"M {cx+d} {cy} Q {x + w*0.55} {cy} {x + w*0.62} {yy}",
                    lijn_=(INKT, 1.0)),
                vlak(f"uit{i}", x + w * 0.64, yy - 9, w * 0.34, 18,
                     vulling=(INKT, 0.55 if i == 0 else 0.16), lijn_=(INKT, 1.0))]
    return uit


def zwembanen(x, y, w, h):
    banen = 3
    bh = h / banen
    uit = []
    stappen = [[(0.02, 0.22), (0.40, 0.24)], [(0.26, 0.20), (0.64, 0.22)], [(0.50, 0.24)]]
    for r in range(banen):
        by = y + r * bh
        uit.append(lijn(f"baan{r}", x, by, x + w, by, kleur=INKT, dikte=0.5, dekking=DOF))
        for i, (a, bw) in enumerate(stappen[r]):
            uit.append(vlak(f"s{r}{i}", x + a * w, by + bh * 0.22, bw * w, bh * 0.5,
                            vulling=(INKT, 0.20 + r * 0.18), lijn_=None))
    uit.append(lijn("onder", x, y + h, x + w, y + h, kleur=INKT, dikte=0.5, dekking=DOF))
    return uit


def bubbelmatrix(x, y, w, h):
    r_lijst = [[7, 3, 11, 5], [4, 9, 6, 13], [10, 5, 3, 7]]
    uit = _as(x, y, w, h)
    for r, rij in enumerate(r_lijst):
        for k, rr in enumerate(rij):
            uit.append(cirkel(f"b{r}{k}", x + (k + 0.5) * w / 4, y + (r + 0.5) * h / 3, rr,
                              vulling=(INKT, 0.45), lijn_=None))
    return uit


def heatmap(x, y, w, h):
    d = [[0.9, 0.6, 0.3, 0.15, 0.5], [0.4, 0.8, 0.55, 0.25, 0.7], [0.2, 0.35, 0.95, 0.6, 0.3]]
    uit = []
    cw, ch = w / 5, h / 3
    for r, rij in enumerate(d):
        for k, v in enumerate(rij):
            uit.append(vlak(f"h{r}{k}", x + k * cw, y + r * ch, cw - 2, ch - 2,
                            vulling=(INKT, max(0.06, v)), lijn_=None))
    return uit


def kalender(x, y, w, h):
    import itertools
    waarden = [0.1, 0.4, 0.8, 0.2, 0.6, 0.05, 0.05, 0.3, 0.9, 0.5, 0.7, 0.15, 0.05, 0.05] * 4
    uit = []
    kol, rij = 14, 5
    cw = w / kol
    ch = min(h / rij, cw)
    for i in range(kol * rij):
        r, k = divmod(i, kol)
        uit.append(vlak(f"k{i}", x + k * cw, y + r * ch, cw - 2, ch - 2,
                        vulling=(INKT, max(0.06, waarden[i % len(waarden)])), lijn_=None))
    return uit


def veelvouden(x, y, w, h):
    reeksen = [[0.3, 0.5, 0.4, 0.7], [0.6, 0.45, 0.5, 0.35], [0.2, 0.35, 0.6, 0.85]]
    uit = []
    pw = (w - 2 * 10) / 3
    for i, d in enumerate(reeksen):
        ox = x + i * (pw + 10)
        uit.append(lijn(f"as{i}", ox, y + h, ox + pw, y + h, kleur=INKT, dikte=0.6, dekking=DOF))
        pts = [(ox + j * pw / (len(d) - 1), y + h - v * h * 0.86) for j, v in enumerate(d)]
        uit.append(pad(f"l{i}", "M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in pts),
                       lijn_=(INKT, 1.4)))
    return uit


def halter(x, y, w, h):
    paren = [(0.22, 0.68), (0.35, 0.86), (0.48, 0.60), (0.15, 0.44)]
    uit = [lijn("as", x, y, x, y + h, kleur=INKT, dikte=0.75, dekking=DOF)]
    for i, (a, b) in enumerate(paren):
        ry = y + 12 + i * (h - 24) / (len(paren) - 1)
        uit += [lijn(f"h{i}", x + a * w, ry, x + b * w, ry, kleur=INKT, dikte=1.2, dekking=0.45),
                cirkel(f"a{i}", x + a * w, ry, 4.2, vulling=(INKT, 0.30), lijn_=(INKT, 1.0)),
                cirkel(f"b{i}", x + b * w, ry, 4.2, vulling=INKT, lijn_=None)]
    return uit


def gestapeld_vlak(x, y, w, h):
    reeksen = [[0.20, 0.26, 0.24, 0.30, 0.34], [0.18, 0.20, 0.26, 0.24, 0.28],
               [0.14, 0.16, 0.14, 0.18, 0.20]]
    n = len(reeksen[0])
    onder = [0.0] * n
    uit = _as(x, y, w, h)
    for s, reeks in enumerate(reeksen):
        boven = [onder[i] + reeks[i] for i in range(n)]
        p_boven = [(x + i * w / (n - 1), y + h - b * h) for i, b in enumerate(boven)]
        p_onder = [(x + i * w / (n - 1), y + h - b * h) for i, b in enumerate(onder)]
        uit.append(pad(f"vl{s}",
                       "M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in p_boven) +
                       " L " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in reversed(p_onder)) + " Z",
                       vulling=(INKT, 0.70 - s * 0.22)))
        onder = boven
    return uit


def cyclus(x, y, w, h):
    import math as _m
    cx, cy = x + w / 2, y + h / 2
    R = min(w, h) * 0.40
    uit = []
    n = 4
    for i in range(n):
        a0 = -_m.pi / 2 + i * 2 * _m.pi / n + 0.16
        a1 = -_m.pi / 2 + (i + 1) * 2 * _m.pi / n - 0.16
        p1 = (cx + R * _m.cos(a0), cy + R * _m.sin(a0))
        p2 = (cx + R * _m.cos(a1), cy + R * _m.sin(a1))
        uit.append(pad(f"boog{i}", f"M {p1[0]:.1f} {p1[1]:.1f} A {R} {R} 0 0 1 "
                                   f"{p2[0]:.1f} {p2[1]:.1f}", lijn_=(INKT, 3.0)))
        pk = (cx + R * _m.cos(a1 + 0.10), cy + R * _m.sin(a1 + 0.10))
        uit.append(cirkel(f"k{i}", pk[0], pk[1], 5, vulling=INKT, lijn_=None))
    return uit


def isotype(x, y, w, h):
    uit = []
    n, gevuld = 10, 7
    bw = w / n
    for i in range(n):
        cxx = x + (i + 0.5) * bw
        dek = 1.0 if i < gevuld else 0.16
        uit += [cirkel(f"kop{i}", cxx, y + h * 0.30, 5.5, vulling=(INKT, dek), lijn_=None),
                pad(f"romp{i}", f"M {cxx-6.5} {y + h*0.72} "
                                f"Q {cxx-6.5} {y + h*0.44} {cxx} {y + h*0.44} "
                                f"Q {cxx+6.5} {y + h*0.44} {cxx+6.5} {y + h*0.72} Z",
                    vulling=(INKT, dek))]
    return uit


def stroomschema(x, y, w, h):
    uit = []
    kb, kh = w * 0.26, 22
    posities = [(0.0, 0.5), (0.37, 0.5), (0.74, 0.18), (0.74, 0.82)]
    vormsoort = ["rond", "ruit", "recht", "recht"]
    for i, ((a, b), soort) in enumerate(zip(posities, vormsoort)):
        cx0, cy0 = x + a * w + kb / 2, y + b * h
        if soort == "ruit":
            d = 15
            uit.append(pad(f"f{i}", f"M {cx0} {cy0-d} L {cx0+d*1.5} {cy0} L {cx0} {cy0+d} "
                                    f"L {cx0-d*1.5} {cy0} Z", vulling=(INKT, 0.16),
                           lijn_=(INKT, 1.0)))
        else:
            uit.append(vlak(f"f{i}", cx0 - kb / 2, cy0 - kh / 2, kb, kh,
                            vulling=(INKT, 0.55) if soort == "rond" else None,
                            lijn_=None if soort == "rond" else (INKT, 1.0),
                            hoek=kh / 2 if soort == "rond" else 0))
    uit += [lijn("p1", x + kb, y + h / 2, x + 0.37 * w, y + h / 2, kleur=INKT, dikte=1.0,
                 dekking=0.5),
            pad("p2", f"M {x + 0.37*w + kb/2 + 22} {y + h/2} Q {x + 0.66*w} {y + h/2} "
                      f"{x + 0.74*w} {y + 0.18*h}", lijn_=(INKT, 1.0)),
            pad("p3", f"M {x + 0.37*w + kb/2 + 22} {y + h/2} Q {x + 0.66*w} {y + h/2} "
                      f"{x + 0.74*w} {y + 0.82*h}", lijn_=(INKT, 1.0))]
    return uit


def getallenlijn(x, y, w, h):
    cy = y + h * 0.55
    merken = [(0.10, "klein"), (0.34, ""), (0.52, ""), (0.88, "groot")]
    uit = [lijn("lijn", x, cy, x + w, cy, kleur=INKT, dikte=1.0, dekking=0.5)]
    for i, (f, _) in enumerate(merken):
        r = 5 + (10 if f == 0.88 else 0)
        uit.append(cirkel(f"m{i}", x + f * w, cy, r,
                          vulling=(INKT, 0.85 if f == 0.88 else 0.25), lijn_=(INKT, 1.0)))
    return uit


def opbouw_lagen(x, y, w, h):
    lagen = [("basis", 1.00), ("dienst", 0.76), ("resultaat", 0.52), ("effect", 0.30)]
    uit = []
    lh = h / len(lagen) - 6
    for i, (_, f) in enumerate(lagen):
        bw = w * f
        uit.append(vlak(f"laag{i}", x, y + h - (i + 1) * (lh + 6) + 6, bw, lh,
                        vulling=(INKT, 0.16 + i * 0.22), lijn_=None))
    return uit

# ---------------------------------------------------------------- de tegels

VORMEN = [
    ("Verandering", "Lijn", "hoe loopt dit over tijd", lijnvorm),
    ("Verandering", "Kolommen over tijd", "hoeveel per periode", kolommen_tijd),
    ("Verandering", "Gestapeld vlak", "hoe verschuift de opbouw", gestapeld_vlak),
    ("Verandering", "Helling", "wie ging vooruit, wie achteruit", helling),
    ("Verandering", "Priestley-tijdlijn", "wat liep wanneer en hoe lang", priestley),
    ("Verandering", "Cirkeltijdlijn", "wanneer gebeurde het, en hoe groot", cirkeltijdlijn),
    ("Verandering", "Kalender-heatmap", "wanneer is het druk", kalender),
    ("Verandering", "Kleine veelvouden", "loopt het overal hetzelfde", veelvouden),
    ("Rangschikking", "Geordende staaf", "wie is groot, wie klein", geordende_staaf),
    ("Rangschikking", "Puntenstrook", "waar zit de spreiding per groep", dot_strip),
    ("Rangschikking", "Lolly", "rangorde met weinig inkt", lollipop),
    ("Rangschikking", "Halter", "hoeveel schoof elk op", halter),
    ("Rangschikking", "Getallenlijn", "waar staat elk op de schaal", getallenlijn),
    ("Deel van geheel", "Gestapelde kolom", "waaruit is het totaal opgebouwd", gestapelde_kolom),
    ("Deel van geheel", "Proportionele staaf", "hoe is elk geheel verdeeld", proportionele_staaf),
    ("Deel van geheel", "Waterval", "wat bouwt op en wat gaat eraf", waterval),
    ("Deel van geheel", "Rasterplot", "hoeveel van de honderd", gridplot),
    ("Deel van geheel", "Ring", "hoe is het ene geheel verdeeld", donut),
    ("Deel van geheel", "Treemap", "welke brokken zijn groot", treemap),
    ("Deel van geheel", "Marimekko", "twee verdelingen tegelijk", marimekko),
    ("Deel van geheel", "Trechter", "waar valt het af", trechter),
    ("Grootte", "Gepaarde staaf", "hoe verhoudt dit zich tot dat", gepaarde_staaf),
    ("Grootte", "Proportioneel symbool", "hoeveel groter is het een", proportioneel_symbool),
    ("Grootte", "Isotype", "hoeveel mensen zijn dit", isotype),
    ("Grootte", "Bulletgrafiek", "haalt het de norm", bullet),
    ("Grootte", "Meter", "hoe ver zijn we", meter),
    ("Grootte", "Radar", "op welke assen scoort het", radar),
    ("Afwijking", "Divergerende staaf", "wie zit boven en wie onder de norm", divergerende_staaf),
    ("Afwijking", "Overschot en tekort", "waar loopt het uit de pas", surplus_tekort),
    ("Stroom", "Sankey", "waar gaat het geld naartoe", sankey),
    ("Stroom", "Naaf", "wie hangt aan wie", naaf),
    ("Stroom", "Chord", "wie wisselt uit met wie", chord),
    ("Stroom", "Cyclus", "wat herhaalt zich", cyclus),
    ("Stroom", "Stroomschema", "hoe loopt het besluit", stroomschema),
    ("Stroom", "Beslisboom", "wat gebeurt er als", beslisboom),
    ("Stroom", "Zwembanen", "wie doet wat wanneer", zwembanen),
    ("Verband", "Venn, twee", "wat delen ze", venn2),
    ("Verband", "Venn, drie", "waar overlappen drie dingen", venn3),
    ("Verband", "Kwadrant", "wie zit in welke hoek", kwadrant),
    ("Verband", "Spreiding", "hangen deze twee samen", spreiding),
    ("Verband", "Bubbelmatrix", "waar zit het zwaartepunt", bubbelmatrix),
    ("Verband", "Heatmap", "welk vak springt eruit", heatmap),
    ("Structuur", "Boom", "hoe hangt het samen", boom),
    ("Structuur", "Piramide", "wat rust waarop", piramide),
    ("Structuur", "Opbouw in lagen", "van inzet naar effect", opbouw_lagen),
    ("Verdeling", "Histogram", "hoe is het verdeeld", histogram),
]


def bouw() -> Path:
    rijen = (len(VORMEN) + KOLOMMEN - 1) // KOLOMMEN
    c = Canvas("woordenboek",
               KOLOMMEN * TB + (KOLOMMEN - 1) * GOOT_X,
               rijen * TH + (rijen - 1) * GOOT_Y)
    vormen = []
    for i, (categorie, naam, vraag, fn) in enumerate(VORMEN):
        r, k = divmod(i, KOLOMMEN)
        ox = k * (TB + GOOT_X)
        oy = r * (TH + GOOT_Y)
        vormen.append(vlak(f"tegel {i}", ox, oy, TB, TH, vulling=None,
                           lijn_=(INKT, 0.5)))
        vormen += fn(ox + 18, oy + 16, TB - 36, TEKEN_H)
        vormen += [
            blok(f"cat {i}", ox + 18, oy + TEKEN_H + 26, TB - 36,
                 [label(categorie, 8, "navy", dekking=0.45)]),
            blok(f"naam {i}", ox + 18, oy + TEKEN_H + 40, TB - 36,
                 [kop(naam, 13)]),
            blok(f"vraag {i}", ox + 18, oy + TEKEN_H + 58, TB - 36,
                 [tekst(vraag, 11, "navy", dekking=0.65)]),
        ]
    uit = HIER.parents[1] / "vormen"
    return schrijf(uit / "vormenwoordenboek.svg", c, vormen,
                   beschrijving="Zesenveertig vormen, structureel, zonder kleur en zonder stijl, "
                                "geordend naar de vraag die ze beantwoorden.")


if __name__ == "__main__":
    import subprocess
    p = bouw()
    subprocess.run([sys.executable, str(HIER.parents[3] / "scripts" / "infographic" / "render_svg.py"),
                    str(p), "--wit", "--schaal", "1"], check=True)
