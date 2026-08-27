#!/usr/bin/env python3
"""De merkwaarden, één keer. §1 en §2 van `reference/merk.md`, machineleesbaar.

Van alle routes. Er waren acht plekken waar een kleurwaarde stond — twee
stylesheets, twee opdrachtwidgets, de SVG-primitieven, de schetslaag, de
keuzekaart van het rapport en de documentenpoort — en dat is zeven plekken te
veel. Niet omdat het onnetjes staat, maar omdat het één keer echt is misgegaan:
het Word-sjabloon `SFNL_Word_sjabloon.dotx` is de merkbron, en de plugin
rendeerde vijf ándere waarden dan het sjabloon. Oranje stond op `#F87F4F` en is
`#FF7F40`, navy op `#201B5C` en is `#21145F` — dat laatste staat 26 keer in de
`styles.xml` van het sjabloon, dus het is geen uitschieter in één stijl. Wie dat
wil rechtzetten moet acht bestanden aanraken en vergeet er één; en de kopie die
overblijft is de tweede huisstijl.

Wat er dan gebeurt, staat in `scripts/documenten/qa_document.py`. Die poort hield
zijn eigen kopie van het palet bij, als rgb-drieling, en meldde na de omzetting
"kleur buiten het palet" over het merkoranje zelf — op elk document. Een toets die
zijn eigen kopie van de waarheid bijhoudt, toetst op een gegeven moment die kopie.

**Wat hier staat en wat hier niet staat.** Hier staan de waarden die in elk
medium hetzelfde zijn: de kleuren, het huisverloop, de letterfamilies. Hier
staat geen puntgrootte, geen marge, geen kleurregister en geen vulgraad. Een
rapport en een PowerPoint horen verschillende maatladders te hebben — ze zijn
aan verschillend drukwerk gemeten — en verschillende regels over wanneer een
vlak vol mag zijn. Hun oranje niet. Staat er een puntgrootte in dit bestand,
dan is dat een fout, en dan hoort hij in de vormentaal van dat ene medium.

**Waarom `contrast()` hier staat.** De vormentalen dragen metingen: "oranje op
wit haalt 2,51 en draagt daarom geen zin". Zo'n getal is alleen een argument
zolang het na te rekenen is, en na de paletmigratie schoof elk van die getallen
een honderdste of twee. Met deze functie zijn ze afleidbaar in plaats van
overgeschreven, en dan kan er geen conclusie op een verouderd getal blijven
staan.

**Waarom `merk.css` een bestand op schijf is.** Een stylesheet kan geen Python
importeren. `--css` schrijft daarom `assets/gedeeld/merk.css` en stempelt
hetzelfde blok tussen de merktekens in de stylesheets die het nodig hebben;
`scripts/preflight.py` hergenereert, vergelijkt en meldt elk verschil.

Waarom gestempeld en niet `@import url("../gedeeld/merk.css")`: dat is
geprobeerd en het werkt hier niet, om twee redenen die elkaar niet uitsluiten.
`bouw.py` van beide drukroutes plakt de stylesheets als tékst achter
`fonts.css` in één `<style>`-blok, en de CSS-parser laat een `@import` die niet
vooraan de stylesheet staat vallen — de kleuren zouden dan zonder melding
allemaal ongedefinieerd zijn. En een relatieve URL in een `<style>` wordt tegen
het documént opgelost en niet tegen de stylesheet, dus het pad klopt alleen
toevallig, per map waarin het document belandt. Een gestempeld blok faalt niet
stil: preflight ziet het verschil.

Gebruik:

    python merk.py --css                 merk.css schrijven en de stylesheets stempelen
    python merk.py --check               alleen melden wat uit de pas loopt
    python merk.py --contrast navy oranje
"""

from __future__ import annotations

from pathlib import Path

HIER = Path(__file__).resolve().parent
WORTEL = HIER.parent.parent
MERKCSS = WORTEL / "assets" / "gedeeld" / "merk.css"

#: Het merkteken waartussen `--css` stempelt. Alles ertussen is gegenereerd;
#: alles erbuiten is van de stylesheet zelf en blijft met rust.
BEGIN = "/* merk:begin — gegenereerd door scripts/gedeeld/merk.py --css */"
EINDE = "/* merk:einde */"

