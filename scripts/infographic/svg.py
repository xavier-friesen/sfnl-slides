"""Primitieven om een SFNL-infographic als SVG te tekenen, en om hem te meten.

Dit is GEEN patroonbibliotheek. Er zit geen tijdlijn in, geen stroomschema, geen
kaartenrij en geen donut. Wat er wel in zit: de dingen die je nodig hebt om zelf een
compositie te tekenen zonder de valkuilen, plus echt rekenwerk zodat je weet hoe hoog een
blok wordt vóórdat je rendert.

De maat is de punt. Eén SVG-eenheid is één pt, precies zoals in PowerPoint, dus de vier
maten uit de vormentaal (drager 28-40, kop 18, body 16, voetnoot 11) gelden hier
letterlijk. De renderloop kijkt naar de PNG, niet naar deze getallen.

**Eén uitzondering, en die is gemeten:** een beeld dat als exhibit in een document of een
rapport komt te staan, rekent in CSS-px. Dat is de eenheid van die containers en van hun
meetapparaat, en het is geen keuze -- zie `EENHEID` verderop in dit bestand. De zes
`doc-*`- en `rap-*`-canvassen staan daarom in px, `Maten.voor()` zet de eenheid mee, en
`schrijf()` weigert een canvas en maten die niet in dezelfde eenheid staan.

Wat deze laag voor je regelt
----------------------------
* een lichte vulling is `fill-opacity` op de volle kleur, per hue gekalibreerd -- nooit een
  lichtere hex, want die leest als eigen kleur in plaats van als achtergrond
* een lijn om een kaart krijgt dezelfde hue als de vulling
* de tekstkleur die bij een vulling en een puntgrootte hoort, met het contrast uitgerekend
* echte regelafbreking op de fontmetriek van Montserrat en Lato, dus `hoogte_van` klopt
* `xml:space` en escaping, `font-family` met fallback, en de baseline op de juiste plek
* geen Gotham Bold: dat is de titelletter, en een infographic heeft geen titel

Gebruik
-------
Het gewone geval is een figuur: een vorm waarin een meting een lengte, een positie, een dikte
of een hoek bepaalt. Hieronder een geordende staaf -- de lengte is het aandeel, dus de lezer
ziet de verhouding zonder de getallen te lezen, en elke staaf draagt zijn eigen label.

    import sys; sys.path.insert(0, "${CLAUDE_PLUGIN_ROOT}/scripts/infographic")
    from svg import (CANVAS, Canvas, Maten, blok, bron, cirkel, cols, container, drager,
                     hoogte_van, kop, label, lijn, op_schaal, pad, regels, schrijf, tekst,
                     tekst_op, vlak)

    c = CANVAS["breed"]
    m = Maten(body=16, kop=18, drager=36, voetnoot=11)
    X, W, RIJ = 300, 480, 34
    POSTEN = [("Begeleiding", 0.52), ("Taal", 0.26), ("Meting", 0.14), ("Rente", 0.08)]

    vormen = [blok("Drager", 30, 60, 240, [drager("EUR 1,2 mln", m.drager, "oranje")])]
    for i, (naam, aandeel) in enumerate(POSTEN):
        y = 60 + i * (RIJ + 10)
        vormen += [
            vlak(f"Staaf {i}", X, y, aandeel * W, RIJ,            # lengte = de informatie
                 vulling="oranje" if i == 0 else ("navy", 0.16), lijn_=None),
            blok(f"Label {i}", X + aandeel * W + 12, y + RIJ / 2, 220,
                 [kop(f"{naam}  {aandeel:.0%}", m.body)], anchor="c"),   # direct gelabeld
        ]
    schrijf("uitvoer/voorbeeld.svg", c, vormen)

Een rij kaarten kan ook -- `cols()` plus `vlak(vulling=container(...))` plus `blok()` -- en is
soms het goede antwoord. Weet dan wel dat je hem gekozen hebt: in een kaartenrij bepaalt geen
enkele meting iets aan de tekening, dus het beeld zegt wie of wat, en niet hoeveel of wanneer.
`pad()`, `cirkel()` en `op_schaal()` zijn er voor alles wat wel meet.
"""

from __future__ import annotations

import glob
import os
import platform
import re
import subprocess
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

PT_PER_INCH = 72.0
PX_PER_PT = 96.0 / 72.0

# ---------------------------------------------------------------- canvas

@dataclass(frozen=True)
class Canvas:
    """Een tekenvlak. `schaal` tilt de vier maten mee voor groot drukwerk.

    `eenheid` is normaal `"pt"`: één SVG-eenheid is één punt, precies zoals in PowerPoint,
    dus de maten uit de vormentaal gelden letterlijk. De canvassen van de zusterskills staan
    op `"px"`, en dat is geen smaak maar een eis van hun meetapparaat -- zie `EENHEID`.
    """
    naam: str
    w: float
    h: float
    schaal: float = 1.0
    achtergrond: str | None = None      # None = doorzichtig; "wit" = expliciet wit vlak
    eenheid: str = "pt"

    @property
    def midden_x(self) -> float:
        return self.w / 2

    @property
    def midden_y(self) -> float:
        return self.h / 2


#: De canvassen. Alles in pt, want 1 pt = 1 SVG-eenheid = de maat uit de vormentaal.
#: `contentzone` is exact de contentzone van een SFNL-slide (12,52 x 5,00 in), dus een
#: infographic op die maat past er zonder herschalen in.
CANVAS: dict[str, Canvas] = {
    "slide":       Canvas("slide", 960, 540),            # 13,33 x 7,50 in -- hele 16:9-slide
    "contentzone": Canvas("contentzone", 901, 360),      # 12,52 x 5,00 in -- in een deck
    "breed":       Canvas("breed", 960, 320),            # band, tijdlijn, processtrook
    "staand":      Canvas("staand", 460, 640),           # kolom in een rapport of in Word
    "kolom":       Canvas("kolom", 460, 500),            # smallere staande kolom
    "vierkant":    Canvas("vierkant", 560, 560),         # één figuur, mail of social
    "spread":      Canvas("spread", 1191, 780, 1.30),    # 420 x 275 mm, SFNL-rapport
    # --- de vlakken van de zusterskills, zodat een infographic die daar in komt te staan
    # er op ware grootte in past. Zie reference/samenstellen.md. Deze zes staan in PX en
    # niet in pt, en dat is nagemeten: zie EENHEID hieronder. De breedtes komen uit
    # reference/documenten-stramien.md 5b en reference/rapport-stramien.md 3 en 7c.
    "doc-breed":   Canvas("doc-breed", 680, 372, eenheid="px"),   # volle zetspiegel
    "doc-kolom2":  Canvas("doc-kolom2", 325, 244, eenheid="px"),  # één van twee kolommen
    "doc-kolom3":  Canvas("doc-kolom3", 207, 207, eenheid="px"),  # één van drie kolommen
    "rap-breed":   Canvas("rap-breed", 650, 366, eenheid="px"),   # volle zetspiegel
    "rap-kolom":   Canvas("rap-kolom", 537, 302, eenheid="px"),   # de kolom in `breed`
    "rap-dubbel":  Canvas("rap-dubbel", 310, 233, eenheid="px"),  # een kolom in `dubbel`
}

