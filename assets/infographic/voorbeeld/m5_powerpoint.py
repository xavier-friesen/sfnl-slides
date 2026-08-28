#!/usr/bin/env python3
"""Maatstaf 5 — een waterval als losse PowerPoint-slide op layout 17. Register: bijna wit.

Layout 17 is het blanco canvas van het SFNL-sjabloon: geen titel, geen oranje dash, geen
placeholders. De slide die hieruit komt kopieer je in elk SFNL-deck; de titel komt daar van de
slide eromheen of van de spreker.

**En hij is echt leeg, maar daar is één stap voor nodig die eerst ontbrak.** Layout 17 is zelf
leeg, maar `slideMaster2.xml` tekent er het SFNL-logo linksonder en een paginanummer rechtsonder
bij. Dat zie je alleen op de render, niet in de XML van de slide. `scripts/infographic/blanco.py` zet
`showMasterSp="0"` op de layout en haalt allebei weg; `add_slide.py --no-page-number` uit de
plugin weigert dat hier, omdat die vlag ook het logo meeneemt en dat voor een deck vrijwel nooit
de bedoeling is. Voor een losse infographic is het dat wél.

In een eerdere versie liep de sluitregel dwars door het logo. Dat was pas op de render te zien,
omdat de versie daarvóór er toevallig een navy band overheen had staan -- precies de reden dat
de renderloop niet overslaanbaar is.

**Er staat ook geen bronregel op.** Dat is een keuze en geen vergetelheid: bij de intake is
gekozen voor "de container draagt de bron", dus de herkomst staat op de slide eromheen of in de
notities. Gaat dit beeld los rondzwerven, dan hoort de bronregel er alsnog op (vormentaal §10).

Waarom een waterval, en waarom dit register
-------------------------------------------
De eerste versie van deze maatstaf was een rij kaarten op containervulling. Die was niet fout,
maar naast de vier SVG-maatstaven zag hij er zwaar en gedateerd uit -- en dat is precies het
oordeel dat een set maatstaven moet uitlokken. De reparatie was niet een lichtere tint maar een
andere vorm: een waterval bouwt het saldo op in vijf stappen, en die vijf stappen vullen een
hele slide zonder dat er één vlak nodig is dat niets zegt.

Wat je hier af kunt kijken:

* **Kleur codeert het teken.** Emerald is een plus, grapefruit een min, navy het eindsaldo.
  Drie hues, en alle drie hebben ze een betekenis die je in één woord kunt zeggen.
* **De laatste kolom is klein, en dat is het punt.** € 1,18 mln aan opbrengsten tegen € 1,10 mln
  aan kosten laat 76 duizend over. Een waterval liegt daar niet over; drie kaarten naast elkaar
  wel.
* **Geen enkele containervulling.** Alleen de kolommen zijn gevuld, en die dragen inhoud.
  De rest is haarlijn en wit.
* **De nullijn loopt door onder alle kolommen.** Zonder die lijn zweven ze.

Twee dingen die alleen in de PowerPoint-route gelden, en die op de render zijn nagemeten:

1. Een tekstvak zonder vulling heeft insets 0, dus tekst begint exact op de vormrand. Zet zo'n
   vak op `x + 0,2`, anders hangt de eerste letter over de rand.
2. `spc_voor` staat in honderdsten van een punt: 600 is 6pt. 14000 is 140pt en zet je alinea
   anderhalve inch lager, dwars door de vorm eronder.

Dit script is herbouwbaar: de eerste regel gooit de builddir weg. Dat is geen nettigheid maar
noodzaak, want `write()` voegt vormen toe vóór `</p:spTree>` en `add_slide.py` hangt een slide
achteraan -- een tweede run op een bestaande map verdubbelt alles wat er al stond.

    python m5_powerpoint.py --uit ./uitvoer

`--plugin` was hier verplicht toen deze skill los stond: de deckscripts lagen ergens anders
en je moest zeggen waar. Sinds `sfnl-infographic` in dezelfde plugin zit als `sfnl-slides`
liggen ze twee mappen hoger, dus dat is nu de standaardwaarde en de vlag is er alleen nog
om naar een andere checkout te wijzen.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

#: De plugin-map. Dit bestand ligt in `assets/infographic/voorbeeld/`, dus drie op.
WORTEL = Path(__file__).resolve().parents[3]

a = argparse.ArgumentParser()
a.add_argument("--plugin", default=str(WORTEL),
               help="map van de plugin; standaard de plugin waar dit bestand in staat")
a.add_argument("--uit", default="./uitvoer")
args = a.parse_args()

PLUG = Path(args.plugin).resolve()
UIT = Path(args.uit).resolve()
BOUW = UIT / "bouw"
sys.path.insert(0, str(PLUG / "scripts"))

if BOUW.exists():
    shutil.rmtree(BOUW)
BOUW.mkdir(parents=True)


def loop(*cmd: str) -> str:
    r = subprocess.run([sys.executable, *cmd], capture_output=True, text=True, cwd=BOUW)
    if r.returncode:
        raise SystemExit(f"{cmd}\n{r.stdout}\n{r.stderr}")
    return r.stdout


S = str(PLUG / "scripts")
loop(f"{S}/prepare_template.py", ".", "--template", str(PLUG / "assets/sfnl-sjabloon.potx"))
loop(f"{S}/add_slide.py", "unpacked", "slideLayout17.xml", "--bare")
# Layout 17 is zelf leeg, maar master 2 tekent er het SFNL-logo en het paginanummer bij.
# `blanco.py` zet `showMasterSp="0"` op de layout en haalt die twee weg. Zie de docstring
# van dat script voor waarom `add_slide.py --no-page-number` dit hier weigert.
sys.path.insert(0, str(WORTEL / "scripts" / "infographic"))
from blanco import blanco  # noqa: E402
blanco(BOUW / "unpacked")

from shapes import (Deck, aanhef, drager, label, para, run, streep, tekst, vlak,  # noqa: E402
                    write)

SLIDE_B, SLIDE_H = 13.333, 7.5
D = Deck(body=14, label=11, sluit=15, display=40)
MARGE = 0.62

# waarde, hue, naam. Een None-waarde is een totaalkolom: die staat vanaf nul.
STAPPEN = [
    (700,   "emerald",    "Uitkeringen\ndie wegvallen"),
    (296,   "emerald",    "Minder\nzorgkosten"),
    (184,   "emerald",    "Belasting\nen premies"),
    (-1104, "grapefruit", "Kosten van\nde aanpak"),
    (None,  "navy",       "Wat overblijft"),
]

TOP, BODEM = 1.62, 5.55                   # het tekenvlak van de waterval
HOOG = BODEM - TOP
MAX = 1180.0                              # de hoogste cumulatieve waarde
KOL_B = 1.42
n = len(STAPPEN)
GOOT = (SLIDE_B - 2 * MARGE - n * KOL_B) / (n - 1)


def y(waarde: float) -> float:
    """De y van een waarde op de schaal. Nul ligt op de bodem."""
    return BODEM - waarde * HOOG / MAX


vormen = [
    vlak("Aanhef", MARGE, 0.55, 6.0, 0.3,
         tekst=[para(label("BUSINESSCASE PER COHORT VAN 120 DEELNEMERS", D.label,
                           "navy"))]),
    vlak("Drager", SLIDE_B - MARGE - 4.6, 0.48, 4.6, 0.95,
         tekst=[para(drager("+ € 0,08 mln", D.display, "emerald"), algn="r")]),
    vlak("Drager regel", SLIDE_B - MARGE - 4.6, 1.36, 4.6, 0.3,
         tekst=[para(run("saldo over drie jaar", "Lato Light", D.body, kleur="navy"),
                     algn="r")]),
]

loop_ = 0.0                               # de lopende stand
for i, (waarde, hue, naam) in enumerate(STAPPEN):
    x = MARGE + i * (KOL_B + GOOT)
    if waarde is None:                    # totaalkolom: vanaf nul
        top, hoog = y(loop_), y(0) - y(loop_)
        toon = loop_
    else:
        nieuw = loop_ + waarde
        top, hoog = y(max(loop_, nieuw)), abs(y(nieuw) - y(loop_))
        toon = waarde
        loop_ = nieuw
    vormen.append(vlak(f"Kolom {i+1}", x, top, KOL_B, hoog, vulling=hue, lijn=None))
    # het getal boven de kolom, in de hue van de kolom
    vormen.append(vlak(f"Kolom {i+1} getal", x, top - 0.34, KOL_B, 0.3,
                       tekst=[para(run(("+ " if (waarde or 0) > 0 else
                                        ("\u2212 " if (waarde or 0) < 0 else "")) +
                                       f"€ {abs(toon) / 1000:.2f}".replace(".", ",") + " mln",
                                       "Montserrat Light", D.body, vet=True,
                                       kleur=hue if hue != "emerald" else "navy"),
                                   algn="ctr")]))
    # de naam onder de nullijn
    vormen.append(vlak(f"Kolom {i+1} naam", x, BODEM + 0.13, KOL_B, 0.62,
                       tekst=[para(run(r, "Lato Light", D.body, kleur="navy"), algn="ctr")
                              for r in naam.split("\n")]))
    # de verbindingslijn naar de volgende kolom, op de stand van dit moment
    if i < n - 1:
        vy = y(loop_)
        vormen.append(streep(f"Verbinding {i+1}", x + KOL_B, vy, GOOT, "navy", 0.75))

vormen += [
    streep("Nullijn", MARGE, BODEM, SLIDE_B - 2 * MARGE, "navy", 1.0),
    # De sluitregel staat bóven de logostrook, niet ernaast: één regel, en dan houdt de
    # onderste 0,6 in zich stil.
    streep("Slotstreep", MARGE, 6.42, SLIDE_B - 2 * MARGE, "navy", 0.75),
    vlak("Sluitregel", MARGE, 6.54, SLIDE_B - 2 * MARGE, 0.34,
         # Eén familie per regel: de aanhef is Lato Light met `vet=True` en niet een
         # SemiBold-snede -- er zijn drie letters in een deck (vormentaal.md §9). Hier
         # stond Montserrat SemiBold naast Lato Light in één alinea, en `para()` weigerde
         # die mix al.
         tekst=[para(*aanhef("De opbrengst valt bij de gemeente",
                             ", de kosten bij de uitvoerder.", D.sluit))]),
]
write(str(BOUW / "unpacked/ppt/slides/slide1.xml"), vormen)

loop(f"{S}/clean.py", "unpacked")
loop(f"{S}/office/pack.py", "unpacked", "infographic.pptx",
     "--original", str(PLUG / "assets/sfnl-sjabloon.potx"))
UIT.mkdir(parents=True, exist_ok=True)
shutil.copy(BOUW / "infographic.pptx", UIT / "m5-powerpoint.pptx")
print(f"nullijn {BODEM} | kolommen {KOL_B:.2f} in met goot {GOOT:.2f} in")
print(UIT / "m5-powerpoint.pptx")