#: De stylesheets die het blok gestempeld krijgen. `rapport.css` staat er niet
#: bij en dat is geen omissie: die komt altijd ná `stijl.css` en erft de
#: waarden daaruit. Twee keer hetzelfde `:root` stempelen zou de vraag
#: openlaten welke van de twee de bron is.
GESTEMPELD = (WORTEL / "assets" / "documenten" / "stijl.css",
              WORTEL / "assets" / "online" / "stijl.css")


# --------------------------------------------------------------------- kleur
#
# §1 van merk.md, in drie groepen, en de groep zegt waar de waarde vandaan
# komt. Dat onderscheid is het hele punt van de migratie van 27 augustus 2026:
# wat in het themapalet van het sjabloon staat, komt uit het sjabloon; wat er
# niet in staat, blijft staan zoals het uit het drukwerk gemeten is. Een
# kleurkiezer in Word en PowerPoint bij SFNL neemt zijn waarden uit dat
# themapalet, dus een plugin die iets anders rendeert, rendeert naast het merk.

#: naam -> hex, rol, en waar de waarde vandaan komt.
KLEUREN: dict[str, dict[str, str]] = {
    # Uit het themapalet van assets/word/SFNL_Word_sjabloon.dotx.
    "navy":        {"hex": "#21145F", "bron": "accent3",
                    "rol": "de inkt. Lopende tekst is nooit puur zwart"},
    "oranje":      {"hex": "#FF7F40", "bron": "accent1",
                    "rol": "het accent. Labels, de streep, de badge"},
    "wit":         {"hex": "#FFFFFF", "bron": "accent6",
                    "rol": "het papier"},
    "grapefruit":  {"hex": "#FF595A", "bron": "accent2",
                    "rol": "het tweede eind van het verloop; alarm, nadruk"},
    "emerald":     {"hex": "#66C9BA", "bron": "accent4",
                    "rol": "positief, uitkomst"},
    "royal":       {"hex": "#425CC7", "bron": "accent5, hlink",
                    "rol": "secundaire data, en de hyperlink"},
    # Niet in het themapalet, dus gemeten uit het drukwerk.
    "sky":         {"hex": "#45B6E2", "bron": "gemeten",
                    "rol": "tertiaire data"},
    "violet":      {"hex": "#6B5DAE", "bron": "gemeten",
                    "rol": "de casespread; een heel paneel of een rail"},
    "grijs":       {"hex": "#F2F2F2", "bron": "gemeten",
                    "rol": "een kaartvulling"},
    # De tinten, gemeten uit de vlakken in het rapport en niet berekend. Wie
    # ze uitrekent uit de volle kleur komt er niet op uit; ze zijn gedrukt.
    "mint-tint":   {"hex": "#E0F4F1", "bron": "gemeten",
                    "rol": "een hele pagina of een paneel in emerald"},
    "periwinkel":  {"hex": "#A0ADE2", "bron": "gemeten",
                    "rol": "het interviewpaneel"},
    "oranje-tint": {"hex": "#FFDFD0", "bron": "gemeten",
                    "rol": "het watermerkcijfer"},
    "navy-tint":   {"hex": "#F4F3F7", "bron": "gemeten",
                    "rol": "een stille container"},
}

#: naam -> hex. Voor een script dat alleen de waarde nodig heeft.
HEX: dict[str, str] = {naam: k["hex"] for naam, k in KLEUREN.items()}

#: De twee rollen die een naam hebben omdat de vormentaal ze zo noemt. Ze staan
#: als variabele in merk.css en worden per pagina overschreven; hier staat
#: alleen waar ze op uitkomen als niemand iets overschrijft.
ROLLEN: dict[str, str] = {"papier": "wit", "inkt": "navy"}

#: Het huisverloop. Er is er één, van oranje naar grapefruit onder 150 graden,
#: en die is gemeten op de omslag en de kaartenrij van het rapport 2025 — het
#: gemeten beginpunt is precies de sjabloonwaarde van oranje. Een ander verloop
#: is een andere huisstijl.
VERLOOP_HOEK = 150
VERLOOP = f"linear-gradient({VERLOOP_HOEK}deg, var(--oranje) 0%, var(--grapefruit) 100%)"

