#!/usr/bin/env python3
"""Een afgemaakte infographic in een van de zusterroutes zetten, en narekenen of hij past.

    python insluiten.py beeld.svg --doel document --kader breed \
        --pagina werk/Main.dc.html --bijschrift "..."
    python insluiten.py beeld.svg --doel rapport --kader kolom --bijschrift "..." --na b0042
    python insluiten.py beeld.svg --doel slide

Waarom dit een script is en geen alinea in de SKILL
---------------------------------------------------
Alle vier de skills in deze plugin kunnen een infographic gebruiken, en alle drie de
containers zeggen dat ook: `documenten-vormentaal.md` §11, `rapport-vormentaal.md` onder
"Geen infographics ontwerpen", en `vormentaal.md` bij de bovengrens van twaalf onderdelen.
Wat er niet stond is hoe.

Het "hoe" bestaat uit drie dingen, en ze hebben iets gemeen: **je ziet ze geen van drieën op
de render van het beeld zelf.** Ze worden pas zichtbaar als het beeld op de pagina staat, en
dan is het te laat om er nog een ontwerpbesluit van te maken. Daarom is dit een poort en geen
rapportje: hij geeft exitcode 1 en levert het fragment niet.

1. **De maten.** Een SVG schaalt álles mee, ook zijn letters. Een beeld dat op 960 pt is
   getekend en in een kader van 680 px staat, krimpt met factor 0,53: een voetnoot van 10 pt
   komt er op 5,31 pt uit, onder de leesvloer, zonder dat er iets in de markup fout staat.
   Dat is de meting die `documenten-vormentaal.md` §11 punt 1 al beschrijft en die niemand
   uitrekende. De reparatie is het canvas: `CANVAS["doc-breed"]` en zijn vijf broers staan
   er precies daarvoor, met `Maten.voor("document")` voor de maatladder.
2. **De omlijsting.** Een los beeld draagt zijn eigen aanhef en bronregel -- er is niets
   anders dat ze draagt, en zo staat het in de inventaris van de SKILL. Een exhibit staat
   onder een kop en boven een bijschrift, dus alles wat het beeld daarvan herhaalt is een
   tweede stem over hetzelfde. Geef `--pagina` en `--bijschrift` mee, dan vergelijkt hij.
   Zie het blok bij `dubbelingen`.
3. **Het dode wit onderin.** De verhouding van het kader komt uit de `viewBox`, dus een
   canvas dat voor 70 procent gevuld is, reserveert 30 procent witruimte op de pagina.
   `pas_hoogte(c, vormen)` in `svg.py` zet de hoogte op de compositie; de regel waarmee hier
   gemeten wordt is `wit_onder()` in datzelfde bestand, zodat de waarschuwing tijdens het
   bouwen en de poort hier niet uit elkaar kunnen lopen.

De drie bestemmingen, en ze verschillen echt
--------------------------------------------
* **`document`** — `sfnl-design-documents`. De artboards zijn met de hand gecomponeerde
  HTML, dus de SVG gaat er **inline** in, in een `.beeldkader` met de verhouding inline.
  Zo doet `assets/documenten/voorbeeld/Geldstroom.dc.html` het ook. Tekst blijft tekst en
  de PDF houdt hem selecteerbaar.
* **`rapport`** — `sfnl-rapport-opmaak`. Daar plaatst `bouw.py` beeld als `<img src>` uit
  de `figuren`-JSON, dus hier is de oplevering een **PNG op 2x** plus de regel voor die
  JSON. Factor 2 is bedoeld -- een bitmap wordt op het dubbele geëxporteerd om op 192 dpi
  te drukken -- en blijft onder de krimpgrens van 2,5 uit `rapport-stramien.md` §7c.
* **`slide`** — `sfnl-slides`. Een PNG op 2x om in een deck te plakken. Wil je een beeld
  dat in PowerPoint zelf bewerkbaar blijft, dan is dit script het verkeerde gereedschap:
  dan bouw je de slide met stap 4B van `sfnl-infographic`.

Het script schrijft niets in het doelbestand. Het levert het fragment of de JSON-regel op
stdout of in een bestand, en de plaatsing blijft een besluit van de route die hem plaatst.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
WORTEL = HIER.parents[1]

PX_PER_PT = 96.0 / 72.0

#: De kaders per bestemming: de breedte in px zoals het stramien hem noemt, en het canvas
#: waarop je voor dat kader hoort te tekenen. Zie `reference/samenstellen.md`.
KADERS: dict[str, dict[str, tuple[float, str]]] = {
    "document": {
        "breed":  (680, "doc-breed"),      # de volle zetspiegel
        "kolom2": (325, "doc-kolom2"),     # één van twee kolommen
        "kolom3": (207, "doc-kolom3"),     # één van drie kolommen
    },
    "rapport": {
        "breed":  (650, "rap-breed"),      # de volle zetspiegel
        "kolom":  (537, "rap-kolom"),      # de tekstkolom in het model `breed`
        "dubbel": (310, "rap-dubbel"),     # een kolom in het model `dubbel`
    },
    "slide": {
        # Een slide rekent in inches en niet in px; de contentzone is 12,52 x 5,00 in.
        "contentzone": (901 * PX_PER_PT, "contentzone"),
        "slide":       (960 * PX_PER_PT, "slide"),
        "kolom":       (425 * PX_PER_PT, "kolom"),
    },
}

#: De leesvloer per bestemming, in pt.
#:
#: Voor een document zijn dit de getallen die `qa_document.py` zelf handhaaft: 10,4 px
#: voor lopende tekst en 8 px voor een gespatieerd kapitaallabel, dus 7,8 en 6 pt. Ze
#: staan hier in punten omdat dit script ook een pt-canvas kan meten, en ze staan
#: precies gelijk aan die regel omdat twee bijna-gelijke vloeren erger zijn dan één:
#: dan keurt het ene script goed wat het andere afkeurt. Het rapport rekent met dezelfde
#: 6 pt als absolute vloer (`rapport-stramien.md` §7c). Op een slide is de vloer hoger,
#: want die wordt geprojecteerd en niet gelezen.
VLOER: dict[str, float] = {"document": 7.8, "rapport": 6.0, "slide": 12.0}

#: De eenheid waarin het canvas van elke bestemming rekent. Zie `svg.py`, `EENHEID`.
EENHEID_DOEL = {"document": "px", "rapport": "px", "slide": "pt"}
#: Wat één eenheid in punten is.
IN_PUNTEN = {"pt": 1.0, "px": 0.75}


def _in(punten: float, eenheid: str) -> float:
    """Een maat in punten, uitgedrukt in de eenheid van het bestand."""
    return punten / IN_PUNTEN[eenheid]


def viewbox(svg: str) -> tuple[float, float]:
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if not m:
        raise SystemExit("geen viewBox in de SVG; schrijf hem met svg.schrijf()")
    return float(m.group(1)), float(m.group(2))


def eenheid_van(svg: str) -> str:
    """De eenheid waarin dit bestand getekend is, uit zijn eigen `width`.

    `svg.py` schrijft `width="960pt"` voor een pt-canvas en `width="680"` voor een
    px-canvas, want px is de standaardeenheid van SVG. Dit leest dus wat er is in plaats
    van aan te nemen wat er hoort te zijn -- en dat is precies het verschil dat dit
    script moet kunnen melden.
    """
    m = re.search(r'\bwidth="[\d.]+(pt|px|)"', svg)
    return (m.group(1) or "px") if m else "px"


def maten_in(svg: str) -> list[float]:
    """Alle `font-size`-waarden in de SVG, in tekeneenheden (dus pt)."""
    return sorted({float(x) for x in re.findall(r'font-size="([\d.]+)"', svg)})


def hoogte_gebruikt(svg: str) -> float | None:
    """Hoe ver de compositie in de hoogte komt, gemeten aan de laagste `y` in het bestand.

    Dit is een nameting op het bestand en geen boekhouding uit het bouwscript, want
    `insluiten.py` krijgt alleen de SVG. Meegenomen: de baseline van elke `tspan`, de
    onderkant van elke `rect`, en het eindpunt van elke `line`. Niet meegenomen: `path`
    en `circle`, want die dragen hun doos niet in hun attributen -- staat je figuur
    grotendeels in paden, dan is dit een ondergrens.
    """
    y: list[float] = []
    y += [float(v) for v in re.findall(r'<tspan[^>]*\by="([\d.]+)"', svg)]
    for m in re.finditer(r'<rect[^>]*\by="([\d.-]+)"[^>]*\bheight="([\d.]+)"', svg):
        y.append(float(m.group(1)) + float(m.group(2)))
    y += [float(v) for v in re.findall(r'<line[^>]*\by2="([\d.]+)"', svg)]
    return max(y) if y else None


# ------------------------------------------------------------------ de dubbeling
#
# Een exhibit staat niet alleen. De pagina eromheen draagt al een kop, vaak een chapeau,
# en onder het kader een bijschrift met de bron; een rapport-exhibit draagt bovendien
# `.exhibit__nr`, `.exhibit__titel` en `.exhibit__eenheid`. Alles wat het beeld daarvan
# herhaalt, is een tweede stem over hetzelfde -- en het is de stem die je het makkelijkst
# per ongeluk meeneemt, want in een LOS beeld hoort er juist wel een aanhef en een
# bronregel op te staan (SKILL, "Wat er op het vlak komt"). De overstap van los beeld naar
# exhibit is precies de plek waar die twee regels tegen elkaar in gaan.
#
# Nagemeten op de eerste gebouwde documentpagina: de kop van de pagina was "De inleg gaat
# voor de helft naar begeleiding", de aanhef op het beeld "WAAR DE INLEG HEEN GAAT", en de
# bronregel stond twee keer -- in de SVG en in de `figcaption` eronder.

#: Woorden die in beide teksten mogen staan zonder dat het iets zegt.
STOP = {
    "de", "het", "een", "en", "van", "in", "op", "voor", "met", "die", "dat", "is",
    "zijn", "naar", "aan", "bij", "over", "per", "als", "om", "te", "er", "ook",
    "tot", "uit", "door", "wat", "waar", "dan", "of", "maar", "niet", "geen",
}


def _woorden(s: str) -> list[str]:
    return [w for w in re.findall(r"[a-zà-ÿ0-9]+", s.lower()) if w not in STOP]


#: Welke rollen op een beeld de OMGEVING kan dragen, en welke niet.
#:
#: Dit onderscheid is de kern van de dubbelingstoets, en het is er na een valse melding:
#: de eerste versie vlagde `Begeleiding op de werkvloer` als dubbeling omdat de chapeau
#: van de pagina diezelfde woorden gebruikte. Maar dat is het label van een staaf, en een
#: figuur die zijn eigen elementen niet meer labelt, is geen figuur meer -- direct
#: labelen is vormentaal §9 en het staat boven deze toets.
#:
#: Wat de container wél kan overnemen is de OMLIJSTING: de aanhef boven het beeld, de
#: bronregel eronder, de sluitregel, en de drager. Precies de vier die in een LOS beeld
#: horen te staan, en die in een exhibit een tweede stem worden.
OMLIJSTING = ("aanhef", "bron", "drager")


def rol_van(attr: str, drager_window: tuple[float, float]) -> str:
    """De rol van een `<text>`, afgeleid uit zijn attributen en niet uit zijn naam.

    Uit de attributen, want een bouwer noemt zijn vormen zoals hij wil en de SKILL
    schrijft alleen een beschrijvende naam voor. Wat er wél vastligt is hoe `svg.py` de
    vier rollen zet: `label()` zet kapitalen met letterspatiëring, `bron()` zet dekking
    0,70, en `drager()` staat in het window van 28 tot 40 pt.
    """
    pt = float(m.group(1)) if (m := re.search(r'font-size="([\d.]+)"', attr)) else 0.0
    if drager_window[0] <= pt <= drager_window[1]:
        return "drager"
    if re.search(r'letter-spacing="[\d.]+"', attr):
        return "aanhef"
    if (o := re.search(r'fill-opacity="([\d.]+)"', attr)) and 0.6 <= float(o.group(1)) <= 0.8:
        return "bron"
    return "element"


def tekst_uit_svg(svg: str, drager_window: tuple[float, float] = (28.0, 40.0)
                  ) -> list[tuple[str, str, str]]:
    """(id, rol, regel) per `<text>`-element, met de tspans eraan geplakt."""
    uit = []
    for m in re.finditer(r'<text\b([^>]*)>(.*?)</text>', svg, re.S):
        attr, binnen = m.group(1), m.group(2)
        idm = re.search(r'id="([^"]*)"', attr)
        regels = re.findall(r"<tspan[^>]*>(.*?)</tspan>", binnen, re.S)
        tekst = " ".join(re.sub(r"<[^>]+>", "", r) for r in regels).strip()
        tekst = re.sub(r"\s+", " ", tekst)
        if tekst:
            uit.append((idm.group(1) if idm else "?", rol_van(attr, drager_window), tekst))
    return uit


def tekst_uit_pagina(html: str) -> str:
    """De zichtbare tekst van een `.dc.html` of een HTML-fragment, plat.

    De SVG's gaan eruit: dat is beeld dat er al staat, en een infographic die naast een
    andere infographic staat hoeft daar niets van te weten.
    """
    h = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", html, flags=re.S | re.I)
    h = re.sub(r"<[^>]+>", " ", h)
    h = h.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", h).strip()


def dubbelingen(svg: str, omgeving: str, drempel: float = 0.6, *,
                drager_window: tuple[float, float] = (28.0, 40.0)
                ) -> tuple[list, list]:
    """(omlijsting, elementen): regels op het beeld die de omgeving ook al zegt.

    Per regel: welk deel van zijn inhoudswoorden ook in de omgeving staat. Boven
    `drempel` is het een overlap. Een regel van één inhoudswoord telt niet mee -- "48%"
    naast een pagina die ergens "48" noemt is geen herhaling maar een label.

    De twee lijsten zijn niet gelijkwaardig. De eerste is de omlijsting en die blokkeert;
    de tweede zijn elementlabels, en die overlappen juist hóórt: de pagina beschrijft wat
    de figuur laat zien, dus dezelfde woorden komen op beide voor. Die lijst is er om te
    kijken, niet om op te ruimen.
    """
    omg = set(_woorden(omgeving))
    kader, elementen = [], []
    for naam, rol, regel in tekst_uit_svg(svg, drager_window):
        w = _woorden(regel)
        if len(w) < 2:
            continue
        deel = sum(1 for x in w if x in omg) / len(w)
        if deel >= drempel:
            (kader if rol in OMLIJSTING else elementen).append((naam, rol, regel, deel))
    return (sorted(kader, key=lambda r: -r[3]),
            sorted(elementen, key=lambda r: -r[3]))


def meet(svg: str, kader_px: float, eenheid: str) -> dict:
    """Wat er met de maten gebeurt als dit beeld in een kader van `kader_px` px staat.

    `eenheid` is de eenheid waarin het beeld getekend hoort te zijn voor déze bestemming.
    Bij een px-bestemming is één tekeneenheid één px, dus een beeld dat op het juiste
    canvas is gebouwd heeft factor 1,0 en houdt zijn opgegeven maten. Dat is geen
    boekhouding: het meetapparaat van de containers leest de OPGEGEVEN maat en niet de
    gerenderde, dus alleen bij factor 1,0 meet het hetzelfde als jij.
    """
    w, h = viewbox(svg)
    naar_pt = IN_PUNTEN[eenheid]
    breed_px = w if eenheid == "px" else w * PX_PER_PT
    factor = kader_px / breed_px
    maten = maten_in(svg)
    return {
        "canvas": [w, h],
        "eenheid": eenheid,
        "kader_px": round(kader_px, 1),
        "hoogte_px": round(h / breed_px * kader_px, 1),
        "factor": round(factor, 3),
        "maten": maten,
        "maten_na_pt": [round(m * naar_pt * factor, 2) for m in maten],
        "kleinste_na_pt": round(min(maten) * naar_pt * factor, 2) if maten else None,
    }


#: `svg.py` schrijft `font-family="Lato Light, Lato, sans-serif"`: de snede vooraan en de
#: familie als terugval. Dat is goed voor een los beeld, maar in een document telt
#: `qa_document.py` de EERSTE naam als de letterfamilie, en dan staan er drie families op
#: de pagina -- Lato, Lato Light en Montserrat -- terwijl de regel er twee toestaat.
#: Nagemeten op een gebouwde documentpagina: `critical letterfamilies: 3`.
#:
#: De reparatie is de snede uit de familienaam halen, want het gewicht staat er al naast:
#: `fonts.css` declareert `'Lato'` op 300 en `'Montserrat'` als variabel over 300-800, dus
#: `font-family="Lato" font-weight="300"` zet exact dezelfde letter als `"Lato Light"`.
FAMILIE = re.compile(r'font-family="([A-Za-z]+)(?: [A-Za-z]+)?, \1, sans-serif"')


def normaliseer_families(svg: str) -> tuple[str, int]:
    """Snedenamen uit `font-family` halen; het gewicht draagt de snede al."""
    return FAMILIE.subn(r'font-family="\1, sans-serif"', svg)


def fragment_document(svg: str, kader_px: float, *, bijschrift: str = "") -> str:
    """Het `.beeldkader` met de SVG erin, klaar om in een `.dc.html` te zetten.

    De omhulling is die van `assets/documenten/voorbeeld/Geldstroom.dc.html` en niet iets
    eigens: een `<figure style="margin: 0">` om een `<div class="beeldkader">`, met het
    bijschrift als `<figcaption class="bron">` eronder. Dat is geen smaak. `stijl.css`
    §8.13b stuurt de SVG met de kindselector `.beeldkader > svg`, dus een `<figure>` mét
    die klasse in plaats van een `<div>` erbinnen zou de regel die breedte en hoogte op
    100 procent zet niet raken -- dan blijft de inline `width="510pt"` staan en schaalt
    het beeld niet met de kolom mee.
    """
    w, h = viewbox(svg)
    binnen = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", svg.strip())
    binnen = "\n".join("    " + r for r in binnen.splitlines())
    onder = (f'\n  <figcaption class="bron" style="margin-top: 10px;">{bijschrift}'
             f'</figcaption>' if bijschrift else "")
    return (f'<figure style="margin: 0;">\n'
            f'  <div class="beeldkader" style="aspect-ratio: {w:g} / {h:g};">\n'
            f'{binnen}\n'
            f'  </div>{onder}\n'
            f'</figure>\n')


def png(pad: Path, *, schaal: float = 2.0, wit: bool = True) -> Path:
    """Render de SVG naar PNG met `render_svg.py`, en geef het pad terug."""
    cmd = [sys.executable, str(HIER / "render_svg.py"), str(pad),
           "--schaal", str(schaal)]
    if wit:
        cmd.append("--wit")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"renderen mislukte:\n{r.stdout}\n{r.stderr}")
    uit = pad.with_suffix(".png")
    if not uit.is_file():
        raise SystemExit(f"{uit} is niet geschreven; zie:\n{r.stdout}")
    return uit


def main() -> int:
    a = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("svg")
    a.add_argument("--doel", required=True, choices=sorted(KADERS))
    a.add_argument("--kader", default=None,
                   help="welk vlak van die bestemming; standaard het breedste")
    a.add_argument("--bijschrift", default="",
                   help="het bijschrift. In het rapport komt dit in de figuren-JSON")
    a.add_argument("--na", default=None,
                   help="rapport: de blok-id waar het beeld achter komt (figuren-JSON)")
    a.add_argument("--pagina", default=None,
                   help="de pagina waar dit beeld in komt (.dc.html of HTML). Wordt "
                        "gelezen om te zien wat de container al zegt")
    a.add_argument("--uit", default=None, help="schrijf het fragment naar dit bestand")
    a.add_argument("--toch", action="store_true",
                   help="lever het fragment ook als de maten door de vloer zakken")
    args = a.parse_args()

    pad = Path(args.svg)
    if not pad.is_file():
        raise SystemExit(f"niet gevonden: {pad}")
    svg = pad.read_text(encoding="utf-8")

    kaders = KADERS[args.doel]
    naam = args.kader or max(kaders, key=lambda k: kaders[k][0])
    if naam not in kaders:
        raise SystemExit(f"onbekend kader {naam!r} voor {args.doel}; "
                         f"kies uit {', '.join(sorted(kaders))}")
    kader_px, canvas = kaders[naam]

    eh = eenheid_van(svg)                       # waarin is het getekend
    wil = EENHEID_DOEL[args.doel]               # waarin hoort het voor deze bestemming
    m = meet(svg, kader_px, eh)
    vloer = VLOER[args.doel]
    past = m["kleinste_na_pt"] is None or m["kleinste_na_pt"] >= vloer

    print(f"{pad.name} -> {args.doel}/{naam}", file=sys.stderr)
    print(f"  getekend op {m['canvas'][0]:g} x {m['canvas'][1]:g} {eh}, "
          f"komt in {m['kader_px']:g} x {m['hoogte_px']:g} px", file=sys.stderr)
    print(f"  factor {m['factor']}  maten {m['maten']} {eh} "
          f"-> {m['maten_na_pt']} pt gerenderd", file=sys.stderr)
    print(f"  vloer {vloer:g} pt: {'past' if past else 'ZAKT ERDOOR'}", file=sys.stderr)

    if eh != wil and args.doel != "slide":
        print(f"  en het staat in {eh} terwijl {args.doel} in {wil} rekent. Dat is meer "
              f"dan een omrekening: het meetapparaat van deze container leest de "
              f"OPGEGEVEN maat en niet de gerenderde, dus het meet straks andere getallen "
              f"dan hierboven staan. Bouw op CANVAS[\"{canvas}\"].", file=sys.stderr)
    elif eh != wil:
        # Een slide krijgt een PNG, dus daar is geen meetapparaat dat de opgegeven maat
        # leest -- alleen een schaalverschil, en dat staat hierboven al als factor.
        print(f"  het staat in {eh} en een slide rekent in {wil}; op een PNG is dat alleen "
              f"de factor hierboven. Wil je scherpte op ware grootte, bouw dan op "
              f"CANVAS[\"{canvas}\"].", file=sys.stderr)

    # --- het dode wit onderin. De regel komt uit `svg.py`, zodat de waarschuwing tijdens
    # het bouwen en de poort hier niet uit elkaar kunnen lopen. Zie `hoogte_gebruikt`.
    sys.path.insert(0, str(HIER))
    from svg import BINNENMARGE, wit_onder
    gebruikt = hoogte_gebruikt(svg)
    hoog = m["canvas"][1]
    leeg, over, wit_ok = wit_onder(hoog, gebruikt, eh) if gebruikt else (0.0, 0.0, True)
    if gebruikt:
        print(f"  hoogte: compositie tot {gebruikt:g} van {hoog:g} {eh}"
              f" -- {leeg:g} {eh} leeg ({leeg / hoog:.0%})"
              f"{'' if wit_ok else '  DOOD WIT'}", file=sys.stderr)

    # --- wat de container al zegt. Zie het blok bij `dubbelingen`.
    omgeving = args.bijschrift
    if args.pagina:
        pg = Path(args.pagina)
        if not pg.is_file():
            raise SystemExit(f"niet gevonden: {pg}")
        omgeving += " " + tekst_uit_pagina(pg.read_text(encoding="utf-8"))
    window = (_in(28.0, eh), _in(40.0, eh))
    dubbel, ook = (dubbelingen(svg, omgeving, drager_window=window)
                   if omgeving.strip() else ([], []))
    if dubbel:
        print(f"  DUBBEL met de omgeving, {len(dubbel)} keer in de omlijsting:",
              file=sys.stderr)
        for el, rol, regel, deel in dubbel:
            print(f"    {el} ({rol}): {regel[:64]!r} -- {deel:.0%} staat er al",
                  file=sys.stderr)
    elif omgeving.strip():
        print("  dubbeling in de omlijsting: geen", file=sys.stderr)
    elif args.doel != "slide":
        print("  dubbeling: niet gecontroleerd -- geef --pagina of --bijschrift mee, "
              "anders weet dit script niet wat de container al zegt", file=sys.stderr)
    if ook:
        print(f"  ({len(ook)} elementlabel(s) komen ook in de omgeving voor; dat hoort zo "
              f"-- de pagina beschrijft wat de figuur laat zien. Niet weghalen: direct "
              f"labelen gaat voor)", file=sys.stderr)

    fout = []
    if not past:
        fout.append(
            f"De kleinste tekst komt op {m['kleinste_na_pt']} pt uit en de vloer van deze "
            f"bestemming is {vloer:g} pt. Dat repareer je niet met het kader maar met het "
            f"canvas: teken dit beeld opnieuw op CANVAS[\"{canvas}\"] met "
            f"Maten.voor(\"{args.doel if args.doel != 'slide' else 'los'}\").")
    if not wit_ok and args.doel != "slide":
        fout.append(
            f"Er blijft {leeg:g} {eh} ({leeg / hoog:.0%}) leeg onder de compositie, "
            f"{over:g} {eh} meer dan de ene ondermarge die erbij hoort. Op een los beeld "
            f"zie je dat op de render; in een kader zie je het niet, want de verhouding van "
            f"het kader komt uit de viewBox -- dus die leegte wordt gereserveerde witruimte "
            f"op de pagina en duwt de tekst eronder weg. Zet de hoogte op de inhoud met "
            f"`pas_hoogte(c, vormen)` en bouw opnieuw; dat geeft hier ongeveer "
            f"{gebruikt + BINNENMARGE.get(eh, 12.0):.0f} {eh} in plaats van {hoog:g}.")
    if dubbel:
        welke = ", ".join(f"{el} ({rol})" for el, rol, _, _ in dubbel)
        fout.append(
            f"De omlijsting van dit beeld zegt wat de omgeving ook al zegt: {welke}. In "
            f"een LOS beeld horen een aanhef, een drager en een bronregel er juist op -- "
            f"daar is geen container die ze draagt. In een exhibit is er wel een, en twee "
            f"stemmen over hetzelfde is er een te veel. Haal ze van het beeld (de pagina "
            f"houdt ze) of laat de container ze weg, maar kies. De elementlabels blijven "
            f"hoe dan ook staan: direct labelen gaat voor.")

    if fout and not args.toch:
        print("\n" + "\n\n".join(fout) +
              "\n\nZie reference/samenstellen.md. Is een van deze een bewuste keuze, "
              "dan is --toch de weg; noem hem dan bij de oplevering.", file=sys.stderr)
        return 1

    if m["factor"] != 1.0 and eh == wil == "px":
        print(f"  let op: factor {m['factor']} en niet 1,0, dus dit beeld is op een ander "
              f"kader gebouwd dan waar het in komt. Zelfde bezwaar als hierboven: de "
              f"container meet de opgegeven maat. Bouw op CANVAS[\"{canvas}\"].",
              file=sys.stderr)

    if args.doel == "document":
        svg, n = normaliseer_families(svg)
        if n:
            print(f"  {n} font-family-waarden genormaliseerd: de snede uit de naam, want "
                  f"qa_document.py telt de eerste naam als familie en de pagina mag er "
                  f"twee hebben", file=sys.stderr)
        uit = fragment_document(svg, kader_px, bijschrift=args.bijschrift)
    elif args.doel == "rapport":
        beeld = png(pad)
        regel = {"bestand": str(beeld), **({"na": args.na} if args.na else {}),
                 **({"bijschrift": args.bijschrift} if args.bijschrift else {})}
        uit = json.dumps([regel], ensure_ascii=False, indent=2) + "\n"
        if not args.na:
            print("  let op: geen --na, dus vul de blok-id zelf in. `lees_docx.py` geeft "
                  "ze; zonder id weet de zetmotor niet waar het beeld hoort.",
                  file=sys.stderr)
        print(f"  PNG op 2x: {beeld}", file=sys.stderr)
    else:
        beeld = png(pad)
        breedte_in = kader_px / 96.0
        uit = (f"# plak {beeld} op de slide, {breedte_in:.2f} in breed\n"
               f"# de titel draagt de bewering: idx 0 van layout 19, ALL CAPS\n")
        print(f"  PNG op 2x: {beeld}", file=sys.stderr)

    if args.uit:
        p = Path(args.uit)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(uit, encoding="utf-8")
        print(f"  geschreven: {p}", file=sys.stderr)
    else:
        print(uit, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
