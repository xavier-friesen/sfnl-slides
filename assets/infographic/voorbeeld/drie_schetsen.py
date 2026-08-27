#!/usr/bin/env python3
"""Schetsen — drie concepten voor dezelfde boodschap, om te laten kiezen.

Dezelfde inhoud als voorbeeld 1: vier rollen in een resultaatfinanciering, en de betaling die
alleen bij resultaat volgt. Drie wezenlijk verschillende plattegronden, niet drie varianten
van dezelfde.

**Twee van de drie zijn een figuur en één is een rooster, en dat is een regel en geen toeval.**
Een eerdere versie van dit bestand liet drie roosters zien -- kolommen met kaarten, rijen met
kaarten, en twee kolommen met kaarten -- omdat `schets.py` toen niets anders kon tekenen. De
gebruiker koos dus altijd tussen drie keer hetzelfde beeld, en wat er daarna gebouwd werd was
een rij dozen, ook als de vormtoets met een sankey en een tijdlijn begon. Zie de regel in
stap 2D van de SKILL: ten hoogste één van de drie schetsen is een rooster.

Wat elke schets kost, en dat hoort erbij als je ze voorlegt:

* **A, de geldstroom** — de dikte van elke stroom is het aandeel, dus de lezer ziet zonder
  te rekenen waar het geld heen gaat. Kost: de volgorde in de tijd verdwijnt, en de rol van
  de meting is er alleen als ontvanger van een stroom.
* **B, de tijdlijn op schaal** — de gaten tussen de momenten zijn echte gaten, dus je ziet
  dat de betaling pas ná de meting komt en hoe lang daar tussen zit. Kost: de bedragen staan
  er als getal bij en niet als vorm, dus de verhouding tussen de posten is niet zichtbaar.
* **C, vier kolommen op volgorde** — elke rol krijgt evenveel gewicht en er is ruimte voor
  een zin per rol. Kost: er is geen enkele meting die een lengte of een positie bepaalt, dus
  dit beeld zegt wél wie er meedoen en niet hoeveel of wanneer. Dat is de prijs van een
  rooster, en die noem je hardop.

A en B zijn vormkeuzes binnen dezelfde boodschap; C is een andere infographic, want C gaat
over de rollen en niet over het geld. Dat verschil hoort in een set van drie.

En de canvaskeuze zit hier al in: alle drie staan op `breed`, want een band van 960 × 320pt
was de opdracht. Was er een naaf uit de vormtoets gekomen -- "wie hangt aan wie" -- dan had
die een vierkant canvas gevraagd en was het canvas meegegaan met de vorm, niet andersom.
"""
import sys
from pathlib import Path

HIER = Path(__file__).resolve()
sys.path.insert(0, str(HIER.parents[3] / "scripts" / "infographic"))
from schets import (Cel, Rij, as_op_schaal, canvas_manifest, contactblad, rol,  # noqa: E402
                    schets, schets_vrij, seed_helper, stroom)
from svg import CANVAS, lijn, op_schaal  # noqa: E402

UIT = HIER.parents[1] / "maatstaf"
c = CANVAS["breed"]
MARGE = 30

# --- A: de geldstroom. Dikte is het aandeel; de vier posten tellen op tot de inleg.
a = [rol("aanhef", MARGE, 46, 220), rol("drager", MARGE, 84, 220)]
a += stroom(x1=MARGE + 200, x2=c.w - MARGE - 232, y=40, h=150,
            aandelen=[0.52, 0.26, 0.14, 0.08])
a += [rol("post + aandeel", c.w - MARGE - 216, 60 + i * 40, 216) for i in range(4)]
a += [lijn("Slotstreep", MARGE, 232, c.w - MARGE, 232, kleur="navy", dikte=0.75,
           dekking=0.20),
      rol("sluitregel", MARGE, 250, 520),
      rol("bronregel", c.w - MARGE - 250, 250, 250, algn="end")]

