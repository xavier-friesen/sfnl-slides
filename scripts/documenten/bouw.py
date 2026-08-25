#!/usr/bin/env python3
"""Van artboards naar een document: één bron, twee uitvoeren.

De `.dc.html`-artboards zijn de bron. Dit script leidt daar twee dingen uit af
en houdt ze in de pas:

1. **Het losse HTML-bestand** — alle pagina's onder elkaar in één bewerkbaar
   bestand met `@page` erin, dat in een browser opent en via
   `sfnl-html-to-pdf` een PDF wordt. Dat is wat de gebruiker overhoudt.
2. **`canvas.json`** — de plaatsing van de artboards op het design-canvas, als
   spreads: pagina 1 alleen rechts, daarna 2-3, 4-5. Dat is hoe een lezer een
   document ziet, en het is de enige manier om twee tegenover elkaar liggende
   pagina's samen te beoordelen.

Daarnaast **stempelt** het script `stijl.css` in de `<helmet>` van elk artboard.
Artboards delen op het canvas niets met elkaar — geen stijl, geen state — dus
elk bestand draagt zijn eigen kopie. Dat stempelen is idempotent: het vervangt
wat tussen de twee markers staat en laat de rest met rust. Zo blijft `stijl.css`
de enige plek waar de huisstijl staat, ook nadat iemand in het canvas heeft
zitten schuiven.

Waarom het artboard de bron is en niet een los fragment: het canvas schrijft
terug. Bewerkt iemand een pagina in de browser en slaat hij op, dan haal je die
met `seed-canvas.mjs --extract` weer als `.dc.html` op. Was de bron een fragment
geweest, dan had je vanaf dat moment twee waarheden.

Elke pagina beschrijft zichzelf in data-attributen op zijn `.pagina`-element:

    <div class="pagina" data-formaat="sfnl" data-veld="wit"
         data-volgnr="3" data-kopregel="Inleiding" data-folio="3">

`data-volgnr` bepaalt de volgorde, `data-formaat` de bladmaat, `data-folio`
het paginanummer (of `nee`), `data-kopregel` de hoofdstuknaam rechtsboven.
Ontbreekt `data-volgnr`, dan telt de bestandsnaam.

Gaat het document naar een drukker, dan moet het aantal pagina's op de pers
bestaan. Met `--gedrukt` rekent het script dat uit met
`scripts/gedeeld/drukwerk.py` en zet het onder `katern` in zijn verslag. Het
rekent en het meldt, meer niet: er komt geen pagina bij en er gaat er geen af.
Er zijn drie uitwegen uit een aantal dat niet uitkomt — pagina's erbij, pagina's
eraf, of het bij een PDF houden — en welke de goede is hangt af van wat het
document is. Dat is een besluit van de gebruiker; stilzwijgend afronden is het
defect. Deze route kent geen `ontwerp.json`, dus het besluit staat bovenaan
`outline.md` en de vlag draagt het hierheen.

Gebruik:

    python bouw.py <werkmap>                       # stempelen + bouwen
    python bouw.py <werkmap> --gedrukt             # met de katernsom erbij
    python bouw.py <werkmap> --uit uitnodiging.html
    python bouw.py <werkmap> --nieuw Programma --volgnr 2 --formaat sfnl
    python bouw.py <werkmap> --alleen-stempel
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
WORTEL = HIER.parent.parent
STIJL_STANDAARD = WORTEL / "assets" / "documenten" / "stijl.css"
FONTS_STANDAARD = WORTEL / "assets" / "documenten" / "fonts" / "fonts.css"

# De katernsom en de PDF-stap zijn van twee routes tegelijk en staan
# daarom in `scripts/gedeeld`.
sys.path.insert(0, str(WORTEL / "scripts" / "gedeeld"))
from drukwerk import katern  # noqa: E402
from canvas import manifest as leg_neer  # noqa: E402

#: De terugval als de ingesloten letters ontbreken. Hij werkt, maar hij werkt
#: alleen mét internet, en de PNG- en PDF-export van het canvas neemt een
#: Google Font niet mee — dan valt de export terug op de systeemletter.
#: `haal_fonts.py` maakt de ingesloten versie.
GOOGLE_LINK = ('  <link rel="stylesheet" href="https://fonts.googleapis.com/css2'
               '?family=Montserrat:wght@300;400;700;800'
               '&amp;family=Lato:ital,wght@0,300;0,400;0,700;1,300;1,400'
               '&amp;display=swap">')

MARKER_START = "/* == SFNL-STIJL — gestempeld door bouw.py, niet met de hand bijwerken == */"
MARKER_EIND = "/* == einde SFNL-STIJL == */"

#: Bladmaten in px bij 96 dpi. Dit is de enige plek waar ze staan; `stijl.css`
#: heeft dezelfde tabel voor de CSS-kant en de twee horen gelijk te blijven.
FORMATEN = {
    "sfnl": (794, 1039),          # 210 x 275 mm — het SFNL-rapportformaat
    "sfnl-spread": (1587, 1039),  # 420 x 275 mm — de dubbelpagina
    "a4": (794, 1123),
    "a4-liggend": (1123, 794),
    "a5": (559, 794),
    "dl": (374, 794),             # 99 x 210 mm — één paneel van een drieluik
}

#: Ruimte tussen de artboards op het canvas. De naamstrip en de tweakchips
#: staan bóven elk frame, dus tussen twee rijen moet meer lucht dan tussen twee
#: frames naast elkaar. De design-skill noemt 80 en 120 als ondergrens.
KIER_SPREAD = 24     # tussen twee pagina's van dezelfde spread: de rug
KIER_RIJ = 150       # tussen twee spreads onder elkaar

SJABLOON = """<!doctype html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
{link}  <style>
{stijl}
  </style>