# ---------------------------------------------------------------- de eenheid
#
# Eén SVG-eenheid is één punt. Dat is de hele maatafspraak van deze laag en van de
# vormentaal, en voor een los beeld klopt hij.
#
# **Voor een exhibit klopt hij niet, en dat is gemeten en niet beredeneerd.** De
# containers rekenen in CSS-px, en hun meetapparaat leest de SVG in USER UNITS: de
# `te-klein`-regel van `qa_document.py` neemt `getComputedStyle(el).fontSize`, en dat
# getal is de opgegeven maat in het lokale coördinatenstelsel -- niet de gerenderde
# grootte. Een `viewBox` die de inhoud opschaalt, ziet die regel dus niet. Een
# infographic van 510 pt breed in een kader van 680 px rendert zijn 10-punts brood
# keurig op 13,33 px, en toch meldde `qa_document.py` er acht keer `te-klein: tspan
# staat op 10 px (7,5 pt)` over. Nagemeten op een gebouwde documentpagina: elf
# `critical`, en geen ervan was een echt defect.
#
# Daarom staan de zes canvassen hierboven in px en dragen ze de px-ladder van hun route.
# Dat is ook precies wat `documenten-stramien.md` §5b al voorschreef -- "teken de SVG op
# schaal 1:1, `viewBox` even breed als het kader in px" -- en wat §11 punt 2 bedoelt met
# "de maatladder geldt ook binnen de SVG".
#
# En dan moeten de drie drempels in deze laag mee, want die staan in punten: de
# dragerwindow van 28 tot 40, de kopvloer van 18 waaronder een lichte hue geen tekst mag
# dragen, en de displayvloer van 40 waarboven wit op een lichte hue mag. Op een px-canvas
# zijn dat 25 procent kleinere fysieke maten, dus zonder omrekening zou een lichte hue
# ineens tekst van 13,5 pt mogen dragen waar de regel 18 pt eist. `eenheid()` zet de
# eenheid en `schrijf()` controleert dat hij bij het canvas hoort.

_EENHEID = "pt"
#: Wat één eenheid in punten is, per eenheid.
EENHEID = {"pt": 1.0, "px": 0.75}


def eenheid(naam: str | None = None) -> str:
    """Zet of lees de eenheid van de maten. Zet hem één keer, naast de canvaskeuze.

        c = CANVAS["doc-breed"]
        eenheid(c.eenheid)              # "px": de ladder van het document
        m = Maten.voor("document")

    Vergeet je dit, dan zegt `schrijf()` het -- de eenheid van het canvas en die van de
    maten moeten dezelfde zijn, want anders wordt er wel getekend en klopt er niets.
    """
    global _EENHEID
    if naam is not None:
        if naam not in EENHEID:
            raise ValueError(f"eenheid {naam!r} bestaat niet; kies uit {list(EENHEID)}")
        _EENHEID = naam
    return _EENHEID


def _in_eenheid(punten: float) -> float:
    """Een drempel in punten, uitgedrukt in de eenheid die nu geldt."""
    return punten / EENHEID[_EENHEID]


#: Maatpresets per bestemming, en ze bestaan omdat de maatladder van de container geldt
#: en niet die van de infographic. Een beeld in een document dat zijn eigen 16pt-body
#: meeneemt, zet een zevende maat op een pagina die er zes heeft, en `qa_document.py`
#: meldt dat -- nagemeten in `documenten-vormentaal.md` §11 punt 2.
#:
#: `los` staat in punten, de andere twee in px, want dat is de eenheid van hun canvas.
#: De documentenladder is brood 13,33 / klein 10,67 / kop 16 uit
#: `documenten-stramien.md` §3; de rapportladder brood 13,33 / klein 10,67 / noot 9,33
#: uit `rapport-stramien.md` §3. In punten: 10, 8 en 7.
MATEN_DOEL: dict[str, dict[str, float]] = {
    "los":      {"body": 16, "kop": 18, "voetnoot": 11, "dicht": 12},
    "document": {"body": 13.33, "kop": 16, "voetnoot": 10.67, "dicht": 10.67},
    "rapport":  {"body": 13.33, "kop": 16, "voetnoot": 9.33, "dicht": 10.67},
}

#: Welke eenheid bij welke bestemming hoort.
EENHEID_DOEL = {"los": "pt", "document": "px", "rapport": "px"}


@dataclass
class Maten:
    """De vier maten, één keer per infographic vastgelegd. Eén maat per rol."""
    body: float = 16
    kop: float = 18
    voetnoot: float = 11
    drager: float | None = None          # 28 t/m 40, of None als de drager niet groot is
    dicht: float = 12                    # de vloer: tabelcel of rij van vier of meer
    schaal: float = 1.0

    @classmethod
    def voor(cls, doel: str, **kw) -> "Maten":
        """De maten van de bestemming: `los`, `document` of `rapport`.

        **Dit zet ook de eenheid**, want die hoort bij de ladder: `los` rekent in punten
        en de andere twee in px, de eenheid van hun container. Zie `EENHEID` in dit
        bestand voor waarom dat niet vrij te kiezen is.

        `Maten.voor("document")` zet brood 13,33, kop 16 en noot 10,67 px -- dat is 10, 12
        en 8 pt, de ladder uit `documenten-stramien.md` §3. De drager blijft `None`, en dat
        is geen omissie. Zijn window is 28 tot 40 pt en dat staat niet ter discussie, maar
        op een documentpagina is 28 pt luider dan de titelmaat van die pagina zelf (20 pt).
        Een drager in een exhibit is dus het luidste element na de dektitel. Dat mag, als
        het gekozen is: `Maten.voor("document", drager=37.33)` -- 28 pt in px. De gewone
        uitkomst is dat de figuur zijn eigen bewering draagt en de pagina de woorden.
        """
        if doel not in MATEN_DOEL:
            raise ValueError(f"onbekende bestemming {doel!r}; kies uit {list(MATEN_DOEL)}")
        eenheid(EENHEID_DOEL[doel])
        return cls(**{**MATEN_DOEL[doel], **kw})

    def __post_init__(self) -> None:
        if self.drager is not None:
            d = self.drager
            vloer, plafond = _in_eenheid(DRAGER_VLOER), _in_eenheid(DRAGER_PLAFOND)
            if not (vloer <= d <= plafond):
                raise ValueError(
                    f"drager {d} valt buiten {vloer:g} t/m {plafond:g} "
                    f"({_EENHEID}; dat is 28 t/m 40 pt). Groter leest niet luider; "
                    "wil je meer nadruk, maak de compositie rustiger."
                )
        for naam in ("body", "kop", "voetnoot", "dicht", "drager"):
            v = getattr(self, naam)
            if v is not None:
                setattr(self, naam, round(v * self.schaal, 2))
        self.schaal = 1.0                # schaal is verrekend, niet nog een keer


