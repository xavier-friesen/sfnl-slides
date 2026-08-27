"""Wireframes om een visueel concept te laten zien vóórdat er iets gebouwd wordt.

Een schets is geen ontwerp. Er staat geen echte tekst in, geen accentkleur en geen getal --
alleen de meetkunde en de rol die erin komt. Dat is het punt: de gebruiker beoordeelt de
plattegrond en niet de opmaak, en jij hoeft geen infographic te bouwen om te weten of de
richting klopt.

Drie schetsen kosten ongeveer een tiende van één gebouwde infographic. Dat is de hele reden
dat dit bestand bestaat.

TWEE ROUTES, EN DE EERSTE IS DE GEWONE
--------------------------------------
`schets_vrij()` schetst een **figuur**: een vorm waarin een meting een coördinaat, een
lengte, een dikte of een hoek bepaalt. Vijfenveertig van de zesenveertig vormen in het
woordenboek zijn zo'n figuur, dus dit is de route die je bijna altijd nodig hebt.

`schets()` met `Rij` en `Cel` schetst een **rooster**: rijen en kolommen dozen. Dat is één
plattegrond van de vele, bruikbaar voor rollen naast elkaar of een set kaarten, en het is de
enige die deze module ooit kon tekenen. Daardoor kwamen er drie roosters uit een brainstorm
die met een sankey, een naaf en een helling begon -- de vorm werd stilzwijgend platgeslagen
tot dozen omdat de schetslaag niets anders kon. Vandaar de figuurhelpers hieronder.

**Ten hoogste één van je drie schetsen is een rooster.** Overleefden er figuren de vormtoets,
dan schets je die als figuur; anders kiest de gebruiker tussen drie keer hetzelfde beeld.

Figuur schetsen
---------------
Zes helpers, één per meetkundig archetype, plus alles wat je zelf tekent met `svg.py`. Ze
geven allemaal een lijst `Vorm` terug, dus je plakt ze achter elkaar:

    from schets import as_op_schaal, rol, schets_vrij, staven, stroom
    from svg import CANVAS

    c = CANVAS["breed"]
    v  = as_op_schaal(150, [0, 9, 21, 33], 0, 36, c=c)        # tijdlijn: x is de datum
    v += staven(360, 40, 240, [1.0, 0.62, 0.31, 0.18])        # rangschikking: lengte is de waarde
    v += [rol("drager", 30, 230, 200), rol("sluitregel", 30, 268, 500)]
    schets_vrij("uitvoer/concept-a.svg", c, "A — tijdlijn op schaal", v)

De helpers, en de rechthoekige fout die elk van ze vervangt:

    as_op_schaal   afstand is de informatie          i.p.v. vier gelijke banden
    staven         lengte is de informatie           i.p.v. een rij getallen in kaarten
    stroom         dikte is de informatie            i.p.v. pijlen tussen dozen
    naaf           middelpunt en omloop zijn de rol  i.p.v. een rij kaarten
    raster         het aantal is de informatie       i.p.v. een percentage in tekst
    wig            de hoek is de informatie          i.p.v. twee getallen naast elkaar

Alles wat hier niet in staat -- een venn, een marimekko, een treemap, een kwadrant -- teken
je met `vlak()`, `cirkel()`, `pad()` en `lijn()` uit `svg.py` in de schetskleur, en je zet
het door `schets_vrij()`. Dat is bewust: dit is een schetsblok en geen patroonbibliotheek.

Rooster schetsen
----------------
De spec is één lijst rijen, van boven naar beneden, en de hoogtes zijn verhoudingen die
samen het canvas vullen:

    from schets import Rij, Cel, schets

    schets("uitvoer/concept-c.svg", CANVAS["breed"],
           "C — vier kolommen met kopband",
           [Rij(0.18, [Cel("kopband", stijl="vol")] * 4, goot=14),
            Rij(0.55, [Cel("rol + toelichting", stijl="tint")] * 4, goot=14),
            Rij(0.05, [Cel("bronregel", stijl="leeg")]),
            Rij(0.22, [Cel("drager", 0.35, "vol"), Cel("sluitregel", 0.65, "vol")],
                afbloeden=True)])

Vier stijlen, en ze zeggen alleen wat de vulling doet:

    vol      een volle kleur; de letter erin is wit of navy
    tint     een container van 7 tot 12 procent met een haarlijn in de eigen hue
    lijn     wit met een haarlijn
    leeg     geen vlak; los tekstwerk

`afbloeden=True` laat de rij van canvasrand tot canvasrand lopen in plaats van binnen de
marge. Dat is hoe een afsluitende band eruitziet.

Een rij met `Cel("wit")` en stijl `leeg` zonder label is bewuste witruimte. Zet die er alleen
in als je hem bedoelt: dood wit onderin is de fout die deze schetsen juist moeten voorkomen.

Beide routes reserveren dezelfde 26pt onderaan voor het onderschrift, dus een figuurschets en
een roosterschets komen even hoog uit en staan vergelijkbaar op één contactblad.

Voorleggen: het canvas
----------------------
Geef `artboard_=` mee en de schets schrijft zich ook weg als een `.dc.html`-artboard, naast de
SVG. Zet er met `canvas_manifest()` een manifest bij, seed het met de helper die
`seed_helper()` opzoekt, en publiceer het: dan kiest de gebruiker op een canvas waar de vier
regels naast hun eigen schets staan, in plaats van in de `description` van een keuzemenu.

    p_a = schets_vrij("uitvoer/a.svg", c, "A", a, artboard_="uitvoer/canvas/Main.dc.html")
    canvas_manifest("uitvoer/canvas/canvas.json", [
        {"bestand": "uitvoer/canvas/Main.dc.html", "canvas": c, "titel": "A — geldstroom",
         "regels": ["Plattegrond: ...", "Meting: ...", "Drager: ...", "Kost: ..."]}, ...])

Het artboard krijgt géén onderschrift -- de titel staat in het manifest -- en de tekening erin
is dezelfde SVG. Dat is bewust het goedkoopste dat werkt: een schets is er om de plattegrond te
beoordelen en niet om aan te schuiven, dus hij hoeft niet per element bewerkbaar te zijn.

`contactblad()` blijft, en je gebruikt hem twee keer: altijd om zelf naar je drie schetsen te
kijken vóór je iets voorlegt, en als terugval wanneer node of de design-skill ontbreekt.
`preflight.py` zegt of de canvasroute er is.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from svg import (Canvas, Vorm, blok, cirkel, kop, label, lijn, op_schaal,  # noqa: E402
                 pad as svg_pad, schrijf, tekst, vlak)

STIJLEN = ("vol", "tint", "lijn", "leeg")


@dataclass
class Cel:
    """Eén doos in een rij. `w` is een verhouding binnen de rij."""
    naam: str = ""
    w: float = 1.0
    stijl: str = "tint"

    def __post_init__(self) -> None:
        if self.stijl not in STIJLEN:
            raise ValueError(f"stijl {self.stijl!r} bestaat niet; kies uit {STIJLEN}")


@dataclass
class Rij:
    """Eén band over de breedte. `h` is een verhouding van de canvashoogte."""
    h: float
    cellen: list[Cel] = field(default_factory=list)
    goot: float = 14.0
    afbloeden: bool = False


#: De schetskleur. Eén hue, want een schets gaat niet over kleur.
SCHETS = "navy"
#: Dekking per stijl -- alleen om vol, tint en lijn van elkaar te onderscheiden.
DEK = {"vol": 0.55, "tint": 0.10, "lijn": 0.0, "leeg": 0.0}
#: Hoogte die beide routes onderaan vrijhouden voor het onderschrift.
ONDERSCHRIFT_H = 26.0


def _onderschrift(c: Canvas, naam: str) -> Vorm:
    return blok("Onderschrift", 0, c.h - 14, c.w, [tekst(naam, 12, "navy", dekking=0.55)])


def schets(pad: str | Path, c: Canvas, naam: str, rijen: list[Rij], *,
           marge: float = 0.0, rij_gat: float = 12.0,
           artboard_: str | Path | None = None) -> Path:
    """Schrijf één ROOSTERwireframe: rijen en kolommen dozen.

    Dit is één plattegrond van de vele. Is de gekozen vorm een figuur -- en dat zijn er
    vijfenveertig van de zesenveertig -- gebruik dan `schets_vrij()` met de helpers eronder.
    """
    if not rijen:
        raise ValueError("een schets zonder rijen is geen schets")

    vlak_h = c.h - ONDERSCHRIFT_H
    som = sum(r.h for r in rijen)
    beschikbaar = vlak_h - rij_gat * (len(rijen) - 1)

    vormen: list[Vorm] = []
    y = 0.0
    for i, rij in enumerate(rijen):
        h = beschikbaar * rij.h / som
        x0 = 0.0 if rij.afbloeden else marge
        breedte = c.w - (0.0 if rij.afbloeden else 2 * marge)
        wsom = sum(cel.w for cel in rij.cellen) or 1.0
        goot_totaal = rij.goot * max(0, len(rij.cellen) - 1)
        x = x0
        for cel in rij.cellen:
            w = (breedte - goot_totaal) * cel.w / wsom
            dek = DEK[cel.stijl]
            if cel.stijl == "leeg":
                vormen.append(lijn(f"{cel.naam} lijn", x, y + h, x + w, y + h,
                                   kleur=SCHETS, dikte=0.5, dekking=0.30,
                                   streep="3 3"))
            elif cel.stijl == "lijn":
                vormen.append(vlak(f"{cel.naam} vlak", x, y, w, h,
                                   vulling=None, lijn_=(SCHETS, 1.0)))
            else:
                vormen.append(vlak(f"{cel.naam} vlak", x, y, w, h,
                                   vulling=(SCHETS, dek),
                                   lijn_=(SCHETS, 1.0) if cel.stijl == "tint" else None))
            if cel.naam:
                kleur = "wit" if cel.stijl == "vol" else "navy"
                dekking = 1.0 if cel.stijl == "vol" else 0.65
                # Een label dat buiten zijn doos hangt, toont een fout die in een schets niet
                # beoordeeld mag worden. Verklein tot het past, en kort pas daarna af.
                pt = 11.0
                from svg import breedte as _br
                while pt > 6 and _br(cel.naam.upper(), "Montserrat SemiBold", pt,
                                     pt * 0.12) > w - 12:
                    pt -= 0.5
                vormen.append(blok(f"{cel.naam} label", x + 6, y + h / 2, w - 12,
                                   [label(cel.naam, pt, kleur, dekking=dekking,
                                          algn="middle")], anchor="c"))
            x += w + rij.goot
        y += h + rij_gat

    if artboard_:                       # zonder onderschrift: canvas.json draagt de naam
        artboard(artboard_, c, vormen, beschrijving=f"Wireframe: {naam}")
    vormen.append(_onderschrift(c, naam))
    return schrijf(pad, c, vormen, beschrijving=f"Wireframe: {naam}")


# --------------------------------------------------------------------- figuurschetsen
#
# Zes archetypen, en één ding gemeen: er is een meting die een coördinaat, een lengte, een
# dikte of een hoek bepaalt. Dat is wat een figuur van een rooster onderscheidt, en het is de
# vraag die je jezelf stelt als je twijfelt of je iets hebt gekozen of alleen iets hebt
# opgemaakt: wélke meting bepaalt hier wat, en zou de tekening veranderen als het getal
# verandert? Bij een rij kaarten is het antwoord nee.


def schets_vrij(pad: str | Path, c: Canvas, naam: str, vormen: list[Vorm], *,
                artboard_: str | Path | None = None) -> Path:
    """Schrijf één FIGUURwireframe uit losse vormen, met hetzelfde onderschrift als `schets()`.

    Alles is toegestaan: de helpers hieronder, en verder `vlak()`, `cirkel()`, `pad()` en
    `lijn()` uit `svg.py`. Houd je aan `SCHETS` als kleur en gebruik geen accentkleur -- een
    schets gaat over de plattegrond, en kleur leidt daarvan af.
    """
    if not vormen:
        raise ValueError("een schets zonder vormen is geen schets")
    alles = [*vormen, _onderschrift(c, naam)]
    if artboard_:                       # zonder onderschrift: canvas.json draagt de naam
        artboard(artboard_, c, vormen, beschrijving=f"Wireframe: {naam}")
    return schrijf(pad, c, alles, beschrijving=f"Wireframe: {naam}")


def rol(naam: str, x: float, y: float, w: float = 160.0, *, algn: str = "start",
        pt: float = 10.0) -> Vorm:
    """Een rolnaam in de schets: waar tekst komt te staan, niet wélke tekst."""
    return blok(f"{naam} rol", x, y, w, [label(naam, pt, "navy", dekking=0.60, algn=algn)])


def as_op_schaal(y: float, waarden: list[float], laagst: float, hoogst: float, *,
                 x: float = 30.0, w: float | None = None, c: Canvas | None = None,
                 hoog: float = 13.0, stip: float = 4.5) -> list[Vorm]:
    """Een as waarop afstand de informatie is: elk moment op `op_schaal()`.

    Voor een tijdlijn, een getallenlijn en alles waar de gaten tussen de momenten het verhaal
    zijn. Vier gelijke banden onder elkaar zijn geen tijdlijn (vormentaal §8), en deze helper
    staat er om dat verschil al in de schets zichtbaar te maken.
    """
    if w is None:
        w = (c.w if c is not None else 0.0) - 2 * x
    v = [lijn("As", x, y, x + w, y, kleur=SCHETS, dikte=1.0, dekking=0.45)]
    for i, waarde in enumerate(waarden):
        px = op_schaal(waarde, laagst, hoogst, x, w)
        v.append(lijn(f"Moment {i+1} tik", px, y - hoog, px, y,
                      kleur=SCHETS, dikte=1.0, dekking=0.45))
        v.append(cirkel(f"Moment {i+1}", px, y, stip, vulling=(SCHETS, 0.55), lijn_=None))
    return v


def staven(x: float, y: float, w: float, aandelen: list[float], *, rij_h: float = 24.0,
           goot: float = 10.0, nul: float = 0.0, spoor: bool = True) -> list[Vorm]:
    """Staven waarvan de lengte de waarde is. `aandelen` loopt van -1 tot 1.

    `nul` is de nullijn als deel van de breedte: 0 voor een gewone geordende staaf, 0,5 voor
    een divergerende staaf met kost links en baat rechts. Een negatief aandeel loopt naar
    links. `spoor` tekent het lege deel als haarlijnvlak, zodat je ziet waartegen je afzet.
    """
    v: list[Vorm] = []
    x_nul = x + w * nul
    for i, a in enumerate(aandelen):
        ry = y + i * (rij_h + goot)
        if spoor:
            v.append(vlak(f"Spoor {i+1}", x, ry, w, rij_h, vulling=(SCHETS, 0.05),
                          lijn_=None))
        lengte = abs(a) * w * (1 - nul if a >= 0 else nul)
        sx = x_nul if a >= 0 else x_nul - lengte
        v.append(vlak(f"Staaf {i+1}", sx, ry, lengte, rij_h, vulling=(SCHETS, 0.45),
                      lijn_=None))
    if nul:
        onder = y + len(aandelen) * (rij_h + goot) - goot
        v.append(lijn("Nullijn", x_nul, y - 6, x_nul, onder + 6, kleur=SCHETS, dikte=1.0,
                      dekking=0.55))
    return v


def stroom(x1: float, x2: float, y: float, h: float, aandelen: list[float], *,
           gat: float = 16.0, balk: float = 8.0) -> list[Vorm]:
    """Eén bron die opsplitst in banden waarvan de dikte het aandeel is. De sankeyschets.

    `aandelen` telt op tot 1; doet het dat niet, dan liegt de dikte en is het een
    stroomschema en geen sankey (vormkeuze, valkuil 3).
    """
    som = sum(aandelen)
    if abs(som - 1.0) > 0.02:
        raise ValueError(f"de aandelen tellen op tot {som:.2f} en niet tot 1; een sankey "
                         "waarvan de delen niet optellen liegt over zijn diktes")
    v = [vlak("Bronbalk", x1, y, balk, h, vulling=(SCHETS, 0.55), lijn_=None)]
    netto = h - gat * (len(aandelen) - 1)
    y_in = y_uit = y
    for i, a in enumerate(aandelen):
        h_in, h_uit = h * a, netto * a
        xa, cx = x1 + balk, (x1 + balk + x2) / 2
        v.append(svg_pad(
            f"Stroom {i+1}",
            f"M {xa} {y_in:.1f} C {cx} {y_in:.1f} {cx} {y_uit:.1f} {x2} {y_uit:.1f} "
            f"L {x2} {y_uit + h_uit:.1f} C {cx} {y_uit + h_uit:.1f} {cx} "
            f"{y_in + h_in:.1f} {xa} {y_in + h_in:.1f} Z",
            vulling=(SCHETS, 0.16)))
        v.append(vlak(f"Uitbalk {i+1}", x2, y_uit, balk, h_uit, vulling=(SCHETS, 0.45),
                      lijn_=None))
        y_in += h_in
        y_uit += h_uit + gat
    return v


def naaf(cx: float, cy: float, r: float, n: int, *, knoop_r: float = 34.0,
         satelliet_r: float = 22.0, start: float = -90.0) -> list[Vorm]:
    """Eén centrale partij met `n` satellieten eromheen. De naafschets.

    De plek op de omloop is de rol: in het midden staat wie alles bij elkaar houdt, eromheen
    wie eraan hangt. Een rij kaarten zegt dat niet, en dat is het verschil dat deze schets
    moet laten zien.
    """
    v = [cirkel("Naaf", cx, cy, knoop_r, vulling=(SCHETS, 0.45), lijn_=None)]
    for i in range(n):
        hoek = math.radians(start + i * 360.0 / n)
        sx, sy = cx + r * math.cos(hoek), cy + r * math.sin(hoek)
        # De spaak loopt van rand tot rand en niet van hart tot hart, anders staat er een
        # streep dwars door beide knopen heen.
        v.insert(0, lijn(f"Spaak {i+1}",
                         cx + knoop_r * math.cos(hoek), cy + knoop_r * math.sin(hoek),
                         cx + (r - satelliet_r) * math.cos(hoek),
                         cy + (r - satelliet_r) * math.sin(hoek),
                         kleur=SCHETS, dikte=1.0, dekking=0.35))
        v.append(cirkel(f"Satelliet {i+1}", sx, sy, satelliet_r, vulling=(SCHETS, 0.10),
                        lijn_=(SCHETS, 1.0)))
    return v


def raster(x: float, y: float, aantal: int, gevuld: int, *, kolommen: int = 10,
           stap: float = 15.0, punt: float = 4.5) -> list[Vorm]:
    """Een rasterplot: `aantal` stippen waarvan er `gevuld` donker zijn.

    Het aantal is de informatie, dus de lezer kan het natellen. Dat is wat een rasterplot doet
    en wat een percentage in tekst niet doet.
    """
    v = []
    for i in range(aantal):
        r_, k = divmod(i, kolommen)
        v.append(cirkel(f"Stip {i+1}", x + k * stap, y + r_ * stap, punt,
                        vulling=(SCHETS, 0.50 if i < gevuld else 0.12), lijn_=None))
    return v


def wig(cx: float, cy: float, r: float, aandelen: list[float], *,
        start: float = -90.0, gat_binnen: float = 0.0) -> list[Vorm]:
    """Segmenten waarvan de hoek het aandeel is. Ring, meter of taart.

    Boven vier delen kan niemand hoeken meer vergelijken (vormkeuze, valkuil 2), dus deze
    helper weigert er meer. Wil je er meer laten zien, dan is het een staaf.
    """
    if len(aandelen) > 4:
        raise ValueError(f"{len(aandelen)} segmenten: boven vier delen zijn hoeken "
                         "onvergelijkbaar. Gebruik staven().")
    v, hoek = [], start
    for i, a in enumerate(aandelen):
        eind = hoek + a * 360.0
        h0, h1 = math.radians(hoek), math.radians(eind)
        groot = 1 if a > 0.5 else 0
        x0, y0 = cx + r * math.cos(h0), cy + r * math.sin(h0)
        x1, y1 = cx + r * math.cos(h1), cy + r * math.sin(h1)
        if gat_binnen:
            ri = r * gat_binnen
            xi0, yi0 = cx + ri * math.cos(h0), cy + ri * math.sin(h0)
            xi1, yi1 = cx + ri * math.cos(h1), cy + ri * math.sin(h1)
            d = (f"M {x0:.1f} {y0:.1f} A {r} {r} 0 {groot} 1 {x1:.1f} {y1:.1f} "
                 f"L {xi1:.1f} {yi1:.1f} A {ri} {ri} 0 {groot} 0 {xi0:.1f} {yi0:.1f} Z")
        else:
            d = (f"M {cx} {cy} L {x0:.1f} {y0:.1f} "
                 f"A {r} {r} 0 {groot} 1 {x1:.1f} {y1:.1f} Z")
        v.append(svg_pad(f"Segment {i+1}", d,
                         vulling=(SCHETS, 0.45 if i == 0 else 0.10 + i * 0.05),
                         lijn_=(SCHETS, 1.0)))
        hoek = eind
    return v


def contactblad(paden: list[str | Path], uit: str | Path, kolommen: int = 1,
                max_breedte: int = 1100) -> Path:
    """Zet de gerenderde schetsen ONDER elkaar in één PNG, zodat je ze kunt vergelijken.

    Eén kolom is de default en dat is geen smaak: de conceptkeuze gaat over het verschil in
    plattegrond, en dat zie je alleen als de schetsen dezelfde breedte hebben. `max_breedte`
    schaalt het blad daarna terug, want een contactblad van 4600 pixels breed kost bij het
    bekijken drie keer zoveel als een van 1100, en je ziet er niet meer op.
    """
    from PIL import Image

    beelden = [Image.open(p).convert("RGBA") for p in paden]
    marge = 24
    kb = max(b.width for b in beelden)
    kh = max(b.height for b in beelden)
    rijen = (len(beelden) + kolommen - 1) // kolommen
    blad = Image.new("RGBA",
                     (kolommen * kb + (kolommen + 1) * marge,
                      rijen * kh + (rijen + 1) * marge),
                     (255, 255, 255, 255))
    for i, b in enumerate(beelden):
        r, k = divmod(i, kolommen)
        blad.alpha_composite(b, (marge + k * (kb + marge), marge + r * (kh + marge)))
    if max_breedte and blad.width > max_breedte:
        h = round(blad.height * max_breedte / blad.width)
        blad = blad.resize((max_breedte, h), Image.LANCZOS)
    p = Path(uit)
    blad.convert("RGB").save(p)
    print(f"{p}  {blad.width}x{blad.height}px  {len(beelden)} schetsen")
    return p

# ------------------------------------------------------------------ canvas voorleggen
#
# Sinds de conceptkeuze op een canvas gaat, schrijven de schetsen zich ook weg als
# `.dc.html`-artboards. Het is dezelfde tekening: de SVG die je hierboven al maakte, in een
# artboard-omhulsel. Dat is bewust het goedkoopste dat werkt -- een schets is er om de
# plattegrond te beoordelen, niet om aan te schuiven, dus hij hoeft niet per element
# bewerkbaar te zijn. Wat het canvas wél toevoegt staat in stap 2D van de SKILL: de vier
# regels per concept komen naast de schets te staan in plaats van in een keuzemenu, drie
# concepten met verschillende canvasmaten passen naast elkaar op ware verhouding, en de
# keuze en de uitwerking blijven in één document.

DC_ROMP = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;600&amp;family=Lato:wght@300&amp;display=swap">
  <style>
    body { margin: 0; background: #FFFFFF; }
    a { color: #F87F4F; } a:hover { color: #D9603A; }
  </style>
</helmet>
<div style="position: relative; width: WIDTHpt; height: HEIGHTpt; background: #FFFFFF">
SVG
</div>
</x-dc>
<script data-dc-script data-props='{}'>
class Component extends DCLogic {
  renderVals() { return {}; }
}
</script>
</body>
</html>
"""


