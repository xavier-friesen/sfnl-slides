"""Primitieven om eigen vormen in de contentzone te schrijven, en om ze te meten.

Dit is GEEN patroonbibliotheek. Er zit geen kaartenrij in, geen stroomschema, geen tegel en
geen band. Wat er wel in zit: de dingen die je nodig hebt om zélf een compositie te tekenen,
correct en zonder de valkuilen, plus rekenwerk om te weten hoe hoog een blok moet zijn
vóórdat je het rendert.

De grens is: dit bestand levert een `vlak`, een `lijn`, een `run`, een `raster` en een
`hoogte`. Wat je daarmee bouwt is jouw beslissing, elke slide opnieuw. Zodra hier een functie
zou staan die drie kaarten op vaste baselines neerzet, is het compose.py geworden en dan gaat
de vormgeving weer op de automaat.

Waarom dit bestaat
------------------
De eerste deck die met sfnl-slides gebouwd werd, had op vier contentslides 31 gevulde
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

    d = Deck(body=16, label=14, display=32)        # maten per rol, één keer per deck
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
    "wit": "lt2", "zwartblauw": "dk1",
}

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
OP_VOL = {"navy": "wit", "royal": "wit",
          "oranje": "navy", "grapefruit": "navy", "sky": "navy", "emerald": "navy"}

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
    return OP_VOL.get(hue, "navy")


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
    slot = HUE.get(hue, hue)
    inner = f'<a:alpha val="{int(alpha)}"/>' if alpha else ""
    return f'<a:schemeClr val="{slot}">{inner}</a:schemeClr>' if inner else \
           f'<a:schemeClr val="{slot}"/>'


def vulling_xml(v) -> str:
    """`"emerald"` is vol, `("emerald", 9000)` is een container, `"container:emerald"`
    pakt de gekalibreerde alpha, `None` is geen vulling."""
    if v is None:
        return "<a:noFill/>"
    if isinstance(v, str) and v.startswith("container:"):
        hue = v.split(":", 1)[1]
        return f"<a:solidFill>{_clr(hue, CONTAINER_ALPHA.get(hue, 10000))}</a:solidFill>"
    hue, alpha = _split(v)
    return f"<a:solidFill>{_clr(hue, alpha)}</a:solidFill>"


def lijn_xml(l) -> str:
    """`("emerald", 1)` is een haarlijn van 1pt in emerald. `None` is geen lijn.

    De lijn heeft dezelfde hue als de vulling. Een lijn in een ándere hue -- grijs om wit,
    navy om een getint vlak -- is de Word-tabellook, en dat is het enige wat hier verboden
    is. In de winnende deck staat drie keer op één slide een 1pt lijn in exact de hue van
    de vulling; dat is wat een vlak van 9% nog als kaart laat lezen in plaats van als vlek.
    """
    if l is None:
        return "<a:ln><a:noFill/></a:ln>"
    hue, pt = (list(l) + [1])[:2]
    return (f'<a:ln w="{int(round(pt * 12700))}" cap="flat">'
            f"<a:solidFill>{_clr(hue)}</a:solidFill></a:ln>")


# ---------------------------------------------------------------- tekst

#: De grijze regel voor een bron of een eenheid: navy op 70% dekking. Simpeler dan het
#: lumMod-grijs van V1 en het is wat de winnende decks gebruiken.
GRIJS = ("navy", 70000)


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
        raise ValueError("cursief is in deze huisstijl niet toegestaan")
    if font.strip().lower() == TITELFONT.lower():
        raise ValueError(
            f"{TITELFONT} schrijf je nooit zelf: dat is de titelletter en die erf je uit de "
            f"layout. Op de slide is de letter licht -- {DRAGERFONT} voor een drager of een "
            "kop, Lato Light voor lopende tekst."
        )
    b = ' b="1"' if vet else ""
    s = f' spc="{spc}"' if spc is not None else ""
    c = ' cap="all"' if caps else ""
    # De eenheid blijft bij het getal (voice.md): een gewone spatie na het euroteken
    # laat "€" op de vorige regel achter zodra de regel daar breekt. Vastgezet met een
    # non-breaking space, zodat de regel dat nooit kan.
    tekst = tekst.replace("€ ", "€ ")
    esc = (tekst.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    hue, alpha = _split(kleur)
    return (f'<a:r><a:rPr lang="nl-NL" sz="{int(round(pt * 100))}"{b}{s}{c} dirty="0">'
            f'<a:solidFill>{_clr(hue, alpha)}</a:solidFill>'
            f'<a:latin typeface="{font}"/></a:rPr>'
            f'<a:t>{esc}</a:t></a:r>')
    # Let op: GEEN xml:space="preserve" op <a:t>. Dat is WordprocessingML; in DrawingML
    # keurt het schema het af. Voor- en achterloopruimte blijft in DrawingML gewoon staan.


def label(tekst: str, pt: float = 14, kleur: str = "navy") -> str:
    """Kapitaallabel in Montserrat SemiBold met de juiste spatiëring."""
    return run(tekst, "Montserrat SemiBold", pt, kleur,
               spc=150 if pt <= 13 else 100, caps=True)


def drager(tekst: str, pt: float, kleur: str = "navy", *, spc: int | None = None) -> str:
    """De drager: het getal, de verhouding of het kernbegrip dat de slide draagt.

    Altijd Montserrat Light, en dat is het punt. Een getal van 32pt in een licht gewicht
    springt er even goed uit als hetzelfde getal in een vet gewicht, maar het schreeuwt niet
    mee met de titel erboven -- en de titel is de enige plek waar Gotham Bold staat.

    De maat moet in de band vallen: onder 28pt is er geen drager, boven 40pt is hij luider
    dan de boodschap. Gebruik dit ten hoogste op één slide op drie; op de andere slides is
    de drager gewicht en kleur (18pt SemiBold in de hue van zijn categorie) of de compositie
    zelf.
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