class _Auto:
    """Sentinel: 'kies de lijn zelf'. `lijn_=None` betekent expliciet geen lijn."""
    def __repr__(self) -> str:
        return "AUTO"


AUTO = _Auto()

DRAGER_VLOER = 28.0
DRAGER_PLAFOND = 40.0
REGELFACTOR = 1.12                       # regelafstand, overal hetzelfde
#: Marge op elke breedtemeting. Twee redenen: er wordt niet gekernd, en de renderer haalt
#: Montserrat en Lato via Google Fonts terwijl de meting het lokale bestand leest -- dezelfde
#: familie, niet gegarandeerd dezelfde versie. Nagemeten verschil op een sluitregel van 537pt:
#: 3,4 procent. Deze marge dekt dat, en daarom breekt de meting eerder af dan strikt nodig.
VEILIGHEID = 1.035
#: Regellengte. Boven deze grens leest een alinea als tekst die over was in plaats van als
#: een uitspraak. `blok()` waarschuwt erboven; het is geen weigering.
MAX_TEKENS_PER_REGEL = 95

# ---------------------------------------------------------------- kleur

HEX = {
    "navy":        "#201B5C",
    "oranje":      "#F87F4F",
    "grapefruit":  "#F95D63",
    "royal":       "#3B62C1",
    "sky":         "#45B6E2",
    "emerald":     "#6AC6BA",
    "wit":         "#FFFFFF",
    "zwartblauw":  "#233348",
}

#: Dekking die van een hue een container maakt in plaats van een kleur. Per hue
#: gekalibreerd -- navy is veel donkerder dan emerald. Gemeten in de winnende SFNL-decks.
CONTAINER = {
    "navy": 0.07, "royal": 0.10, "sky": 0.10,
    "emerald": 0.10, "grapefruit": 0.09, "oranje": 0.12,
}

#: WCAG-contrast op wit, uitgerekend.
OP_WIT = {"navy": 15.30, "royal": 5.67, "grapefruit": 3.10,
          "oranje": 2.58, "sky": 2.32, "emerald": 2.02, "zwartblauw": 12.60}

#: Tekstkleur op een VOLLE vulling.
OP_VOL = {"navy": "wit", "royal": "wit", "zwartblauw": "wit",
          "oranje": "navy", "grapefruit": "navy", "sky": "navy", "emerald": "navy"}

#: Boven deze maat leest een cijfer als vorm en mag wit ook op een lichte hue.
DISPLAY_VLOER = 40.0
#: Onder deze maat draagt een lichte hue geen tekst op wit; dan is de letter navy.
KOP_VLOER = 18.0


def container(hue: str) -> tuple[str, str]:
    """De vulling die als achtergrond leest in plaats van als kleur."""
    if hue not in CONTAINER:
        raise ValueError(f"geen container-dekking voor {hue!r}; kies uit {sorted(CONTAINER)}")
    return (hue, "container")


def _vulling(v) -> tuple[str | None, float]:
    """Normaliseer een vulling naar (hue, dekking). None = geen vulling."""
    if v is None:
        return None, 0.0
    if isinstance(v, str):
        return v, 1.0
    hue, dek = v
    if dek == "container":
        dek = CONTAINER[hue]
    return hue, float(dek)


def tekst_op(vulling, pt: float = 0) -> str:
    """Welke tekstkleur hoort op deze vulling, gegeven de puntgrootte."""
    hue, dek = _vulling(vulling)
    if hue in (None, "wit") or dek <= 0.20:
        return "navy"                                    # wit of container: navy
    if OP_VOL[hue] == "wit":
        return "wit"
    if pt >= _in_eenheid(DISPLAY_VLOER):
        return "wit"                                     # het cijfer leest als vorm
    return "navy"


def mag_dragen(hue: str, pt: float) -> bool:
    """Mag deze hue op wit tekst van deze maat dragen?

    De vloer is 18 pt en die geldt fysiek, dus op een px-canvas is hij 24 -- anders zou
    een lichte hue er tekst van 13,5 pt mogen dragen. Zie `EENHEID`.
    """
    if hue in ("navy", "royal", "zwartblauw", "wit"):
        return True
    return pt >= _in_eenheid(KOP_VLOER)


# ---------------------------------------------------------------- fontmetriek

FAMILIES = {
    "Montserrat Light":    ("Montserrat", 300),
    "Montserrat SemiBold": ("Montserrat", 600),
    "Lato Light":          ("Lato", 300),
}
VERBODEN = ("Gotham",)


#: De plugin-map. `scripts/infographic/svg.py` ligt twee mappen diep, dus dit is de
#: wortel waar `assets/` en de andere skills onder hangen.
WORTEL = Path(__file__).resolve().parents[2]

#: De letters die de plugin zélf meedraagt, en waar ze vandaan komen.
#:
#: `assets/documenten/fonts/` staat er voor de HTML-drukroutes: `fonts.css` sluit deze
#: woff2-bestanden als data-URI in, zodat een document ook zonder internet in de goede
#: letter rendert. Een woff2 is een gecomprimeerde TrueType en fontTools leest hem, dus
#: dezelfde bestanden zijn hier de METRIEKBRON. Daarmee is de afbreking van een
#: infographic uit de doos echt gemeten en niet geschat -- op elke machine, ook in een
#: sandbox zonder fonts en zonder netwerk. Vóór deze route was dat het gewone geval, en
#: dan is `hoogte_van()` ruim en beoordeel je regelval niet op de render.
#:
#: Montserrat komt als één variabel bestand over het bereik 300-800, en zijn
#: standaardinstantie is `wght=100`. Wie de `hmtx` rauw leest, meet dus Thin: de `e` is
#: daar 587/1000 tegen 597 op Light en 622 op SemiBold, en dat is vier procent op de
#: regel. Daarom staat het gewicht hieronder en instantieert `_metriek()` erop.
#: Lato zit er als statische snede in en heeft dat niet nodig.
INGESLOTEN: dict[str, tuple[str, int | None]] = {
    "Montserrat Light":    ("Montserrat-300-800.woff2", 300),
    "Montserrat SemiBold": ("Montserrat-300-800.woff2", 600),
    "Lato Light":          ("Lato-300.woff2", None),
}

