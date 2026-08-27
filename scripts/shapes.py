"""Primitieven om eigen vormen in de contentzone te schrijven, en om ze te meten.

Dit is GEEN patroonbibliotheek. Er zit geen kaartenrij in, geen stroomschema, geen tegel en
geen band. Wat er wel in zit: de dingen die je nodig hebt om zélf een compositie te tekenen,
correct en zonder de valkuilen, plus rekenwerk om te weten hoe hoog een blok moet zijn
vóórdat je het rendert.

De grens is: dit bestand levert een `vlak`, een `lijn`, een `run`, een `raster`, een `hoogte`,
een handvol merktekens die élk één ding tekenen (`punt`, `meter`, `pijl`, `streep`), en het
gereedschap om zelf te componeren (`adj`, `contour`, `verbind`, `anker`, `groep`, `schaal`).
Wat je daarmee bouwt is jouw beslissing, elke slide opnieuw. Zodra hier een functie zou staan
die drie kaarten op vaste baselines neerzet, is het compose.py geworden en dan gaat de
vormgeving weer op de automaat. Er komt dus geen `kaartenrij()`, geen `stroomschema()` en geen
`tijdlijn()`: bij twijfel generieker in plaats van specifieker.

Een eigen vorm even makkelijk als een vlak
------------------------------------------
Drie wegen, in deze volgorde:

1. **Een presetvorm met zijn handvatten.** `vlak(prst=..., adj=...)`. `PRESET_ADJ` in dit
   bestand zegt per vorm wat `adj1` en `adj2` doen -- een halve punt is
   `prst="pie", adj={"adj1": 5400000, "adj2": 16200000}`, een stap in een volgorde is
   `prst="chevron", adj={"adj": 25000}`. Zonder die tabel was élke preset behalve rechthoek en
   cirkel onbruikbaar, want een leeg `<a:avLst/>` geeft je PowerPoints defaults en die zijn op
   deze maten fout.
2. **Een merkteken.** `punt`, `meter`, `pijl`, `streep`, `verbind`. Elk tekent één ding, elk
   houdt zich aan de kleur- en contrastregels, en elk komt in `assets/maatstaf/11` tot `14`
   voor.
3. **Een eigen contour.** `contour()` neemt punten in inch en schrijft het `custGeom`. Dat is
   een vorm die het sjabloon niet kent, zonder XML te typen.

De discipline geldt op alle drie: alpha in plaats van `lumMod` voor een container, absolute
hoekradius, lijn in de hue van de vulling, expliciete `<a:latin/>`, `noAutofit`, de bindende
elementvolgorde, `lnSpc` 112%, en de contrastregels. Een eigen vorm is geen achterdeur.

Waarom dit bestaat
------------------
De eerste deck die met slides gebouwd werd, had op vier contentslides 31 gevulde
rechthoeken, nul gekleurde letters en niets groter dan 19pt. Dat kwam niet doordat de bouwer
geen smaak had, maar doordat de bouwlaag die hij ad hoc schreef `<a:ln><a:noFill/>` op elke
vorm hardcodeerde en zijn lichte vullingen met `lumMod` maakte. Twee van de mooiste slides in
de referentie -- witte kolommen met een haarlijn in de eigen hue, en een verzadigde kop boven
een nauwelijks getint paneel -- waren daarmee structureel onbouwbaar.

Gemeten in de vijf decks die de blinde vergelijking wonnen:

* nul keer `lumMod`; élke lichte vulling is `<a:alpha>` op de volle kleur
* 11 tot 39 `<a:ln>`-elementen per deck, dus er wordt lijnwerk gebruikt
* `roundRect` draagt altijd een expliciete `adj`, meestal 4000 tot 6000
* regelafstand staat expliciet op 110000 tot 115000
* accenten staan als tekstkleur op wit, niet alleen als vulling

Dit bestand maakt die vijf dingen even makkelijk als het gevulde vlak dat nu de default is.

Gebruik
-------
    import sys; sys.path.insert(0, "<plugin>/scripts")
    from shapes import ZONE, Deck, cols, drager, hoogte_van, para, run, vlak, lijn, write

    d = Deck(body=14, kop=18, label=14, display=32)   # maten per rol, één keer per deck
    xs, w = cols(3, 0.24)
    vormen = [
        vlak("Kaart 1", xs[0], 1.93, w, 2.4, vulling=("emerald", 9000), hoek=0.10,
             tekst=[para(drager("62", d.display, "emerald"))]),
    ]
    write("unpacked/ppt/slides/slide3.xml", vormen)
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "gedeeld"))
import merk as _merk  # noqa: E402

EMU_PER_INCH = 914400

#: De contentzone van layout 19 t/m 22. Boven `y` staat de geërfde header.
ZONE = {"x": 0.48, "y": 1.93, "w": 12.52, "h": 5.00, "right": 13.00, "bottom": 6.93}

#: Layout 17, het blanco canvas: geen header, dus het hele vlak.
CANVAS = {"x": 0.36, "y": 0.40, "w": 12.64, "h": 6.57, "right": 13.00, "bottom": 6.97}


def emu(inches: float) -> str:
    return str(int(round(inches * EMU_PER_INCH)))


def cols(n: int, goot: float = 0.24) -> tuple[list[float], float]:
    """x-posities en breedte voor `n` gelijke kolommen over de volle contentbreedte.

    De goot is smaller dan je denkt: bij gevulde vlakken doet de vulling het
    scheidingswerk, dus 0.20 tot 0.24 in is genoeg. Staan er ongevulde prozakolommen naast
    elkaar, neem dan 0.43 in -- dat is de maat die layout 21 en 22 zelf gebruiken, en zonder
    vulling heeft de tekst die lucht nodig.
    """
    w = (ZONE["w"] - goot * (n - 1)) / n
    return [round(ZONE["x"] + i * (w + goot), 4) for i in range(n)], round(w, 4)


#: De twee prozakolommen op de eigen maat van layout 21 en 22.
PROZA_2 = ([0.48, 6.82], 5.91)


# ---------------------------------------------------------------- kleur

#: Merknaam naar themaslot.
HUE = {
    "navy": "dk2", "oranje": "accent1", "grapefruit": "accent2",
    "royal": "accent3", "sky": "accent4", "emerald": "accent5",
    "wit": "lt2", "zwartblauw": "dk1", "grijs": "tx1",
}

#: De hues die als lichtheidstrap geschreven worden in plaats van met alpha, met hun
#: `(lumMod, lumOff)`. Er is er één, en dat is het voetnootgrijs dat `sjabloon.md` onder
#: Kleur als hét grijs documenteert: `tx1` met `lumMod 65000` / `lumOff 35000`.
#:
#: Het heet grijs en het is het niet: op de render is dit `#5176A7`, contrast 4,67 op wit en
#: 51 procent verzadiging -- een staalblauw dat in een deck met sky of royal als vijfde lid
#: van de set meedoet. Geen enkele trap van dit slot is neutraal (27 tot 52 procent
#: verzadiging over lumMod 40 tot 80), want `tx1` is zelf `#233348`. Zie
#: `assets/proeven/LEESMIJ.md` voor de vier metingen. §3 van `vormentaal.md` maakt hem sinds
#: die proef de default voor een KAPITAALlabel, ook in een deck met een set hues: caps krijgen
#: spatiëring (§2), spatiëring gaat niet samen met alpha (zie `run()`), en dan blijft dit de
#: enige kleur over. Voor een stille regel zonder kapitalen is navy op alpha 70 de kleur.
#:
#: Waarom dit naast de alpharegel bestaat, en waarom het die regel niet ondermijnt: §4 van
#: `vormentaal.md` gaat over een lichte VULLING -- een container, en die is altijd alpha op
#: de volle kleur. Grijs is hier geen container maar een TEKSTKLEUR: de bronregel, de
#: eenheid, de kolomkop boven een tabel. Voor die rol werkt alpha in de praktijk niet, want
#: alpha op de tekstkleur samen met `spc` (letterspatiëring) laat de LibreOffice-render de
#: laatste glyph van de run weg -- zie de waarschuwing in `run()`. `vulling_xml()` weigert
#: `"grijs"` daarom als vulling.
LUM = {"grijs": (65000, 35000)}

#: Alphawaarde die van een hue een container maakt in plaats van een kleur. Per hue
#: gekalibreerd, want navy is veel donkerder dan emerald: gemeten uit de vijf winnende
#: decks, waar navy op 6000-8000 staat en de accenten op 9000-14000.
CONTAINER_ALPHA = {
    "navy": 7000, "royal": 10000, "sky": 10000,
    "emerald": 10000, "grapefruit": 9000, "oranje": 12000,
}

#: Contrast op wit, echt uitgerekend (WCAG-verhouding).
#: navy 15.30 | royal 5.67 | grapefruit 3.10 | oranje 2.58 | sky 2.32 | emerald 2.02
OP_WIT = {"navy": 15.30, "royal": 5.67, "grapefruit": 3.10,
          "oranje": 2.58, "sky": 2.32, "emerald": 2.02}

#: Tekstkleur op een VOLLE vulling. Wit staat op navy en royal; op de lichte accenten
#: staat navy, want daar haalt wit 2.0 tot 3.1. Uitzondering: op displaymaat (>= 40pt)
#: mag wit ook op de lichte accenten -- dan leest het cijfer als vorm en niet als tekst,
#: en dat is wat de sterkste referentieslide doet. `tekst_op` dwingt dat af.
#: De tekstkleur op een volle vulling. Stond hier als tabel en dat was een
#: onderhoudsval: `violet` ontbrak, en `tekst_op()` viel daarop stil terug op
#: navy -- navy op violet haalt 2,86 en dat is precies de paring die
#: `reference/merk.md` §1 als de val aanwijst. De tabel komt nu uit
#: `merk.inkt_op()`, die hem per kleur uitrekent, dus hij kan niet meer uit de
#: pas lopen met het palet.
OP_VOL = {naam: _merk.inkt_op(naam) for naam in _merk.HEX
          if naam not in ("wit",)}

DISPLAY_VLOER = 40.0

#: De band waarin een drager mag staan, en dat is een huisbesluit boven de meting. De
#: winnende decks zetten hun grote getal op 44 tot 56pt, maar met die band eronder werd de
#: aandachtstrekker op elke slide gezet, en dan trekt hij niets meer. De drager staat nu op
#: 28 tot 40pt, en hij is de uitzondering: ten hoogste één slide op drie draagt hem.
DRAGER_VLOER = 28.0
DRAGER_PLAFOND = 40.0

#: Gotham Bold is de titelletter en die erf je uit de layout -- je schrijft hem nooit zelf.
#: Op de slide zelf is de letter licht: Montserrat Light of Lato Light. De drager staat in
#: Montserrat Light, want een groot getal in een licht gewicht is stiller dan hetzelfde
#: getal in een vet gewicht en zegt precies hetzelfde.
TITELFONT = "Gotham Bold"
DRAGERFONT = "Montserrat Light"

#: De aanhef binnen een doorlopende regel. Eén familie per regel: staat de aanhef midden in
#: een alinea Lato Light, dan is de aanhef een zwaarder Lato en niet Montserrat SemiBold.
#: `Lato Semibold` bestaat als eigen familienaam in de fontlijst -- geen `b="1"`-nepvet.
#: Nagemeten op de render (LibreOffice 24.2.7.2, fonts-lato 2.015-1), dezelfde zin op 16pt
#: met elk Lato-gewicht als aanhef naast Lato Light als rest: `Lato` regular en `Lato Medium`
#: zetten een verschil dat je pas ziet als je het weet, `Lato Heavy` gaat met de kop erboven
#: concurreren. `Lato Semibold` zet dezelfde gewichtssprong als Montserrat SemiBold deed,
#: binnen dezelfde letterbouw en dezelfde x-hoogte.
AANHEFFONT = "Lato Semibold"

#: De families die niet in dezelfde alinea mogen staan. Zie `para()`.
_MONTSERRAT = "montserrat"
_LATO = "lato"


def tekst_op(vulling: str | tuple, pt: float = 0) -> str:
    """Welke tekstkleur hoort op deze vulling, gegeven de puntgrootte."""
    hue, alpha = _split(vulling)
    if hue in (None, "wit") or (alpha and alpha <= 20000):
        return "navy"                      # wit of een container: navy erop
    if pt >= DISPLAY_VLOER:
        return "wit"                       # displaymaat: wit mag op elke volle hue
    # Geen `.get(hue, "navy")` meer. Een hue die hier niet in staat, is een hue
    # die niet in het palet staat, en dan is navy geen antwoord maar een gok --
    # zie de noot bij OP_VOL. `merk.inkt_op()` rekent hem alsnog uit als het een
    # merkkleur is, en klaagt als het er geen is.
    if hue in OP_VOL:
        return OP_VOL[hue]
    return _merk.inkt_op(hue)


def _split(v):
    """(hue, alpha) uit `"emerald"`, `("emerald", 9000)` of `"container:emerald"`."""
    if v is None:
        return None, None
    if isinstance(v, str):
        if v.startswith("container:"):
            hue = v.split(":", 1)[1]
            return hue, CONTAINER_ALPHA.get(hue, 10000)
        return v, None
    hue, alpha = (list(v) + [None])[:2]
    return hue, alpha


def _clr(hue: str, alpha: int | None = None) -> str:
    """Eén `<a:schemeClr>`. Volgorde binnen het element is bindend: `lumMod`, dan `lumOff`,
    dan `alpha` (`sjabloon.md`, Volgorde binnen de XML).

    De alpha is een **honderdduizendste**: `7000` is 7 procent en `100000` is dekkend. Dat
    is de OOXML-eenheid en die staat vast. `svg.py` van `sfnl-infographic` rekent met een
    breuk tussen 0 en 1, en die twee lagen worden nu door twee skills gebruikt -- dus een
    breuk die hier binnenkomt is niet zeldzaam maar te verwachten. Zonder de grens
    hieronder was `("navy", 0.16)` geldige invoer: `int(0.16)` is 0, dus
    `<a:alpha val="0"/>`, dus een vorm die volledig doorzichtig is. Nagemeten op de
    keten van layout 19: drie van de vier staven waren er niet, en de XML valideerde
    schoon. Dat is een uur zoeken in een render.
    """
    if alpha is not None and 0 < alpha < 1000:
        raise ValueError(
            f"alpha {alpha} is geen OOXML-alpha. Deze laag rekent in honderdduizendsten, "
            f"dus 7 procent is 7000 en niet 0,07. Kwam dit uit svg.py van "
            f"infographic, die rekent met een breuk: vermenigvuldig met 100000, of "
            f"gebruik `\"container:{hue}\"` voor de gekalibreerde containerdekking."
        )
    slot = HUE.get(hue, hue)
    inner = ""
    if hue in LUM:
        mod, off = LUM[hue]
        inner += f'<a:lumMod val="{mod}"/><a:lumOff val="{off}"/>'
    if alpha:
        inner += f'<a:alpha val="{int(alpha)}"/>'
    return f'<a:schemeClr val="{slot}">{inner}</a:schemeClr>' if inner else \
           f'<a:schemeClr val="{slot}"/>'


def vulling_xml(v) -> str:
    """`"emerald"` is vol, `("emerald", 9000)` is een container, `"container:emerald"`
    pakt de gekalibreerde alpha, `None` is geen vulling."""
    if v is None:
        return "<a:noFill/>"
    if isinstance(v, str) and v.startswith("container:"):
        hue = v.split(":", 1)[1]
        _geen_grijs_vlak(hue)
        return f"<a:solidFill>{_clr(hue, CONTAINER_ALPHA.get(hue, 10000))}</a:solidFill>"
    hue, alpha = _split(v)
    _geen_grijs_vlak(hue)
    return f"<a:solidFill>{_clr(hue, alpha)}</a:solidFill>"


def _geen_grijs_vlak(hue) -> None:
    """`"grijs"` is een tekstkleur, geen vulling en geen kaartlijn.

    Een grijs vlak of een grijze rand om een gekleurde kaart is de Word-tabellook uit §8, en
    het is precies de achterdeur die een nieuwe kleur in de laag zou openzetten. De lichte
    vulling is alpha op de volle kleur (§4); de neutrale container is `("navy", 7000)`.
    """
    if hue in LUM:
        raise ValueError(
            f'"{hue}" is in deze laag een TEKSTkleur -- de bronregel, de eenheid, de '
            "kolomkop -- en geen vulling of kaartlijn. Een grijs vlak of een grijze rand om "
            "een gekleurde kaart is de Word-tabellook (vormentaal.md §8). Wil je een licht "
            'vlak: dat is alpha op de volle kleur, `("navy", 7000)` voor de neutrale '
            'container of `"container:<hue>"` voor de gekalibreerde tint. Wil je een lijn: '
            "geef hem de hue van de vulling."
        )


#: De streepvormen die een lijn mag dragen. Meer bestaat er in OOXML, maar op de render zijn
#: dit de drie die van elkaar te onderscheiden zijn op 0,75 tot 2pt.
DASH = ("solid", "dash", "sysDash", "dashDot", "lgDash", "dot", "sysDot")


def lijn_xml(l) -> str:
    """`("emerald", 1)` is een haarlijn van 1pt in emerald. `None` is geen lijn.

    Drie vormen, en de derde is de nadruk:

    * `("emerald", 1)` -- doorlopend, 1pt, emerald
    * `(("navy", 25000), 0.75)` -- hetzelfde kleurtupel als `vulling` en `run()`: hue met
      alpha, dus een haarlijn in het lichte register van §8
    * `("oranje", 2, "dash")` -- gestreept. Dit is de nadrukomlijning: een `roundRect` zonder
      vulling met een streepjeslijn eromheen, zoals de tweede kaart op `maatstaf/11`. Zonder
      deze parameter kostte die ene omlijning 18 regels ruwe XML.

    De lijn heeft dezelfde hue als de vulling. Een lijn in een ándere hue -- grijs om wit,
    navy om een getint vlak -- is de Word-tabellook, en dat is het enige wat hier verboden
    is. In de winnende deck staat drie keer op één slide een 1pt lijn in exact de hue van
    de vulling; dat is wat een vlak van 9% nog als kaart laat lezen in plaats van als vlek.
    De uitzondering waarvoor de dash bestaat: een gestreepte lijn in een ándere hue om een
    kaart heen is geen rand maar een aanwijzing -- ze omcirkelt iets, ze omlijnt het niet.

    Volgorde binnen `<a:ln>` is bindend: eerst de vulling, dan `prstDash`. Andersom keurt
    het schema het af.
    """
    if l is None:
        return "<a:ln><a:noFill/></a:ln>"
    delen = list(l)
    kleur = delen[0]
    pt = delen[1] if len(delen) > 1 else 1
    dash = delen[2] if len(delen) > 2 else None
    hue, alpha = _split(kleur)
    _geen_grijs_vlak(hue)
    if dash and dash not in DASH:
        raise ValueError(
            f'streepvorm "{dash}" kent deze laag niet. Kies uit {", ".join(DASH)} -- '
            '"dash" is de nadrukomlijning uit `maatstaf/11`.'
        )
    streepjes = f'<a:prstDash val="{dash}"/>' if dash and dash != "solid" else ""
    return (f'<a:ln w="{int(round(pt * 12700))}" cap="flat">'
            f"<a:solidFill>{_clr(hue, alpha)}</a:solidFill>{streepjes}</a:ln>")


# ---------------------------------------------------------------- tekst

#: De grijze regel voor een bron of een eenheid: navy op 70% dekking. Het is wat de
#: winnende decks gebruiken, en het blijft geldig -- maar alleen op een run ZONDER `spc`.
#: Alpha op de tekstkleur samen met letterspatiëring laat de LibreOffice-render de laatste
#: glyph van de run weg (nagemeten: `MEETDOEL` wordt `MEETDOE`). Voor een grijs kapitaallabel
#: is de kleur daarom `"grijs"`, het voetnootgrijs uit `sjabloon.md`. Zie `run()`.
GRIJS = ("navy", 70000)

#: De bovengrens voor een cursieve run. Cursief is toegestaan voor een korte, niet-lopende
#: regel -- een datum, een eenheid, een bron, een scenario-aanduiding -- en verboden voor
#: lopende tekst en voor alles van meer dan één regel. 48 tekens is ruim genoeg voor
#: `Aug/september 2026` of `Bron: monitor 2024`, en te krap voor een bewering.
CURSIEF_MAX = 48


def run(tekst: str, font: str, pt: float, kleur="navy", *,
        vet: bool = False, spc: int | None = None, caps: bool = False,
        cursief: bool = False) -> str:
    """Eén tekstrun. `kleur` mag elke merknaam zijn, ook een accent -- kleur hoeft niet in
    een vlak te zitten.

    De expliciete `<a:latin/>` is niet optioneel: een eigen vorm erft `otherStyle`, en dat
    is Calibri 18pt.

    Een kapitaallabel krijgt letterspatiëring: `spc=150` tot en met 13pt, `spc=100`
    daarboven. Zonder spatiëring leest een caps-label als geschreeuw in plaats van als
    label.

    **Alpha op de tekstkleur en `spc` gaan niet samen -- renderobservatie.** Een run met
    zowel een alphakleur (`("navy", 70000)`, `GRIJS`) als `spc` verliest in de
    LibreOffice-render zijn laatste glyph: `MEETDOEL` komt eruit als `MEETDOE`, `GEWICHT` als
    `GEWICH`. Nagemeten op LibreOffice 24.2.7.2. Of echte PowerPoint hetzelfde doet is hier
    niet te toetsen -- observatie op deze renderer, geen OOXML-feit.

    Nagemeten in `assets/proeven/06`, en dat verandert wat je ertegen kunt doen: de glyph valt
    niet weg maar wordt GEKLIPT, en het is geen aan-of-uit. Bij `spc=60` staat de L van
    `MEETDOEL` er half, bij `spc=100` vrijwel niet, en `VERANTWOORDEN` verliest bij `spc=100`
    de hele N -- het tekort loopt op met de spatiëring maal het aantal tekens. Een spatie
    achter het woord repareert het dus niet (geprobeerd, variant 2 van die proef) en een breder
    tekstvak ook niet, want het klipt op de run en niet op de doos. Er is geen veilige
    ondergrens: bij alpha zet je géén `spc`.

    Deze functie weigert de combinatie daarom niet, maar `label()` wel, want die zet `spc`
    altijd. Wil je een STIL label: dat is navy op alpha 70 zonder `spc` (`#625E8C`, contrast
    6,0) -- dezelfde hue als navy, alleen lichter, dus geen extra kleur in de deck. Wil je
    spatiëring op dat label, dan is de kleur `"grijs"` (`tx1` met lumMod/lumOff), maar let op
    wat dat werkelijk is: `#5176A7`, 51 procent verzadigd, dus een vijfde blauw dat naast sky
    en royal meedoet in een set (`vormentaal.md` §3, met de vier lichtheidstrappen in
    `assets/proeven/LEESMIJ.md`). Op een gewone regel zonder spatiëring -- een bron, een
    eenheid -- is `GRIJS` gewoon goed.

    De val die dit kostte, en waarom hij hier staat: de vorige bouwer zocht de ontbrekende
    letter eerst in de vakbreedte en heeft twee ronden aan een te smal tekstvak gerekend dat
    niet te smal was.

    **Cursief mag, beperkt.** `cursief=True` is toegestaan voor een korte, niet-lopende
    regel: een datum, een eenheid, een bron, een scenario-aanduiding. Eén regel, ten hoogste
    48 tekens (`CURSIEF_MAX`), en geen tweede zin erin. Het origineel van `maatstaf/11` zet de
    datumregel per kaart zo, en dat werkt daar omdat de regel niet gelezen maar herkend
    wordt. Voor lopende tekst blijft cursief verboden (`vormentaal.md` §9): een cursieve
    alinea leest langzamer en er is een goedkoper middel voor nadruk, namelijk kleur.

    Gotham Bold weigert deze functie. Die letter staat in de titel en komt uit de layout;
    op de slide zelf is het Montserrat Light of Lato Light, met Montserrat SemiBold voor wat
    lósstaat en op zijn eigen regel begint: een kop, een kapitaallabel, een rolnaam, een
    kolomkop. Een aanhef binnen een doorlopende regel is dus géén Montserrat: die zet je met
    `aanhef()`, in `Lato Semibold` op een Lato Light-alinea. `para()` weigert een alinea die
    beide families bevat.

    `vet=True` is er voor het geval dat een echt gewicht niet bestaat. Zet het niet op een
    Lato Light- of Montserrat Light-run om nadruk te maken: dat is nepvet, en de renderer
    kiest zelf wat hij ervan maakt. Er is een echt gewicht: `Lato Semibold`,
    `Montserrat SemiBold`.

    **Geen hoge punt als scheiding binnen een regel.** `tekst tekst · meer tekst` is de vorm
    die ontstaat als twee feiten op één regel worden geperst -- en twee feiten zijn twee
    regels, twee cellen of twee elementen. Dit geldt in de contentzone, in een label en in
    een bronregel. Deze functie blokkeert het niet, want een middelpunt kan een legitiem
    teken zijn; het is een regel die je zelf aanhoudt (`vormentaal.md` §9,
    `adviesvorm.md` §4).
    """
    if cursief:
        kort = tekst.strip()
        if len(kort) > CURSIEF_MAX or ". " in kort:
            raise ValueError(
                f"cursief mag alleen op een korte, niet-lopende regel: een datum, een "
                f"eenheid, een bron, een scenario-aanduiding, van één regel en ten hoogste "
                f"{CURSIEF_MAX} tekens. Deze run is {len(kort)} tekens"
                + (" en bevat meer dan één zin" if ". " in kort else "")
                + ". Voor lopende tekst is cursief verboden (vormentaal.md §9); nadruk in "
                "een alinea doe je met kleur, of met `aanhef()` voor twee niveaus binnen "
                "één regel."
            )
    if font.strip().lower() == TITELFONT.lower():
        raise ValueError(
            f"{TITELFONT} schrijf je nooit zelf: dat is de titelletter en die erf je uit de "
            f"layout. Op de slide is de letter licht -- {DRAGERFONT} voor een drager of een "
            "kop, Lato Light voor lopende tekst."
        )
    b = ' b="1"' if vet else ""
    i = ' i="1"' if cursief else ""
    s = f' spc="{spc}"' if spc is not None else ""
    c = ' cap="all"' if caps else ""
    # De eenheid blijft bij het getal (voice.md): een gewone spatie na het euroteken
    # laat "€" op de vorige regel achter zodra de regel daar breekt. Vastgezet met een
    # non-breaking space, zodat de regel dat nooit kan.
    tekst = tekst.replace("€ ", "€ ")
    esc = (tekst.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    hue, alpha = _split(kleur)
    return (f'<a:r><a:rPr lang="nl-NL" sz="{int(round(pt * 100))}"{b}{i}{s}{c} dirty="0">'
            f'<a:solidFill>{_clr(hue, alpha)}</a:solidFill>'
            f'<a:latin typeface="{font}"/></a:rPr>'
            f'<a:t>{esc}</a:t></a:r>')
    # Let op: GEEN xml:space="preserve" op <a:t>. Dat is WordprocessingML; in DrawingML
    # keurt het schema het af. Voor- en achterloopruimte blijft in DrawingML gewoon staan.


def label(tekst: str, pt: float = 14, kleur="navy", *,
          spc: int | float | None = -1) -> str:
    """Kapitaallabel in Montserrat SemiBold met de juiste spatiëring.

    Wil je het label grijs -- een kolomkop boven een tabel, een rolnaam die de rij niet moet
    overstemmen -- dan is de kleur `"grijs"`: het voetnootgrijs `tx1` met lumMod/lumOff dat
    `sjabloon.md` onder Kleur als hét grijs documenteert. **Niet `GRIJS`**, want dat is navy
    op alpha, en alpha samen met de `spc` die deze functie altijd zet laat de
    LibreOffice-render de laatste letter weg: `MEETDOEL` wordt `MEETDOE`, `GEWICHT` wordt
    `GEWICH`. Nagemeten met zeven varianten; elk van de twee apart rendert goed. Of echte
    PowerPoint dezelfde glyph laat vallen is hier niet te toetsen -- renderobservatie, geen
    OOXML-feit. Deze functie weigert de combinatie daarom, met de kleur `"grijs"` als weg
    eruit; het `GRIJS`-recept blijft geldig op een run zonder spatiëring, en dat is de
    bronregel van §11.

    En dat is de gewone weg, ook in een deck met een set hues: §3 kiest voor een kapitaallabel
    `"grijs"` mét spatiëring boven navy-op-alpha zónder, omdat caps zonder spatiëring als
    geschreeuw lezen (§2). Dat het `#5176A7` is en dus een vijfde blauw naast sky en royal, is de
    prijs en staat in §3 opgeschreven. `label("MEETDOEL", 14, GRIJS, spc=None)` blijft mogelijk
    en is dan jouw besluit; navy op alpha is de kleur voor een stille regel zónder kapitalen,
    zoals de bronregel van §11.

    `spc=None` zet de spatiëring uit. Dat is de ontsnappingsklep waarmee een alphakleur
    alsnog kan, en dan is het jouw keuze: een caps-label zonder spatiëring leest als
    geschreeuw in plaats van als label (§2), dus doe het alleen als de render je overtuigt.
    """
    if spc == -1:
        spc = 150 if pt <= 13 else 100
    _, alpha = _split(kleur)
    if alpha and spc is not None:
        raise ValueError(
            "een kapitaallabel met een alphakleur mist in de render zijn laatste letter: "
            "alpha op de tekstkleur samen met `spc` laat LibreOffice de laatste glyph weg "
            "(MEETDOEL -> MEETDOE). Twee wegen eruit: (1) gebruik de kleur \"grijs\" -- het "
            "voetnootgrijs tx1 met lumMod/lumOff uit sjabloon.md, en dat is precies de kleur "
            "die daar als het grijs staat; (2) `label(..., spc=None)` als je de spatiëring "
            "wilt opgeven, maar dan leest caps als geschreeuw. Op een gewone regel zonder "
            "spatiëring -- een bronregel, een eenheid -- is `GRIJS` gewoon goed."
        )
    return run(tekst, "Montserrat SemiBold", pt, kleur, spc=spc, caps=True)


def drager(tekst: str, pt: float, kleur: str = "navy", *, spc: int | None = None) -> str:
    """De drager: het getal, de verhouding of het kernbegrip dat de slide draagt.

    Altijd Montserrat Light, en dat is het punt. Een getal van 32pt in een licht gewicht
    springt er even goed uit als hetzelfde getal in een vet gewicht, maar het schreeuwt niet
    mee met de titel erboven -- en de titel is de enige plek waar Gotham Bold staat.

    De maat moet in de band vallen: onder 28pt is er geen drager, boven 40pt is hij luider
    dan de boodschap. Gebruik dit ten hoogste op één slide op drie; op de andere slides is
    de drager gewicht en kleur (18pt SemiBold in de hue van zijn categorie) of de compositie
    zelf.

    Een cijfer en een label op dezelfde baseline
    --------------------------------------------
    Twee runs in ÉÉN alinea, met `anchor="b"` op het vak:

        tekst("Kolom 1 kop", x, y, w, 0.62,
              [para(drager("1  ", D.display, "oranje"),
                    label("ZELF OPSCHRIJVEN", D.label, "navy"), regelafstand=None)],
              anchor="b")

    Dat zet een cijfer van 32pt en een label van 14pt op één baseline zonder twee vakken en
    zonder ze met de hand uit te lijnen -- de rangnummerkop van `maatstaf/14`. Twee
    Montserrat-gewichten, dus `para()` laat het door: dit is geen familiemix. De twee spaties
    achter het cijfer zijn de tussenruimte; op displaymaat is één spatie te smal.

    Dit patroon neemt de plek in van het verboden recept met een Montserrat-aanhef in een
    Lato-alinea (§9). Het verschil is dat de twee runs hier niet één doorlopende regel vormen
    maar twee elementen zijn die op één lijn staan.
    """
    if not DRAGER_VLOER <= pt <= DRAGER_PLAFOND:
        raise ValueError(
            f"drager op {pt}pt valt buiten de band {DRAGER_VLOER:.0f}-{DRAGER_PLAFOND:.0f}pt. "
            "Daaronder springt er niets uit; daarboven neemt de drager de slide over."
        )
    return run(tekst, DRAGERFONT, pt, kleur, spc=spc)


def aanhef(kop: str, rest: str, pt: float, kleur: str = "navy") -> list[str]:
    """Twee runs in één alinea: `Lato Semibold` als aanhef, Lato Light voor de rest.

    Dit is het middel waarmee je twee hiërarchieniveaus binnen één tekstregel haalt, zonder
    een tweede kolom en zonder een tweede vak. **Eén familie per regel**: de aanhef staat
    binnen een doorlopende Lato-alinea, dus is hij Lato -- in een echt zwaarder gewicht, niet
    met `b="1"` erop. Montserrat SemiBold blijft voor wat lósstaat en op zijn eigen regel
    begint: een kop, een kapitaallabel (`label()`), een rolnaam, een kolomkop.

    Wat hier eerder stond, en waarom het is omgezet
    -----------------------------------------------
    Deze docstring beriep zich op een meting: "Gemeten in `maatstaf/04`: acht alinea's, elk
    met een SemiBold aanhef van twee tot vier woorden op dezelfde 16pt". Die meting is
    nagerekend en ze is juist -- `04` zet werkelijk Montserrat SemiBold in een Lato
    Light-alinea. Nagemeten op de PNG van `assets/maatstaf/04`, op 1920 px (144 dpi):

    * `Vaste` in de aanhef is 92 px breed bij een kapitaalhoogte van 23 px, verhouding 4,00.
      Montserrat SemiBold zet die verhouding op 4,00; Lato Semibold op 3,35.
    * `noemen` in de rest is 106 px breed bij een x-hoogte van 17 px, verhouding 6,2.
      Lato Light zet 6,8; Montserrat Light 8,0.
    * De hele regel nagebouwd op 16pt in Montserrat SemiBold + Lato Light valt op de
      pixel over de originele regel; in Lato Semibold + Lato Light is de aanhef ruim 14 procent
      korter en breekt de regel elders.

    De regel hier overruled dus een gemeten patroon uit een winnende deck, en niet een
    verkeerde meting. Dat is een besluit: twee families binnen één tekstregel zetten twee
    letterbouwen en twee x-hoogtes naast elkaar op dezelfde maat, en dat leest als een
    zetfout in plaats van als hiërarchie. `assets/maatstaf/04` is voor dít aspect geen lat
    meer; voor de rest van die slide -- twee hues voor een tegenstelling, proza als exhibit
    -- blijft hij dat wel. Zie `reference/vormentaal.md` §9.
    """
    return [run(kop.rstrip() + " ", AANHEFFONT, pt, kleur),
            run(rest, "Lato Light", pt, kleur)]


_LATIN = re.compile(r'<a:latin typeface="([^"]*)"')


def _een_familie(runs: tuple[str, ...]) -> None:
    """Weiger een alinea die Montserrat en Lato door elkaar zet.

    Dit is de guard die 'één familie per regel' onmogelijk te vergeten maakt. Hij staat hier
    en niet in `run()`, want een run kent zijn buren niet: de fout bestaat pas op het niveau
    van de alinea. En hij staat niet in `vlak()` of `tekst()`, want dan zou een alinea die
    los wordt doorgegeven aan een tabelcel of aan `retext_slide.py` er langs glippen.
    """
    families = set()
    for r in runs:
        for naam in _LATIN.findall(r or ""):
            kleine = naam.strip().lower()
            if kleine.startswith(_MONTSERRAT):
                families.add("Montserrat")
            elif kleine.startswith(_LATO):
                families.add("Lato")
    if len(families) > 1:
        raise ValueError(
            "Montserrat en Lato in dezelfde alinea: één alinea is één doorlopende regel, en "
            "twee families op dezelfde maat zetten daar twee letterbouwen en twee x-hoogtes "
            "naast elkaar. Twee wegen eruit: (1) is het een kop, een kapitaallabel, een "
            "rolnaam of een kolomkop, zet hem dan als eigen alinea of eigen vak in "
            f"Montserrat SemiBold -- `label()` doet dat; (2) is het een aanhef binnen de "
            f"regel, gebruik dan `aanhef()`, die zet hem in {AANHEFFONT} met Lato Light "
            "voor de rest."
        )


def para(*runs: str, algn: str | None = None, spc_voor: int | None = None,
         regelafstand: int | None = 112000, num: bool = False) -> str:
    """Eén alinea.

    `regelafstand` staat default op 112000 (112%), want een eigen vorm erft geen
    regelafstand en Lato Light op enkel wit staat te dicht. De winnende decks zetten
    110000 tot 115000. Zet hem op None voor een label of een getal van één regel.

    `spc_voor` in honderdsten van een punt: 600 (6pt) tussen alinea's in een kaart of
    tabelcel, ongeveer een hele regelhoogte in een prozakolom -- daar is de witruimte de
    enige scheiding tussen twee beweringen.

    **Eén familie per alinea.** Deze functie weigert een alinea die zowel een Montserrat- als
    een Lato-run bevat. Eén alinea is één doorlopende regel, en twee families op dezelfde
    maat zetten daar twee letterbouwen en twee x-hoogtes naast elkaar. Een alinea met alleen
    Montserrat (een kop, een label, een drager) en een alinea met alleen Lato (body) gaan
    gewoon door.
    """
    _een_familie(runs)
    bits = f' algn="{algn}"' if algn else ""
    # Volgorde in CT_TextParagraphProperties is bindend: lnSpc, dan spcBef, dan spcAft, dan
    # de bullet-elementen. Andersom keurt het schema het af.
    inner = ""
    if regelafstand:
        inner += f'<a:lnSpc><a:spcPct val="{int(regelafstand)}"/></a:lnSpc>'
    if spc_voor:
        inner += f'<a:spcBef><a:spcPts val="{int(spc_voor)}"/></a:spcBef>'
    if num:
        inner += '<a:buFont typeface="+mj-lt"/><a:buAutoNum type="arabicPeriod"/>'
    ppr = f"<a:pPr{bits}>{inner}</a:pPr>" if (bits or inner) else ""
    return f"<a:p>{ppr}{''.join(runs)}</a:p>"


#: Insets. Een vak MET vulling houdt marge; een tekstvak zonder vulling krijgt 0, zodat de
#: tekst met de vakrand uitlijnt en dus met de rest van de kolom.
INSETS_GEVULD = (0.20, 0.20, 0.15, 0.15)
INSETS_KAAL = (0.0, 0.0, 0.0, 0.0)


def tekstvak(paras: list[str], *, insets=INSETS_GEVULD, anchor: str = "t") -> str:
    """`<p:txBody>` met `noAutofit`.

    `noAutofit` is verplicht: past de tekst niet, dan wordt het vak groter of de tekst
    korter, nooit het font kleiner. Eén vak met 90%-schaling haalt een hele rij uit de lijn.

    Over `anchor`: staat een blok ALLEEN, dan mag `ctr` en is de overgebleven lucht padding.
    Staat het in een rij of naast een tweede blok, dan is de bovenkant vast (`t`) met
    dezelfde `tIns`, en valt de restlucht onderaan. Centreren in een rij zet de eerste
    regels van de buren millimeters uit elkaar zodra de een meer regels heeft dan de ander,
    en dat leest als slordig.
    """
    l, r, t, b = insets
    return (f'<p:txBody><a:bodyPr lIns="{emu(l)}" rIns="{emu(r)}" tIns="{emu(t)}" '
            f'bIns="{emu(b)}" anchor="{anchor}" wrap="square"><a:noAutofit/></a:bodyPr>'
            f'<a:lstStyle/>{"".join(paras)}</p:txBody>')


# ---------------------------------------------------------------- vormen

_ids = [200]


def adj_van(hoek: float, w: float, h: float) -> int:
    """De `adj` van een `roundRect` uit een ABSOLUTE hoekradius in inch.

    `adj = 100000 x radius / min(breedte, hoogte)`, geklemd op 0 tot 50000. Dit staat los van
    `vlak()` omdat de berekening buiten een vorm net zo vaak nodig is: een gestreepte
    nadrukomlijning die 0,14 in buiten een kaart valt, moet dezelfde absolute radius houden
    en dus een andere `adj`. Dat handmatig terugrekenen was op `maatstaf/11` de helft van de
    18 regels die die ene omlijning kostte.

    Waarom absoluut en niet in procenten: `sjabloon.md`, Vormen. Een `roundRect` zonder
    expliciete `adj` krijgt 16,67% van de korte zijde, en dan is een blok van 1 in hoog een
    pil en een blok van 2,5 in een nette kaart -- vier radii in één deck zonder dat iemand er
    iets aan koos.
    """
    return max(0, min(50000, int(round(100000 * hoek / min(w, h)))))


#: Wat de `adj`-handvatten van de presetvormen doen die op een SFNL-slide voorkomen. Dit is
#: de tabel die nergens te vinden was, en daardoor was élke presetvorm behalve rechthoek en
#: cirkel onbruikbaar: `vlak()` schreef een leeg `<a:avLst/>` en je kreeg PowerPoints
#: defaults. `ss` is de korte zijde, `min(breedte, hoogte)`.
#:
#: ==================  ==========================================================
#: `roundRect`         `adj` = hoekradius als 1/100000 van `ss`. Gebruik `hoek=` of
#:                     `adj_van()`; default 16667 is de val uit §8.
#: `round1Rect`        idem, maar alleen de rechterbovenhoek.
#: `ellipse`           geen handvat. Cirkel: geef `w == h`.
#: `pie`               `adj1` = starthoek, `adj2` = eindhoek, in 1/60000 graad,
#:                     rechtsom vanaf 3 uur. Halve punt (links gevuld):
#:                     `adj1=5400000` (90°), `adj2=16200000` (270°). Kwart:
#:                     `adj1=16200000`, `adj2=0`. Default 0 tot 16200000 is
#:                     driekwart en leest als een pacman.
#: `arc`, `chord`      dezelfde twee hoeken; `arc` is alleen de boog (geef hem een
#:                     `lijn` en geen vulling), `chord` sluit met een koorde.
#: `donut`             `adj` = ringdikte als 1/100000 van `ss`; 12500 is een dunne
#:                     ring, default 25000 een dikke.
#: `blockArc`          `adj1`/`adj2` = start- en eindhoek (1/60000 graad),
#:                     `adj3` = ringdikte als 1/100000 van `ss`. Dit is de boog
#:                     voor een aandeel: 0 tot 21600000 x aandeel.
#: `rightArrow`        `adj1` = schachtdikte als 1/100000 van `ss` (100000 is de
#:                     volle hoogte), `adj2` = koplengte als 1/100000 van `ss`.
#:                     Beide default 50000, en dáár gaat het mis: op een pijl van
#:                     0,24 in hoog is de kop dan 0,12 in en leest het geheel als
#:                     een driehoekje. Zie `pijl()`.
#: `leftArrow`,        idem, gespiegeld respectievelijk gedraaid.
#: `upArrow`,
#: `downArrow`
#: `leftRightArrow`    `adj1` = schachtdikte, `adj2` = koplengte per kant.
#: `chevron`,          `adj` = puntlengte als 1/100000 van `ss`. Een rij chevrons met
#: `homePlate`         `adj=25000` leest als een volgorde; default 50000 maakt van
#:                     elke stap een pijlpunt en dan is de navigatie luider dan de
#:                     boodschap (§1).
#: `triangle`          `adj` = x van de top, 0 is linksonder, 50000 gelijkbenig.
#: `trapezoid`         `adj` = inspringing van de bovenzijde per kant.
#: `plaqueTabs`,       `adj` = hoekmaat als 1/100000 van `ss`.
#: `snip1Rect`,
#: `bevel`
#: `stripedRightArrow` `adj1` = schachtdikte, `adj2` = koplengte.
#: ==================  ==========================================================
#:
#: De volledige lijst met formules staat in ECMA-376 deel 1, bijlage met de
#: presetShapeDefinitions; wat hierboven staat is wat op deze slides werkelijk voorkwam,
#: nagemeten op de render.
PRESET_ADJ = {
    "roundRect": ("adj",),
    "round1Rect": ("adj",),
    "pie": ("adj1", "adj2"),
    "arc": ("adj1", "adj2"),
    "chord": ("adj1", "adj2"),
    "donut": ("adj",),
    "blockArc": ("adj1", "adj2", "adj3"),
    "rightArrow": ("adj1", "adj2"),
    "leftArrow": ("adj1", "adj2"),
    "upArrow": ("adj1", "adj2"),
    "downArrow": ("adj1", "adj2"),
    "leftRightArrow": ("adj1", "adj2"),
    "stripedRightArrow": ("adj1", "adj2"),
    "chevron": ("adj",),
    "homePlate": ("adj",),
    "triangle": ("adj",),
    "trapezoid": ("adj",),
    "leftBrace": ("adj1", "adj2"),
    "rightBrace": ("adj1", "adj2"),
    "leftBracket": ("adj",),
    "rightBracket": ("adj",),
    "snip1Rect": ("adj",),
    "bevel": ("adj",),
}


def _avlst(adj: dict | None) -> str:
    """`<a:avLst>` uit een dict van handvatnaam naar waarde."""
    if not adj:
        return "<a:avLst/>"
    binnen = "".join(f'<a:gd name="{n}" fmla="val {int(v)}"/>' for n, v in adj.items())
    return f"<a:avLst>{binnen}</a:avLst>"


def vlak(naam: str, x: float, y: float, w: float, h: float, *,
         prst: str = "rect", vulling=None, lijn=None, hoek: float | None = None,
         adj: dict | None = None, rot: float | None = None,
         tekst: list[str] | None = None, insets=None, anchor: str = "t") -> str:
    """Eén `<p:sp>`. Met `prst` en `adj` is dit de weg naar élke presetvorm.

    `prst` is de vrije parameter en de belangrijkste ontsnappingsklep die deze laag heeft:
    `prst="ellipse"` met `w == h` is de cirkelbadge, `prst="pie"` een halve punt,
    `prst="chevron"` een stap in een volgorde. Wat je niet met een preset kunt tekenen, gaat
    via `contour()`.

    `adj` zet de handvatten van die preset: één dict die letterlijk
    `<a:gd name=... fmla="val ..."/>` uitschrijft. Zonder deze parameter kreeg élke vorm
    behalve rechthoek en cirkel PowerPoints defaults, en dan is de halve punt een pacman en
    de pijl een driehoekje. `PRESET_ADJ` hierboven zegt per vorm wat de waarden doen:

        vlak("Halve punt", x, y, d, d, prst="pie", vulling="oranje",
             adj={"adj1": 5400000, "adj2": 16200000})

    `hoek` is de hoekradius in INCH en de bestaande snelweg voor een `roundRect`: geef je
    hem, dan wordt `prst` automatisch `roundRect` en rekent `adj_van()` de handvatwaarde per
    vorm terug naar diezelfde absolute radius. `hoek` en `adj` samen is een fout, want dan
    zeggen twee parameters iets over hetzelfde handvat.

    `rot` is een rotatie in graden, voor het geval een preset alleen in één richting bestaat.
    Gebruik hem spaarzaam: gedraaide tekst is in dit sjabloon nooit goed, en een gedraaid
    vlak lijnt met niets uit (§7).
    """
    _ids[0] += 1
    if hoek and adj:
        raise ValueError(
            "`hoek` en `adj` samen: beide zetten het handvat van een roundRect. Gebruik "
            "`hoek` (absolute radius in inch, de huisregel uit §8), of `adj` als je een "
            "andere presetvorm zet."
        )
    if hoek:
        prst = "roundRect"
        geom = (f'<a:prstGeom prst="roundRect">'
                f'{_avlst({"adj": adj_van(hoek, w, h)})}</a:prstGeom>')
    else:
        if adj:
            bekend = PRESET_ADJ.get(prst)
            if bekend and not set(adj) <= set(bekend):
                raise ValueError(
                    f'prst="{prst}" kent de handvatten {", ".join(bekend)}; je geeft '
                    f'{", ".join(sorted(set(adj) - set(bekend)))}. Zie `PRESET_ADJ` in '
                    "shapes.py voor wat elk handvat doet."
                )
        geom = f'<a:prstGeom prst="{prst}">{_avlst(adj)}</a:prstGeom>'
    if insets is None:
        insets = INSETS_GEVULD if vulling is not None else INSETS_KAAL
    body = tekstvak(tekst, insets=insets, anchor=anchor) if tekst else ""
    draai = f' rot="{int(round(rot * 60000)) % 21600000}"' if rot else ""
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{_ids[0]}" name="{naam}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr>'
            f'<a:xfrm{draai}><a:off x="{emu(x)}" y="{emu(y)}"/>'
            f'<a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>{geom}'
            f'{vulling_xml(vulling)}{lijn_xml(lijn)}</p:spPr>{body}</p:sp>')


def tekst(naam: str, x: float, y: float, w: float, h: float, paras: list[str], *,
          anchor: str = "t", insets=INSETS_KAAL) -> str:
    """Tekst zonder vulling: insets 0, dus de tekst lijnt uit met de vakrand."""
    _ids[0] += 1
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{_ids[0]}" name="{naam}"/>'
            f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr>'
            f'<a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/>'
            f'<a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/>'
            f'<a:ln><a:noFill/></a:ln></p:spPr>'
            f'{tekstvak(paras, insets=insets, anchor=anchor)}</p:sp>')


def streep(naam: str, x: float, y: float, lengte: float, kleur="navy",
           pt: float = 1.0, *, richting: str = "h", dash: str | None = None) -> str:
    """Eén rechte lijn, horizontaal (`richting="h"`) of verticaal (`richting="v"`).

    Een streep scheidt lichter dan een gevuld vlak: onder een label, tussen twee registers,
    boven een sluitregel, als rasterlijn in een verdeling. Dat lichte register (§8) ontbreekt
    zodra je alleen vlakken hebt.

    `kleur` neemt hetzelfde tupel als `vulling` en `run()`: `"navy"` is vol, `("navy", 25000)`
    is een haarlijn die er nauwelijks is -- precies wat een rasterlijn achter een plot moet
    zijn. Twee dingen die deze functie eerder niet kon, en die elk een eigen hulpfunctie in
    een los bestand kostten: verticaal (`cy` stond hard op 0) en alpha (het kleurargument ging
    zonder alpha naar `_clr()`). Het ontdekken kostte een render, want de fout was stil.

    `dash="dash"` maakt hem gestreept. Voor een verbinding tussen twee punten die niet op één
    as liggen: `verbind()`.
    """
    if richting not in ("h", "v"):
        raise ValueError(
            f'richting="{richting}" bestaat niet: "h" is horizontaal, "v" is verticaal. Een '
            "schuine lijn tussen twee punten is `verbind()`."
        )
    dx, dy = (lengte, 0.0) if richting == "h" else (0.0, lengte)
    return verbind(naam, (x, y), (x + dx, y + dy), kleur, pt, dash=dash)


def verbind(naam: str, van: tuple[float, float], naar: tuple[float, float],
            kleur="navy", pt: float = 1.0, *, dash: str | None = None) -> str:
    """Een rechte verbinding tussen twee punten in inch. `streep()` is de rechte variant.

    Dit is hoe je twee vormen verbindt zonder te rekenen met `flipH`/`flipV`: geef de twee
    punten, deze functie zet de `xfrm` en de spiegeling. Gebruik `anker()` om een punt op de
    rand van een vorm te vinden, dan raakt de lijn de vorm en niet zijn hoek.

    Een verbinding is een lijn en dus het lichte register: geef hem alpha
    (`("navy", 25000)`) tenzij de verbinding zelf informatie draagt -- de balk tussen de twee
    punten van een dumbbell dóet dat, en die staat op de hue van de reeks.
    """
    (x0, y0), (x1, y1) = van, naar
    hue, alpha = _split(kleur)
    _geen_grijs_vlak(hue)
    if dash and dash not in DASH:
        raise ValueError(f'streepvorm "{dash}" kent deze laag niet: kies uit {", ".join(DASH)}.')
    flip = ""
    if x1 < x0:
        flip += ' flipH="1"'
    if y1 < y0:
        flip += ' flipV="1"'
    _ids[0] += 1
    streepjes = f'<a:prstDash val="{dash}"/>' if dash and dash != "solid" else ""
    return (f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{_ids[0]}" name="{naam}"/>'
            f'<p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr><p:spPr>'
            f'<a:xfrm{flip}><a:off x="{emu(min(x0, x1))}" y="{emu(min(y0, y1))}"/>'
            f'<a:ext cx="{emu(abs(x1 - x0))}" cy="{emu(abs(y1 - y0))}"/></a:xfrm>'
            f'<a:prstGeom prst="line"><a:avLst/></a:prstGeom>'
            f'<a:ln w="{int(round(pt * 12700))}" cap="flat">'
            f'<a:solidFill>{_clr(hue, alpha)}</a:solidFill>{streepjes}</a:ln></p:spPr>'
            f'<p:style><a:lnRef idx="1"><a:schemeClr val="dk2"/></a:lnRef>'
            f'<a:fillRef idx="0"><a:schemeClr val="dk2"/></a:fillRef>'
            f'<a:effectRef idx="0"><a:schemeClr val="dk2"/></a:effectRef>'
            f'<a:fontRef idx="minor"><a:schemeClr val="lt1"/></a:fontRef></p:style>'
            f'</p:cxnSp>')


#: De negen ankerpunten van een doos, voor `anker()`.
KANTEN = ("l", "r", "b", "o", "lb", "rb", "lo", "ro", "m")


def anker(doos: tuple[float, float, float, float], kant: str = "m") -> tuple[float, float]:
    """Een punt op de rand of in het midden van een doos `(x, y, w, h)`, in inch.

    `"l"` en `"r"` zijn links- en rechtsmidden, `"b"` en `"o"` boven- en ondermidden, `"lb"`
    tot `"ro"` de vier hoeken, `"m"` het midden. Hiermee zet je een vorm op de rand van een
    andere en laat je `verbind()` twee vormen raken in plaats van hun hoeken.
    """
    x, y, w, h = doos
    if kant not in KANTEN:
        raise ValueError(f'kant "{kant}" bestaat niet: kies uit {", ".join(KANTEN)}.')
    px = {"l": x, "lb": x, "lo": x, "r": x + w, "rb": x + w, "ro": x + w}.get(kant, x + w / 2)
    py = {"b": y, "lb": y, "rb": y, "o": y + h, "lo": y + h, "ro": y + h}.get(kant, y + h / 2)
    return round(px, 4), round(py, 4)


#: De lichte punt van een meter: navy op alpha 25000. Geen `"grijs"`, want dit is een VULLING
#: en die is alpha op de volle kleur (§4).
LEEG = ("navy", 25000)


def punt(naam: str, x: float, y: float, d: float, hue="navy", *,
         tekst: str | None = None, pt: float = 16, kleur=None,
         font: str = "Montserrat SemiBold", deel: float = 1.0, leeg=LEEG) -> str:
    """Eén ronde punt van `d` inch, met een optioneel gecentreerd cijfer erin.

    Wat dit codeert: één ding uit een reeks. De genummerde badge in de hue van zijn kaart
    (`maatstaf/11`), een bolletje in een legenda, een punt op een as, een punt van een
    puntenmeter (`maatstaf/12`, zie `meter()`). Het is het goedkoopste merkteken dat er is en
    het vervangt een genummerde bulletlijst.

    Waarom dit een eigen functie is en niet `vlak(prst="ellipse")`: een cirkel met een cijfer
    erin heeft `insets=(0,0,0,0)`, `anchor="ctr"` en `algn="ctr"` nodig, en `vlak()` geeft een
    gevulde vorm terecht `INSETS_GEVULD`. Dat zelf onthouden was op zes plekken handwerk, en
    vergeet je het, dan staat het cijfer niet in het midden -- op de render zichtbaar als een
    badge waarvan het getal naar rechtsonder is gezakt.

    `deel` is hoeveel van de punt gevuld is: 1.0 vol, 0.0 leeg (in `leeg`), en daartussen een
    gevulde `pie` over een lege punt -- 0.5 is de halve punt die op `maatstaf/12` gewicht
    codeert. Die tussenvorm komt terug als één groep, dus als één vorm in je lijst.

    `kleur` is de kleur van het cijfer; zonder hem kiest `tekst_op()` en dan staat er navy op
    een lichte hue, want wit haalt daar 2,0 tot 3,1 (§3). `maatstaf/11` zet het badgecijfer
    wél wit op sky, emerald en oranje: op een badge van 0,50 in leest één cijfer als vorm en
    niet als tekst, net als de drageruitzondering op 40pt. Dat is een bewuste keuze die je op
    de render controleert -- `kleur="wit"` -- en geen default.

    Misplaatst als: de punten iets meten dat een getal is. Drie van de drie punten is geen
    69 procent; een puntenmeter codeert een grofheid (zwaar, licht, niet) en juist dat is zijn
    waarde. Wil je een precieze verhouding, dan is dat een balk of een grafiek (§12).
    """
    if not 0.0 <= deel <= 1.0:
        raise ValueError(f"deel={deel} valt buiten 0.0 tot 1.0: het is een fractie van de punt.")
    paras = None
    if tekst is not None:
        paras = [para(run(tekst, font, pt, tekst_op(hue, pt) if kleur is None else kleur),
                      algn="ctr", regelafstand=None)]
    if deel >= 1.0:
        return vlak(naam, x, y, d, d, prst="ellipse", vulling=hue, tekst=paras,
                    insets=(0, 0, 0, 0), anchor="ctr")
    onder = vlak(f"{naam} leeg", x, y, d, d, prst="ellipse", vulling=leeg, tekst=paras,
                 insets=(0, 0, 0, 0), anchor="ctr")
    if deel <= 0.0:
        return onder
    # Een `pie` rechtsom vanaf 3 uur, in 1/60000 graad. Voor een halve punt begint hij op
    # 90 graden en eindigt op 270: dan is de LINKERhelft gevuld, en dat is de leesrichting.
    start = 5400000
    eind = int(round(start + 21600000 * deel)) % 21600000
    boven = vlak(f"{naam} deel", x, y, d, d, prst="pie", vulling=hue,
                 adj={"adj1": start, "adj2": eind})
    return groep(naam, x, y, d, d, [onder, boven])


def meter(naam: str, x: float, y: float, waarden, hue="navy", *,
          d: float = 0.16, pitch: float = 0.22, leeg=LEEG) -> str:
    """Een puntenmeter: een rij punten waarvan de eerste `n` gevuld zijn.

    `waarden` is een reeks fracties -- `(1, 1, 0.5)` is twee volle punten en een halve, en
    dat is hoe `maatstaf/12` "zwaar" van "licht" onderscheidt zonder een getal te noemen. De
    hele meter komt terug als één groep, dus als één vorm.

    Wat het codeert: een grofheid op een schaal van drie of vier stappen, naast een label dat
    hetzelfde in een woord zegt. De punten zijn er om de rij te kunnen aflezen zonder de
    woorden te vergelijken.

    Misplaatst als: er meer dan vijf punten nodig zijn (dan wordt het tellen en is het een
    balk), of als de waarde precies is (dan is het een getal of een grafiek, §12).
    """
    waarden = list(waarden)
    if len(waarden) > 5:
        raise ValueError(
            f"{len(waarden)} punten is een meter die je moet tellen in plaats van aflezen. "
            "Boven vijf punten is de vorm een balk of een getal (vormentaal.md §12)."
        )
    breedte = (len(waarden) - 1) * pitch + d
    kinderen = [punt(f"{naam} {i + 1}", x + i * pitch, y, d, hue, deel=float(v), leeg=leeg)
                for i, v in enumerate(waarden)]
    return groep(naam, x, y, breedte, d, kinderen)


def pijl(naam: str, x: float, y: float, w: float, h: float, hue="oranje", *,
         richting: str = "r", dikte: float = 0.45, kop: float | None = None) -> str:
    """Een pijl die een volgorde draagt: van hier naar daar, en niet als versiering.

    `dikte` is de schachtdikte als fractie van de hoogte, `kop` de koplengte in INCH. De
    defaults van PowerPoint zijn hier onbruikbaar: `adj1` en `adj2` staan beide op 50000, en
    op een pijl van 0,24 in hoog is de kop dan 0,12 in -- het geheel leest als een
    driehoekje in plaats van als een pijl. Nagemeten op `maatstaf/14`, waar drie van deze
    pijlen de drie stappen verbinden.

    Misplaatst als: de pijl navigatie is in plaats van inhoud. Blijven bij de kneepoefening
    (§1) de pijltjes over en niet de boodschap, dan is de pijl te zwaar of overbodig. En een
    gekleurd vlak dat alleen kleur is, gaat eruit (§8) -- dat geldt ook voor een pijl.
    """
    prst = {"r": "rightArrow", "l": "leftArrow", "b": "upArrow", "o": "downArrow"}.get(richting)
    if not prst:
        raise ValueError(
            f'richting="{richting}" bestaat niet: "r" rechts, "l" links, "b" boven, '
            '"o" onder.'
        )
    ss = min(w, h)
    # Default: een kop van 45 graden, dus zo lang als de vorm hoog is -- en nooit meer dan
    # de helft van de pijl, want dan is de schacht weg en leest het als een driehoekje.
    kop = min(ss, w / 2) if kop is None else min(kop, w)
    return vlak(naam, x, y, w, h, prst=prst, vulling=hue,
                adj={"adj1": max(0, min(100000, int(round(dikte * 100000)))),
                     "adj2": max(0, min(100000, int(round(kop / ss * 100000))))})


#: Het raster waarop een icoon getekend wordt. 24 eenheden, zoals elk lijnpictogram dat
#: bestaat, want dan liggen de halve en de derde maat op een hele eenheid: 12 is het midden,
#: 8 en 16 zijn de derden, en 4 is de marge die het icoon van zijn buur vrijhoudt.
ICOON_RASTER = 24

#: De schachtdikte van een icoon in punten, en de reden dat er één is: twee diktes in één
#: icoon leest als een tekenfout, en twee diktes tussen twee iconen naast elkaar laat het ene
#: zwaarder wegen dan het andere terwijl ze hetzelfde niveau dragen. Gemeten op de render bij
#: een icoon van 0,72 in -- zie `assets/proeven/09`.
ICOON_PT = 1.5

#: De ondergrens van een icoon in inch. Daaronder lopen de lijnen van 1,5pt in elkaar en is
#: het een vlekje; dan is de streep of het kapitaallabel het betere merkteken.
ICOON_MIN = 0.44

#: Boven dit aantal onderdelen is het geen icoon meer maar een tekening, en dan hoort het in
#: `sfnl-infographic` en niet op een slide naast een kop van 18pt.
ICOON_MAX_DELEN = 12


def _ln_icoon(hue, pt: float) -> str:
    """`<a:ln>` met ronde uiteinden en ronde hoeken -- de zetting van een lijnicoon.

    `lijn_xml()` zet `cap="flat"`, en dat is goed voor een kaartrand en een aslijn: die
    eindigt tegen iets aan. Een icoonlijn eindigt in de lucht, en een vlakke kop maakt daar
    een afgesneden steel van. Vandaar een eigen `<a:ln>` in plaats van een parameter op
    `lijn_xml()`: de rand van een kaart hoort niet rond te worden omdat een icoon dat nodig
    heeft.
    """
    kleur, alpha = _split(hue)
    _geen_grijs_vlak(kleur)
    return (f'<a:ln w="{int(round(pt * 12700))}" cap="rnd">'
            f'<a:solidFill>{_clr(kleur, alpha)}</a:solidFill><a:round/></a:ln>')


def icoon(naam: str, x: float, y: float, d: float, delen, *,
          hue="navy", pt: float = ICOON_PT, raster: int = ICOON_RASTER) -> str:
    """Eén zelf getekend lijnicoon, als groep, op een raster van 24 bij 24 eenheden.

    **Dit is geen iconenbibliotheek en die komt er ook niet.** Je geeft de geometrie, deze
    functie geeft de discipline: één schachtdikte, één hue, geen vulling, ronde uiteinden,
    alles binnen het vierkant, en één groep zodat het icoon als één vorm verschuift. Wat je
    tekent bedenk je per icoon, net als bij `contour()` -- een catalogus zou hier hetzelfde
    doen wat een patroonbibliotheek met de compositie doet.

    `delen` is een lijst van tuples in RASTEREENHEDEN (0 tot 24, y naar beneden):

        ("lijn", x1, y1, x2, y2)                 een rechte lijn
        ("pad", [(x, y), ...])                   een open polylijn
        ("vorm", [(x, y), ...])                  een gesloten omtrek, alleen lijn
        ("cirkel", cx, cy, r)                    een open cirkel
        ("stip", cx, cy, r)                      de enige gevulde vorm die mag
        ("boog", cx, cy, r, vanaf, tot)          graden, 0 is rechts, met de klok mee
        ("rechthoek", x, y, w, h)                 en optioneel een zevende: hoek in eenheden

    Een documenticoon is dus:

        icoon("Doc", 1.0, 3.0, 0.72, [
            ("vorm", [(6, 2), (15, 2), (18, 5), (18, 22), (6, 22)]),
            ("lijn", 15, 2, 15, 5), ("lijn", 15, 5, 18, 5),
            ("lijn", 9, 10, 15, 10), ("lijn", 9, 14, 15, 14), ("lijn", 9, 18, 13, 18),
        ])

    Drie grenzen, en ze weigeren met een reden:

    * onder `ICOON_MIN` (0,44 in) lopen de lijnen in elkaar; dan is een streep of een
      kapitaallabel het betere merkteken
    * boven `ICOON_MAX_DELEN` (12) is het een tekening, en die hoort in `sfnl-infographic`
    * een gevulde vorm anders dan `("stip", ...)` bestaat hier niet: een icoon is lijnwerk
      (§8), en een gevuld icoon concurreert met de dragers op de slide

    Wanneer een icoon zijn plek verdient staat in `vormentaal.md` §14, en dat is de vraag die
    vóór deze functie komt: draagt het icoon informatie die de tekst niet al draagt? Een
    icoon naast elk kopje is decoratie, en decoratie valt onder dezelfde regel als een
    gekleurd vlak dat alleen kleur is -- die gaat eruit (§8).
    """
    if d < ICOON_MIN:
        raise ValueError(
            f"een icoon van {d:.2f} in is te klein: onder {ICOON_MIN} in lopen de lijnen van "
            f"{pt}pt in elkaar en leest het als een vlekje. Maak hem groter, of gebruik een "
            "streep, een punt of een kapitaallabel."
        )
    if len(delen) > ICOON_MAX_DELEN:
        raise ValueError(
            f"{len(delen)} onderdelen is geen icoon meer maar een tekening (max "
            f"{ICOON_MAX_DELEN}). Laat weg wat de betekenis niet draagt, of bouw het als "
            "losse infographic met `sfnl-infographic`."
        )
    u = d / raster                       # inch per rastereenheid
    def px(gx):
        return x + gx * u
    def py(gy):
        return y + gy * u
    ln = _ln_icoon(hue, pt)
    kinderen: list[str] = []
    for deel in delen:
        soort = deel[0]
        if soort == "lijn":
            _, x1, y1, x2, y2 = deel
            kinderen.append(verbind(f"{naam} lijn", (px(x1), py(y1)), (px(x2), py(y2)),
                                    hue, pt).replace(lijn_xml((hue, pt)), ln))
        elif soort in ("pad", "vorm"):
            punten = [(px(a), py(b)) for a, b in deel[1]]
            pad = contour(f"{naam} {soort}", 0, 0, punten, sluit=(soort == "vorm"))
            kinderen.append(pad.replace("<a:ln><a:noFill/></a:ln>", ln))
        elif soort in ("cirkel", "stip"):
            _, cx, cy, r = deel
            vulling = hue if soort == "stip" else None
            vorm = vlak(f"{naam} {soort}", px(cx - r), py(cy - r), 2 * r * u, 2 * r * u,
                        prst="ellipse", vulling=vulling)
            kinderen.append(vorm if soort == "stip"
                            else vorm.replace("<a:ln><a:noFill/></a:ln>", ln))
        elif soort == "boog":
            _, cx, cy, r, vanaf, tot = deel
            kinderen.append(
                vlak(f"{naam} boog", px(cx - r), py(cy - r), 2 * r * u, 2 * r * u,
                     prst="arc", adj={"adj1": int(round(vanaf * 60000)),
                                      "adj2": int(round(tot * 60000))})
                .replace("<a:ln><a:noFill/></a:ln>", ln))
        elif soort == "rechthoek":
            _, gx, gy, gw, gh = deel[:5]
            hoek = deel[5] * u if len(deel) > 5 else None
            kinderen.append(
                vlak(f"{naam} vlak", px(gx), py(gy), gw * u, gh * u, hoek=hoek)
                .replace("<a:ln><a:noFill/></a:ln>", ln))
        else:
            raise ValueError(
                f'onderdeel "{soort}" bestaat niet in een icoon. Kies uit lijn, pad, vorm, '
                "cirkel, stip, boog, rechthoek -- zie de docstring."
            )
    return groep(f"Icoon {naam}", x, y, d, d, kinderen)


def contour(naam: str, x: float, y: float, punten, *, vulling=None, lijn=None,
            sluit: bool = True) -> str:
    """Een eigen vorm (`custGeom`) uit een reeks punten in INCH, zonder XML te typen.

    `punten` zijn absolute inch-coördinaten op de slide, net als bij elke andere functie
    hier; deze functie rekent zelf de omhullende doos en de padcoördinaten uit. Drie punten
    is een driehoek, vijf een gebogen band, en met `sluit=False` en een `lijn` is het een
    open lijnstuk -- een accolade, een knik in een verbinding, een haaks aftakkende leider.

    Dit is de weg naar een vorm die het sjabloon niet kent. Alle discipline geldt onverkort:
    de vulling gaat door `vulling_xml()` en is dus alpha op een volle hue, de lijn door
    `lijn_xml()` en is dus in de hue van de vulling.

    Misplaatst als er een preset is die het al doet: een `pie`, een `chevron`, een `donut` en
    een `blockArc` zijn met `vlak(prst=..., adj=...)` één regel, en een preset schaalt netter
    dan een polygoon die je met de hand hebt uitgezet. Zie `PRESET_ADJ`.
    """
    punten = [(float(a), float(b)) for a, b in punten]
    if len(punten) < 2:
        raise ValueError(
            "een contour heeft minstens twee punten. Eén punt is geen vorm; een rechte lijn "
            "tussen twee punten is `verbind()`, een rechthoek is `vlak()`."
        )
    xs = [p[0] for p in punten]
    ys = [p[1] for p in punten]
    x0, y0 = min(xs), min(ys)
    w = max(max(xs) - x0, 1e-4)
    h = max(max(ys) - y0, 1e-4)
    stappen = "".join(
        f'<a:{"moveTo" if i == 0 else "lnTo"}><a:pt x="{emu(px - x0)}" '
        f'y="{emu(py - y0)}"/></a:{"moveTo" if i == 0 else "lnTo"}>'
        for i, (px, py) in enumerate(punten)
    )
    if sluit:
        stappen += "<a:close/>"
    geom = (f'<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/>'
            f'<a:rect l="0" t="0" r="r" b="b"/>'
            f'<a:pathLst><a:path w="{emu(w)}" h="{emu(h)}">{stappen}</a:path>'
            f'</a:pathLst></a:custGeom>')
    _ids[0] += 1
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{_ids[0]}" name="{naam}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr>'
            f'<a:xfrm><a:off x="{emu(x0 + x)}" y="{emu(y0 + y)}"/>'
            f'<a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>{geom}'
            f'{vulling_xml(vulling)}{lijn_xml(lijn)}</p:spPr></p:sp>')


def groep(naam: str, x: float, y: float, w: float, h: float, kinderen: list[str], *,
          van: tuple[float, float, float, float] | None = None) -> str:
    """Groepeer verwante vormen, en verplaats of schaal ze als één.

    Zonder `van` zijn `chOff`/`chExt` gelijk aan `off`/`ext`: er is niets te schalen en je
    blijft in slidecoördinaten rekenen. Dat is de default en meestal wat je wil.

    Met `van=(x, y, w, h)` zeg je in welke doos de kinderen getekend ZIJN, terwijl
    `x, y, w, h` zegt waar de groep terecht KOMT. Verschilt de positie, dan schuift de groep;
    verschilt de maat, dan schaalt hij -- en dan schaalt de tekst erin niet mee, dus doe dat
    alleen met een schema van vormen en lijnen. Waarvoor het bestaat: een merkteken één keer
    op zijn eigen maat uitrekenen en het daarna neerzetten waar de compositie het wil, zonder
    elke coördinaat opnieuw te rekenen.
    """
    _ids[0] += 1
    kx, ky, kw, kh = van if van else (x, y, w, h)
    return (f'<p:grpSp><p:nvGrpSpPr><p:cNvPr id="{_ids[0]}" name="{naam}"/>'
            f'<p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr>'
            f'<a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/>'
            f'<a:ext cx="{emu(w)}" cy="{emu(h)}"/>'
            f'<a:chOff x="{emu(kx)}" y="{emu(ky)}"/>'
            f'<a:chExt cx="{emu(kw)}" cy="{emu(kh)}"/></a:xfrm></p:grpSpPr>'
            f'{"".join(kinderen)}</p:grpSp>')


# ---------------------------------------------------------------- op schaal

def accolade(naam: str, x: float, y: float, w: float, h: float, hue="oranje", *,
             kant: str = "rechts", punt_y: float | None = None, pt: float = 2) -> str:
    """Een accolade die een groep vormen aan één uitkomst knoopt.

    Dit is het merkteken met het hoogste rendement uit `reference/merktekens.md`, en het is
    geoogst en niet bedacht: de effectenkaart in het MDT-eindrapport gebruikt hem acht keer,
    tussen elke kolom van de resultatenketen. Dat is waarom die slide met dertig blokken
    leesbaar blijft. Hij zegt "deze vier dingen leiden samen tot dat ene" met één haak; met
    pijlen was het een kabelbos geworden.

    `kant` is de kant waar de punt naar wijst: `"rechts"` haakt een groep links in en wijst
    naar het blok rechts (`prst="rightBrace"`), `"links"` andersom.

    **`punt_y` is de reden dat deze functie bestaat.** Het handvat `adj2` van een brace zet de
    punt als duizendste van de eigen hoogte, en zonder eigen waarde staat hij op 50 procent:
    precies in het midden, en dus zelden bij de vorm waar hij naar moet wijzen. Geef de
    absolute y van het midden van de doelvorm, dan rekent deze functie het handvat terug. Ligt
    de punt buiten de haak, dan is dat een fout in de compositie en niet in de waarde: de haak
    moet de groep omvatten die hij bundelt, en de doelvorm hoort daar tegenover te staan.

        v.append(accolade("Haak 1", 5.90, 1.95, 0.22, 1.80, "oranje",
                          punt_y=anker(doel, "m")[1]))

    Een brace heeft geen vulling; hij is lijnwerk (§8), dus de hue zit in de lijn. Op minder
    dan 1,5pt verdwijnt hij naast een gevuld blok.
    """
    if kant not in {"links", "rechts"}:
        raise ValueError('kant is "links" of "rechts", niet ' + repr(kant))
    if h <= 0:
        raise ValueError("een accolade zonder hoogte bundelt niets")
    frac = 50000
    if punt_y is not None:
        rel = (punt_y - y) / h
        if not 0.0 <= rel <= 1.0:
            raise ValueError(
                f"punt_y={punt_y:.2f} ligt buiten de haak ({y:.2f} tot {y + h:.2f}). De haak "
                "hoort de groep te omvatten die hij bundelt, en de doelvorm staat ernaast — "
                "vergroot de haak of verplaats het doel."
            )
        frac = int(round(rel * 100000))
    prst = "rightBrace" if kant == "rechts" else "leftBrace"
    return vlak(naam, x, y, w, h, prst=prst, lijn=(hue, pt),
                adj={"adj1": 8333, "adj2": frac})


#: Extensies die het sjabloon al als Default in `[Content_Types].xml` heeft staan. Wat hier
#: niet in staat, voegt `media()` toe -- en `jpg` staat er inderdaad niet in, alleen `jpeg`,
#: dus een foto die `.jpg` heet maakt zonder die stap een deck dat PowerPoint weigert.
BEELDTYPES = {"png": "image/png", "jpeg": "image/jpeg", "jpg": "image/jpeg",
              "gif": "image/gif", "emf": "image/x-emf", "svg": "image/svg+xml",
              "tiff": "image/tiff", "webp": "image/webp"}


def media(slide_pad: str | Path, bestand: str | Path) -> str:
    """Zet een afbeelding in de uitgepakte boom en geef de `rId` terug.

    Dit is de ontbrekende schakel naar een beeld, en het gat dat hij dicht is groot: drie
    merktekens uit `reference/merktekens.md` lopen erop vast — het ronde portret op de
    teamslide, de partnerlogo's op een mede-merk-cover, en het verkleinde eindproduct als
    artefactvoorbeeld. Het handmatige alternatief was een plaatje ná de bouw in PowerPoint
    erin slepen, en dan is het deck niet meer herbouwbaar; dat is precies de eigenschap waar
    deze plugin op staat.

    Drie dingen gebeuren hier, en alle drie stil misgaan als je ze zelf doet:

    1. Het bestand wordt naar `ppt/media/` gekopieerd, met een naam die niet botst.
    2. Er komt een relationship in `ppt/slides/_rels/slideN.xml.rels`, met een `rId` die nog
       vrij is. Een tweede aanroep met hetzelfde bestand hergebruikt de bestaande `rId` in
       plaats van een tweede kopie te maken -- de bouw is herhaalbaar.
    3. De extensie komt als `Default` in `[Content_Types].xml` als hij er nog niet staat.
       `jpeg` staat er wel en `jpg` niet, en zonder die regel weigert PowerPoint het bestand.
    """
    slide = Path(slide_pad)
    src = Path(bestand)
    if not src.is_file():
        raise SystemExit(f"beeld niet gevonden: {src}")
    ext = src.suffix.lstrip(".").lower()
    if ext not in BEELDTYPES:
        raise SystemExit(
            f"onbekend beeldtype .{ext}. Bekend: {', '.join(sorted(BEELDTYPES))}"
        )
    ppt = slide.parent.parent
    if ppt.name != "ppt":
        raise SystemExit(
            f"{slide} ziet niet uit als ppt/slides/slideN.xml — media() werkt op de "
            "uitgepakte boom, niet op een ingepakt deck"
        )
    wortel = ppt.parent
    mediadir = ppt / "media"
    mediadir.mkdir(exist_ok=True)

    rels = slide.parent / "_rels" / (slide.name + ".rels")
    if not rels.is_file():
        raise SystemExit(f"geen rels naast {slide.name}; is dit een echte slide?")
    xml = rels.read_text(encoding="utf-8")

    doel = None
    for kandidaat in sorted(mediadir.iterdir()):
        if kandidaat.is_file() and kandidaat.read_bytes() == src.read_bytes():
            doel = kandidaat
            break
    if doel is None:
        n = 1
        while (mediadir / f"beeld{n}.{ext}").exists():
            n += 1
        doel = mediadir / f"beeld{n}.{ext}"
        doel.write_bytes(src.read_bytes())

    bestaand = re.search(
        r'Id="(rId\d+)"[^>]*Target="\.\./media/' + re.escape(doel.name) + r'"', xml)
    if bestaand:
        return bestaand.group(1)

    gebruikt = {int(m) for m in re.findall(r'Id="rId(\d+)"', xml)}
    rid = f"rId{max(gebruikt, default=0) + 1}"
    rel = (f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/'
           f'officeDocument/2006/relationships/image" Target="../media/{doel.name}"/>')
    rels.write_text(xml.replace("</Relationships>", rel + "</Relationships>"),
                    encoding="utf-8")

    ct = wortel / "[Content_Types].xml"
    if ct.is_file():
        ctxml = ct.read_text(encoding="utf-8")
        if f'Extension="{ext}"' not in ctxml:
            regel = f'<Default Extension="{ext}" ContentType="{BEELDTYPES[ext]}"/>'
            ct.write_text(ctxml.replace("<Types ", "<Types ", 1).replace(
                "<Default", regel + "<Default", 1), encoding="utf-8")
    return rid


def beeld(naam: str, x: float, y: float, w: float, h: float, rid: str, *,
          prst: str = "rect", hoek: float | None = None, lijn=None,
          rot: float | None = None, uitsnede: tuple[float, float, float, float] | None = None
          ) -> str:
    """Een afbeelding als vorm: `<p:pic>` met een `blipFill` in een presetgeometrie.

    Omdat de geometrie vrij is, is een foto in een cirkel één aanroep: `prst="ellipse"` met
    `w == h` geeft het ronde portret van de teamslide. `hoek` doet hetzelfde voor een
    afgeronde hoek als bij `vlak()`, met dezelfde absolute radius in inch.

    `uitsnede` is `(links, boven, rechts, onder)` als fractie van 0 tot 1, en het is de reden
    dat een rond portret niet uitgerekt staat: een `blipFill` vult de vorm, dus een liggende
    foto in een vierkante cirkel wordt platgedrukt tenzij je links en rechts wegsnijdt.
    `uitsnede_vullend()` rekent die waarden voor je uit.
    """
    _ids[0] += 1
    if hoek:
        prst = "roundRect"
        geom = (f'<a:prstGeom prst="roundRect">'
                f'{_avlst({"adj": adj_van(hoek, w, h)})}</a:prstGeom>')
    else:
        geom = f'<a:prstGeom prst="{prst}"><a:avLst/></a:prstGeom>'
    if uitsnede:
        l, tb, r, b = (int(round(v * 100000)) for v in uitsnede)
        rect = f'<a:srcRect l="{l}" t="{tb}" r="{r}" b="{b}"/>'
    else:
        rect = ""
    draai = f' rot="{int(round(rot * 60000)) % 21600000}"' if rot else ""
    return (f'<p:pic><p:nvPicPr><p:cNvPr id="{_ids[0]}" name="{naam}"/>'
            f'<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/>'
            f'</p:nvPicPr><p:blipFill><a:blip r:embed="{rid}"/>{rect}'
            f'<a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr>'
            f'<a:xfrm{draai}><a:off x="{emu(x)}" y="{emu(y)}"/>'
            f'<a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>{geom}'
            f'{lijn_xml(lijn)}</p:spPr></p:pic>')


def uitsnede_vullend(bestand: str | Path, w: float, h: float
                     ) -> tuple[float, float, float, float]:
    """De `uitsnede` die een beeld de doos laat vullen zonder te vervormen.

    Snijdt symmetrisch van de lange kant af, net als "vullen" in PowerPoint. Zonder Pillow of
    zonder leesbare maten geeft hij `(0, 0, 0, 0)` terug: dan vult het beeld de doos wél maar
    is het uitgerekt, en dat zie je op de render.
    """
    try:
        from PIL import Image
        with Image.open(bestand) as im:
            bw, bh = im.size
    except Exception:
        return (0.0, 0.0, 0.0, 0.0)
    if not bw or not bh:
        return (0.0, 0.0, 0.0, 0.0)
    doel = w / h
    bron = bw / bh
    if abs(bron - doel) < 1e-6:
        return (0.0, 0.0, 0.0, 0.0)
    if bron > doel:
        weg = (1 - doel / bron) / 2
        return (weg, 0.0, weg, 0.0)
    weg = (1 - bron / doel) / 2
    return (0.0, weg, 0.0, weg)


def foto(slide_pad: str | Path, naam: str, x: float, y: float, w: float, h: float,
         bestand: str | Path, *, prst: str = "rect", hoek: float | None = None,
         lijn=None, vullend: bool = True) -> str:
    """`media()` en `beeld()` in één aanroep, met de uitsnede al gerekend.

    Dit is de weg die je in de praktijk neemt:

        v.append(foto(slide, "Portret Liza", 0.48, 2.20, 1.60, 1.60,
                      "foto/liza.jpg", prst="ellipse"))
    """
    rid = media(slide_pad, bestand)
    snee = uitsnede_vullend(bestand, w, h) if vullend else None
    return beeld(naam, x, y, w, h, rid, prst=prst, hoek=hoek, lijn=lijn, uitsnede=snee)


def schaal(x: float, w: float, lo: float, hi: float):
    """Een schaal: geeft een functie terug die een waarde omzet naar een x (of y) in inch.

    Dit is de formule uit §7 -- `0,48 + 12,52 x (t - t0) / (t1 - t0)` -- als functie, en dat
    is het enige rekenwerk in deze laag waar het oog de fout niet kan repareren. Draagt
    afstand informatie, dan staat hij op schaal: een tijdlijn, een as, een verdeling, de twee
    punten van een dumbbell. Vier banden onder elkaar zijn geen tijdlijn, want dan staat elke
    stap even ver van de vorige.

        px = schaal(ZONE["x"], ZONE["w"], 2024, 2027)
        px(2025.5)          # -> inch

    Werkt ook verticaal: geef `y` en `h` in plaats van `x` en `w`. En omgekeerd, met `hi < lo`
    of een negatieve `w`, loopt de schaal andersom -- dat is hoe een y-as van boven naar
    beneden telt.

    Buiten `lo`..`hi` extrapoleert hij gewoon door; dat is bewust, want een punt dat net
    buiten de as valt moet je op de render zien en niet stil op de rand vinden. Wat je
    daarvoor gebruikt is `binnen()`.
    """
    if hi == lo:
        raise ValueError(
            "een schaal met lo == hi heeft geen bereik: elke waarde zou op dezelfde plek "
            "staan. Geef het werkelijke bereik van je as, ook als er maar één waarde in valt."
        )
    return lambda v: round(x + w * (float(v) - lo) / (hi - lo), 4)


def binnen(x: float, w: float, *, links: float | None = None,
           rechts: float | None = None) -> float:
    """Schuif een blok van `w` breed zó dat het binnen de zone blijft, en geef zijn x.

    Waarvoor dit bestaat: op alle vier de reconstructies zat het echte werk niet in de posities
    maar in de aslabels. Een label van 2,3 in dat bij zijn tik op 11,90 begint, loopt 1,2 in
    buiten de slide -- op de render zichtbaar als een afgekapt woord, en dat kostte twee
    ronden. Deze functie klemt de x, en dan hoort de tekst rechts uitgelijnd (`algn="r"`),
    zodat hij nog steeds bij zijn tik eindigt.

    Klemmen verandert de POSITIE VAN HET LABEL en nooit de positie van het punt waar het bij
    hoort: dat punt staat op schaal en blijft daar (§7). Botsen twee labels, dan wijken de
    teksten uit naar twee rijen -- nooit de posities.
    """
    links = ZONE["x"] if links is None else links
    rechts = ZONE["right"] if rechts is None else rechts
    if w > rechts - links:
        raise ValueError(
            f"een blok van {w} in past niet in een zone van {round(rechts - links, 2)} in: "
            "klemmen lost dat niet op. Kort het label in, zet het op twee regels, of geef het "
            "een kleinere maat."
        )
    return round(min(max(x, links), rechts - w), 4)


# ---------------------------------------------------------------- meten

def regelhoogte(pt: float) -> float:
    """Regelhoogte in inch, nagemeten op de PowerPoint-render: 1.34 x pt / 72.

    Niet 1.12. De 112% uit `para()` vermenigvuldigt de NATUURLIJKE regelhoogte van het
    font, en die is bij Lato en Montserrat ongeveer 1,2 em -- samen 1,12 x 1,2 = 1,34.
    De oude waarde 1.12 mat elke tekst ~20% te krap, en dat is de oorzaak van drie
    afzonderlijke overloopdefecten in twee validatiedecks: een paneel waarvan de
    laatste regel achter de bronregel verdween, een afwegingsblok dat achter een band
    wegviel, en een kaartrij die uit de zone liep. Gemeten op de render: 16pt Lato op
    112% zet op een pitch van 0,30 in, en 0,30 x 72 / 16 = 1,35.
    """
    return 1.34 * pt / 72.0


def _meet_breedte(tekst_: str, font: str, pt: float) -> float | None:
    """Werkelijke tekstbreedte in inch, als het font te vinden is."""
    try:
        from PIL import ImageFont

        from _deck import find_font_file
        path = find_font_file(font)
        if not path:
            return None
        f = ImageFont.truetype(str(path), size=200)
        return f.getlength(tekst_) / 200.0 * pt / 72.0
    except Exception:
        return None


def regels_nodig(tekst_: str, breedte: float, pt: float,
                 font: str = "Lato Light") -> int:
    """Hoeveel regels deze tekst nodig heeft in een vak van `breedte` inch BRUIKBAAR.

    Meet met het echte font als dat gevonden wordt; anders met de vuistregel van ongeveer
    12 tekens per inch op 12pt, dus `144 / pt` tekens per inch. Woorden worden niet
    afgebroken, dus dit is een greedy wrap.
    """
    woorden = (tekst_ or "").split()
    if not woorden:
        return 0
    per_inch = _meet_breedte("n" * 40, font, pt)
    if per_inch:
        def breed(s):
            return _meet_breedte(s, font, pt) or len(s) * pt / 144.0
    else:
        def breed(s):
            return len(s) * pt / 144.0
    regels, huidig = 1, ""
    for w in woorden:
        kandidaat = (huidig + " " + w).strip()
        if breed(kandidaat) <= breedte or not huidig:
            huidig = kandidaat
        else:
            regels += 1
            huidig = w
    return regels


def hoogte_van(paras: list[tuple[str, float, str]], breedte: float, *,
               insets=INSETS_GEVULD, alinea_gap: float = 0.08) -> float:
    """Hoe hoog een vak moet zijn voor deze inhoud, in inch.

    `paras` is een lijst van `(tekst, puntgrootte, font)`. De uitkomst is de som van de
    regelhoogtes plus de alineagaten plus tIns en bIns, en er komt NIETS bovenop -- de
    marge van het kaartrecept ís de inset.

    Dit is de functie die 'een blok is zo hoog als zijn inhoud' uitvoerbaar maakt. Zonder
    meten wordt het een intentie, en dan krijg je vier kaarten waarvan de onderste helft
    leeg gekleurd vlak is.

    De meting is strak en PowerPoint zet nét ruimer, ook met de gecorrigeerde regelhoogte van
    `regelhoogte()`: alinearuimte en de descender van de laatste regel zitten er niet in.
    Nagemeten gevolg: een paneel met drie alinea's op precies deze hoogte liet zijn laatste
    regel onder de rand uitsteken. Geef een gevuld blok met meerdere alinea's daarom ~0,2 in
    boven de meting, en laat de render oordelen.

    Diezelfde strakheid werkt de andere kant op bij `vulgraad()`: de uitkomst ziet er voller
    uit dan het getal zegt, dus een middelmatige vulgraad is een gat. Lees de norm daar.
    """
    l, r, t, b = insets
    bruikbaar = breedte - l - r
    totaal = t + b
    for i, (txt, pt, font) in enumerate(paras):
        totaal += regels_nodig(txt, bruikbaar, pt, font) * regelhoogte(pt)
        if i:
            totaal += alinea_gap
    return round(totaal, 3)


def gat_onder(paras: list[tuple[str, float, str]], breedte: float, hoogte: float,
              *, insets=INSETS_GEVULD) -> float:
    """De restruimte onder de tekst in INCH. Dit is het getal dat de kijker ziet.

    Een verhouding is schaalblind: 0,80 op een blok van 1,2 in is 0,24 in lucht en valt niet
    op, 0,80 op een kolom van 5 in is een vol centimeter dood gekleurd vlak. Meet daarom
    altijd ook absoluut, en houd het gat onder 0,25 in.
    """
    return round(hoogte - hoogte_van(paras, breedte, insets=insets), 3) if hoogte else 0.0


def vulgraad(paras: list[tuple[str, float, str]], breedte: float, hoogte: float,
             *, insets=INSETS_GEVULD) -> float:
    """Welk deel van het vak de tekst werkelijk vult.

    **De norm is 0,9, niet 0,5.** Deze meting rekent strakker dan de renderer zet -- ze telt
    kale regelhoogtes, terwijl PowerPoint fontmetriek, alinearuimte en de descender van de
    laatste regel meeneemt. De uitkomst leest dus altijd voller dan het getal suggereert, en
    de val is om een middelmatig getal als voldoende te lezen. Nagemeten: een kolomblok dat
    hier 0,78 gaf, liet op de render een duidelijk gat onderin zien.

    De grens is tweeledig, want een verhouding alleen is schaalblind:

    * vulgraad >= 0,9, EN
    * `gat_onder(...)` <= 0,25 in

    Zakt een van de twee, dan is het antwoord niet een iets lager blok met een gat eronder,
    en ook niet een hoger blok. Het is: meer inhoud, grotere letters, een andere compositie,
    of het blok inkorten en de slide met een ander element afsluiten -- een drager met een
    getal, een afwegingsregel, een tweede sectie. Ruimte tussen de blokken is compositie,
    ruimte ónderin een blok is een gat.

    Het getal is een ondergrens, geen bewijs. Boven 0,9 kijk je nog steeds naar de render.
    """
    return round(hoogte_van(paras, breedte, insets=insets) / hoogte, 3) if hoogte else 0.0


# ---------------------------------------------------------------- maten per rol

@dataclass
class Deck:
    """De maten per rol, één keer per deck vastgelegd.

    Vier getallen — drager, kop, body, voetnoot — en elke slide gebruikt die vier. Zonder dit
    krijg je wat de eerste V2-deck kreeg: vier bodymaten en drie sluitregelmaten over vier
    slides, waardoor de zetting per slide verspringt zonder dat iemand kan zien waarom.

    `label` is de vijfde en is geen keuze: 14pt is het kapitaallabel (§2), dezelfde maat als de
    body maar in Montserrat SemiBold en in kapitalen. Er is geen veld voor een sluitregel, en
    dat is opzet: een sluitregel staat op bodymaat, want een eigen maat voor de laatste regel is
    het defect waar dit vak tegen bestaat.

    `display` is de maat van de drager: het getal, de verhouding of het kernbegrip dat de
    slide draagt. Hij staat tussen 28 en 40pt. Onder 28pt springt er niets uit -- de geërfde
    titel van 24pt telt niet mee, want die staat op elke slide en onderscheidt dus niets.
    Boven 40pt neemt de drager de slide over, en dat is precies waar het misging: een
    aandachtstrekker van 40pt op elke slide is geen aandacht meer. Zet hem op ten hoogste
    één slide op drie, in Montserrat Light, via `drager()`.
    """

    body: float = 14
    kop: float = 18
    label: float = 14
    display: float = 32
    voetnoot: float = 11
    hoek: float | None = None          # None = rechte hoeken, deckbreed
    rol_kleur: dict = field(default_factory=dict)

    def __post_init__(self):
        if not DRAGER_VLOER <= self.display <= DRAGER_PLAFOND:
            raise ValueError(
                f"display={self.display}pt valt buiten de band {DRAGER_VLOER:.0f} tot "
                f"{DRAGER_PLAFOND:.0f}pt. Daaronder springt er niets uit; daarboven staat er "
                "een aandachtstrekker die de slide overneemt."
            )

    def kleur(self, rol: str) -> str:
        """De hue van een rol, deckbreed. Eén keer toewijzen, daarna niet meer beslissen."""
        return self.rol_kleur.setdefault(rol, "navy")


# ---------------------------------------------------------------- wegschrijven

def write(slide_pad: str | Path, vormen: list[str]) -> None:
    pad = Path(slide_pad)
    xml = pad.read_text(encoding="utf-8")
    if "</p:spTree>" not in xml:
        raise SystemExit(f"geen spTree in {pad}")
    pad.write_text(xml.replace("</p:spTree>", "".join(vormen) + "</p:spTree>"),
                   encoding="utf-8")
    print(f"{pad.name}: {len(vormen)} vormen")