# --- B: de tijdlijn. De x is de datum, dus de gaten zijn echte gaten.
MOMENTEN = [0, 4, 16, 28, 33]
b = [rol("aanhef", MARGE, 46, 260), rol("drager", c.w - MARGE - 220, 46, 220, algn="end")]
b += as_op_schaal(150, MOMENTEN, 0, 36, x=MARGE, w=c.w - 2 * MARGE)
# Het label staat onder zijn eigen tik en niet op een vaste steek -- anders is de schets zelf
# de vier-gelijke-banden-fout die deze vorm juist moet vermijden (vormentaal §8).
b += [rol("moment", op_schaal(t, 0, 36, MARGE, c.w - 2 * MARGE) - 6, 172, 150)
      for t in MOMENTEN[:-1]]
b += [lijn("Slotstreep", MARGE, 232, c.w - MARGE, 232, kleur="navy", dikte=0.75,
           dekking=0.20),
      rol("sluitregel", MARGE, 250, 520),
      rol("bronregel", c.w - MARGE - 250, 250, 250, algn="end")]

# De artboardnaam is niet de leesbare naam: het eerste artboard heet Main omdat de
# canvashelper dat eist, en "A — geldstroom" staat in het manifest.
DC = HIER.parents[1] / "canvas"
paden = [
    schets_vrij(UIT / "schets-a.svg", c, "A — geldstroom: dikte is het aandeel", a,
                artboard_=DC / "Main.dc.html"),
    schets_vrij(UIT / "schets-b.svg", c, "B — tijdlijn op schaal: afstand is de tijd", b,
                artboard_=DC / "ConceptB.dc.html"),
    schets(UIT / "schets-c.svg", c, "C — vier kolommen op volgorde, band eronder", [
        Rij(0.14, [Cel("kopband rol", stijl="vol") for _ in range(4)]),
        Rij(0.46, [Cel("toelichting + getal", stijl="tint") for _ in range(4)]),
        Rij(0.04, [Cel("bronregel", stijl="leeg")]),
        Rij(0.30, [Cel("drager", 0.34, "vol"), Cel("sluitregel", 0.66, "vol")],
            goot=0, afbloeden=True),
    ], artboard_=DC / "ConceptC.dc.html"),
]

# De vier regels uit stap 2D. Ze staan hier en niet in een keuzemenu, want naast de schets
# is de enige plek waar de prijs van een concept gelezen wordt.
canvas_manifest(DC / "canvas.json", [
    {"bestand": DC / "Main.dc.html", "canvas": c, "titel": "A — geldstroom",
     "regels": ["Plattegrond: stroom die opsplitst",
                "Meting: dikte is het aandeel",
                "Drager: de inleg, links op displaymaat",
                "Kost: de volgorde in de tijd verdwijnt"]},
    {"bestand": DC / "ConceptB.dc.html", "canvas": c, "titel": "B — tijdlijn op schaal",
     "regels": ["Plattegrond: as met vijf momenten",
                "Meting: x is de datum, de gaten zijn echt",
                "Drager: de doorlooptijd, rechtsboven",
                "Kost: de bedragen staan er als getal, niet als vorm"]},
    {"bestand": DC / "ConceptC.dc.html", "canvas": c, "titel": "C — vier kolommen",
     "regels": ["Plattegrond: vier kolommen met kopband",
                "Meting: geen — dit is het rooster van de drie",
                "Drager: de band onderaan",
                "Kost: zegt wie er meedoen, niet hoeveel of wanneer"]},
])

if __name__ == "__main__":
    import subprocess
    subprocess.run([sys.executable, str(HIER.parents[3] / "scripts" / "infographic" / "render_svg.py"),
                    *[str(p) for p in paden], "--wit", "--schaal", "2"], check=True)
    contactblad([str(p.with_suffix(".png")) for p in paden],
                UIT / "schetsen-drie-concepten.png", kolommen=1)
    print("canvas gereed in", DC, "— seed met", seed_helper() or "(design-skill niet gevonden)")
