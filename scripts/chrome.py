"""De chromeband onderaan de slide, en de vraag of er iemand overheen tekent.

Deze module is de meetlaag onder twee gebruikers: `shapes.write()` waarschuwt ermee op het
moment van schrijven, en `qa_chrome.py` meldt ermee op de gebouwde deck. Zelf beslist hij
niets over vormgeving; hij rekent alleen uit wat wát dekt.

Waarom dit bestaat
------------------
Het logo linksonder is geen vorm op de slide en geen vorm op de layout: het is `Picture 4`
in `slideMaster2`, op 0,36 / 7,07 · 1,10 × 0,29. Masterchrome wordt ONDER alles getekend
wat de layout en de bouwer erop zetten. Elke opake vorm die tot onder 7,07 loopt, wist hem
dus -- zonder foutmelding, zonder verschil in de XML, en zonder dat een van de drie poorten
er iets over zei.

Nagemeten: een `vlak("Kaart", 0.48, 2.0, 12.52, 5.4, vulling="wit")` op layout 20 loopt tot
7,40, dat is 0,47 in voorbij de zonevloer van 6,93, en het logo is van de render verdwenen.
`qa_text.py` gaf `"verdict": "clean"`, `qa_tellingen.py` klaagde over de maatsprong en
`fit_title.py` zweeg. `ZONE["bottom"]` stond wel als getal in `shapes.py`, maar niets
toetste het.

Wat het gemeen maakt: met een dóórschijnende vulling (`container:navy`) blijft het logo
zichtbaar, alleen gedempt. Dezelfde fout is op de ene slide onzichtbaar en op de volgende
fataal, en dat is precies het soort defect dat een oog op een render mist.

Twee dingen die dit NIET zijn
-----------------------------
1. **Geen zonepolitie.** De trigger is de chromeband en niet `ZONE["bottom"]` (6,93). Het
   blanco canvas van layout 17 loopt zelf tot 6,97 (`CANVAS` in `shapes.py`), dus een
   melding op 6,93 zou op elke layout-17-slide afgaan zonder dat er iets dekt. Wat schade
   doet is de overlap met de chrome zelf, en dat is wat er gemeten wordt.
2. **Geen verbod op het verzadigde register.** Een vol vlak over de héle slide haalt logo
   én paginanummer weg, en bij de uitspraakslide is dat de bedoeling
   (`reference/merktekens.md` §11: "verder niets -- geen titel, geen logo behalve het
   merk"). Dat is daarom een `warn` met die uitleg erbij, en geen `critical`. Een vorm die
   de chrome maar gedeeltelijk afsnijdt -- een kaart, een band, een tabel -- is nooit
   bedoeld, en dat is de `critical`.

Hoe chrome herkend wordt
------------------------
Niet uit een tabel met coördinaten, want die loopt bij de eerste sjabloonwijziging uit de
pas. Chrome is een GETEKENDE vorm (dus zonder `<p:ph>`) in de master of de layout die
volledig in de onderste strook ligt en klein is: `y >= CHROME_TOP`, breedte
`<= CHROME_MAX_W`, hoogte `<= CHROME_MAX_H`. Dat vangt in dit sjabloon precies de vijf
merktekens en het paginanummer:

    image7.png   0.36, 7.07 · 1.10 × 0.29   vol logo, master 2 en layout 4 en 5
    image10.emf  0.15, 6.02 · 1.53 × 1.53   merkteken wit, de fotodividers 6 t/m 16
    image21.png  0.36, 6.47 · 1.23 × 0.65   merkteken wit, de sectieslides 25 t/m 30
    image4.png  10.58, 6.66 · 2.47 × 0.69   vol logo wit, de oranje outro 2 en 3
    het paginanummervak                     12.60, 7.12 · 0.62 × 0.24

en het laat de dingen die géén chrome zijn buiten de deur: de fotodivider (y = 0, volle
hoogte), de witte logokaart van de cover (y = 3,33) en de oranje dash (y = 1,72).

Ontbreekt de chrome met opzet -- `showMasterSp="0"` op de slide of op de layout, de weg die
`add_slide.py --no-page-number` en `infographic/blanco.py` gebruiken -- dan valt er niets te
dekken en meldt deze module niets.
"""

from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

EMU_PER_INCH = 914400

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS = {"a": A, "p": P}