</helmet>
{inhoud}
</x-dc>
</body>
</html>
"""

SKELET = """<div class="pagina" data-formaat="{formaat}" data-veld="wit" data-volgnr="{volgnr}"{extra}>

  <!-- Aflopend werk staat hier, buiten de zetspiegel: .aflopend,
       .aflopend-boven, .aflopend-links. Het raakt de snijrand. -->

  <div class="zetspiegel">
    <!-- Componeer hier. De marge zit op .zetspiegel, dus alles binnen dit
         blok staat vanzelf goed. -->
  </div>

</div>
"""


# ---------------------------------------------------------------------------
# Lezen
# ---------------------------------------------------------------------------

def _inspringen(tekst: str) -> str:
    return "\n".join("    " + r if r.strip() else r for r in tekst.splitlines())


def lees_stijl(stijl: Path, fonts: Path) -> tuple[str, str, str]:
    """(ruwe CSS, ingesprongen CSS, de <link>-regel of leeg).

    Staan de letters ingesloten, dan gaan ze vóór `stijl.css` en vervalt de
    Google-link: twee bronnen voor dezelfde familienaam is vragen om de ene
    machine die de andere snede pakt.
    """
    if not stijl.exists():
        sys.exit(f"stijl niet gevonden: {stijl}")
    css = stijl.read_text(encoding="utf-8")
    if fonts.exists():
        css = fonts.read_text(encoding="utf-8") + "\n" + css
        link = ""
    else:
        link = GOOGLE_LINK + "\n"
        print("let op: assets/documenten/fonts/fonts.css ontbreekt, dus de letters "
              "komen van Google Fonts. Dat werkt alleen met internet en de PNG- "
              "en PDF-export van het canvas neemt ze niet mee. Draai "
              "`python scripts/documenten/haal_fonts.py`.", file=sys.stderr)
    return css, _inspringen(css), link


def _inhoud_van(bron: str) -> str:
    """De pagina zelf: alles binnen <x-dc> ná </helmet>.

    Is er geen <x-dc>, dan is het bestand een kaal fragment — alleen het
    `<div class="pagina">`-blok — en dan is het bestand de inhoud. Dat is de
    manier waarop je een pagina schrijft: de omhulling en de stijl zijn
    boilerplate en die stempelt dit script erin. Een artboard dat terugkomt uit
    het canvas draagt de omhulling wél, en dan geldt de eerste tak.
    """
    m = re.search(r"<x-dc>(.*)</x-dc>", bron, re.S | re.I)
    if not m:
        return bron.strip("\n")
    binnen = m.group(1)
    h = re.search(r"</helmet\s*>", binnen, re.I)
    if h:
        binnen = binnen[h.end():]
    return binnen.strip("\n")


def _attributen(inhoud: str) -> dict:
    """De data-attributen van het eerste .pagina-element."""
    m = re.search(r"<div[^>]*class=\"[^\"]*\bpagina\b[^\"]*\"[^>]*>", inhoud, re.I)
    if not m:
        return {}
    tag = m.group(0)
    return {k: html.unescape(v)
            for k, v in re.findall(r'data-([a-z0-9-]+)\s*=\s*"([^"]*)"', tag, re.I)}


class Pagina:
    def __init__(self, pad: Path, stijl_lengte: int):
        self.pad = pad
        self.naam = pad.name[:-len(".dc.html")] if pad.name.endswith(".dc.html") else pad.stem
        self.bron = pad.read_text(encoding="utf-8")
        self.inhoud = _inhoud_van(self.bron)
        self.attr = _attributen(self.inhoud)
        self.formaat = self.attr.get("formaat", "sfnl")
        if self.formaat not in FORMATEN:
            sys.exit(f"{pad.name}: onbekend formaat {self.formaat!r}. "
                     f"Kies uit: {', '.join(FORMATEN)}")
        self.breedte, self.hoogte = FORMATEN[self.formaat]
        volg = self.attr.get("volgnr")
        self.volgnr = int(volg) if volg and volg.isdigit() else None

    def __repr__(self) -> str:
        return f"<Pagina {self.naam} #{self.volgnr} {self.formaat}>"


def verzamel(werkmap: Path, stijl_lengte: int = 0) -> list[Pagina]:
    paden = sorted(werkmap.glob("*.dc.html"))
    if not paden:
        sys.exit(f"geen artboards (*.dc.html) in {werkmap}")
    paginas = [Pagina(p, stijl_lengte) for p in paden]
    zonder = [p.naam for p in paginas if p.volgnr is None]
    if zonder:
        # Bestandsnaam telt: alfabetisch achter de genummerde pagina's aan.
        hoogste = max([p.volgnr for p in paginas if p.volgnr is not None] or [0])
        for i, p in enumerate(sorted((p for p in paginas if p.volgnr is None),
                                     key=lambda p: p.naam)):
            p.volgnr = hoogste + 1 + i
        print(f"let op: geen data-volgnr op {', '.join(zonder)} — "
              f"op bestandsnaam achteraan gezet", file=sys.stderr)
    paginas.sort(key=lambda p: p.volgnr)
    dubbel = [p.volgnr for p in paginas if [q.volgnr for q in paginas].count(p.volgnr) > 1]
    if dubbel:
        print(f"let op: data-volgnr {sorted(set(dubbel))} staat meer dan één keer",
              file=sys.stderr)
    return paginas


# ---------------------------------------------------------------------------
# Stempelen
# ---------------------------------------------------------------------------

def stempel(paginas: list[Pagina], stijl: str, link: str = "") -> int:
    """Zet stijl.css in de <helmet> van elk artboard. Idempotent."""
    blok = f"{MARKER_START}\n{stijl}\n    {MARKER_EIND}"
    veranderd = 0
    for p in paginas:
        bron = p.bron
        if MARKER_START in bron and MARKER_EIND in bron:
            nieuw = re.sub(re.escape(MARKER_START) + r".*?" + re.escape(MARKER_EIND),
                           lambda _: blok, bron, flags=re.S)
        else:
            nieuw = SJABLOON.format(stijl=blok, inhoud=p.inhoud, link=link)
        if nieuw != bron:
            p.pad.write_text(nieuw, encoding="utf-8")
            p.bron = nieuw
            veranderd += 1
    return veranderd


# ---------------------------------------------------------------------------
# canvas.json — de spreadindeling
# ---------------------------------------------------------------------------

def canvas(paginas: list[Pagina]) -> dict:
    """Leg de pagina's neer zoals een lezer ze ziet: 1 alleen, dan 2-3, 4-5.

    Een spread is de eenheid waarop editorial ontwerp beoordeeld wordt: de
    lezer ziet twee pagina's tegelijk, dus de linker en de rechter moeten
    samen kloppen. Wie de pagina's in een rij van vier neerlegt, kan dat niet
    zien.
    """
    # De spreadindeling zelf staat in `scripts/gedeeld/canvas.py`: de
    # rapportroute legt zijn afgeleide artboards op precies dezelfde
    # manier neer, en twee kopieën van deze rekensom gaan een keer
    # uiteenlopen.
    manifest = leg_neer([{"bestand": f"{p.naam}.dc.html",
                          "breedte": p.breedte, "hoogte": p.hoogte,
                          "titel": _titel_van(p)} for p in paginas],
                        kier_spread=KIER_SPREAD, kier_rij=KIER_RIJ)
    artboards = manifest["artboards"]
    if next((a for a in artboards if a["file"] == "Main.dc.html"), None) is None:
        print("let op: geen Main.dc.html — het canvas kiest dan het eerste "
              "artboard op naam. Noem de eerste pagina Main.", file=sys.stderr)
    return manifest


def _titel_van(p: Pagina) -> str:
    kop = p.attr.get("kopregel") or p.attr.get("titel") or p.naam
    folio = p.attr.get("folio")
    if folio and folio.lower() not in ("nee", "geen", "false"):
        return f"{folio} · {kop}"
    return kop


# ---------------------------------------------------------------------------
# Het losse HTML-bestand
# ---------------------------------------------------------------------------

DOC = """<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titel}</title>
{link}<style>
{stijl}