#: Waar die bestanden staan, vanaf de plugin-map.
INGESLOTEN_MAP = WORTEL / "assets" / "documenten" / "fonts"


def _ingesloten(familie: str) -> Path | None:
    """Het meegeleverde woff2 voor deze familie, of None."""
    val = INGESLOTEN.get(familie)
    if not val:
        return None
    p = INGESLOTEN_MAP / val[0]
    return p if p.is_file() else None


def _fontbestand_kandidaten(familie: str) -> list[str]:
    zoek: list[str] = []
    slug = familie.replace(" ", "")
    # `assets/documenten/fonts/` is de map waar de deckroute zijn eigen .ttf's verwacht
    # (`scripts/_deck.py`, `find_font_file`); staat daar een volledige snede, dan gaat
    # die vóór het ingesloten subset -- meer tekens, en niets te instantiëren.
    for wortel in (WORTEL / "assets" / "fonts", WORTEL / "assets"):
        zoek += [str(wortel / f"*{slug}*.ttf"), str(wortel / f"*{slug}*.otf")]
    if platform.system() == "Windows":
        lok = os.environ.get("LOCALAPPDATA", "")
        zoek += [
            rf"{lok}\Microsoft\FontCache\4\CloudFonts\{familie.split()[0]}\*",
            rf"C:\Windows\Fonts\{slug}*.ttf",
            rf"C:\Windows\Fonts\{slug}*.otf",
        ]
    else:
        zoek += [
            f"/usr/share/fonts/**/{slug}*.ttf",
            f"/usr/share/fonts/**/{slug}*.otf",
            f"{Path.home()}/.fonts/**/{slug}*.ttf",
            f"{Path.home()}/.local/share/fonts/**/{slug}*.ttf",
        ]
    uit: list[str] = []
    for p in zoek:
        uit += sorted(glob.glob(p, recursive=True))
    return uit


@lru_cache(maxsize=None)
def vind_font(familie: str) -> str | None:
    """Pad naar het echte fontbestand, of None. Dan wordt er geschat.

    Vier routes, in deze volgorde: een volledige snede op de machine, het woff2 dat de
    plugin zelf meedraagt, fontconfig, en anders niets. De tweede is er zodat een
    infographic ook op een kale machine op echte metriek breekt; hij dekt de
    latin-subset, dus alles wat een SFNL-infographic zet behalve het promillageteken.
    """
    for kand in _fontbestand_kandidaten(familie):
        if Path(kand).is_file() and Path(kand).suffix.lower() in (".ttf", ".otf", ""):
            return kand
    eigen = _ingesloten(familie)
    if eigen:
        return str(eigen)
    try:                                                  # laatste redmiddel: fontconfig
        uit = subprocess.run(["fc-match", "-f", "%{file}", familie],
                             capture_output=True, text=True, timeout=8).stdout.strip()
        if uit and Path(uit).is_file() and familie.split()[0].lower() in uit.lower():
            return uit
    except Exception:
        pass
    return None


@dataclass
class _Metriek:
    advances: dict[str, float]
    upem: float
    ascent: float
    descent: float
    geschat: bool = False


@lru_cache(maxsize=None)
def _metriek(familie: str) -> _Metriek:
    pad = vind_font(familie)
    if pad:
        try:
            from fontTools.ttLib import TTFont
            f = TTFont(pad, fontNumber=0, lazy=True)
            gewicht = INGESLOTEN.get(familie, (None, None))[1]
            if gewicht and "fvar" in f:
                # Een variabel bestand levert zijn standaardinstantie, en die is bij
                # Montserrat wght=100. Instantiëren op het gevraagde gewicht is het
                # verschil tussen Thin meten en Light of SemiBold meten.
                from fontTools.varLib import instancer
                f = TTFont(pad, fontNumber=0)
                instancer.instantiateVariableFont(f, {"wght": gewicht}, inplace=True,
                                                  updateFontNames=False)
            upem = f["head"].unitsPerEm
            cmap = f.getBestCmap()
            hmtx = f["hmtx"]
            adv = {}
            for code, naam in cmap.items():
                try:
                    adv[chr(code)] = hmtx[naam][0]
                except Exception:
                    pass
            hhea = f["hhea"]
            return _Metriek(adv, upem, hhea.ascent, abs(hhea.descent))
        except Exception:
            pass
    # Geschat: gemiddelde breedte van een humanistische sans. Ruim, dus de afbreking is
    # conservatief in plaats van te krap.
    breed = 0.56 if "SemiBold" in familie else 0.53
    return _Metriek({"_default": breed}, 1.0, 0.97, 0.25, geschat=True)


def breedte(s: str, familie: str, pt: float, spatie: float = 0.0) -> float:
    """Breedte van `s` in pt, inclusief letterspatiëring. Zonder kerning, dus ~1 procent ruim.

    `spatie` telt mee omdat `label()` hem automatisch zet: een kapitaallabel van 20 tekens op
    11pt met 1,65pt spatiëring is 33pt breder dan de som van de advances. Dat werd een keer
    13 procent onderschatting, en dus een regel die te laat afbrak.
    """
    m = _metriek(familie)
    if m.geschat:
        kern = len(s) * m.advances["_default"] * pt
    else:
        tot = 0.0
        # Een teken dat het bestand niet kent, kreeg eerst de breedte van een spatie, en
        # dat is de verkeerde kant op: het promillageteken zit niet in de latin-subset en
        # is bijna twee keer een cijfer breed, dus zo'n regel brak te laat af. Een cijfer
        # is de veilige schatting -- ruim voor interpunctie, niet te krap voor een teken.
        val = m.advances.get("0") or m.advances.get(" ", 0.3 * m.upem)
        for ch in s:
            tot += m.advances.get(ch, val)
        kern = tot / m.upem * pt * VEILIGHEID
    return kern + max(0, len(s) - 1) * spatie


def regelmaten(familie: str, pt: float) -> tuple[float, float]:
    """(ascent, descent) in pt, uit de echte fontmetriek."""
    m = _metriek(familie)
    if m.geschat:
        return 0.97 * pt, 0.25 * pt
    return m.ascent / m.upem * pt, m.descent / m.upem * pt


