#!/usr/bin/env python3
"""Een afgemaakte infographic in een van de zusterroutes zetten, en narekenen of hij past.

    python insluiten.py beeld.svg --doel document --kader breed
    python insluiten.py beeld.svg --doel rapport --kader kolom --bijschrift "..." --na b0042
    python insluiten.py beeld.svg --doel slide

Waarom dit een script is en geen alinea in de SKILL
---------------------------------------------------
Alle vier de skills in deze plugin kunnen een infographic gebruiken, en alle drie de
containers zeggen dat ook: `documenten-vormentaal.md` §11, `rapport-vormentaal.md` onder
"Geen infographics ontwerpen", en `vormentaal.md` bij de bovengrens van twaalf onderdelen.
Wat er niet stond is hoe. En het "hoe" is precies waar het stil misgaat, want **een SVG
schaalt álles mee, ook zijn letters**. Een beeld dat op 960 pt is getekend en in een kader
van 680 px staat, krimpt met factor 1,88: een label van 11 pt komt er op 5,9 pt uit, onder
de leesvloer, zonder dat er iets in de markup fout staat. Dat is de meting die
`documenten-vormentaal.md` §11 punt 1 al beschrijft en die niemand uitrekende.

Dit script rekent hem uit. Het leest de `viewBox` en alle `font-size`-waarden uit de SVG,
vergelijkt de kleinste met de vloer van de bestemming, en zegt of het beeld erin mag. Zegt
het nee, dan is het antwoord niet "toch plaatsen" maar **opnieuw tekenen op het canvas van
de bestemming**: `CANVAS["doc-breed"]` en zijn vijf broers staan er precies daarvoor, met
`Maten.voor("document")` voor de maatladder.

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

    if eh != wil:
        print(f"  en het staat in {eh} terwijl {args.doel} in {wil} rekent. Dat is meer "
              f"dan een omrekening: het meetapparaat van deze container leest de "
              f"OPGEGEVEN maat en niet de gerenderde, dus het meet straks andere getallen "
              f"dan hierboven staan. Bouw op CANVAS[\"{canvas}\"].", file=sys.stderr)

    if not past and not args.toch:
        print(f"\nDe kleinste tekst komt op {m['kleinste_na_pt']} pt uit en de vloer van "
              f"deze bestemming is {vloer:g} pt. Dat repareer je niet met het kader maar "
              f"met het canvas: teken dit beeld opnieuw op CANVAS[\"{canvas}\"] met "
              f"Maten.voor(\"{args.doel if args.doel != 'slide' else 'los'}\"). Zie "
              f"reference/samenstellen.md. Wil je het fragment toch: --toch.",
              file=sys.stderr)
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