#: De vijf waarden die op 27 augustus 2026 zijn vervangen, en waardoor. Alleen
#: om ze te kunnen herkennen: `scripts/preflight.py` grept ernaar, want een
#: oude waarde die ergens is blijven staan ziet er precies zo uit als een
#: goede. Zie de tabel in `reference/merk.md` §1 voor de verschuiving per rol.
VERVANGEN: dict[str, str] = {
    "#F87F4F": "oranje",
    "#F95D63": "grapefruit",
    "#201B5C": "navy",
    "#6AC6BA": "emerald",
    "#3B62C1": "royal",
}


# --------------------------------------------------------------------- letter
#
# §2 van merk.md. De familie is invariant, de maat is per medium — dus staan
# hier de families en staat er geen puntgrootte.

#: familie -> gewichten, licentie, waar de bestanden staan, en of hij mee mag.
LETTERS: dict[str, dict] = {
    "Gotham": {
        "gewichten": ["Bold"],
        "licentie": "commercieel, Hoefler&Co",
        "mag_mee": False,
        "pad": None,
        "waarom": "de merkletter. Staat op een SFNL-machine en nergens anders: "
                  "niet in een sandbox, niet in een browser, niet bij een klant",
    },
    "Montserrat": {
        "gewichten": ["300 Light", "600 SemiBold", "700 Bold", "800 ExtraBold"],
        "licentie": "SIL OFL 1.1",
        "mag_mee": True,
        "pad": "assets/documenten/fonts/",
        "waarom": "de terugval voor Gotham, en zelf de displayletter",
    },
    "Lato": {
        "gewichten": ["300 Light", "400", "700", "300 cursief", "400 cursief"],
        "licentie": "SIL OFL 1.1",
        "mag_mee": True,
        "pad": "assets/documenten/fonts/",
        "waarom": "de broodletter",
    },
}

#: Wat er in plaats van Gotham komt, en het is een expliciet besluit. Word en
#: LibreOffice substitueren anders stil, en dan verandert de regelval zonder
#: melding — dat is de fout die je pas op papier ziet.
TERUGVAL = "Montserrat SemiBold"

#: De twee stapels zoals ze in een stylesheet staan. De familie is invariant;
#: de terugval erachter is er voor de machine zonder de ingesloten snedes.
STAPELS: dict[str, str] = {
    "display": "'Montserrat', 'Helvetica Neue', Arial, sans-serif",
    "brood":   "'Lato', 'Helvetica Neue', Arial, sans-serif",
}


# --------------------------------------------------------------------- meting


def _kanaal(waarde: float) -> float:
    """Eén kanaal lineair maken. De sRGB-transferfunctie uit WCAG 2.1."""
    return waarde / 12.92 if waarde <= 0.03928 else ((waarde + 0.055) / 1.055) ** 2.4


def rgb(kleur: str) -> tuple[int, int, int]:
    """`(r, g, b)` van een merknaam of een hexwaarde."""
    h = HEX.get(kleur, kleur).lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"geen merknaam en geen hexwaarde: {kleur!r}")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def luminantie(kleur: str) -> float:
    """De relatieve luminantie, WCAG 2.1."""
    r, g, b = (_kanaal(k / 255) for k in rgb(kleur))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    """De WCAG-contrastverhouding tussen twee kleuren, op twee decimalen.

    Beide argumenten mogen een merknaam of een hexwaarde zijn, want een
    vormentaal meet ook tegen een kleur die geen merkkleur is. De uitkomst is
    afgerond zoals de vormentalen hem opschrijven, zodat een getal in de tekst
    en een getal uit dit script niet op de derde decimaal uit elkaar lopen.

    >>> contrast("oranje", "wit")
    2.51
    >>> contrast("navy", "oranje")
    6.29
    >>> contrast("navy", "wit")
    15.79
    """
    la, lb = luminantie(a), luminantie(b)
    hoog, laag = max(la, lb), min(la, lb)
    return round((hoog + 0.05) / (laag + 0.05), 2)


def op_wit(*namen: str) -> dict[str, float]:
    """De verhouding op wit per kleur. Zonder namen: alle merkkleuren."""
    return {n: contrast(n, "wit") for n in (namen or tuple(HEX))}


def mag_zin_dragen(kleur: str, achter: str = "wit") -> bool:
    """Haalt deze combinatie de 4,5 van WCAG AA voor lopende tekst?

    Dat is geen vormregel maar de meting eronder. Wanneer een medium ook een
    kop van 40 px op 3,0 toestaat, staat dat in de vormentaal van dat medium.
    """
    return contrast(kleur, achter) >= 4.5