def artboard(pad: str | Path, c: Canvas, vormen: list[Vorm], *,
             beschrijving: str = "") -> Path:
    """Schrijf één `.dc.html`-artboard met dezelfde tekening als `schets_vrij()`.

    `pad` moet op `.dc.html` eindigen en de stam moet een naam zijn die het canvas accepteert:
    letters, cijfers, koppel- en liggend streepje. Het eerste artboard van een set heet
    `Main.dc.html` -- dat is de eis van de canvashelper, en de leesbare naam ("A -- geldstroom")
    zet je in `canvas_manifest()`, niet in de bestandsnaam.
    """
    from svg import svg as _svg
    p = Path(pad)
    if p.suffix != ".html" or not p.name.endswith(".dc.html"):
        raise ValueError(f"{p.name} is geen .dc.html; het canvas herkent alleen die naam")
    p.parent.mkdir(parents=True, exist_ok=True)
    doc = _svg(c, vormen, beschrijving=beschrijving)
    binnen = "\n".join("  " + r for r in doc.strip().splitlines())
    p.write_text(
        DC_ROMP.replace("WIDTH", f"{c.w:g}").replace("HEIGHT", f"{c.h:g}")
               .replace("SVG", binnen), encoding="utf-8")
    print(f"{p}  artboard {int(c.w)}x{int(c.h)}{c.eenheid}")
    return p


