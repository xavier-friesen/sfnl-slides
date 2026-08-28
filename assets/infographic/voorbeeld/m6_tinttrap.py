#!/usr/bin/env python3
"""Maatstaf 6 — verschil bínnen één categorie. Vorm: verdeelde band. Register: wit.

De vier uitvoerders van Werk in Zicht zijn geen vier categorieën. Ze dragen allemaal
dezelfde grootheid, dus vier hues zouden vier soorten suggereren die er niet zijn — en
het palet draagt er ook maar drie. Daarom staat hier één hue met een tinttrap: de
**breedte** is het aantal deelnemers, de **tint** het plaatsingspercentage.

Daarmee haalt de kleur de toets van §6b van `reference/infographic-vormentaal.md`:
nergens anders in dit beeld staat het percentage als lengte, dus de tint codeert iets
wat de vorm niet al zegt. En de trap mag hier staan omdat de band op deelnemersaantal
is gesorteerd — een grootheid, geen alfabet — zodat de aflopende tint een volgorde
herhaalt die de figuur zelf laat zien, in plaats van er een te verzinnen.

Drie stappen en niet vier: `svg.trap_draagt("navy")` rekent uit dat navy er drie
draagt, en dat is de donkerste hue die er is. De vierde stap (`licht`) haalt 1,70 op
wit en leest als leeg spoor. Dat de data drie clusters heeft — 44,9 alleen, 35,9 en
35,6 nauwelijks uit elkaar, 29,6 alleen — is geluk; hij was er ook drie geweest als
dat niet zo was, en dan had de indeling het moeten uitleggen.

Wat er in de eerste versie misging: de namen stonden ín de segmenten. "Basis & Beroep"
is 127 pt breed op 16 pt en het smalste segment is er 137 — met binnenmarge past dat
niet, dus brak de naam over twee regels en had het smalste segment vijf regels waar de
andere drie er drie hadden. Boven de band heeft elke naam de volle segmentbreedte.
"""
import sys
from pathlib import Path

HIER = Path(__file__).resolve()
sys.path.insert(0, str(HIER.parents[3] / "scripts" / "infographic"))
from svg import (CANVAS, Maten, blok, bron, drager, kop, lijn,  # noqa: E402
                 pas_hoogte, schrijf, tekst, tekst_op, tint, trap_draagt, vlak)

# --- de casus, en niets erbuiten -------------------------------------------
TOTAAL_DEELNEMERS = 612
UITVOERDERS = [                      # naam, deelnemers, plaatsingen, percentage
    ("Aan de Slag",      198, 89, 44.9),
    ("Werkpunt Twente",  174, 62, 35.6),
    ("De Nieuwe Kans",   142, 51, 35.9),
    ("Basis & Beroep",    98, 29, 29.6),
]
DOEL = 45.0

# --- de trap ----------------------------------------------------------------
# Drie stappen, want dat is wat navy draagt; `trap_draagt` rekent het uit en de
# assert houdt dit script eerlijk als het palet ooit schuift.
STAPPEN = ["vol", "sterk", "half"]
assert trap_draagt("navy") == len(STAPPEN)


def stap_van(pct: float) -> str:
    """Welke trapstap hoort bij dit percentage? Drie klassen, want drie stappen.

    De grenzen liggen in de gaten die er in de data zitten: 44,9 staat alleen,
    35,9 en 35,6 liggen 0,3 procentpunt uit elkaar en horen dus in dezelfde stap,
    29,6 staat alleen. Vier tinten zouden twee uitvoerders uit elkaar trekken die
    niet uit elkaar liggen -- en navy draagt er ook maar drie.
    """
    return "vol" if pct >= 40 else ("sterk" if pct >= 33 else "half")


def nl(x: float) -> str:
    return f"{x:.1f}".replace(".", ",")


c = CANVAS["breed"]
m = Maten.voor("los", drager=36)

MARGE = 40.0
BREEDTE = c.w - 2 * MARGE
GAT = 8.0
NAAM_Y = 132.0                       # de namen staan bóven de band
BAND_Y, BAND_H = 158.0, 76.0
PAD = 16.0

SPREIDING = UITVOERDERS[0][3] - UITVOERDERS[-1][3]

vormen = [
    blok("Drager", MARGE, 30, 520, [
        drager(f"{nl(SPREIDING)} pp", m.drager, "oranje"),
        tekst("verschil in slaagkans tussen de grootste uitvoerder en de kleinste",
              m.body, dekking=0.75, ruimte_voor=6),
        tekst("De breedte is het aantal deelnemers, de tint het plaatsingspercentage.",
              m.dicht, dekking=0.60, ruimte_voor=10),
    ]),
    # De rechterhelft boven de band vullen met inhoud en niet met lucht: één zin die
    # zegt wat de donkerste tint waard is. §14, stand "één regel".
    blok("Sluitregel", 540, 44, BREEDTE - 500, [
        tekst("Aan de Slag is de grootste uitvoerder en de enige die de doelstelling "
              "van 45% bijna haalt.", m.body, dekking=0.85,
              aanhef=("Aan de Slag", "Montserrat SemiBold")),
    ]),
]

# De namen staan boven de band en niet erin. Nagemeten reden: "Basis & Beroep" is
# 127 pt breed op 16 pt en het smalste segment is er 137 -- met binnenmarge past hij
# niet en breekt hij over twee regels, en dan heeft het smalste segment vijf regels
# waar de andere drie er drie hebben. Boven de band heeft elke naam de volle
# segmentbreedte.
netto = BREEDTE - GAT * (len(UITVOERDERS) - 1)
x = MARGE
for naam, deeln, plaats, pct in UITVOERDERS:
    w = netto * deeln / TOTAAL_DEELNEMERS
    vulling = tint("navy", stap_van(pct))
    inkt = tekst_op(vulling, m.kop)          # vol en sterk dragen wit, half draagt navy
    vormen += [
        blok(f"Naam {naam}", x, NAAM_Y, w, [kop(naam, m.body)]),
        vlak(f"Segment {naam}", x, BAND_Y, w, BAND_H, vulling=vulling, lijn_=None),
        blok(f"Cijfer {naam}", x + PAD, BAND_Y + BAND_H / 2, w - 2 * PAD, [
            tekst(f"{nl(pct)}%", m.kop, inkt),
            tekst(f"{plaats} van {deeln}", m.dicht, inkt, dekking=0.85, ruimte_voor=3),
        ], anchor="c"),
    ]
    x += w + GAT

# Afsluiten met een haarlijn plus een sluitregel, nooit met een kader.
ONDER = BAND_Y + BAND_H + 18
vormen += [
    lijn("Slotstreep", MARGE, ONDER, c.w - MARGE, ONDER,
         kleur="navy", dikte=0.75, dekking=0.20),
    blok("Bron", MARGE, ONDER + 12, BREEDTE, [
        bron("Werk in Zicht, na twaalf maanden: 231 van 612 geplaatst (37,7%), "
             f"doelstelling {int(DOEL)}%.")
    ]),
]

c = pas_hoogte(c, vormen)
schrijf(HIER.parents[1] / "maatstaf" / "m6-tinttrap.svg", c, vormen,
        beschrijving="612 deelnemers over vier uitvoerders; de breedte is het "
                     "deelnemersaantal, de navytint het plaatsingspercentage")
