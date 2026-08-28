#!/usr/bin/env python3
"""De keuzekaarten bouwen: de vormbesluiten, echt gezet.

Onderhoudsscript, geen bouwstap. Het bestaat omdat de vier layoutmodellen
en de vier kleurregisters met woorden niet uit te leggen zijn. "Kantlijn"
en "dubbel" zeggen niets; twee gezette pagina's naast elkaar zeggen alles.
En omdat de kaarten door dít script uit dezelfde pijplijn komen als het
echte rapport, kunnen ze niet uit de pas gaan lopen met wat de skill
werkelijk bouwt — een kaart die iets belooft wat de zetmotor niet doet,
is erger dan geen kaart.

Drie kaarten:

* `modellen.png` — de vier layoutmodellen, elk als één tekstpagina, met
  de kolommaat en het aantal tekens per regel eronder.
* `registers.png` — de vier kleurregisters, elk als een hoofdstukopener
  plus een tekstpagina, want een register verschilt vooral bij het
  openen van een hoofdstuk.
* `openers.png` — de drie manieren waarop een hoofdstuk begint, met wat
  elk aan ruimte kost.

Gebruik:

    python keuzekaart.py
    python keuzekaart.py --uit assets/rapport/keuzekaarten --alleen modellen
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HIER = Path(__file__).resolve().parent
WORTEL = HIER.parent.parent
# De documentenmap eerst, want `_browser` staat daar — en daarna HIER
# vóóraan, want er staat in beide mappen een `bouw.py` en die van deze
# skill moet winnen. Zonder deze volgorde importeert `from bouw import
# lees_stijl` de documentenversie, die een andere signatuur heeft.
sys.path.insert(0, str(WORTEL / "scripts" / "documenten"))
sys.path.insert(0, str(HIER))
from _browser import browser, wacht_op_letters  # noqa: E402

#: De tafel waarop de gerenderde pagina's liggen. Geen merkkleur maar de
#: achtergrond van het beeld zelf, en dezelfde als die van `body` in `stijl.css`
#: -- de kaart moet eruitzien als een pagina op een tafel en niet als een pagina
#: in het niets. De merkkleuren staan hieronder als `var(--navy)` en
#: `var(--oranje)`: deze CSS wordt achter de gebouwde stijl gezet, en die draagt
#: het merkblok uit `scripts/gedeeld/merk.py` al. Een tweede oranje hier zou het
#: oranje van de kaart laten afwijken van het oranje op de pagina eronder, en de
#: kaart bestaat juist om te laten zien wat de zetmotor werkelijk doet.
TAFEL = "#E7E6EA"

#: Genoeg tekst om drie pagina's te vullen in elk model, met een kop, een
#: opsomming, een figuur en een voetnoot erin. De inhoud is bewust een
#: echt SFNL-onderwerp: een kaart met blindtekst laat je niet zien of de
#: zetting Nederlandse woorden aankan.
PROEF = """# Wat werkt bij resultaatfinanciering

## De opgave

Preventie loont, maar zelden voor de partij die ervoor betaalt. Een gemeente die
investeert in schuldhulpverlening ziet de opbrengst neerslaan bij de zorgverzekeraar
en bij het Rijk. Dat heet in de literatuur een wrong pockets probleem, en het is de
reden dat veel bewezen effectieve interventies niet worden opgeschaald. Het
financieringsvraagstuk is daarmee geen boekhoudkwestie maar een ontwerpvraag.

In de afgelopen tien jaar zijn er in Nederland vijftien social impact bonds tot stand
gekomen, met een gezamenlijke omvang van ongeveer 35 miljoen euro. De uitkomsten
lopen sterk uiteen, en dat is minder verrassend dan het lijkt: een instrument dat op
één plek werkt, werkt op een andere plek niet, omdat de context van de uitvoering
meeweegt.

### Wat opvalt

Wat wel opvalt is dat de instrumenten die het langst standhouden, allemaal een
uitvoerder hebben die het werk al deed voordat de financiering er was. De rol van de
investeerder verschuift daarmee van financier naar medeontwerper van het contract.
Dat vraagt om een andere verhouding tussen opdrachtgever en uitvoerder dan de
aanbesteding gewend is.

- De transactiekosten blijven het meest genoemde bezwaar en zijn ook het best
  gedocumenteerd.
- Een gemiddelde bond kostte in de voorbereiding tussen de negen en achttien maanden
  aan doorlooptijd.
- De standaardisatie van contracten zou daar het meeste aan kunnen doen, en gebeurt
  tot nu toe nauwelijks.

## Wat de cijfers laten zien

