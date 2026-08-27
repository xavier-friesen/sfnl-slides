#!/usr/bin/env python3
"""Bouwt een `.docx` uit het SFNL-Word-sjabloon door te erven, niet te herdefiniëren.

Dit script begint van `assets/word/SFNL_Word_sjabloon.dotx` en schrijft
alleen een nieuwe body. Elk ander onderdeel van het archief gaat
byte-voor-byte mee: `styles.xml`, `theme1.xml`, `numbering.xml`,
`settings.xml`, de vijf kop- en voetteksten en de twee logobeelden. Dat is
hetzelfde principe als `add_slide.py` in de deckroute, waar de layout de
opmaak levert en het script alleen de tekst — en het is hier belangrijker,
want het sjabloon is een stijlendrager en geen voorbeeldpagina. Er is niets
om na te tekenen, en dus ook geen reden om iets na te bouwen. Wie in plaats
daarvan een vers `.docx` opzet en de stijlen nabouwt, verliest het thema, de
kopregel, het logo en de nummering, en merkt dat pas op papier.

Twee dingen worden letterlijk uit het bronbestand geknipt in plaats van
opgeschreven: de openingstag van `w:document` (30 namespace-declaraties,
inclusief `mc:Ignorable`) en de hele `w:sectPr` (de vijf kop- en
voetverwijzingen, `pgSz`, `pgMar`, `titlePg`). Beide zijn lijsten die je
fout krijgt als je ze hertypt, en beide staan buiten wat dit script te
zeggen heeft.

**Er zijn precies vier wijzigingen buiten de body, en elk staat in het
verslag.**

* `[Content_Types].xml` — de override voor `/word/document.xml` staat op
  `…wordprocessingml.template.main+xml`. Zolang dat er staat is het bestand
  een sjabloon, hoe je het ook noemt. `template.main` wordt `document.main`.
  Dit is de enige verplichte wijziging.
* `styles.xml`, de alinea-afstand — `Standaard` heeft geen `w:pPr`, dus 0 pt
  boven, 0 pt onder, regelafstand enkel. Twee alinea's raken elkaar. Er komt
  8 pt onder en 1,15 × interlinie bij, in de stijl zelf en niet als directe
  opmaak: het erft door naar de koppen, het overleeft doortypen in Word, en
  het staat op één plek. De `rPr` blijft ongemoeid, dus Lato Light en
  `nl-NL` sneuvelen niet. De meting staat in
  `reference/word-stramien.md` §7.
* `styles.xml`, de letter van `Kop1` — zie hieronder.
* `docProps/core.xml` wordt leeggemaakt, want er staat een auteursnaam in en
  een `lastPrinted` van 2024. Een gegenereerd document dat naar buiten gaat
  hoort niet de naam van degene die het sjabloon maakte te dragen.

**Het Gotham-besluit.** `Kop1` vraagt `Gotham Bold Regular`, commercieel en
niet in de plugin. Op een SFNL-machine staat hij, in een sandbox en op de
machine van een klant niet, en dan substitueert Word stil: geen melding, wel
een andere breedte en dus een andere regelval. Dit script kiest daarom
expliciet — `--kop1 auto` kijkt of de letter er is, `gotham` en
`montserrat` dwingen — en zet het besluit in het bestand. Wat er in staat,
staat in het verslag onder `kop1`, en dat hoort bij de oplevering te worden
genoemd.

Er is geen `python-docx` en geen `lxml` voor nodig. Een `.docx` is een zip
met XML erin; `zipfile` en `xml.etree` uit de stdlib doen het, en dan is
meteen duidelijk uit welk onderdeel welk stuk komt. Dezelfde afweging als in
`scripts/rapport/lees_docx.py`.

De invoer is een markdownbestand met een kleine, vaste woordenschat. Wat
erbuiten valt wordt lopende tekst — er is geen stille interpretatie:

    ---                     frontmatter, alleen bovenaan
    titel: …                 -> Titel
    ondertitel: …            -> Ondertitel
    ---

    # kop                    -> Kop2   (14 pt Montserrat Light)
    ## kop                   -> Kop3   (12 pt Montserrat Light, navy)
    ### kop                  -> Kop4   (12 pt Montserrat Light, navy)
    gewone regel(s)          -> Standaard
    - punt                   -> Lijstalinea + numId 2 (streepje in Lato Light)
      - punt                 -> niveau 2; dat is een `o` in Courier New, dus liever niet
    1. punt                  -> Lijstalinea + numId 6 (decimaal)
    > citaat                 -> Citaat
    >> citaat                -> Duidelijkcitaat (met de oranje lijnen)
    | a | b |                -> tabel in TableGrid1, eerste rij is kop
    |---|---|
    <!-- pagina -->          -> pagina-einde
    **vet**  *cursief*       -> tekenstijl Zwaar / Nadruk
    [tekst](https://…)       -> hyperlink met de tekenstijl Hyperlink
    [DATUM]                  -> blijft staan; qa_word.py vindt hem terug

Gebruik:

    python bouw.py notitie.md --uit werkmap/notitie.docx
    python bouw.py notitie.md --uit werkmap/notitie.docx --pdf
    python bouw.py notitie.md --uit werkmap/notitie.docx --kop1 montserrat
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

HIER = Path(__file__).resolve().parent
WORTEL = HIER.parents[1]
SJABLOON = WORTEL / "assets" / "word" / "SFNL_Word_sjabloon.dotx"

sys.path.insert(0, str(WORTEL / "scripts" / "gedeeld"))

# --------------------------------------------------------------------------
# Wat er uit het sjabloon komt, en dus niet hier hoort te staan
# --------------------------------------------------------------------------
#
# Geen enkele hexwaarde en geen enkele puntgrootte in dit bestand. De kleuren
# en de corpsen zitten in `styles.xml` van het sjabloon en worden geërfd; de
# letterfamilies komen uit `scripts/gedeeld/merk.py`. Wat hieronder wél staat
# zijn de nummers van de nummeringsdefinities en de twee afstanden uit
# `word-stramien.md` §7 — dat zijn eigenschappen van dít sjabloon en van deze
# route, geen merkfeiten.

#: `numId 2` uit `numbering.xml`: een streepje in Lato Light. De enige van de
#: 27 opsommingsdefinities in het sjabloon waarvan het teken in de broodletter
#: staat; de andere 26 halen het uit Symbol, Arial of Wingdings, en dat is een
#: tweede letter op de pagina die niemand heeft gekozen.
NUM_STREEPJE = 2

#: `numId 6`: decimaal `1.` / `a.` / `i.`, met dezelfde indent-ladder.
NUM_DECIMAAL = 6

#: 8 pt in twips. Zie de docstring: `Standaard` heeft geen alinea-afstand.
NA_ALINEA = 160

#: De kopladder van dít medium, in halve punten (`w:sz` rekent in halve punten).
#: Het sjabloon levert Kop2 op 18 pt en dat is te luid voor een werkdocument van
#: twee of drie pagina's: 18 tegen een brood van 12 is een sprong van anderhalf,
#: en op een notitie waar drie of vier secties op één blad staan leest dat als
#: een rapportkop. Op 14 pt houdt de kop zijn rang en neemt hij geen regel meer
#: dan hij nodig heeft. Kop3 en Kop4 staan in het sjabloon al op 12 en blijven
#: daar; ze onderscheiden zich van het brood door hun familie (Montserrat Light
#: tegen Lato Light) en door navy, niet door hun corps.
#:
#: Kop1 staat er niet in, en dat is het besluit eronder: Kop1 is de titelrang en
#: geen sectiekop. Zie `titelrang_alleen` en §7 van het stramien.
KOPLADDER = {"Kop2": 28, "Kop3": 24, "Kop4": 24}

#: 1,15 × interlinie in 240sten van een regel, met `lineRule="auto"`. De
#: zetspiegel is 159,1 mm en dat is gemeten 84 tekens per regel op 12 pt, met
#: 91 in de langste; het leesbare bereik is 65-75. De marges liggen vast in
#: het sjabloon, dus wat overblijft is de interlinie.
REGELAFSTAND = 276

#: 1,0 mm celmarge boven en onder. `Standaardtabel` zet ze op 0, dus tekst
#: raakt de rand van de cel.
CEL_MARGE = 57

#: De zetspiegel in twips: 11900 - 2 x 1440. Uit `pgSz`, niet uit "A4 min
#: marges" — het sjabloon staat op 11900 en echte A4 is 11906.
ZETSPIEGEL = 9020

#: Een plaatshouder die de gebruiker moet invullen: `[DATUM]`, `[BEDRAG]`.
#: Twee of meer hoofdletters tussen blokhaken, zonder een `(` erachter (dat
#: zou een link zijn).
PLAATSHOUDER = re.compile(r"\[([A-Z][A-Z0-9 _/-]{1,40})\](?!\()")


def _letterfamilies() -> dict:
    """Levert `LETTERS` uit `scripts/gedeeld/merk.py`, en anders een fout.

    De vorm van `LETTERS` staat in `reference/merk.md` §5: familie ->
    gewichten, licentie, bestandspad. Dit script leest er één ding uit — de
    naam van de terugvalletter voor `Kop1` — en is tolerant over hóé de
    waarden erin zitten, omdat het niet de plek is om die vorm vast te
    leggen.
    """
    try:
        from merk import LETTERS                              # noqa: PLC0415
    except ImportError as e:                                  # pragma: no cover
        raise SystemExit(
            "scripts/gedeeld/merk.py is niet te importeren: %s\n"
            "Dat bestand is de enige plek waar een letterfamilie staat "
            "(reference/merk.md §5). Zonder hem kan dit script het "
            "Gotham-besluit niet nemen." % e) from e
    return dict(LETTERS)


def _gewichten(waarde) -> list[str]:
    """De gewichten uit één `LETTERS`-regel, welke vorm die ook heeft."""
    if isinstance(waarde, dict):
        for sleutel in ("gewichten", "weights", "sneden"):
            if sleutel in waarde:
                g = waarde[sleutel]
                return list(g) if not isinstance(g, str) else [g]
        return []
    for attr in ("gewichten", "weights", "sneden"):
        if hasattr(waarde, attr):
            g = getattr(waarde, attr)
            return list(g) if not isinstance(g, str) else [g]
    if isinstance(waarde, (list, tuple)):
        return list(waarde)
    return []


def terugvalletter() -> str:
    """De naam waarmee `Kop1` wordt gezet als Gotham er niet is.

    `merk.py` noemt hem zelf in `TERUGVAL`, en dan is dat de waarheid. Staat
    hij daar niet, dan wordt hij afgeleid: de familie met een SemiBold-snede
    die wél mee mag. Dat is Montserrat SemiBold, en dat is ook de letter die
    `Titel` al gebruikt, dus de kop en de titel blijven uit dezelfde familie
    komen.
    """
    try:
        from merk import TERUGVAL                              # noqa: PLC0415
        if isinstance(TERUGVAL, str) and TERUGVAL.strip():
            return TERUGVAL.strip()
    except ImportError:
        pass
    for familie, waarde in _letterfamilies().items():
        for gewicht in _gewichten(waarde):
            g = str(gewicht)
            if "semibold" in g.replace(" ", "").lower():
                # De gewichtsnotatie in merk.md is "600 SemiBold"; Word wil
                # de naam waaronder de snede geïnstalleerd staat.
                naam = re.sub(r"^\s*\d+\s*", "", g).strip()
                return f"{familie} {naam}"
    raise SystemExit("geen SemiBold-snede in merk.LETTERS; "
                     "de terugval voor Kop1 is niet te bepalen")


def gothamnaam(styles_xml: str) -> str | None:
    """De letternaam die `Kop1` in dít sjabloon vraagt.

    Niet hardgecodeerd, want de naam in het bestand is `Gotham Bold Regular`
    en niet `Gotham Bold` — wie op het tweede zoekt, vindt niets. Hij wordt
    dus uit `styles.xml` gelezen: de `w:ascii` van `Kop1`.
    """
    m = re.search(r'w:styleId="Kop1">.*?<w:rFonts w:ascii="([^"]+)"',
                  styles_xml, re.S)
    return m.group(1) if m else None


def letter_aanwezig(naam: str) -> bool:
    """Staat deze letterfamilie op deze machine?

    Drie manieren, want dit moet ook waar zijn in een Linux-sandbox en op
    een Office-machine waar Montserrat als cloud font in de FontCache staat
    in plaats van in de fontmap.
    """
    kern = naam.split()[0].lower()

    fc = shutil.which("fc-list")
    if fc:
        try:
            uit = subprocess.run([fc, ":", "family"], capture_output=True,
                                 text=True, timeout=20).stdout
            if kern in uit.lower():
                return True
        except (OSError, subprocess.SubprocessError):
            pass

    mappen = [Path.home() / ".fonts", Path.home() / ".local/share/fonts",
              Path("/usr/share/fonts"), Path("/Library/Fonts"),
              Path.home() / "Library/Fonts", Path("C:/Windows/Fonts")]
    lokaal = Path.home() / "AppData/Local/Microsoft/FontCache/4/CloudFonts"
    mappen.append(lokaal)
    for m in mappen:
        if not m.is_dir():
            continue
        try:
            for p in m.rglob("*"):
                if p.suffix.lower() in (".ttf", ".otf", ".ttc") \
                        and kern in p.name.lower():
                    return True
                if p.is_dir() and kern in p.name.lower():
                    return True
        except OSError:
            continue
    return False


# --------------------------------------------------------------------------
# De invoer ontleden
# --------------------------------------------------------------------------

INLINE = re.compile(
    r"(\*\*.+?\*\*"                      # **vet**
    r"|\*[^*\n]+?\*"                     # *cursief*
    r"|\[[^\]\n]+?\]\([^)\s]+\))")       # [tekst](url)

SCHEIDING = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")

#: Een regel die een nieuw blok begint. Alles wat hier niet op past en wat niet
#: leeg is, is een vervolgregel van het blok waar je in zit. Zonder deze test
#: werd de tweede regel van een opsommingspunt een losse alinea onder de lijst
#: -- gemeten op de eerste proef, en het is het soort fout dat je alleen op de
#: render ziet, want de tekst is compleet en staat op de goede plek in de bron.
BLOKSTART = re.compile(r"^\s*(#{1,3}\s|>{1,2}|[-*+]\s|\d+[.)]\s|\||<!--)")


def ontleed(tekst: str) -> tuple[dict, list[dict]]:
    """Van markdown naar een lijst blokken, zonder iets te verzinnen.

    Levert de frontmatter en de blokken in leesvolgorde. Elk blok heeft een
    `soort` en een `tekst` of `rijen`. Wat niet in de woordenschat van de
    docstring staat, wordt een alinea — er is geen stille interpretatie en er
    komt geen blok bij dat niet in de bron stond.
    """
    regels = tekst.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    kop: dict[str, str] = {}

    if regels and regels[0].strip() == "---":
        for i in range(1, len(regels)):
            if regels[i].strip() == "---":
                for r in regels[1:i]:
                    if ":" in r:
                        k, _, v = r.partition(":")
                        kop[k.strip().lower()] = v.strip()
                regels = regels[i + 1:]
                break

    blokken: list[dict] = []
    alinea: list[str] = []

    def sluit_alinea() -> None:
        if alinea:
            blokken.append({"soort": "alinea", "tekst": " ".join(alinea)})
            alinea.clear()

    i = 0
    while i < len(regels):
        regel = regels[i]
        kaal = regel.strip()

        if not kaal:
            sluit_alinea()
            i += 1
            continue

        if kaal in ("<!-- pagina -->", "<!--pagina-->"):
            sluit_alinea()
            blokken.append({"soort": "pagina"})
            i += 1
            continue

        if kaal.startswith("<!--"):
            i += 1
            continue

        m = re.match(r"^(#{1,3})\s+(.*)$", kaal)
        if m:
            sluit_alinea()
            blokken.append({"soort": "kop", "niveau": len(m.group(1)),
                            "tekst": m.group(2).strip()})
            i += 1
            continue

        m = re.match(r"^(>{1,2})\s*(.*)$", kaal)
        if m:
            sluit_alinea()
            niveau = len(m.group(1))
            deel = [m.group(2)]
            while i + 1 < len(regels):
                v = re.match(r"^\s*(>{1,2})\s*(.*)$", regels[i + 1])
                if not v or len(v.group(1)) != niveau:
                    break
                deel.append(v.group(2))
                i += 1
            blokken.append({"soort": "citaat", "niveau": niveau,
                            "tekst": " ".join(x.strip() for x in deel).strip()})
            i += 1
            continue

        m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", regel)
        if m:
            sluit_alinea()
            deel = [m.group(3).strip()]
            # Een opsommingspunt dat over twee regels loopt is één punt.
            while i + 1 < len(regels) and regels[i + 1].strip() \
                    and not BLOKSTART.match(regels[i + 1]):
                i += 1
                deel.append(regels[i].strip())
            blokken.append({
                "soort": "lijst",
                "geordend": m.group(2)[0].isdigit(),
                "ilvl": min(1, len(m.group(1).expandtabs(4)) // 2),
                "tekst": " ".join(deel).strip()})
            i += 1
            continue

        if kaal.startswith("|") and i + 1 < len(regels) \
                and SCHEIDING.match(regels[i + 1]):
            sluit_alinea()
            rijen = []
            j = i
            while j < len(regels) and regels[j].strip().startswith("|"):
                if not SCHEIDING.match(regels[j]):
                    cellen = [c.strip() for c in
                              regels[j].strip().strip("|").split("|")]
                    rijen.append(cellen)
                j += 1
            breed = max(len(r) for r in rijen)
            rijen = [r + [""] * (breed - len(r)) for r in rijen]
            blokken.append({"soort": "tabel", "rijen": rijen})
            i = j
            continue

        alinea.append(kaal)
        i += 1

    sluit_alinea()
    return kop, blokken


# --------------------------------------------------------------------------
# Naar WordprocessingML
# --------------------------------------------------------------------------

class Rels:
    """Houdt de externe verwijzingen bij die de body erbij nodig heeft.

    Alleen hyperlinks. Ze worden achteraan `word/_rels/document.xml.rels`
    gezet met een rId die niet bestaat, want het sjabloon gebruikt rId1 tot
    rId16 en Word verwijdert een relatie waarnaar niets wijst niet.
    """

    def __init__(self, bestaand: str) -> None:
        self.xml = bestaand
        gebruikt = [int(m) for m in re.findall(r'Id="rId(\d+)"', bestaand)]
        self.volgend = max(gebruikt or [0]) + 1
        self.nieuw: list[str] = []

    def link(self, url: str) -> str:
        rid = f"rId{self.volgend}"
        self.volgend += 1
        self.nieuw.append(
            f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org'
            f'/officeDocument/2006/relationships/hyperlink" '
            f'Target="{html.escape(url, quote=True)}" TargetMode="External"/>')
        return rid

    def uit(self) -> str:
        if not self.nieuw:
            return self.xml
        return self.xml.replace("</Relationships>",
                                "".join(self.nieuw) + "</Relationships>")


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def run(tekst: str, rstyle: str | None = None) -> str:
    if not tekst:
        return ""
    rpr = f'<w:rPr><w:rStyle w:val="{rstyle}"/></w:rPr>' if rstyle else ""
    return (f"<w:r>{rpr}"
            f'<w:t xml:space="preserve">{esc(tekst)}</w:t></w:r>')


def runs(tekst: str, rels: Rels) -> str:
    """De inline opmaak van één blok.

    Vet en cursief gaan via de **tekenstijlen** `Zwaar` en `Nadruk` uit het
    sjabloon en niet via een `w:b` of `w:i` op de run. Dat is hetzelfde
    verschil als tussen een alineastijl en directe opmaak: wie de stijl
    aanpast, past alles aan, en `qa_word.py` kan zien dat de opmaak uit het
    sjabloon komt.
    """
    uit = []
    for stuk in INLINE.split(tekst):
        if not stuk:
            continue
        if stuk.startswith("**") and stuk.endswith("**") and len(stuk) > 4:
            uit.append(run(stuk[2:-2], "Zwaar"))
        elif stuk.startswith("*") and stuk.endswith("*") and len(stuk) > 2:
            uit.append(run(stuk[1:-1], "Nadruk"))
        elif stuk.startswith("["):
            m = re.match(r"^\[([^\]]+)\]\(([^)\s]+)\)$", stuk)
            if m:
                rid = rels.link(m.group(2))
                uit.append(f'<w:hyperlink r:id="{rid}" w:history="1">'
                           f'{run(m.group(1), "Hyperlink")}</w:hyperlink>')
            else:
                uit.append(run(stuk))
        else:
            uit.append(run(stuk))
    return "".join(uit)


def alinea(inhoud: str, pstyle: str | None = None, extra: str = "") -> str:
    ppr = ""
    if pstyle or extra:
        ppr = "<w:pPr>"
        if pstyle:
            ppr += f'<w:pStyle w:val="{pstyle}"/>'
        ppr += extra + "</w:pPr>"
    return f"<w:p>{ppr}{inhoud}</w:p>"


def tabel(rijen: list[list[str]], rels: Rels) -> str:
    """Een tabel in `TableGrid1`, met een kopregel die je zelf moet maken.

    Het sjabloon geeft de tabelstijl randen van 0,5 pt en 11 pt tekst, maar
    geen kopregelopmaak: geen vulling, geen vet, geen band. De eerste rij
    krijgt hier dus `Zwaar` op de runs en `w:tblHeader` op de rij, zodat hij
    over een paginagrens meegaat.

    De kolommen worden verdeeld naar de langste cel per kolom, met een
    ondergrens van 12 % en een bovengrens van 50 % van de zetspiegel. Gelijke
    kolommen zetten "Bedrag" net zo breed als "Toelichting", en dan staat de
    tabel scheef zonder dat er iets fout is.
    """
    n = len(rijen[0])
    gewicht = [max((len(r[k]) for r in rijen), default=1) or 1
               for k in range(n)]
    laag, hoog = 0.12, 0.50
    deel = [g / sum(gewicht) for g in gewicht]
    deel = [min(hoog, max(laag, d)) for d in deel]
    deel = [d / sum(deel) for d in deel]
    breed = [int(round(ZETSPIEGEL * d)) for d in deel]
    breed[-1] += ZETSPIEGEL - sum(breed)

    grid = "".join(f'<w:gridCol w:w="{b}"/>' for b in breed)
    uit = [
        "<w:tbl><w:tblPr>"
        '<w:tblStyle w:val="TableGrid1"/>'
        f'<w:tblW w:w="{ZETSPIEGEL}" w:type="dxa"/>'
        '<w:tblLayout w:type="fixed"/>'
        f'<w:tblCellMar><w:top w:w="{CEL_MARGE}" w:type="dxa"/>'
        f'<w:bottom w:w="{CEL_MARGE}" w:type="dxa"/></w:tblCellMar>'
        '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" '
        'w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/>'
        f"</w:tblPr><w:tblGrid>{grid}</w:tblGrid>"]

    for r, rij in enumerate(rijen):
        trpr = "<w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>" if r == 0 else ""
        uit.append(f"<w:tr>{trpr}")
        for k, cel in enumerate(rij):
            inhoud = (run(cel, "Zwaar") if r == 0 and cel
                      else runs(cel, rels))
            # `contextualSpacing` haalt de 8 pt uit Standaard weer uit de cel;
            # een cel van een regel hoort niet 8 pt onderwit te dragen.
            uit.append(
                f'<w:tc><w:tcPr><w:tcW w:w="{breed[k]}" w:type="dxa"/>'
                "</w:tcPr>"
                f"{alinea(inhoud, None, '<w:contextualSpacing/>')}</w:tc>")
        uit.append("</w:tr>")
    uit.append("</w:tbl>")
    # Word wil een alinea na een tabel, anders plakt de volgende tabel eraan
    # vast en is er geen plek om de cursor te zetten.
    uit.append(alinea(""))
    return "".join(uit)


def body(kop: dict, blokken: list[dict], rels: Rels) -> tuple[str, dict]:
    """De blokken naar XML, en een telling per soort voor het verslag."""
    uit: list[str] = []
    telling: dict[str, int] = {}

    def tel(soort: str) -> None:
        telling[soort] = telling.get(soort, 0) + 1

    if kop.get("titel"):
        uit.append(alinea(runs(kop["titel"], rels), "Titel"))
        tel("titel")
    if kop.get("ondertitel"):
        uit.append(alinea(runs(kop["ondertitel"], rels), "Ondertitel"))
        tel("ondertitel")

    #: Het `numId` van het vorige blok, of None als dat geen lijst was. Alleen
    #: nodig voor de samensmelting die hieronder bij `soort == "lijst"` staat.
    vorige_num: str | None = None

    for b in blokken:
        soort = b["soort"]
        if soort != "lijst":
            vorige_num = None
        if soort == "kop":
            uit.append(alinea(runs(b["tekst"], rels),
                              f"Kop{kopstijl_niveau(b['niveau'])}"))
            tel(f"kop{kopstijl_niveau(b['niveau'])}")
        elif soort == "alinea":
            uit.append(alinea(runs(b["tekst"], rels)))
            tel("alinea")
        elif soort == "lijst":
            num = NUM_DECIMAAL if b["geordend"] else NUM_STREEPJE
            extra = (f'<w:numPr><w:ilvl w:val="{b["ilvl"]}"/>'
                     f'<w:numId w:val="{num}"/></w:numPr>')
            # Twee lijsten achter elkaar smelten samen, en dat is op de pagina
            # te zien en in de XML niet. `Lijstalinea` draagt
            # `contextualSpacing`, en dat haalt de alinea-afstand weg tussen
            # alinea's van dezelfde stijl -- ook tussen het laatste item van
            # de ene lijst en het eerste van de volgende. Nagemeten op de
            # proefnotitie: drie genummerde punten en twee streepjes lazen als
            # één lijst met twee soorten opsommingstekens.
            #
            # `w:spacing w:before` erbij zetten helpt niet, en dat is de val:
            # `contextualSpacing` is geen waarde die je overschrijft maar een
            # schakelaar die de afstand negeert. Eerst gemeten met alleen de
            # spacing erin -- de XML klopte, de pagina veranderde niet. Dus
            # moet de schakelaar zelf om, met `w:val="0"`.
            #
            # En die schakelaar geldt voor beide kanten, dus toen hij omging
            # kreeg dat ene item ook zijn onderruimte terug en stond er
            # ineens lucht tussen het eerste en het tweede streepje. Vandaar
            # `after="0"` erbij: alleen de bovenkant hoort open te gaan.
            if vorige_num is not None and vorige_num != num and not b["ilvl"]:
                extra += (f'<w:spacing w:before="{NA_ALINEA}" w:after="0"/>'
                          '<w:contextualSpacing w:val="0"/>')
            vorige_num = num
            uit.append(alinea(runs(b["tekst"], rels), "Lijstalinea", extra))
            tel("lijst" + ("-genummerd" if b["geordend"] else ""))
            if b["ilvl"]:
                tel("lijst-niveau2")
        elif soort == "citaat":
            stijl = "Duidelijkcitaat" if b["niveau"] == 2 else "Citaat"
            uit.append(alinea(runs(b["tekst"], rels), stijl))
            tel(stijl.lower())
        elif soort == "tabel":
            uit.append(tabel(b["rijen"], rels))
            tel("tabel")
        elif soort == "pagina":
            uit.append(alinea('<w:r><w:br w:type="page"/></w:r>'))
            tel("pagina-einde")

    return "".join(uit), telling


# --------------------------------------------------------------------------
# Het archief
# --------------------------------------------------------------------------

def patch_standaard(styles: str) -> tuple[str, bool]:
    """Zet de alinea-afstand in de stijl `Standaard`.

    `w:pPr` moet vóór `w:rPr` staan, dus de insertie gaat vlak voor de `rPr`
    van precies die ene stijl. Slaagt de insertie niet — het sjabloon is
    veranderd en heeft al een `pPr` — dan gebeurt er niets en meldt het
    verslag dat.
    """
    m = re.search(r'(<w:style [^>]*w:styleId="Standaard">)(.*?)(</w:style>)',
                  styles, re.S)
    if not m or "<w:pPr>" in m.group(2):
        return styles, False
    blok = m.group(2)
    ppr = (f'<w:pPr><w:spacing w:after="{NA_ALINEA}" '
           f'w:line="{REGELAFSTAND}" w:lineRule="auto"/></w:pPr>')
    if "<w:rPr>" in blok:
        blok = blok.replace("<w:rPr>", ppr + "<w:rPr>", 1)
    else:
        blok = blok + ppr
    return styles[:m.start(2)] + blok + styles[m.end(2):], True


#: Kop1 is de titelrang en geen sectiekop. Een werkdocument heeft één ding op
#: dat niveau en dat is de titel; alles daaronder is een sectie. Vóór dit besluit
#: werd `#` een Kop1 van 22 pt, en op een notitie van drie pagina's stonden er dan
#: vier van, elk zo luid als de titel — vier titels op één stuk. De body begint
#: daarom bij Kop2, en `#` uit de bron komt daar terecht.
#:
#: Kop9 is de bodem van het sjabloon, dus dieper dan dat schuift niet mee; wie
#: zes niveaus diep schrijft heeft een ander probleem dan een kopstijl.
TITELRANG = 1
DIEPSTE_KOP = 9


def kopstijl_niveau(bronniveau: int) -> int:
    """`#` wordt Kop2, `##` wordt Kop3. Zie `TITELRANG`."""
    return min(bronniveau + TITELRANG, DIEPSTE_KOP)


def patch_kopladder(styles: str) -> tuple[str, dict[str, int]]:
    """Zet de corpsen van Kop2 tot Kop4 op de maten van `KOPLADDER`.

    Anders dan `patch_standaard` gaat dit niet om een ontbrekende eigenschap
    maar om een die er al staat: elke kopstijl heeft een `w:sz` in zijn `rPr`,
    en die wordt overschreven. `w:szCs` gaat mee, want anders wijkt de
    complex-script-variant af en dat is precies het soort verschil dat je pas
    ziet als er een keer een euroteken of een aanhalingsteken anders valt.

    Levert per gewijzigde stijl de nieuwe maat in punten, zodat het verslag kan
    zeggen wat er is verzet in plaats van dat het gebeurd is.
    """
    verzet: dict[str, int] = {}
    for stijl, halve in KOPLADDER.items():
        m = re.search(rf'(<w:style [^>]*w:styleId="{stijl}">)(.*?)(</w:style>)',
                      styles, re.S)
        if not m:
            continue
        blok = m.group(2)
        nieuw_blok, n = re.subn(r'<w:sz w:val="\d+"/>',
                                f'<w:sz w:val="{halve}"/>', blok)
        nieuw_blok, n2 = re.subn(r'<w:szCs w:val="\d+"/>',
                                 f'<w:szCs w:val="{halve}"/>', nieuw_blok)
        if not (n or n2):
            # Kop3 tot Kop7 dragen in het sjabloon geen eigen `w:sz` en erven
            # hun corps van `docDefaults`. Dat komt nu op 12 pt uit en dat is de
            # bedoeling, maar een geërfde maat is geen belofte: verzet iemand
            # ooit de standaardmaat, dan schuift de hele kopladder mee zonder
            # dat er iets aan de koppen is veranderd. Daarom wordt hij hier
            # ingeschreven in plaats van overschreven.
            maat = f'<w:sz w:val="{halve}"/><w:szCs w:val="{halve}"/>'
            if "<w:rPr>" in nieuw_blok:
                nieuw_blok = nieuw_blok.replace("</w:rPr>", maat + "</w:rPr>", 1)
            else:
                nieuw_blok = nieuw_blok + f"<w:rPr>{maat}</w:rPr>"
        styles = styles[:m.start(2)] + nieuw_blok + styles[m.end(2):]
        verzet[stijl] = halve // 2
    return styles, verzet


def bouw(bron: Path, uit: Path, kop1: str = "auto",
         sjabloon: Path = SJABLOON) -> dict:
    if not sjabloon.is_file():
        raise SystemExit(f"sjabloon niet gevonden: {sjabloon}")

    brontekst = bron.read_text(encoding="utf-8")
    kopdata, blokken = ontleed(brontekst)

    with zipfile.ZipFile(sjabloon) as z:
        namen = z.namelist()
        orig = {n: z.read(n) for n in namen}

    doc = orig["word/document.xml"].decode("utf-8")
    styles = orig["word/styles.xml"].decode("utf-8")

    # De openingstag en de sectPr letterlijk overnemen. Zie de docstring.
    m = re.search(r"^(.*?<w:document\b[^>]*>)\s*<w:body>", doc, re.S)
    if not m:
        raise SystemExit("geen <w:document>/<w:body> in het sjabloon")
    aanhef = m.group(1)
    ms = re.search(r"<w:sectPr\b.*?</w:sectPr>", doc, re.S)
    if not ms:
        raise SystemExit("geen <w:sectPr> in het sjabloon; "
                         "dan is de bladmaat niet te erven")
    sectpr = ms.group(0)

    rels = Rels(orig["word/_rels/document.xml.rels"].decode("utf-8"))
    inhoud, telling = body(kopdata, blokken, rels)
    nieuw_doc = f"{aanhef}<w:body>{inhoud}{sectpr}</w:body></w:document>"

    # Het Gotham-besluit.
    gevraagd = gothamnaam(styles)
    terugval = terugvalletter()
    if kop1 == "auto":
        neem_gotham = bool(gevraagd) and letter_aanwezig(gevraagd)
    else:
        neem_gotham = kop1 == "gotham"
    if neem_gotham or not gevraagd:
        kop1_naam, vervangen = gevraagd, 0
    else:
        kop1_naam = terugval
        styles = styles.replace(f'"{gevraagd}"', f'"{terugval}"')
        vervangen = orig["word/styles.xml"].decode("utf-8").count(
            f'"{gevraagd}"')

    styles, gepatcht = patch_standaard(styles)
    styles, kopladder = patch_kopladder(styles)

    ct = orig["[Content_Types].xml"].decode("utf-8")
    if "wordprocessingml.template.main+xml" not in ct:
        raise SystemExit("de bron is geen .dotx: geen template-contenttype")
    ct = ct.replace("wordprocessingml.template.main+xml",
                    "wordprocessingml.document.main+xml")

    nu = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    core = orig["docProps/core.xml"].decode("utf-8")
    core = re.sub(r"<dc:title>.*?</dc:title>",
                  f"<dc:title>{esc(kopdata.get('titel', uit.stem))}</dc:title>",
                  core, flags=re.S)
    core = re.sub(r"<dc:creator>.*?</dc:creator>",
                  "<dc:creator>Social Finance NL</dc:creator>", core, flags=re.S)
    core = re.sub(r"<cp:lastModifiedBy>.*?</cp:lastModifiedBy>",
                  "<cp:lastModifiedBy>Social Finance NL</cp:lastModifiedBy>",
                  core, flags=re.S)
    core = re.sub(r"<cp:lastPrinted>.*?</cp:lastPrinted>", "", core, flags=re.S)
    core = re.sub(r'(<dcterms:(created|modified)[^>]*>).*?(</dcterms:\2>)',
                  lambda x: x.group(1) + nu + x.group(3), core, flags=re.S)

    vervang = {
        "word/document.xml": nieuw_doc.encode("utf-8"),
        "word/styles.xml": styles.encode("utf-8"),
        "word/_rels/document.xml.rels": rels.uit().encode("utf-8"),
        "[Content_Types].xml": ct.encode("utf-8"),
        "docProps/core.xml": core.encode("utf-8"),
    }

    uit.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(uit, "w", zipfile.ZIP_DEFLATED) as z:
        for n in namen:                      # zelfde volgorde als het sjabloon
            z.writestr(n, vervang.get(n, orig[n]))

    plaatshouders = sorted(set(PLAATSHOUDER.findall(brontekst)))

    return {
        "sjabloon": str(sjabloon),
        "uit": str(uit),
        "kb": round(uit.stat().st_size / 1024, 1),
        "blokken": telling,
        "kop1": {
            "gevraagd": gevraagd,
            "gezet": kop1_naam,
            "gotham": neem_gotham,
            "terugval": terugval,
            "vervangingen_in_styles": vervangen,
            "modus": kop1,
        },
        "patches": {
            "contenttype": "template.main -> document.main",
            "standaard_alinea_afstand": (
                f"after={NA_ALINEA}tw line={REGELAFSTAND}"
                if gepatcht else "niet gezet: Standaard had al een pPr"),
            "kopladder": ({f"{k} -> {v} pt" for k, v in kopladder.items()}
                          and {k: f"{v} pt" for k, v in kopladder.items()}
                          or "niet verzet: geen kopstijl met een w:sz gevonden"),
            "core_leeggemaakt": True,
        },
        "hyperlinks": len(rels.nieuw),
        "plaatshouders": plaatshouders,
    }


def naar_pdf(docx: Path) -> Path | None:
    """Het document één keer echt bekijken, via LibreOffice.

    Dit is geen oplevering en geen drukPDF; het is de enige vormbeoordeling
    die deze route heeft. Een document dat je niet hebt gezien is niet af, en
    LibreOffice substitueert dezelfde letters als Word — dus als er iets
    ontbreekt, ziet je het hier ook.
    """
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if not exe:
        return None
    r = subprocess.run([exe, "--headless", "--norestore", "--convert-to", "pdf",
                        "--outdir", str(docx.parent), str(docx)],
                       capture_output=True, text=True, timeout=300)
    pdf = docx.with_suffix(".pdf")
    if not pdf.is_file():
        print(r.stdout + r.stderr, file=sys.stderr)
        return None
    return pdf


def main() -> int:
    a = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("bron", type=Path, help="het markdownbestand")
    a.add_argument("--uit", type=Path, required=True, help="het .docx")
    a.add_argument("--kop1", choices=("auto", "gotham", "montserrat"),
                   default="auto",
                   help="de letter van Kop1; auto kijkt of Gotham er staat")
    a.add_argument("--sjabloon", type=Path, default=SJABLOON)
    a.add_argument("--pdf", action="store_true",
                   help="converteer erna naar PDF om ernaar te kijken")
    args = a.parse_args()

    if not args.bron.is_file():
        raise SystemExit(f"niet gevonden: {args.bron}")

    verslag = bouw(args.bron, args.uit, args.kop1, args.sjabloon)
    if args.pdf:
        pdf = naar_pdf(args.uit)
        verslag["pdf"] = str(pdf) if pdf else None
        if not pdf:
            verslag["pdf_fout"] = ("geen LibreOffice; dan is het document niet "
                                   "visueel geverifieerd en dat hoort bij de "
                                   "oplevering te worden gezegd")

    print(json.dumps(verslag, indent=2, ensure_ascii=False))
    if not verslag["kop1"]["gotham"]:
        print(f"\nKop1 staat in {verslag['kop1']['gezet']} en niet in "
              f"{verslag['kop1']['gevraagd']}. Noem dat bij de oplevering.",
              file=sys.stderr)
    if verslag["plaatshouders"]:
        print("\nplaatshouders die de gebruiker moet invullen: "
              + ", ".join(verslag["plaatshouders"]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