# --------------------------------------------------------------------- css


def _regel(naam: str, waarde: str, uitleg: str = "", breedte: int = 14) -> str:
    kop = f"  --{naam}:".ljust(breedte + 5)
    stuk = f"{kop}{waarde};"
    return f"{stuk.ljust(32)}/* {uitleg} */" if uitleg else stuk


def css_variabelen() -> str:
    """Het `:root`-blok: de kleuren, de rollen, het verloop en de letters.

    Dit is de enige vorm waarin een stylesheet de merkwaarden hoort te
    krijgen. De `-rgb`-drieling staat erbij omdat een haarlijn, een container
    en een stille regel navy op alpha zijn, en `rgba(32, 27, 92, .16)` is
    dezelfde hardgecodeerde merkwaarde in een ander notatiestelsel — één die
    geen enkele grep op `#` vindt. Zo stonden er negenendertig navy's van vóór
    de migratie in de repo, plus zes drielingen met een oranje, een emerald of
    een violet. Schrijf dus `rgba(var(--navy-rgb), .16)`.
    """
    uit = [BEGIN, ":root {",
           "  /* Uit het themapalet van SFNL_Word_sjabloon.dotx: dat sjabloon is de",
           "     merkbron en niet deze plugin. Zie reference/merk.md §1. */"]
    for naam, k in KLEUREN.items():
        if k["bron"] == "gemeten":
            continue
        uit.append(_regel(naam, k["hex"], f'{k["bron"]} — {k["rol"]}'))
    uit += ["", "  /* Niet in het themapalet, dus gemeten uit het drukwerk. */"]
    for naam, k in KLEUREN.items():
        if k["bron"] != "gemeten":
            continue
        uit.append(_regel(naam, k["hex"], k["rol"]))
    uit += ["",
            "  /* De twee rollen. Per pagina overschreven; dit is waar ze op",
            "     uitkomen als niemand iets overschrijft. */"]
    for rol, naam in ROLLEN.items():
        uit.append(_regel(rol, f"var(--{naam})"))
    uit += ["",
            "  /* Dezelfde kleuren als drieling, voor alpha: schrijf",
            "     rgba(var(--navy-rgb), .16) en nooit de cijfers zelf. */"]
    for naam in KLEUREN:
        uit.append(_regel(f"{naam}-rgb", ", ".join(str(k) for k in rgb(naam)), breedte=18))
    uit += ["",
            "  /* Het huisverloop. Er is er één en die is gemeten; een tweede",
            "     verloop is een tweede huisstijl. */",
            _regel("verloop", VERLOOP),
            "",
            "  /* De letterstapels. De familie is invariant, de maat staat per",
            "     medium in de vormentaal van dat medium en dus niet hier.",
            f"     Gotham reist nooit mee; de terugval is {TERUGVAL}. */"]
    for naam, stapel in STAPELS.items():
        uit.append(_regel(naam, stapel))
    uit += ["}", EINDE]
    return "\n".join(uit)


KOP = """/* =====================================================================
   merk.css — de merkwaarden voor elke stylesheet in deze plugin.

   GEGENEREERD uit `scripts/gedeeld/merk.py`, dat de machineleesbare vorm
   van `reference/merk.md` §1 en §2 is. Niet met de hand wijzigen: de
   waarde die je hier verandert, verandert niet mee in merk.py, en
   `scripts/preflight.py` hergenereert dit bestand en meldt het verschil.

   Een kleurwaarde staat één keer, een kleurregel staat per medium. Wat
   hier NIET staat en er ook niet in hoort: een puntgrootte, een marge,
   een raster, een kleurregister, een vulgraad. Die horen in de
   vormentaal van het medium dat ze gemeten heeft.
   ===================================================================== */

"""


def merk_css() -> str:
    """De hele inhoud van `assets/gedeeld/merk.css`."""
    return KOP + css_variabelen() + "\n"