Op de langere termijn is de vraag niet of dit soort constructies blijven bestaan,
maar welke vorm ze aannemen wanneer de subsidie wegvalt. De ervaring uit het
Verenigd Koninkrijk wijst op een beweging naar outcomes funds, waarin meerdere
opdrachtgevers hun middelen bundelen. Daarmee verdwijnt de bilaterale onderhandeling
die elke afzonderlijke bond zo duur maakte.

Nederland kent die bundeling nog niet, al zijn er twee initiatieven die die kant op
bewegen. Wat de gemeente daarvoor terugkrijgt is een uitvoering die aantoonbaar op
resultaat stuurt. Of dat de prijs waard is, hangt af van wat het alternatief kost en
dat wordt zelden uitgerekend.

| Instrument | Jaar | Omvang (mln) | Uitkomst |
| --- | --- | --- | --- |
| Bond 1 | 2016 | 1,4 | gehaald |
| Bond 2 | 2017 | 2,8 | deels |
| Bond 3 | 2018 | 4,2 | gehaald |

Dat is niet vol te houden voor een opgave die volgend jaar geregeld moet zijn. De
standaardisatie van contracten zou daar het meeste aan kunnen doen, en gebeurt tot nu
toe nauwelijks. Wat de gemeente daarvoor terugkrijgt is een uitvoering die aantoonbaar
op resultaat stuurt.

## Handelingsperspectief

Een instrument dat op één plek werkt, werkt op een andere plek niet, omdat de context
van de uitvoering meeweegt. Preventie loont, maar zelden voor de partij die ervoor
betaalt. Een gemeente die investeert in schuldhulpverlening ziet de opbrengst
neerslaan bij de zorgverzekeraar en bij het Rijk.