def vlak(naam: str, x: float, y: float, w: float, h: float, *,
         prst: str = "rect", vulling=None, lijn=None, hoek: float | None = None,
         tekst: list[str] | None = None, insets=None, anchor: str = "t") -> str:
    """Eén `<p:sp>`.

    `hoek` is de hoekradius in INCH, niet in procenten. Zonder deze parameter krijgt een
    `roundRect` PowerPoints default van 16,67% van de korte zijde, en dan wordt een blok van
    1 in hoog een pil terwijl een blok van 2,5 in een nette kaart is -- vier verschillende
    radii in één deck zonder dat iemand er iets aan koos. Geef je `hoek`, dan wordt `prst`
    automatisch `roundRect` en rekent dit de `adj` per vorm terug naar diezelfde absolute
    radius. In de winnende decks staat de adj op 4000 tot 6000, wat bij die maten neerkomt
    op ongeveer 0,08 tot 0,12 in.
    """
    _ids[0] += 1
    if hoek:
        prst = "roundRect"
        adj = max(0, min(50000, int(round(100000 * hoek / min(w, h)))))
        geom = (f'<a:prstGeom prst="roundRect"><a:avLst>'
                f'<a:gd name="adj" fmla="val {adj}"/></a:avLst></a:prstGeom>')
    else:
        geom = f'<a:prstGeom prst="{prst}"><a:avLst/></a:prstGeom>'
    if insets is None:
        insets = INSETS_GEVULD if vulling is not None else INSETS_KAAL
    body = tekstvak(tekst, insets=insets, anchor=anchor) if tekst else ""
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{_ids[0]}" name="{naam}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr>'
            f'<a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/>'
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


def streep(naam: str, x: float, y: float, w: float, hue: str = "navy",
           pt: float = 1.0) -> str:
    """Een horizontale lijn. Een streep onder een label of tussen twee blokken scheidt
    lichter dan een gevuld vlak, en dat register ontbreekt zodra je alleen vlakken hebt."""
    _ids[0] += 1
    return (f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{_ids[0]}" name="{naam}"/>'
            f'<p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr><p:spPr>'
            f'<a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/>'
            f'<a:ext cx="{emu(w)}" cy="0"/></a:xfrm>'
            f'<a:prstGeom prst="line"><a:avLst/></a:prstGeom>'
            f'<a:ln w="{int(round(pt * 12700))}" cap="flat">'
            f'<a:solidFill>{_clr(hue)}</a:solidFill></a:ln></p:spPr>'
            f'<p:style><a:lnRef idx="1"><a:schemeClr val="dk2"/></a:lnRef>'
            f'<a:fillRef idx="0"><a:schemeClr val="dk2"/></a:fillRef>'
            f'<a:effectRef idx="0"><a:schemeClr val="dk2"/></a:effectRef>'
            f'<a:fontRef idx="minor"><a:schemeClr val="lt1"/></a:fontRef></p:style>'
            f'</p:cxnSp>')


def groep(naam: str, x: float, y: float, w: float, h: float, kinderen: list[str]) -> str:
    """Groepeer verwante vormen. `chOff` gelijk aan `off` en `chExt` gelijk aan `ext`, dan
    is er niets te schalen en blijf je in slidecoördinaten rekenen."""
    _ids[0] += 1
    return (f'<p:grpSp><p:nvGrpSpPr><p:cNvPr id="{_ids[0]}" name="{naam}"/>'
            f'<p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr>'
            f'<a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/>'
            f'<a:ext cx="{emu(w)}" cy="{emu(h)}"/>'
            f'<a:chOff x="{emu(x)}" y="{emu(y)}"/>'
            f'<a:chExt cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm></p:grpSpPr>'
            f'{"".join(kinderen)}</p:grpSp>')


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

    Vier getallen, en elke slide gebruikt die vier. Zonder dit krijg je wat de eerste
    V2-deck kreeg: vier bodymaten en drie sluitregelmaten over vier slides, waardoor de
    zetting per slide verspringt zonder dat iemand kan zien waarom.

    `display` is de maat van de drager: het getal, de verhouding of het kernbegrip dat de
    slide draagt. Hij staat tussen 28 en 40pt. Onder 28pt springt er niets uit -- de geërfde
    titel van 24pt telt niet mee, want die staat op elke slide en onderscheidt dus niets.
    Boven 40pt neemt de drager de slide over, en dat is precies waar het misging: een
    aandachtstrekker van 40pt op elke slide is geen aandacht meer. Zet hem op ten hoogste
    één slide op drie, in Montserrat Light, via `drager()`.
    """

    body: float = 16
    label: float = 14
    sluit: float = 15
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