def regels(s: str, familie: str, pt: float, w: float, spatie: float = 0.0,
           eerste_w: float | None = None) -> list[str]:
    """Breek `s` af op breedte `w`. Respecteert een expliciete \\n.

    `eerste_w` maakt de eerste regel smaller. Daarmee vang je een aanhef in Montserrat
    SemiBold: die is breder dan Lato Light op dezelfde maat, en zonder correctie past een
    sluitregel volgens de meting wel en op de render niet.
    """
    uit: list[str] = []
    for alinea in str(s).split("\n"):
        woorden = alinea.split()
        if not woorden:
            uit.append("")
            continue
        regel = woorden[0]
        for woord in woorden[1:]:
            kand = f"{regel} {woord}"
            grens = w if uit else (eerste_w if eerste_w is not None else w)
            if breedte(kand, familie, pt, spatie) <= grens:
                regel = kand
            else:
                uit.append(regel)
                regel = woord
        uit.append(regel)
    return uit


def _aanhef_straf(t: "Tekst") -> float:
    """Hoeveel smaller de eerste regel moet zijn omdat de aanhef in een zwaarder gewicht staat."""
    if not t.aanhef:
        return 0.0
    woorden, fam = t.aanhef
    return max(0.0, breedte(woorden, fam, t.pt, t.spatie)
               - breedte(woorden, t.familie, t.pt, t.spatie))


def regels_van(t: "Tekst", w: float) -> list[str]:
    """De afgebroken regels van één alinea, met spatiëring en aanhef meegerekend."""
    straf = _aanhef_straf(t)
    return regels(t.inhoud, t.familie, t.pt, w, t.spatie,
                  eerste_w=w - straf if straf else None)


# ---------------------------------------------------------------- tekst

@dataclass
class Tekst:
    """Eén alinea binnen een blok."""
    inhoud: str
    pt: float
    familie: str = "Lato Light"
    kleur: str = "navy"
    dekking: float = 1.0
    caps: bool = False
    spatie: float = 0.0                  # letterspatiëring in pt
    algn: str = "start"                  # start | middle | end
    ruimte_voor: float = 0.0             # alinea-afstand in pt
    aanhef: tuple[str, str] | None = None  # (woorden, familie) -- twee gewichten in één regel

    def __post_init__(self) -> None:
        for v in VERBODEN:
            if v.lower() in self.familie.lower():
                raise ValueError(
                    f"{self.familie} mag niet: Gotham Bold is de titelletter, en een "
                    "infographic heeft geen titel. Gebruik Montserrat of Lato."
                )
        if self.caps:
            self.inhoud = self.inhoud.upper()
            if not self.spatie:
                self.spatie = self.pt * (0.15 if self.pt <= 13 else 0.10)
        if self.kleur in HEX and not mag_dragen(self.kleur, self.pt):
            raise ValueError(
                f"{self.kleur} op wit haalt {OP_WIT.get(self.kleur)}:1 en draagt geen tekst "
                f"van {self.pt} {_EENHEID}. Vanaf {_in_eenheid(KOP_VLOER):g} {_EENHEID} "
                f"(18 pt) mag het als kop; daaronder is de letter navy."
            )


def tekst(inhoud: str, pt: float, kleur: str = "navy", **kw) -> Tekst:
    """Lopende tekst: Lato Light."""
    return Tekst(inhoud, pt, "Lato Light", kleur, **kw)


def kop(inhoud: str, pt: float, kleur: str = "navy", **kw) -> Tekst:
    """Kop, kolomkop of rolnaam: Montserrat SemiBold."""
    kw.setdefault("caps", False)
    return Tekst(inhoud, pt, "Montserrat SemiBold", kleur, **kw)


def label(inhoud: str, pt: float, kleur: str = "navy", **kw) -> Tekst:
    """Kapitaallabel: Montserrat SemiBold in caps, met letterspatiëring."""
    kw["caps"] = True
    return Tekst(inhoud, pt, "Montserrat SemiBold", kleur, **kw)


def drager(inhoud: str, pt: float, kleur: str = "oranje", **kw) -> Tekst:
    """Het getal of begrip dat de infographic draagt: Montserrat Light, 28 t/m 40pt."""
    vloer, plafond = _in_eenheid(DRAGER_VLOER), _in_eenheid(DRAGER_PLAFOND)
    if not (vloer <= pt <= plafond):
        raise ValueError(f"een drager staat op {vloer:g} t/m {plafond:g} {_EENHEID} "
                         f"(28 t/m 40 pt), niet op {pt}")
    return Tekst(inhoud, pt, "Montserrat Light", kleur, **kw)


def bron(inhoud: str, pt: float | None = None) -> Tekst:
    """De herkomstregel: Lato Light navy op 70 procent, direct onder zijn eigen doos.

    De standaardmaat van 11 geldt alleen in punten, en daarom wordt er in een px-exhibit
    om een maat gevraagd in plaats van er een te verzinnen. Een stilzwijgende 11 zou daar
    8,25 pt worden en dus onder de noot van de pagina zakken -- en de omgekeerde
    aanname, 11 pt omgerekend naar 14,67 px, zou een zevende maat op een pagina zetten
    die er zes heeft. Geef `m.voetnoot` mee; dat is de noot van de container.
    """
    if pt is None:
        if _EENHEID != "pt":
            raise ValueError(
                "geef bron() een maat mee in een exhibit: de noot is die van de container "
                "en niet die van deze laag. Gebruik `bron(tekst, m.voetnoot)` met de "
                "`Maten.voor(...)` van je bestemming."
            )
        pt = 11
    return Tekst(inhoud, pt, "Lato Light", "navy", dekking=0.70)


# ---------------------------------------------------------------- vormen

@dataclass
class Vorm:
    """Een getekend ding plus de doos die het beslaat, zodat `schrijf()` kan controleren.

    De doos is er niet voor de tekening maar voor de controle: `buiten_canvas()` keek eerst
    alleen naar `y_onder`, en miste daarmee horizontale overloop -- het defect dat in twee
    van de drie testopdrachten de eerste renderronde kostte.
    """
    naam: str
    xml: str
    y_onder: float = 0.0
    x_links: float | None = None
    x_rechts: float | None = None
    y_boven: float | None = None


def _kleur(hue: str) -> str:
    if hue.startswith("#"):
        return hue
    if hue not in HEX:
        raise ValueError(f"onbekende kleur {hue!r}; kies uit {sorted(HEX)}")
    return HEX[hue]