/* -- Drukwerk. De pagina draagt zijn eigen marge, dus @page staat op nul. -- */
{pagina_regels}
</style>
</head>
<body>
<div class="vel">
{paginas}
</div>
</body>
</html>
"""


def _mm(px: float) -> str:
    return f"{px / 96 * 25.4:.3g}mm"


def document(paginas: list[Pagina], stijl_ruw: str, titel: str, link: str = "") -> str:
    maten = []
    gezien = set()
    for p in paginas:
        if p.formaat in gezien:
            continue
        gezien.add(p.formaat)
        maten.append(
            f"@page {p.formaat.replace('-', '_')} "
            f"{{ size: {_mm(p.breedte)} {_mm(p.hoogte)}; margin: 0; }}"
        )
    # Chromium leest maar één @page-blok zonder naam; een document met twee
    # formaten drukt daarom op de maat van de eerste pagina. Dat staat hier
    # expliciet omdat het anders stil misgaat.
    eerste = paginas[0]
    regels = [f"@page {{ size: {_mm(eerste.breedte)} {_mm(eerste.hoogte)}; margin: 0; }}"]
    if len(gezien) > 1:
        regels.append(
            "/* Dit document heeft meer dan één bladmaat. Chromium drukt alles\n"
            f"   op {_mm(eerste.breedte)} x {_mm(eerste.hoogte)}. Wil je beide\n"
            "   maten echt, exporteer dan per maat een apart bestand. */")
    body = "\n".join(p.inhoud for p in paginas)
    return DOC.format(titel=html.escape(titel), stijl=stijl_ruw, link=link,
                      pagina_regels="\n".join(regels), paginas=body)


# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("werkmap", type=Path)
    ap.add_argument("--stijl", type=Path, default=STIJL_STANDAARD)
    ap.add_argument("--fonts", type=Path, default=FONTS_STANDAARD,
                    help="ingesloten @font-face-CSS; ontbreekt hij, dan valt het "
                         "bestand terug op Google Fonts")
    ap.add_argument("--uit", default=None,
                    help="naam van het losse HTML-bestand (default: document.html)")
    ap.add_argument("--titel", default=None)
    ap.add_argument("--gedrukt", action="store_true",
                    help="dit document gaat naar een drukker, dus reken de "
                         "katernsom mee en zet hem in het verslag. Default uit: "
                         "een PDF op een scherm is aan geen katern gebonden")
    ap.add_argument("--alleen-stempel", action="store_true")
    ap.add_argument("--nieuw", default=None, metavar="NAAM",
                    help="schrijf een leeg artboard met die naam en stop")
    ap.add_argument("--volgnr", type=int, default=None)
    ap.add_argument("--formaat", default="sfnl", choices=sorted(FORMATEN))
    ap.add_argument("--kopregel", default=None)
    ap.add_argument("--folio", default=None)
    a = ap.parse_args()

    a.werkmap.mkdir(parents=True, exist_ok=True)
    stijl_ruw, stijl_ingesprongen, link = lees_stijl(a.stijl, a.fonts)

    if a.nieuw:
        naam = a.nieuw[:-len(".dc.html")] if a.nieuw.endswith(".dc.html") else a.nieuw
        doel = a.werkmap / f"{naam}.dc.html"
        if doel.exists():
            sys.exit(f"bestaat al: {doel}")
        volgnr = a.volgnr if a.volgnr is not None else len(list(a.werkmap.glob("*.dc.html"))) + 1
        extra = ""
        if a.kopregel:
            extra += f' data-kopregel="{html.escape(a.kopregel)}"'
        if a.folio:
            extra += f' data-folio="{html.escape(a.folio)}"'
        blok = f"{MARKER_START}\n{stijl_ingesprongen}\n    {MARKER_EIND}"
        doel.write_text(SJABLOON.format(
            stijl=blok, link=link,
            inhoud=SKELET.format(formaat=a.formaat, volgnr=volgnr, extra=extra),
        ), encoding="utf-8")
        print(json.dumps({"geschreven": str(doel), "volgnr": volgnr,
                          "formaat": a.formaat, "maat": FORMATEN[a.formaat]}))
        return 0

    paginas = verzamel(a.werkmap)
    n = stempel(paginas, stijl_ingesprongen, link)

    if a.alleen_stempel:
        print(json.dumps({"gestempeld": n, "paginas": len(paginas)}))
        return 0

    manifest = canvas(paginas)
    (a.werkmap / "canvas.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    titel = a.titel or a.werkmap.resolve().name.replace("-", " ").title()
    uit = a.werkmap / (a.uit or "document.html")
    uit.write_text(document(paginas, stijl_ruw, titel, link), encoding="utf-8")

    # En de PDF, altijd. De artboards zijn hier de bron en die staan er dus
    # al; wat er tot nu toe ontbrak was het bestand dat je aan een
    # opdrachtgever geeft. Het recept stond als proza in de skill — marges
    # op nul, `prefer_css_page_size` — en proza wordt overgeslagen. Nu is
    # het een stap, en hij staat in `scripts/gedeeld` omdat de rapportroute
    # hem net zo hard nodig heeft.
    from naar_pdf import naar_pdf  # noqa: E402
    pdf = naar_pdf(uit)

    som = katern(len(paginas), gedrukt=a.gedrukt)
    if not som["klopt"]:
        # Melden, niet repareren. Wie hier pagina's zou bijmaken, zou een pagina
        # bouwen waar geen materiaal voor is.
        print(f"let op: {som['uitleg']} — leg de keuze voor in plaats van "
              f"stilzwijgend af te ronden", file=sys.stderr)

    print(json.dumps({
        "paginas": [{"nr": p.volgnr, "artboard": f"{p.naam}.dc.html",
                     "formaat": p.formaat, "maat": [p.breedte, p.hoogte]}
                    for p in paginas],
        "katern": som,
        "pdf": str(pdf),
        "gestempeld": n,
        "canvas": str(a.werkmap / "canvas.json"),
        "document": str(uit),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