def canvas_manifest(pad: str | Path, concepten: list[dict], *,
                    kolom_gat: float = 80.0) -> Path:
    """Schrijf `canvas.json`: de artboards onder elkaar, met de vier regels als notitie.

    Elk concept is een dict met `bestand` (de .dc.html), `canvas` (het Canvas), `titel` (de
    leesbare naam) en `regels` (de vier regels uit stap 2D, als lijst). De notitie komt links
    naast zijn eigen artboard te staan -- dat is het hele punt van deze route: de prijs van
    een concept staat naast het concept en niet in een keuzemenu dat je één keer ziet.
    """
    PT2PX = 96.0 / 72.0
    NOTITIE_W = 300
    artboards, notities = [], []
    y = 0.0
    for i, k in enumerate(concepten):
        c = k["canvas"]
        w, h = round(c.w * PT2PX), round(c.h * PT2PX)
        artboards.append({"file": Path(k["bestand"]).name, "x": 0, "y": round(y),
                          "w": w, "h": h, "title": k["titel"]})
        regels = k.get("regels") or []
        if regels:
            notities.append({"id": f"concept-{i+1}", "x": -(NOTITIE_W + 40),
                             "y": round(y), "w": NOTITIE_W,
                             "text": k["titel"] + "\n\n" + "\n".join(regels)})
        y += h + kolom_gat
    manifest = {"artboards": artboards, "launch": {"view": "canvas"}}
    if notities:
        manifest["annotations"] = notities
    p = Path(pad)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{p}  {len(artboards)} artboards, {len(notities)} notities")
    return p


def seed_helper() -> str | None:
    """Pad naar `seed-canvas.mjs` van de design-skill, of None.

    Dit is `scripts/gedeeld/canvas.py::zoek_helper`, en het staat daar omdat alle vier de
    skills in deze plugin hun werk op een canvas voorleggen en dus alle vier hetzelfde
    pad moeten opzoeken. Twee kopieën van deze zoekactie hebben hier bestaan en ze waren
    niet gelijk: de ene koos de alfabetisch laatste kandidaat en dus soms een verouderde
    payload. Deze naam blijft staan omdat de SKILL hem noemt.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gedeeld"))
    from canvas import zoek_helper
    return zoek_helper()