def vlak(naam: str, x: float, y: float, w: float, h: float, *,
         vulling=None, lijn_=AUTO, hoek: float = 0.0) -> Vorm:
    """Een vlak. Een container krijgt automatisch een haarlijn in zijn eigen hue.

    Dat is de best gevalideerde vormregel die er is: een vlak van 9 procent vulling zonder
    lijn leest als een vlek, met een 1pt lijn in exact dezelfde hue als een kaart. Een
    grijze of navy rand eromheen maakt er een Word-tabel van.

    Wil je echt geen lijn -- bij een staafje, een spoor of een volvlak -- geef dan
    `lijn_=None`. Dat is expliciet, want auto is de default.

    `hoek` is de radius in pt en is absoluut: één radius voor alle vlakken in dezelfde
    infographic. Nul is recht.
    """
    hue, dek = _vulling(vulling)
    attrs = [f'x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}"']
    if hoek:
        attrs.append(f'rx="{_n(hoek)}" ry="{_n(hoek)}"')
    if hue:
        attrs.append(f'fill="{_kleur(hue)}"')
        if dek < 1.0:
            attrs.append(f'fill-opacity="{dek:g}"')
    else:
        attrs.append('fill="none"')
    if isinstance(lijn_, _Auto):
        lijn_ = (hue, 1.0) if (hue and dek < 1.0) else None
    if lijn_:
        lh, lw = lijn_
        attrs.append(f'stroke="{_kleur(lh)}" stroke-width="{_n(lw)}"')
    return Vorm(naam, f'  <rect id="{_id(naam)}" {" ".join(attrs)}/>', y + h,
                x, x + w, y)


def lijn(naam: str, x1: float, y1: float, x2: float, y2: float, *,
         kleur: str = "navy", dikte: float = 1.0, dekking: float = 1.0,
         streep: str | None = None) -> Vorm:
    a = [f'x1="{_n(x1)}" y1="{_n(y1)}" x2="{_n(x2)}" y2="{_n(y2)}"',
         f'stroke="{_kleur(kleur)}" stroke-width="{_n(dikte)}"']
    if dekking < 1.0:
        a.append(f'stroke-opacity="{dekking:g}"')
    if streep:
        a.append(f'stroke-dasharray="{streep}"')
    return Vorm(naam, f'  <line id="{_id(naam)}" {" ".join(a)}/>', max(y1, y2),
                min(x1, x2), max(x1, x2), min(y1, y2))


def pad(naam: str, d: str, *, vulling=None, lijn_=None,
        hoek_rond: bool = True) -> Vorm:
    """Een eigen pad: pijl, wig, curve, verbinding. Voor alles wat geen rechthoek is."""
    hue, dek = _vulling(vulling)
    a = [f'd="{d}"']
    a.append(f'fill="{_kleur(hue)}"' if hue else 'fill="none"')
    if hue and dek < 1.0:
        a.append(f'fill-opacity="{dek:g}"')
    if lijn_ and not isinstance(lijn_, _Auto):
        lh, lw = lijn_
        a.append(f'stroke="{_kleur(lh)}" stroke-width="{_n(lw)}"')
        if hoek_rond:
            a.append('stroke-linecap="round" stroke-linejoin="round"')
    return Vorm(naam, f'  <path id="{_id(naam)}" {" ".join(a)}/>')


def cirkel(naam: str, cx: float, cy: float, r: float, *, vulling=None,
           lijn_=AUTO) -> Vorm:
    """Een cirkel. Net als `vlak()`: een containervulling krijgt automatisch een haarlijn in
    de eigen hue, want anders is het een vlek en geen vorm (vormentaal §7)."""
    hue, dek = _vulling(vulling)
    if isinstance(lijn_, _Auto):
        lijn_ = (hue, 1.0) if (hue and dek < 1.0) else None
    a = [f'cx="{_n(cx)}" cy="{_n(cy)}" r="{_n(r)}"']
    a.append(f'fill="{_kleur(hue)}"' if hue else 'fill="none"')
    if hue and dek < 1.0:
        a.append(f'fill-opacity="{dek:g}"')
    if lijn_ and not isinstance(lijn_, _Auto):
        lh, lw = lijn_
        a.append(f'stroke="{_kleur(lh)}" stroke-width="{_n(lw)}"')
    return Vorm(naam, f'  <circle id="{_id(naam)}" {" ".join(a)}/>', cy + r,
                cx - r, cx + r, cy - r)


def hoogte_van(alineas: list[Tekst], w: float) -> float:
    """Hoe hoog wordt dit blok? Som van de regelhoogtes plus de alinearuimte."""
    h = 0.0
    for i, t in enumerate(alineas):
        rs = regels_van(t, w)
        n = max(1, len(rs))
        h += (t.ruimte_voor if i else 0.0) + n * t.pt * REGELFACTOR
    return round(h, 2)


def blok(naam: str, x: float, y: float, w: float, alineas: list[Tekst], *,
         anchor: str = "t") -> Vorm:
    """Een tekstblok met `y` als bovenkant van de eerste regel.

    `anchor="t"` is de default en de regel: naast elkaar betekent bovenaan uitgelijnd.
    Staat het blok alleen, dan mag `anchor="c"` en is `y` het midden.
    """
    if isinstance(alineas, Tekst):
        alineas = [alineas]
    h = hoogte_van(alineas, w)
    top = y - h / 2 if anchor == "c" else y
    delen: list[str] = []
    cur = top
    breedst = 0.0
    for i, t in enumerate(alineas):
        if i:
            cur += t.ruimte_voor
        rs = regels_van(t, w) or [""]
        asc, desc = regelmaten(t.familie, t.pt)
        lijnhoogte = t.pt * REGELFACTOR
        leading = (lijnhoogte - (asc + desc)) / 2
        fam, gewicht = FAMILIES.get(t.familie, (t.familie, 400))
        tx = {"start": x, "middle": x + w / 2, "end": x + w}[t.algn]
        a = [f'x="{_n(tx)}"',
             f'font-family="{t.familie}, {fam}, sans-serif"',
             f'font-weight="{gewicht}"',
             f'font-size="{_n(t.pt)}"',
             f'fill="{_kleur(t.kleur)}"']
        if t.dekking < 1.0:
            a.append(f'fill-opacity="{t.dekking:g}"')
        if t.spatie:
            a.append(f'letter-spacing="{_n(t.spatie)}"')
        if t.algn != "start":
            a.append(f'text-anchor="{t.algn}"')
        spans: list[str] = []
        for j, r in enumerate(rs):
            basis = cur + leading + asc + j * lijnhoogte
            inhoud = escape(r)
            if j == 0 and t.aanhef:
                woorden, aanheffamilie = t.aanhef
                if r.upper().startswith(woorden.upper()):
                    rest = r[len(woorden):]
                    af, ag = FAMILIES.get(aanheffamilie, (aanheffamilie, 600))
                    inhoud = (f'<tspan font-family="{aanheffamilie}, {af}, sans-serif" '
                              f'font-weight="{ag}">{escape(woorden)}</tspan>'
                              f'{escape(rest)}')
            spans.append(f'<tspan x="{_n(tx)}" y="{_n(basis)}">{inhoud}</tspan>')
        for r in rs:
            breedst = max(breedst, breedte(r, t.familie, t.pt, t.spatie)
                          + (_aanhef_straf(t) if r is rs[0] else 0.0))
        for r in rs:
            if len(r) > MAX_TEKENS_PER_REGEL:
                print(f"LET OP: {naam!r} heeft een regel van {len(r)} tekens "
                      f"(grens {MAX_TEKENS_PER_REGEL}); maak het blok smaller of de tekst korter.")
        cur += len(rs) * lijnhoogte
        delen.append(f'  <text id="{_id(naam)}-{i}" {" ".join(a)} '
                     f'xml:space="preserve">{"".join(spans)}</text>')
    algn = alineas[0].algn if alineas else "start"
    if algn == "middle":
        xl, xr = x + w / 2 - breedst / 2, x + w / 2 + breedst / 2
    elif algn == "end":
        xl, xr = x + w - breedst, x + w
    else:
        xl, xr = x, x + breedst
    return Vorm(naam, "\n".join(delen), round(top + h, 2), xl, xr, top)