#: Een getekende vorm in de master of de layout is chrome als hij hier helemaal onder ligt
#: en binnen deze maten valt. Zie de module-noot voor de meting waar deze drie uit komen.
CHROME_TOP = 6.0
CHROME_MAX_W = 3.0
CHROME_MAX_H = 1.6

#: Onder deze alpha (OOXML-honderdduizendsten) schemert de chrome er nog doorheen: dan is
#: het een `warn` en geen `critical`. 90000 is 90 procent dekking; de containervullingen van
#: `shapes.py` zitten op 7000 tot 25000 en vallen daar dus ruim onder.
OPAAK_ALPHA = 90000

#: Een vorm die de slide tot op deze marge in inch volledig dekt, is een vol vlak over de
#: hele slide en dus het verzadigde register -- geen ongeluk.
VOL_VLAK_MARGE = 0.02

#: Onder deze fractie van de chrome-oppervlakte is de overlap een haarlijn en geen hap.
MIN_HAP = 0.10


@dataclass(frozen=True)
class Doos:
    """Een vorm met zijn doos in inch.

    `gevuld` zegt of er iets te dekken IS -- een tekstvak zonder vulling laat de chrome
    staan. `alpha` is None bij een volle vulling, een beeld, een tabel of een grafiek, en
    anders de OOXML-alpha: dan schemert de chrome er nog door. Die twee staan los van elkaar,
    want een doorschijnende kaart over het logo is een andere bevinding dan een opake.
    """

    naam: str
    x: float
    y: float
    w: float
    h: float
    gevuld: bool = True
    alpha: int | None = None

    @property
    def rechts(self) -> float:
        return self.x + self.w

    @property
    def onder(self) -> float:
        return self.y + self.h

    @property
    def oppervlak(self) -> float:
        return max(0.0, self.w) * max(0.0, self.h)

    def maat(self) -> str:
        return (f"{self.x:.2f}-{self.rechts:.2f} × {self.y:.2f}-{self.onder:.2f}")


def overlap(a: Doos, b: Doos) -> float:
    """De oppervlakte van de doorsnede in vierkante inch."""
    breed = min(a.rechts, b.rechts) - max(a.x, b.x)
    hoog = min(a.onder, b.onder) - max(a.y, b.y)
    return breed * hoog if breed > 0 and hoog > 0 else 0.0


# ---------------------------------------------------------------- de parts lezen