1. Standaardiseer het contract, want daar zit de doorlooptijd.
2. Bundel de opdrachtgevers, want daar zit de schaal.
3. Reken het alternatief door, want anders is de prijs niet te wegen.
"""

MODELLEN = [
    ("breed", "één kolom van 537 px",
     "77 tekens per regel, brood op 11/16,5 pt. De maat van een Bain-rapport, "
     "en het model dat nooit een lege kolom heeft."),
    ("kantlijn", "één kolom van 480 px plus een kantlijn van 140",
     "76 tekens, brood op 10/13 pt. De noten en de bronnen staan in de kantlijn, "
     "naast de regel waar ze bij horen. Zonder noten staat die kolom leeg."),
    ("dubbel", "twee kolommen van 310 px",
     "48 tekens, brood op 10/13 pt. De maat van het SFNL-drukwerk zelf, "
     "en de dichtste zetting van de vier."),
    ("flexibel", "kantlijn als basis, per sectie anders",
     "Eén broodmaat voor het hele rapport. Een figuur of een brede tabel krijgt "
     "een pagina over de volle breedte."),
]

REGISTERS = [
    ("helder", "wit papier, navy inkt, oranje accent",
     "De default. Het rustigste van de vier en het enige dat een rapport van "
     "tachtig pagina's volhoudt zonder te gaan schreeuwen."),
    ("diep", "hoofdstukken openen op een heel navy blad",
     "Kost een pagina per hoofdstuk en geeft er ritme voor terug. Pas vanaf "
     "veertig pagina's."),
    ("zacht", "emerald in plaats van oranje",
     "Voor een onderzoeksrapport of een evaluatie. Oranje blijft over voor de "
     "folio, zodat het merk niet verdwijnt."),
    ("contrast", "violet als hoofdaccent, oranje als tweede",
     "Het register van de casespread. Voor een rapport dat uit cases bestaat "
     "die van elkaar moeten verschillen."),
]

OPENERS = [
    ("nummer", "kop met een watermerkcijfer",
     "Kost geen pagina. Het cijfer staat half achter de titel."),
    ("band", "een aflopende band bovenaan de eerste pagina",
     "Kost ongeveer een kwart pagina per hoofdstuk."),
    ("blad", "een heel blad met alleen de hoofdstuknaam",
     "Kost een pagina per hoofdstuk. Pas vanaf veertig pagina's."),
]


def bouw_variant(werk: Path, naam: str, **overschrijf) -> Path:
    """Eén variant echt bouwen, via dezelfde route als een echt rapport."""
    map_ = werk / naam
    map_.mkdir(parents=True, exist_ok=True)
    shutil.copy(werk / "document.json", map_ / "document.json")
    shutil.copy(werk / "bron-tekst.txt", map_ / "bron-tekst.txt")
    ontwerp = {"model": "breed", "register": "helder", "formaat": "sfnl",
               "opener": "nummer", "bandhoogte": 232, "dubbelzijdig": False,
               "omslag": False, "inhoudsopgave": False, "hoofdstuknummers": True,
               "exhibitnummers": True, "eersteFolio": 1, "folioVanaf": 1,
               "rapporttitel": "Wat werkt bij resultaatfinanciering"}
    ontwerp.update(overschrijf)
    (map_ / "ontwerp.json").write_text(json.dumps(ontwerp, ensure_ascii=False),
                                       encoding="utf-8")
    uit = subprocess.run(
        [sys.executable, str(HIER / "bouw.py"), str(map_), "--uit", "proef.html"],
        capture_output=True, text=True)
    if uit.returncode:
        sys.exit(f"bouw mislukte voor {naam}:\n{uit.stderr[-1500:]}")
    return map_ / "proef.html"


KAART_CSS = """
  body { background: %s; margin: 0; padding: 0; font-family: Lato, system-ui, sans-serif; }
  .vel { display: block !important; padding: 0 !important; }
  .kaartrij { display: flex; gap: 26px; align-items: flex-start; }
  .kolom { width: 320px; flex: 0 0 auto; }
  /* Padding op de kaart zelf en niet op het lichaam: het beeld wordt van
     dit element genomen, en padding op het lichaam valt er dan buiten. */
  #kaart { display: inline-block; padding: 30px 34px 34px; }
  .beeldrij { display: flex; gap: 2px; box-shadow: 0 3px 14px rgba(var(--navy-rgb),.24);
              background: #fff; margin-bottom: 12px; }
  .beeldrij .pagina { box-shadow: none !important; margin: 0 !important; }
  h2 { font-family: Montserrat, system-ui, sans-serif; font-weight: 800;
       font-size: 17px; color: var(--navy); margin: 0 0 3px; letter-spacing: -.01em; }
  .maat { font-family: Montserrat, system-ui, sans-serif; font-weight: 700;
          font-size: 10px; letter-spacing: .1em; text-transform: uppercase;
          color: var(--oranje); margin: 0 0 6px; }
  p.uitleg { font-size: 12.5px; line-height: 16.5px; color: var(--navy); margin: 0; }
  h1 { font-family: Montserrat, system-ui, sans-serif; font-weight: 800;
       font-size: 24px; color: var(--navy); margin: 0 0 4px; }
  .intro { font-size: 13px; line-height: 17px; color: var(--navy); opacity: .74;
           margin: 0 0 26px; max-width: 900px; }
""" % TAFEL


def montage(page, titel: str, intro: str, kolommen: list, uit: Path) -> None:
    """De gerenderde pagina's naast elkaar met hun uitleg eronder."""
    page.evaluate("""([titel, intro, kolommen]) => {
        const houder = document.createElement('div');
        houder.id = 'kaart';
        const h = document.createElement('h1'); h.textContent = titel;
        const i = document.createElement('p'); i.className = 'intro'; i.textContent = intro;
        houder.appendChild(h); houder.appendChild(i);
        const rij = document.createElement('div'); rij.className = 'kaartrij';
        for (const k of kolommen) {
          const kol = document.createElement('div'); kol.className = 'kolom';
          if (k.breed) kol.style.width = k.breed + 'px';
          const beeld = document.createElement('div'); beeld.className = 'beeldrij';
          beeld.style.zoom = k.zoom;
          for (const sel of k.paginas) {
            const el = document.querySelector(sel);
            if (el) beeld.appendChild(el);
          }
          const naam = document.createElement('h2'); naam.textContent = k.naam;
          const maat = document.createElement('p'); maat.className = 'maat';
          maat.textContent = k.maat;
          const uitleg = document.createElement('p'); uitleg.className = 'uitleg';
          uitleg.textContent = k.uitleg;
          kol.appendChild(beeld); kol.appendChild(naam);
          kol.appendChild(maat); kol.appendChild(uitleg);
          rij.appendChild(kol);
        }
        houder.appendChild(rij);
        document.body.innerHTML = '';
        document.body.appendChild(houder);
    }""", [titel, intro, kolommen])
    page.wait_for_timeout(300)
    # Het beeld van de kaart zelf en niet van de pagina. `full_page`
    # neemt de viewporthoogte als ondergrens, en dan staat er onder de
    # kaart een half blad leeg — op de eerste kaart was dat meer dan de
    # kaart zelf.
    page.locator("#kaart").screenshot(path=str(uit))


def kaart(paden: dict, varianten: list, titel: str, intro: str,
          uit: Path, paginas_per: int = 1, zoom: float = 0.4) -> None:
    """Alle varianten in één beeld, elk uit zijn eigen gebouwde bestand.

    De pagina's worden per variant in een eigen tabblad geladen en als
    dataless kopie in de montagepagina gezet; dat kan niet, dus in plaats
    daarvan wordt de montage per variant opgebouwd door de HTML van de
    gewenste pagina's over te nemen.
    """
    with browser() as b:
        page = b.new_page(viewport={"width": 2100, "height": 1000},
                          device_scale_factor=2)
        # Alle varianten samenvoegen in één document, per variant een sectie.
        stukken = []
        for naam, maat, uitleg in varianten:
            html = paden[naam].read_text(encoding="utf-8")
            import re
            paginas = re.findall(
                r'<div class="pagina".*?(?=<div class="pagina"|</div>\s*</body>)',
                html, re.S)
            kies = paginas[:paginas_per]
            stukken.append(f'<div data-variant="{naam}">' + "".join(kies) + "</div>")
        stijl = paden["__stijl"]
        page.set_content(
            f"<!doctype html><html lang='nl'><head><meta charset='utf-8'>"
            f"<style>{stijl}\n{KAART_CSS}</style></head><body>"
            + "".join(stukken) + "</body></html>")
        wacht_op_letters(page)
        # Twee pagina's naast elkaar hebben een bredere kolom nodig,
        # anders snijdt de kolom de rechterpagina af.
        breed = round(794 * paginas_per * zoom) + 8
        kolommen = [
            {"naam": naam, "maat": maat, "uitleg": uitleg, "zoom": zoom,
             "breed": breed,
             "paginas": [f'[data-variant="{naam}"] .pagina:nth-of-type({n + 1})'
                         for n in range(paginas_per)]}
            for naam, maat, uitleg in varianten
        ]
        montage(page, titel, intro, kolommen, uit)
    print(f"geschreven: {uit}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--uit", type=Path,
                    default=WORTEL / "assets" / "rapport" / "keuzekaarten")
    ap.add_argument("--alleen", choices=("modellen", "registers", "openers"))
    a = ap.parse_args()
    a.uit.mkdir(parents=True, exist_ok=True)

    tijdelijk = Path(tempfile.mkdtemp(prefix="sfnl-keuzekaart-"))
    try:
        bron = tijdelijk / "proef.md"
        bron.write_text(PROEF, encoding="utf-8")
        werk = tijdelijk / "werk"
        uit = subprocess.run([sys.executable, str(HIER / "lees_docx.py"),
                              str(bron), "--uit", str(werk)],
                             capture_output=True, text=True)
        if uit.returncode:
            sys.exit(f"lezen mislukte:\n{uit.stderr[-1200:]}")

        from bouw import lees_stijl
        stijl = lees_stijl()

        if a.alleen in (None, "modellen"):
            for naam, _, _ in MODELLEN:
                bouw_variant(werk, "m-" + naam, model=naam)
            paden = {"__stijl": stijl, **{n: (werk / ("m-" + n) / "proef.html")
                                          for n, _, _ in MODELLEN}}
            kaart(paden, MODELLEN, "Vier layoutmodellen",
                  "Eén tekstpagina per model, echt gezet, op dezelfde tekst. "
                  "Het model bepaalt hoeveel er per pagina in gaat en hoe lang "
                  "een regel is; het is het besluit dat alle andere volgen.",
                  a.uit / "modellen.png", paginas_per=1, zoom=0.42)

        if a.alleen in (None, "registers"):
            for naam, _, _ in REGISTERS:
                bouw_variant(werk, "r-" + naam, model="kantlijn", register=naam,
                             opener="blad" if naam in ("diep", "contrast") else "nummer")
            paden = {"__stijl": stijl, **{n: (werk / ("r-" + n) / "proef.html")
                                          for n, _, _ in REGISTERS}}
            kaart(paden, REGISTERS, "Vier kleurregisters",
                  "De eerste twee pagina's per register. Een register verschilt "
                  "vooral bij het openen van een hoofdstuk; op de tekstpagina's "
                  "eronder is het verschil één accentkleur.",
                  a.uit / "registers.png", paginas_per=2, zoom=0.3)

        if a.alleen in (None, "openers"):
            for naam, _, _ in OPENERS:
                bouw_variant(werk, "o-" + naam, model="kantlijn", opener=naam)
            paden = {"__stijl": stijl, **{n: (werk / ("o-" + n) / "proef.html")
                                          for n, _, _ in OPENERS}}
            kaart(paden, OPENERS, "Drie manieren waarop een hoofdstuk begint",
                  "Eén manier voor alle hoofdstukken in een rapport. Wat ze van "
                  "elkaar onderscheidt is niet hoe ze eruitzien maar wat ze kosten.",
                  a.uit / "openers.png", paginas_per=1, zoom=0.42)
    finally:
        shutil.rmtree(tijdelijk, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