def cols(c: Canvas, n: int, goot: float = 17.0) -> tuple[list[float], float]:
    """x-posities en breedte voor `n` gelijke kolommen over de volle canvasbreedte.

    Goot bij gevulde vlakken 14 tot 17pt; staan er ongevulde prozakolommen naast elkaar,
    neem dan ongeveer 31pt, want zonder vulling heeft de tekst die lucht nodig.
    """
    w = (c.w - goot * (n - 1)) / n
    return [round(i * (w + goot), 2) for i in range(n)], round(w, 2)


def op_schaal(waarde: float, laagst: float, hoogst: float,
             x: float = 0.0, w: float | None = None, c: Canvas | None = None) -> float:
    """De x-positie van een waarde op een schaal. Voor tijdlijnen en alles waar afstand
    informatie draagt.

    Dit is de regel uit vormentaal §8 als functie, want `cols()` staat er wel en maakte het
    verkeerde antwoord -- vier gelijke banden -- het makkelijkst. Op een tijdlijn geldt
    `x = breedte * (t - t0) / (t1 - t0)`, en dat reken je niet met de hand.

        >>> maanden = lambda j, m: (j - 2024) * 12 + (m - 1)
        >>> op_schaal(maanden(2025, 9), 0, maanden(2027, 12), c=CANVAS["breed"])
        408.51
    """
    if w is None:
        w = (c.w if c is not None else 0.0) - x
    if hoogst == laagst:
        raise ValueError("een schaal met laagst == hoogst bestaat niet")
    return round(x + w * (waarde - laagst) / (hoogst - laagst), 2)


def vulgraad(alineas: list[Tekst], w: float, blokhoogte: float,
             inset: float = 11.0) -> float:
    """Teksthoogte gedeeld door blokhoogte. Norm 0,90; het restgat blijft onder 18pt."""
    return round(hoogte_van(alineas, w) / (blokhoogte - 2 * inset), 3)


# ---------------------------------------------------------------- schrijven

def _n(v: float) -> str:
    return f"{round(float(v), 2):g}"


def _id(naam: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "-", naam).strip("-") or "vorm"


def svg(c: Canvas, vormen: list[Vorm], *, beschrijving: str = "",
        raster: bool = False) -> str:
    """Het complete SVG-document. Geen titel, geen kader, geen logo.

    `width` en `height` dragen de eenheid van het canvas en niet altijd `pt`. Dat is geen
    detail: een exhibit van 680 px met `width="680pt"` erop gaat een derde te groot open
    zodra iemand het bestand los bekijkt of in Affinity plaatst, en in het `.beeldkader`
    zou je het niet merken omdat `stijl.css` de breedte daar op 100 procent zet.
    """
    e = "" if c.eenheid == "px" else c.eenheid       # px is de standaardeenheid van SVG
    delen = [
        f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
        f'width="{_n(c.w)}{e}" height="{_n(c.h)}{e}" '
        f'viewBox="0 0 {_n(c.w)} {_n(c.h)}">',
    ]
    if beschrijving:
        delen.append(f"  <desc>{escape(beschrijving)}</desc>")
    if c.achtergrond:
        delen.append(f'  <rect x="0" y="0" width="{_n(c.w)}" height="{_n(c.h)}" '
                     f'fill="{_kleur(c.achtergrond)}"/>')
    for v in vormen:
        delen.append(v.xml)
    if raster:                                           # alleen om zelf te kijken
        for x in range(0, int(c.w) + 1, 20):
            delen.append(f'  <line x1="{x}" y1="0" x2="{x}" y2="{_n(c.h)}" '
                         'stroke="#F95D63" stroke-width="0.25" stroke-opacity="0.4"/>')
        for y in range(0, int(c.h) + 1, 20):
            delen.append(f'  <line x1="0" y1="{y}" x2="{_n(c.w)}" y2="{y}" '
                         'stroke="#F95D63" stroke-width="0.25" stroke-opacity="0.4"/>')
    delen.append("</svg>")
    return "\n".join(delen) + "\n"


#: De binnenmarge van de exhibitroute, per eenheid. Klein, want de zetspiegel van de
#: container draagt de witruimte al -- de 30 pt uit vormentaal §2 is er voor een beeld dat
#: zelf de hele slide vult.
BINNENMARGE = {"pt": 12.0, "px": 10.0}

#: Hoeveel leegte er onder de compositie mag blijven bovenop die ene marge, als deel van
#: de canvashoogte. Alles daarboven is dood wit.
WIT_SPELING = 0.05