class Bron:
    """Leest parts uit een ingepakte deck of uit een uitgepakte boom.

    Eén klasse voor beide, want `shapes.write()` zit in een uitgepakte boom en `qa_chrome.py`
    krijgt een .pptx. De partnamen zijn in beide gevallen de OPC-namen
    (`ppt/slides/slide1.xml`), dus de aanroeper hoeft het verschil niet te kennen.
    """

    def __init__(self, pad: str | Path):
        self.pad = Path(pad)
        self._zip = zipfile.ZipFile(self.pad) if self.pad.is_file() else None

    def sluit(self) -> None:
        if self._zip is not None:
            self._zip.close()

    def __enter__(self) -> "Bron":
        return self

    def __exit__(self, *_exc) -> None:
        self.sluit()

    def lees(self, part: str) -> bytes | None:
        if self._zip is not None:
            try:
                return self._zip.read(part)
            except KeyError:
                return None
        bestand = self.pad / part
        return bestand.read_bytes() if bestand.is_file() else None

    def slides(self) -> list[str]:
        """De slideparts in bestandsnaamnummer, niet in de volgorde van de sldIdLst.

        Voor deze meting is de volgorde niet interessant -- elke slide wordt los gemeten --
        en `slide7.xml` is de naam waarmee de bouwer werkt.
        """
        if self._zip is not None:
            namen = [n for n in self._zip.namelist()
                     if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
        else:
            namen = [f"ppt/slides/{p.name}"
                     for p in (self.pad / "ppt" / "slides").glob("slide*.xml")
                     if re.fullmatch(r"slide\d+\.xml", p.name)]
        return sorted(namen, key=lambda n: int(re.search(r"(\d+)\.xml", n).group(1)))

    def slide_maat(self) -> tuple[float, float]:
        """Het slideformaat in inch, uit de deck zelf. Valt terug op 13,333 × 7,5."""
        xml = self.lees("ppt/presentation.xml")
        if xml:
            m = re.search(rb'<p:sldSz[^>]*cx="(\d+)"[^>]*cy="(\d+)"', xml)
            if m:
                return (int(m.group(1)) / EMU_PER_INCH, int(m.group(2)) / EMU_PER_INCH)
        return (13.3333, 7.5)


def _rels_part(part: str) -> str:
    pad = Path(part)
    return (pad.parent / "_rels" / f"{pad.name}.rels").as_posix()


def _doel(bron: Bron, part: str, soort: str) -> str | None:
    """Het relationship-doel van `soort` bij `part`, als OPC-partnaam."""
    rels = bron.lees(_rels_part(part))
    if not rels:
        return None
    for rel in etree.fromstring(rels):
        target = rel.get("Target", "")
        if soort in rel.get("Type", "") and soort in target:
            if target.startswith("/"):
                return target.lstrip("/")
            return _normaliseer(Path(part).parent, target)
    return None


def _normaliseer(basis: Path, target: str) -> str:
    delen: list[str] = list(basis.parts)
    for deel in target.split("/"):
        if deel in ("", "."):
            continue
        if deel == "..":
            if delen:
                delen.pop()
        else:
            delen.append(deel)
    return "/".join(delen)


# ---------------------------------------------------------------- de vormen meten


def _xfrm(shape) -> tuple[float, float, float, float] | None:
    xfrm = shape.find("./p:spPr/a:xfrm", NS)
    if xfrm is None:
        xfrm = shape.find("./p:grpSpPr/a:xfrm", NS)
    if xfrm is None:
        xfrm = shape.find("./p:xfrm", NS)          # p:graphicFrame
    if xfrm is None:
        return None
    off, ext = xfrm.find("a:off", NS), xfrm.find("a:ext", NS)
    if off is None or ext is None:
        return None
    return (int(off.get("x", 0)) / EMU_PER_INCH, int(off.get("y", 0)) / EMU_PER_INCH,
            int(ext.get("cx", 0)) / EMU_PER_INCH, int(ext.get("cy", 0)) / EMU_PER_INCH)


def _kind_transform(grp) -> tuple[float, float, float, float]:
    """`(dx, dy, sx, sy)` om een kindcoördinaat naar slidecoördinaat te rekenen."""
    xfrm = grp.find("./p:grpSpPr/a:xfrm", NS)
    if xfrm is None:
        return (0.0, 0.0, 1.0, 1.0)
    off, ext = xfrm.find("a:off", NS), xfrm.find("a:ext", NS)
    ch_off, ch_ext = xfrm.find("a:chOff", NS), xfrm.find("a:chExt", NS)
    if off is None or ext is None or ch_off is None or ch_ext is None:
        return (0.0, 0.0, 1.0, 1.0)
    x, y = int(off.get("x", 0)), int(off.get("y", 0))
    cx, cy = int(ext.get("cx", 0)), int(ext.get("cy", 0))
    kx, ky = int(ch_off.get("x", 0)), int(ch_off.get("y", 0))
    kcx, kcy = int(ch_ext.get("cx", 1)), int(ch_ext.get("cy", 1))
    sx = cx / kcx if kcx else 1.0
    sy = cy / kcy if kcy else 1.0
    return ((x - kx * sx) / EMU_PER_INCH, (y - ky * sy) / EMU_PER_INCH, sx, sy)


def _naam(shape) -> str:
    cnv = shape.find(".//p:cNvPr", NS)
    naam = cnv.get("name") if cnv is not None else None
    return naam or etree.QName(shape).localname


def _dekking(shape) -> tuple[bool, int | None]:
    """Heeft deze vorm een vulling, en met welke alpha?

    Een beeldvulling dekt altijd, en een tabel of grafiek (`p:graphicFrame`) ook: die
    tekent zijn eigen celvullingen en heeft geen `spPr` om te lezen. Een volle vulling dekt,
    tenzij er alpha op staat. Geen vulling, `noFill`, of een verloop dat we niet uitrekenen:
    dan dekt hij niet -- een tekstvak zonder vulling laat het logo staan, en dat is de
    normale contentslide.
    """
    if etree.QName(shape).localname == "graphicFrame":
        return (True, None)
    if shape.find("./p:blipFill", NS) is not None:
        return (True, None)
    spPr = shape.find("./p:spPr", NS)
    if spPr is None:
        return (False, None)
    if spPr.find("a:blipFill", NS) is not None:
        return (True, None)
    solid = spPr.find("a:solidFill", NS)
    if solid is None:
        return (False, None)
    alpha = solid.find(".//a:alpha", NS)
    if alpha is None:
        return (True, None)
    return (True, int(alpha.get("val", 100000)))


def _loop(node, transform, alleen_getekend: bool, uit: list[Doos]) -> None:
    dx, dy, sx, sy = transform
    for kind in node:
        tag = etree.QName(kind).localname
        if tag == "grpSp":
            kdx, kdy, ksx, ksy = _kind_transform(kind)
            _loop(kind, (dx + kdx * sx, dy + kdy * sy, sx * ksx, sy * ksy),
                  alleen_getekend, uit)
            continue
        if tag not in ("sp", "pic", "graphicFrame"):
            continue
        if alleen_getekend and kind.find(".//p:nvPr/p:ph", NS) is not None:
            continue
        doos = _xfrm(kind)
        if doos is None:
            continue
        x, y, w, h = doos
        gevuld, alpha = _dekking(kind)
        uit.append(Doos(_naam(kind), dx + x * sx, dy + y * sy, w * sx, h * sy,
                        gevuld, alpha))


def vormen(xml: bytes | str, *, alleen_getekend: bool = False) -> list[Doos]:
    """De vormen in een spTree, met hun doos in slidecoördinaten.

    `alleen_getekend` laat de placeholders weg: dat is de chrome-kant van de meting, waar
    een titel- of tekstplaceholder geen chrome is. Op de slide zelf kijken we naar álles,
    want een gevulde placeholder dekt net zo goed.
    """
    root = etree.fromstring(xml.encode("utf-8") if isinstance(xml, str) else xml)
    tree = root.find(".//p:cSld/p:spTree", NS)
    if tree is None:
        tree = root.find(".//p:spTree", NS)
    if tree is None:
        return []
    uit: list[Doos] = []
    _loop(tree, (0.0, 0.0, 1.0, 1.0), alleen_getekend, uit)
    return uit


def is_chrome(doos: Doos) -> bool:
    return (doos.y >= CHROME_TOP
            and doos.w <= CHROME_MAX_W
            and doos.h <= CHROME_MAX_H
            and doos.w > 0 and doos.h > 0)


def _master_sp_uit(xml: bytes) -> bool:
    root = etree.fromstring(xml)
    return root.get("showMasterSp") == "0"


def chrome_van_slide(bron: Bron, slide_part: str) -> tuple[list[Doos], str | None]:
    """De geërfde chrome onder deze slide, en de layoutpart waar hij op staat.

    Leeg wanneer de slide of zijn layout `showMasterSp="0"` draagt: dan is de chrome met
    opzet weg en is er niets te dekken.
    """
    slide_xml = bron.lees(slide_part)
    if slide_xml is None or _master_sp_uit(slide_xml):
        return ([], None)

    layout_part = _doel(bron, slide_part, "slideLayout")
    if layout_part is None:
        return ([], None)
    layout_xml = bron.lees(layout_part)
    if layout_xml is None:
        return ([], layout_part)

    gevonden = [d for d in vormen(layout_xml, alleen_getekend=True) if is_chrome(d)]

    if not _master_sp_uit(layout_xml):
        master_part = _doel(bron, layout_part, "slideMaster")
        master_xml = bron.lees(master_part) if master_part else None
        if master_xml:
            gevonden += [d for d in vormen(master_xml, alleen_getekend=True)
                         if is_chrome(d)]
    return (gevonden, layout_part)


# ---------------------------------------------------------------- het oordeel


def _vol_vlak(doos: Doos, breed: float, hoog: float) -> bool:
    m = VOL_VLAK_MARGE
    return (doos.x <= m and doos.y <= m
            and doos.rechts >= breed - m and doos.onder >= hoog - m)


def bevindingen(eigen: list[Doos], chrome: list[Doos], maat: tuple[float, float],
                *, herkomst: str = "de master") -> list[dict]:
    """Per vorm-die-chrome-dekt één bevinding, zwaarste geval per vorm.

    De drie gevallen, in de volgorde waarin ze gewogen worden:

    * de vorm dekt de héle slide -> `warn`, want dat is het verzadigde register en bij de
      uitspraakslide de bedoeling;
    * de vorm is opaak en snijdt de chrome af -> `critical`;
    * de vorm is doorschijnend -> `warn`, het logo schemert erdoorheen.
    """
    breed, hoog = maat
    uit: list[dict] = []
    for vorm in eigen:
        if not vorm.gevuld:
            continue
        geraakt = [(c, overlap(vorm, c)) for c in chrome]
        geraakt = [(c, o) for c, o in geraakt if c.oppervlak and o / c.oppervlak >= MIN_HAP]
        if not geraakt:
            continue
        namen = ", ".join(f'"{c.naam}" op {c.x:.2f}, {c.y:.2f}' for c, _ in geraakt)
        if _vol_vlak(vorm, breed, hoog):
            uit.append({
                "check": "chrome-vol-vlak",
                "severity": "warn",
                "vorm": vorm.naam,
                "message": (
                    f'"{vorm.naam}" is een vol vlak over de hele slide en haalt daarmee de '
                    f"geërfde chrome weg ({namen}). Bij de uitspraakslide is dat de "
                    "bedoeling — geen titel, geen logo behalve het merk "
                    "(merktekens.md §11). Staat deze slide daar niet voor, dan hoort het "
                    "vlak boven de chromeband te stoppen."
                ),
            })
        elif vorm.alpha is None or vorm.alpha >= OPAAK_ALPHA:
            uit.append({
                "check": "chrome-gedekt",
                "severity": "critical",
                "vorm": vorm.naam,
                "message": (
                    f'"{vorm.naam}" ({vorm.maat()}) dekt {namen} af. Die chrome komt uit '
                    f"{herkomst} en wordt ONDER je vorm getekend, dus hij verdwijnt van de "
                    "render zonder dat er iets aan de vorm te zien is. Houd de onderkant "
                    "boven de chromeband, of maak er bewust een vol vlak over de hele "
                    "slide van."
                ),
            })
        else:
            uit.append({
                "check": "chrome-schemert",
                "severity": "warn",
                "vorm": vorm.naam,
                "message": (
                    f'"{vorm.naam}" ({vorm.maat()}) ligt met alpha {vorm.alpha} over '
                    f"{namen}. Het logo schemert er nu gedempt door. Op de render is dat "
                    "een halve chrome; houd de vorm boven de chromeband."
                ),
            })
    return uit


def meet_slide(bron: Bron, slide_part: str) -> dict:
    """Eén slide: de chrome, de eigen vormen, en de bevindingen."""
    chrome, layout_part = chrome_van_slide(bron, slide_part)
    slide_xml = bron.lees(slide_part)
    eigen = vormen(slide_xml) if slide_xml else []
    herkomst = f"{Path(layout_part).name} en zijn master" if layout_part else "de master"
    return {
        "slide": Path(slide_part).name,
        "layout": Path(layout_part).name if layout_part else None,
        "chrome": [c.naam for c in chrome],
        "findings": bevindingen(eigen, chrome, bron.slide_maat(), herkomst=herkomst),
    }


def dekt_chrome(unpacked_root: str | Path, slide_part: str,
                fragmenten: list[str]) -> list[dict]:
    """De bevindingen voor vormen die nog niet op de slide staan.

    Dit is de ingang voor `shapes.write()`: de fragmenten zijn XML-strings zonder
    namespacedeclaraties, dus ze worden in een wikkel geparseerd. Slikt elke fout — een
    waarschuwing die zelf een bouw kan breken is erger dan geen waarschuwing.
    """
    try:
        with Bron(unpacked_root) as bron:
            chrome, layout_part = chrome_van_slide(bron, slide_part)
            if not chrome:
                return []
            wikkel = (f'<p:x xmlns:p="{P}" xmlns:a="{A}" xmlns:r="http://schemas.'
                      f'openxmlformats.org/officeDocument/2006/relationships">'
                      f'{"".join(fragmenten)}</p:x>')
            root = etree.fromstring(wikkel.encode("utf-8"))
            eigen: list[Doos] = []
            _loop(root, (0.0, 0.0, 1.0, 1.0), False, eigen)
            herkomst = (f"{Path(layout_part).name} en zijn master" if layout_part
                        else "de master")
            return bevindingen(eigen, chrome, bron.slide_maat(), herkomst=herkomst)
    except Exception:
        return []