def stempel(tekst: str) -> str:
    """Het merkblok in een bestaande stylesheet vervangen. Idempotent.

    Weigert een stylesheet zonder merktekens, want dan zou de stempel moeten
    raden waar het blok hoort te staan — en een stylesheet waarin de
    merkwaarden op de verkeerde plek belanden, doet het wel maar niet meer om
    de reden die er staat.
    """
    if BEGIN not in tekst or EINDE not in tekst:
        raise ValueError(f"geen merktekens gevonden; zet {BEGIN} en {EINDE} "
                         "om het :root-blok met de merkwaarden")
    kop, rest = tekst.split(BEGIN, 1)
    _, staart = rest.split(EINDE, 1)
    return kop + css_variabelen() + staart


def verschillen() -> list[str]:
    """Wat er uit de pas loopt met merk.py. Leeg is goed.

    Eén regel per bestand, in de vorm die `scripts/preflight.py` in zijn
    remediatie zet: wat er mis is en welke opdracht het rechtzet.
    """
    uit: list[str] = []
    hoort = merk_css()
    if not MERKCSS.exists():
        uit.append(f"{MERKCSS.relative_to(WORTEL)} ontbreekt — draai "
                   "`python scripts/gedeeld/merk.py --css`")
    elif MERKCSS.read_text(encoding="utf-8") != hoort:
        uit.append(f"{MERKCSS.relative_to(WORTEL)} loopt uit de pas met merk.py — "
                   "draai `python scripts/gedeeld/merk.py --css`")
    for pad in GESTEMPELD:
        if not pad.exists():
            uit.append(f"{pad.relative_to(WORTEL)} ontbreekt")
            continue
        tekst = pad.read_text(encoding="utf-8")
        try:
            gestempeld = stempel(tekst)
        except ValueError as fout:
            uit.append(f"{pad.relative_to(WORTEL)}: {fout}")
            continue
        if gestempeld != tekst:
            uit.append(f"{pad.relative_to(WORTEL)}: het merkblok loopt uit de pas met "
                       "merk.py — draai `python scripts/gedeeld/merk.py --css`")
    return uit


def schrijf() -> list[str]:
    """merk.css schrijven en de stylesheets stempelen. Levert wat er veranderde."""
    gedaan: list[str] = []
    hoort = merk_css()
    MERKCSS.parent.mkdir(parents=True, exist_ok=True)
    if not MERKCSS.exists() or MERKCSS.read_text(encoding="utf-8") != hoort:
        MERKCSS.write_text(hoort, encoding="utf-8")
        gedaan.append(f"geschreven: {MERKCSS.relative_to(WORTEL)}")
    for pad in GESTEMPELD:
        tekst = pad.read_text(encoding="utf-8")
        nieuw = stempel(tekst)
        if nieuw != tekst:
            pad.write_text(nieuw, encoding="utf-8")
            gedaan.append(f"gestempeld: {pad.relative_to(WORTEL)}")
    return gedaan


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--css", action="store_true",
                    help="merk.css schrijven en de stylesheets stempelen")
    ap.add_argument("--check", action="store_true",
                    help="alleen melden wat uit de pas loopt; schrijft niets")
    ap.add_argument("--contrast", nargs=2, metavar=("A", "B"),
                    help="de WCAG-verhouding tussen twee merknamen of hexwaarden")
    a = ap.parse_args()

    if a.contrast:
        print(f"{a.contrast[0]} op {a.contrast[1]}: "
              f"{contrast(*a.contrast):.2f}".replace(".", ","))
        return 0
    if a.check:
        fouten = verschillen()
        for regel in fouten:
            print(regel)
        print("merk.css en de gestempelde stylesheets staan gelijk met merk.py"
              if not fouten else f"{len(fouten)} verschil(len)")
        return 1 if fouten else 0
    if a.css:
        gedaan = schrijf()
        for regel in gedaan:
            print(regel)
        if not gedaan:
            print("niets te doen: alles stond al gelijk met merk.py")
        return 0

    # Zonder vlag: de tabellen zelf, want dat is waar dit bestand over gaat.
    for naam, k in KLEUREN.items():
        print(f"{naam:12s} {k['hex']}  {contrast(naam, 'wit'):5.2f} op wit  "
              f"({k['bron']}) — {k['rol']}")
    print()
    for familie, l in LETTERS.items():
        mee = "mag mee" if l["mag_mee"] else "reist nooit mee"
        print(f"{familie:12s} {', '.join(l['gewichten'])} — {l['licentie']} — {mee}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