def wit_onder(hoogte: float, onderkant: float, eenheid: str) -> tuple[float, float, bool]:
    """(leeg, overtollig, in orde) -- hoeveel wit er onder de compositie staat.

    Eén marge hoort er te zijn en telt dus niet als dood wit; dat is de fout die de eerste
    versie van deze regel maakte -- die vlagde een canvas dat net met `pas_hoogte()` op maat
    was gebracht, en stelde voor de hoogte te veranderen naar precies dezelfde hoogte.

    Deze functie is de enige plek waar de regel staat. `schrijf()` gebruikt hem tijdens het
    bouwen en `insluiten.py` bij het insluiten, en die twee moeten hetzelfde zeggen: een
    waarschuwing die je in de bouw negeert omdat de poort hem straks anders beoordeelt, is
    geen waarschuwing.
    """
    leeg = max(0.0, hoogte - onderkant)
    overtollig = max(0.0, leeg - BINNENMARGE.get(eenheid, 12.0))
    return leeg, overtollig, overtollig <= hoogte * WIT_SPELING


def bodem(vormen: list[Vorm]) -> float:
    """De onderkant van de compositie: de laagste `y_onder` van alle vormen.

    `pad()` en `cirkel()` hebben geen doos, dus die tellen niet mee -- staat je figuur
    grotendeels in paden, lees dit dan als een ondergrens en niet als de waarheid.
    """
    return max((v.y_onder for v in vormen if v.y_onder), default=0.0)


def dood_wit(c: Canvas, vormen: list[Vorm]) -> float:
    """Hoeveel leegte er onder de compositie overblijft, in de eenheid van het canvas."""
    return max(0.0, c.h - bodem(vormen))


def pas_hoogte(c: Canvas, vormen: list[Vorm], marge: float | None = None) -> Canvas:
    """Hetzelfde canvas, maar zo hoog als de compositie plus één marge.

    **Dit is de reparatie voor dood wit onderin, en in de exhibitroute is hij verplicht.**
    Op een los beeld zie je een leeg onderstuk op de render en verklein je het canvas met
    de hand -- dat is stap 5, eerste bevinding. In een `.beeldkader` zie je het niet: de
    verhouding van het kader komt uit de `viewBox`, dus een canvas dat 70 procent gevuld
    is, reserveert op de pagina 30 procent wit dat niemand heeft gekozen en dat de tekst
    eronder wegduwt. Nagemeten op de eerste gebouwde documentpagina: 372 px kader met een
    compositie tot 302, dus 70 px dood wit midden in een zetspiegel.

    De canvasbreedte blijft staan -- die is van de container. Alleen de hoogte beweegt, en
    dat is precies wat `documenten-vormentaal.md` §11 punt 1 voorschrijft: "meer hoogte
    nodig: laat de `viewBox` in de hoogte groeien en houd de breedte gelijk."

        c = CANVAS["doc-breed"]
        m = Maten.voor("document")
        vormen = [...]
        c = pas_hoogte(c, vormen)          # 372 -> 312
        schrijf("uitvoer/exhibit.svg", c, vormen)

    `marge` is standaard de binnenmarge van deze route: 10 in px, 12 in punten. Geef een
    eigen getal als je compositie onderaan zijn eigen lucht heeft.
    """
    if marge is None:
        marge = BINNENMARGE.get(c.eenheid, 12.0)
    h = round(bodem(vormen) + marge, 2)
    if h <= 0:
        raise ValueError("geen enkele vorm heeft een doos, dus de hoogte is niet te meten")
    return Canvas(c.naam, c.w, h, c.schaal, c.achtergrond, c.eenheid)


def buiten_canvas(c: Canvas, vormen: list[Vorm]) -> list[str]:
    """Namen van vormen die buiten het canvas vallen, aan welke kant dan ook.

    Horizontale overloop is het defect dat het vaakst een renderronde kost, en het is het
    goedkoopst hier te vangen. `pad()` heeft geen doos en wordt dus niet gecontroleerd -- dat
    staat er als beperking en niet als belofte.
    """
    uit = []
    for v in vormen:
        buiten = []
        if v.y_onder and v.y_onder > c.h + 0.5:
            buiten.append(f"onder +{v.y_onder - c.h:.0f}")
        if v.y_boven is not None and v.y_boven < -0.5:
            buiten.append(f"boven {v.y_boven:.0f}")
        if v.x_rechts is not None and v.x_rechts > c.w + 0.5:
            buiten.append(f"rechts +{v.x_rechts - c.w:.0f}")
        if v.x_links is not None and v.x_links < -0.5:
            buiten.append(f"links {v.x_links:.0f}")
        if buiten:
            uit.append(f"{v.naam} ({', '.join(buiten)}pt)")
    return uit


def schrijf(pad_: str | Path, c: Canvas, vormen: list[Vorm], *,
            beschrijving: str = "", raster: bool = False) -> Path:
    if c.eenheid != _EENHEID:
        raise ValueError(
            f"het canvas {c.naam!r} rekent in {c.eenheid} en de maten in {_EENHEID}. "
            f"Zet de eenheid naast de canvaskeuze -- `Maten.voor(\"document\")` doet dat "
            f"zelf, of `eenheid(\"{c.eenheid}\")` met de hand. Zonder dat wordt er wel "
            f"getekend en klopt er niets: de drempels van deze laag staan in punten en "
            f"een px-eenheid is 25 procent kleiner."
        )
    p = Path(pad_)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(svg(c, vormen, beschrijving=beschrijving, raster=raster), encoding="utf-8")
    over = buiten_canvas(c, vormen)
    if over:
        print("BUITEN HET CANVAS: " + " | ".join(over))
    # Dood wit onderin is de eerste bevinding van de renderloop, en op een los beeld zie je
    # hem daar ook. In een `.beeldkader` niet: daar wordt de leegte gereserveerde ruimte op
    # de pagina. Dus meldt `schrijf()` hem zelf, met dezelfde regel als `insluiten.py`.
    onder = bodem(vormen)
    if onder:
        leeg, over, ok = wit_onder(c.h, onder, c.eenheid)
        if not ok:
            wat = ("een exhibit reserveert dat als witruimte op de pagina"
                   if c.eenheid == "px" else
                   "maak het canvas korter of zet er meer in -- nooit de blokken hoger")
            print(f"DOOD WIT: {leeg:.0f}{c.eenheid} onder de compositie "
                  f"({leeg / c.h:.0%} van het canvas, {over:.0f} meer dan één marge). "
                  f"{wat}. `pas_hoogte(c, vormen)` geeft "
                  f"{onder + BINNENMARGE.get(c.eenheid, 12.0):.0f}.")
    ontbreekt = [f for f in FAMILIES if not vind_font(f)]
    if ontbreekt:
        print(f"LET OP: geen fontbestand voor {', '.join(ontbreekt)} -- de afbreking is "
              "geschat, dus beoordeel regelval niet op de render.")
    print(f"{p}  {int(c.w)}x{int(c.h)}{c.eenheid}  {len(vormen)} vormen")
    return p
