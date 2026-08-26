#!/usr/bin/env python3
"""Een aangeleverd rapport uitlezen tot een structuur, zonder er iets aan te veranderen.

Dit script is het begin van de route en het is het enige punt waarop de
tekst het systeem binnenkomt. Alles wat er daarna mee gebeurt — zetten,
pagineren, opmaken — leest uit `document.json` en nooit meer uit het
bronbestand. Dat is niet netjesheid maar de reden dat `tekstcheck.py`
achteraf hard kan zeggen of er iets aan de tekst veranderd is: er is
één bron, en die staat vast in `bron-tekst.txt`.

Drie uitvoeren:

* **`document.json`** — de blokken in leesvolgorde, elk met een `id`, de
  platte tekst en de inline opmaak als runs. Koppen met hun niveau,
  lijsten met geordend-of-niet, tabellen als rijen, beeld met zijn
  bestand, voetnoten apart.
* **`bron-tekst.txt`** — dezelfde tekst genormaliseerd, één blok per
  regel. Dit is de vingerafdruk waar `tekstcheck.py` tegenaan houdt.
* **`signalen.json`** — wat er aan de brontekst opvalt en wat de
  vormgeving in de weg zou kunnen zitten. Geen oordeel en geen ingreep:
  een lijst waarnemingen waar de skill wijzigingsvóórstellen van maakt,
  die de gebruiker daarna goedkeurt of afwijst. Er staan twee soorten
  in, elk met zijn eigen `groep`: de `voorstel`-signalen gaan over één
  blok en komen in stap 3 langs, de `vormbesluit`-signalen gaan over het
  document als geheel en moeten vóór het bouwen vaststaan. Die laatste
  staan bovenaan.

Wat dit script uitdrukkelijk **niet** doet: tekst herschrijven, koppen
inkorten, een opsomming van een alinea maken, een bijschrift verzinnen,
lege alinea's weghalen of een "- " aan het begin van een regel
opruimen. Al die dingen zijn wijzigingen in de inhoud, en die worden
voorgesteld en niet gedaan.

Geen python-docx: een `.docx` is een zip met XML erin en de stdlib kan
dat. Dat scheelt een afhankelijkheid en het is meteen duidelijker wat er
uit welk element komt.

Gebruik:

    python lees_docx.py rapport.docx --uit werkmap/
    python lees_docx.py notitie.md   --uit werkmap/
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
CP = "{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}"
DC = "{http://purl.org/dc/elements/1.1/}"

#: Stijlnamen die een kop aanduiden, in het Engels en het Nederlands.
#: Word bewaart de stijl-*id*, en die is taalonafhankelijk in nieuwe
#: bestanden maar niet in oude of in bestanden uit LibreOffice.
KOPSTIJLEN = re.compile(r"^(heading|kop|titre|berschrift)\s*([1-9])$", re.I)
TITELSTIJLEN = {"title", "titel", "documenttitle"}
CITAATSTIJLEN = {"quote", "citaat", "intensequote", "blockquote", "citaatintensief"}
BIJSCHRIFTSTIJLEN = {"caption", "bijschrift", "onderschrift"}
#: Stijlnamen die een lijst aanduiden zonder dat er nummering bij staat.
LIJSTSTIJLEN = {"listparagraph", "listbullet", "listnumber", "lijstalinea",
                "lijstopsomteken", "lijstnummering", "listbullet2",
                "listnumber2", "opsomming", "bullet", "bulletlist"}

#: Koppen die een bronnenlijst aankondigen. De lijst is bewust ruim: een
#: valse treffer kost een vraag aan de gebruiker, een gemiste treffer
#: kost een bronnenlijst die als gewone alinea's wordt gezet.
BRONNENKOP = re.compile(
    r"^(bronnen|bronvermelding|bronnenlijst|literatuur|literatuurlijst|"
    r"geraadpleegde\s+(bronnen|literatuur)|bibliografie|referenties|"
    r"references|bibliography|works\s+cited)\b", re.I)

#: Koppen die een bijlage aankondigen.
BIJLAGEKOP = re.compile(r"^(bijlage[nx]?|appendix|appendices|annex)\b", re.I)

#: Een verwijzing van het type (Auteur, 2016) of (Auteur et al., 2016).
AUTEUR_JAAR = re.compile(
    r"\((?:zie\s+)?[A-ZÀ-Þ][\w'’-]+(?:[^()]{0,60}?)?,\s*\d{4}[a-z]?(?:[,;][^()]{0,40})?\)")

#: Een genummerde verwijzing van het type [12] of [3, 7-9].
GENUMMERD = re.compile(r"\[\d{1,3}(?:\s*[,–-]\s*\d{1,3})*\]")

#: Een regel die met een opsommingsteken of een nummer begint terwijl de
#: alinea niet als lijst is opgemaakt. Dit is de meest voorkomende reden
#: dat een Word-rapport er in de opmaak niet uitziet als een lijst.
HANDMATIG_TEKEN = re.compile(r"^\s*([-–—•*·▪◦o]|\(?\d{1,2}[.)]|[a-z][.)])\s+")

#: De meest voorkomende functiewoorden per taal. Hiermee wordt bepaald
#: in welke taal de bron geschreven is, en dat is met opzet grof: een
#: tekst herkennen aan zijn lidwoorden en voorzetsels valt niet om over
#: één Engels citaat in een Nederlandse alinea, terwijl een fijnere
#: meting — op woordfrequentie, op letterparen — dat wel doet. Er wordt
#: over het hele document geteld en niet per alinea, om dezelfde reden.
TAALWOORDEN = {
    "nederlands": {
        "de", "het", "een", "en", "van", "dat", "die", "op", "te", "voor", "met",
        "niet", "zijn", "aan", "er", "ook", "als", "maar", "om", "worden", "wordt",
        "bij", "uit", "naar", "over", "tot", "deze", "dit", "wat", "hun", "hij",
        "nog", "geen", "meer", "of", "want", "tussen", "onder", "waar", "hoe",
        "moet", "kan", "heeft", "hebben", "was", "werd", "zo", "door", "welke",
        "veel", "andere", "tegen", "zonder", "omdat", "waarin", "daarmee"},
    "engels": {
        "the", "of", "and", "to", "that", "for", "it", "with", "as", "on", "was",
        "are", "be", "this", "by", "from", "at", "or", "an", "which", "but", "not",
        "have", "has", "they", "their", "we", "been", "more", "will", "can",
        "would", "there", "these", "than", "when", "into", "all", "its", "about",
        "could", "such", "only", "also", "each", "were", "between", "through"},
    "duits": {
        "der", "die", "das", "und", "ist", "nicht", "ein", "eine", "mit", "sich",
        "auf", "für", "dass", "den", "dem", "des", "im", "zu", "von", "werden",
        "wird", "auch", "aber", "oder", "durch", "bei", "nach", "über", "unter",
        "wenn", "sind", "war", "haben", "hat", "einer", "als", "es", "wie", "nur",
        "er", "sie", "ich", "noch", "schon", "zwischen"},
    "frans": {
        "de", "le", "la", "les", "des", "une", "dans", "est", "pour", "que", "qui",
        "avec", "sur", "pas", "plus", "par", "au", "aux", "ce", "cette", "ces",
        "sont", "ont", "mais", "ou", "comme", "tout", "nous", "leur", "entre",
        "sous", "aussi", "du", "il", "elle", "se", "ne", "en", "leurs", "dont"},
}

#: Alleen de woorden die in precies één taal voorkomen tellen mee. "de"
#: is Nederlands én Frans, "die" is Nederlands én Duits, "was" is
#: Nederlands én Engels, "des" is Duits én Frans: juist de woorden die
#: het vaakst voorkomen zijn ook het vaakst gedeeld, en die maken het
#: onderscheid troebel in plaats van scherp. Wat overblijft is per taal
#: ruim genoeg — voor het Nederlands nog altijd "het", "een", "van",
#: "dat", "niet", "zijn", "wordt".
_TAALUNIEK = {
    taal: {w for w in woorden
           if sum(1 for andere in TAALWOORDEN.values() if w in andere) == 1}
    for taal, woorden in TAALWOORDEN.items()
}

#: Beeldformaten die Chromium niet toont, met de naam die de gebruiker
#: herkent. Het rapport wordt in een browser gezet, dus een figuur in
#: een van deze formaten komt niet als foutmelding op de pagina maar als
#: een leeg vlak — en een leeg vlak valt in een pdf van tachtig pagina's
#: pas op als de drukker belt. Word stopt er moeiteloos een EMF in: elke
#: grafiek die uit Excel of PowerPoint is geplakt is er een.
NIET_RENDERBAAR = {
    "emf": "Windows-metabestand (EMF)",
    "wmf": "Windows-metabestand (WMF)",
    "tif": "TIFF",
    "tiff": "TIFF",
    "eps": "Encapsulated PostScript",
    "wdp": "Windows Media Photo",
    "hdp": "HD Photo",
    "pict": "Macintosh PICT",
    "pct": "Macintosh PICT",
}

#: Een kop die zijn eigen nummer draagt: "3.", "3.2", "3.2.1", "A.",
#: "IV.", "Annex 2", "Bijlage A", "Hoofdstuk 3". Het losse getal zonder
#: punt staat er niet in, want "15 jaar resultaatfinanciering" is een
#: kop en geen nummering; er moet een punt achter staan of er moet een
#: tweede getal volgen. Het jaartal valt er om dezelfde reden buiten:
#: hoogstens drie cijfers, dus "2024 in cijfers" telt niet mee.
EIGEN_NUMMER = re.compile(
    r"^\s*(?:"
    r"(?i:hoofdstuk|deel|bijlage|annex|appendix|chapter|part|section)\s+"
    r"(?:\d{1,3}|[A-Z]|[IVX]{1,5})(?![A-Za-z])"
    r"|\d{1,3}(?:\.\d{1,3})+"
    r"|\d{1,3}\."
    r"|[A-Z]\."
    r"|[IVX]{1,5}\."
    r")(?=$|[\s:.)\u2013\u2014-])")


# =====================================================================
#  Normaliseren — één definitie, en tekstcheck.py gebruikt dezelfde
# =====================================================================

def normaliseer(tekst: str) -> str:
    """De vorm waarin twee stukken tekst met elkaar vergeleken worden.

    Wat hier wél wegvalt: verschillen in aanhalingsteken, streepje,
    spatiesoort en witruimte. Dat zijn dingen die een zetsysteem
    legitiem verandert — een zachte afbreking die Chromium invoegt, een
    non-breaking space in een getal — en die niets aan de tekst doen.

    Wat hier níét wegvalt: een woord, een leesteken, een hoofdletter,
    een cijfer. Verandert daar iets aan, dan is de tekst veranderd en
    dan hoort tekstcheck.py dat te zeggen.
    """
    t = unicodedata.normalize("NFC", tekst)
    t = t.replace("­", "")                    # zachte afbreking
    t = re.sub(r"[‘’‚′']", "'", t)
    t = re.sub(r"[“”„″\"]", '"', t)
    t = re.sub(r"[‐‑‒–—−-]", "-", t)
    t = re.sub(r"[       ]", " ", t)
    t = t.replace("​", "").replace("﻿", "")
    t = re.sub(r"\s+", " ", t)
    return t.strip()


# =====================================================================
#  De docx
# =====================================================================

class Docx:
    def __init__(self, pad: Path):
        self.pad = pad
        self.zip = zipfile.ZipFile(pad)
        self.rels = self._rels("word/_rels/document.xml.rels")
        self.numfmt = self._numbering()
        self.stijlnum = self._stijlnummering()
        self.voetnoten_xml = self._optioneel("word/footnotes.xml")
        self.eindnoten_xml = self._optioneel("word/endnotes.xml")

    # -- toegang ------------------------------------------------------
    def _optioneel(self, naam: str):
        try:
            return ET.fromstring(self.zip.read(naam))
        except KeyError:
            return None

    def _rels(self, naam: str) -> dict:
        uit = {}
        try:
            wortel = ET.fromstring(self.zip.read(naam))
        except KeyError:
            return uit
        for rel in wortel:
            uit[rel.get("Id")] = rel.get("Target")
        return uit

    def _numbering(self) -> dict:
        """numId + niveau -> 'geordend' of 'bullet'.

        Zonder deze stap is elke lijst een bolletjeslijst, en dan valt
        het verschil weg tussen een verzameling en een reeks. Dat
        verschil zit in de bron en hoort niet door de opmaak te worden
        weggegooid.
        """
        uit: dict = {}
        wortel = self._optioneel("word/numbering.xml")
        if wortel is None:
            return uit
        abstract: dict = {}
        for an in wortel.findall(f"{W}abstractNum"):
            aid = an.get(f"{W}abstractNumId")
            per_niveau = {}
            for lvl in an.findall(f"{W}lvl"):
                ilvl = lvl.get(f"{W}ilvl")
                fmt = lvl.find(f"{W}numFmt")
                waarde = fmt.get(f"{W}val") if fmt is not None else "bullet"
                per_niveau[ilvl] = "bullet" if waarde in ("bullet", "none") else "geordend"
            abstract[aid] = per_niveau
        for num in wortel.findall(f"{W}num"):
            nid = num.get(f"{W}numId")
            verwijzing = num.find(f"{W}abstractNumId")
            if verwijzing is not None:
                uit[nid] = abstract.get(verwijzing.get(f"{W}val"), {})
        return uit

    def _stijlnummering(self) -> dict:
        """stijlId -> (numId, ilvl), inclusief de overgeërfde.

        Een lijst hoeft de nummering niet op de alinea te dragen. Word
        zet hem net zo vaak op de stijl — `ListBullet`, `ListNumber`,
        `Lijstalinea` — en dan staat er in `w:p` alleen een `w:pStyle`.
        Zonder deze stap komt zo'n lijst als losse alinea's binnen en
        staan er straks vier regels onder elkaar zonder inspringing en
        zonder teken. Gemeten op het proefrapport: alle 28 lijstregels
        vielen zo weg.
        """
        wortel = self._optioneel("word/styles.xml")
        if wortel is None:
            return {}
        ruw, basis = {}, {}
        for st in wortel.findall(f"{W}style"):
            sid = st.get(f"{W}styleId") or ""
            bo = st.find(f"{W}basedOn")
            if bo is not None:
                basis[sid] = bo.get(f"{W}val")
            numPr = st.find(f"{W}pPr/{W}numPr")
            if numPr is None:
                continue
            numid = numPr.find(f"{W}numId")
            ilvl = numPr.find(f"{W}ilvl")
            if numid is not None:
                ruw[sid] = (numid.get(f"{W}val"),
                            int(ilvl.get(f"{W}val")) if ilvl is not None else 0)
        # De erfenis oplopen, met een teller tegen een kringverwijzing.
        uit = {}
        for sid in set(list(ruw) + list(basis)):
            huidig, stappen = sid, 0
            while huidig and huidig not in ruw and stappen < 12:
                huidig = basis.get(huidig)
                stappen += 1
            if huidig in ruw:
                uit[sid] = ruw[huidig]
        return uit

    # -- runs ---------------------------------------------------------
    #: Elementen waar tekst in kan zitten die niet zichtbaar is, of die
    #: er niet meer staat. `w:delText` en `w:del` zijn tekst die in een
    #: bijgehouden wijziging is verwijderd; `w:instrText` is een
    #: veldcode. Een rapport met wijzigingen aan staat leest dus zoals
    #: het er ná accepteren uitziet — en `lees_docx.py` zegt dat erbij.
    OVERSLAAN = {f"{W}pPr", f"{W}del", f"{W}delText", f"{W}instrText",
                 f"{W}proofErr", f"{W}bookmarkStart", f"{W}bookmarkEnd",
                 f"{W}commentRangeStart", f"{W}commentRangeEnd",
                 f"{W}commentReference", f"{W}footnoteRef", f"{W}endnoteRef"}

    def _runs(self, el, verzamel_noten: list) -> list:
        """De inline opmaak van een alinea, zonder de tekst aan te raken.

        Dit loopt de boom zelf af in plaats van `iter()` te gebruiken,
        want een `w:t` moet weten onder welke `w:rPr` hij hangt en
        ElementTree kent geen ouderverwijzing. De opmaak wordt van boven
        naar beneden meegegeven; een `w:hyperlink` of een `w:ins` erft
        die van zijn omgeving.
        """
        runs: list = []
        self._loop(el, None, runs, verzamel_noten)
        return self._voeg_samen(runs)

    def _loop(self, el, rPr, runs: list, noten: list) -> None:
        for kind in el:
            tag = kind.tag
            if tag in self.OVERSLAAN:
                continue
            if tag == f"{W}rPr":
                continue
            if tag == f"{W}r":
                eigen = kind.find(f"{W}rPr")
                self._loop(kind, eigen if eigen is not None else rPr, runs, noten)
            elif tag == f"{W}t":
                if kind.text:
                    runs.append(self._run(kind.text, rPr))
            elif tag == f"{W}tab":
                runs.append({"t": "\t"})
            elif tag in (f"{W}br", f"{W}cr"):
                runs.append({"t": "\n"})
            elif tag == f"{W}footnoteReference":
                nr = kind.get(f"{W}id")
                if nr and nr not in ("-1", "0"):
                    noten.append(nr)
                    runs.append({"t": "", "voetnoot": nr})
            elif tag == f"{W}endnoteReference":
                nr = kind.get(f"{W}id")
                if nr and nr not in ("-1", "0"):
                    noten.append("e" + nr)
                    runs.append({"t": "", "voetnoot": "e" + nr})
            else:
                # Onbekend omhulsel — hyperlink, ins, smartTag, sdt,
                # fldSimple. Doorlopen, want er kan tekst in staan.
                self._loop(kind, rPr, runs, noten)

    @staticmethod
    def _run(tekst: str, rPr) -> dict:
        run = {"t": tekst}
        if rPr is None:
            return run
        def aan(naam):
            el = rPr.find(f"{W}{naam}")
            return el is not None and el.get(f"{W}val") not in ("0", "false")
        if aan("b") or aan("bCs"):
            run["vet"] = True
        if aan("i") or aan("iCs"):
            run["cursief"] = True
        va = rPr.find(f"{W}vertAlign")
        if va is not None and va.get(f"{W}val") == "superscript":
            run["sup"] = True
        if va is not None and va.get(f"{W}val") == "subscript":
            run["sub"] = True
        return run

    @staticmethod
    def _voeg_samen(runs: list) -> list:
        """Twee runs met dezelfde opmaak worden er één.

        Word knipt een alinea in tientallen runs — bij elke
        spellingcontrole, elke taalmarkering, elke keer dat iemand de
        cursor ergens neerzette. Zonder dit staat er in de HTML
        `<b>d</b><b>e</b><b> </b><b>zaak</b>`, en dat breekt de
        afbreking en de zoekfunctie allebei.
        """
        uit: list = []
        for run in runs:
            if run.get("t") == "" and "voetnoot" not in run:
                continue
            if uit:
                vorig = uit[-1]
                zelfde = all(vorig.get(k) == run.get(k)
                             for k in ("vet", "cursief", "sup", "sub"))
                if zelfde and "voetnoot" not in run and "voetnoot" not in vorig:
                    vorig["t"] += run["t"]
                    continue
            uit.append(dict(run))
        return uit

    # -- alinea's -----------------------------------------------------
    def _stijl(self, p) -> str:
        pPr = p.find(f"{W}pPr")
        if pPr is None:
            return ""
        st = pPr.find(f"{W}pStyle")
        return (st.get(f"{W}val") or "") if st is not None else ""

    def _kopniveau(self, p, stijl: str) -> int | None:
        m = KOPSTIJLEN.match(stijl.replace("-", "").replace(" ", ""))
        if m:
            return int(m.group(2))
        if stijl.lower().replace("-", "") in TITELSTIJLEN:
            return 0
        pPr = p.find(f"{W}pPr")
        if pPr is not None:
            ol = pPr.find(f"{W}outlineLvl")
            if ol is not None:
                try:
                    n = int(ol.get(f"{W}val"))
                    return n + 1 if n < 9 else None
                except (TypeError, ValueError):
                    pass
        return None

    def _lijst(self, p, stijl: str) -> tuple[bool, int, str] | None:
        """Is dit een lijstregel, en zo ja: geordend, op welk niveau.

        Drie bronnen, in deze volgorde. De alinea zelf wint van de
        stijl, en de stijl wint van de naam. De naam is de laatste
        redding voor bestanden waarin de nummering helemaal ontbreekt —
        dan weten we wél dat het een lijst is, maar niet welk teken
        erbij hoort, en dan wordt het een bolletje.
        """
        nid, niveau = None, 0
        pPr = p.find(f"{W}pPr")
        numPr = pPr.find(f"{W}numPr") if pPr is not None else None
        if numPr is not None:
            ilvl = numPr.find(f"{W}ilvl")
            numid = numPr.find(f"{W}numId")
            niveau = int(ilvl.get(f"{W}val")) if ilvl is not None else 0
            nid = numid.get(f"{W}val") if numid is not None else None
        if nid in (None, "0") and stijl in self.stijlnum:
            nid, niveau = self.stijlnum[stijl]
        if nid in (None, "0"):
            kaal = stijl.lower().replace("-", "").replace(" ", "")
            if kaal in LIJSTSTIJLEN:
                return ("nummer" in kaal or "number" in kaal, 0, "stijl:" + stijl)
            return None
        soort = self.numfmt.get(nid, {}).get(str(niveau), "bullet")
        return (soort == "geordend", niveau, nid)

    def _beeld_in(self, el) -> list:
        """De ingesloten beelden van een alinea, met hun bestandsnaam."""
        uit = []
        for blip in el.iter(f"{A}blip"):
            rid = blip.get(f"{R}embed") or blip.get(f"{R}link")
            doel = self.rels.get(rid)
            if doel:
                uit.append(doel.replace("\\", "/").lstrip("/"))
        return uit

    def _alinea(self, p, noten: list) -> dict | None:
        runs = self._runs(p, noten)
        tekst = "".join(r.get("t", "") for r in runs)
        beeld = self._beeld_in(p)
        stijl = self._stijl(p)
        if not tekst.strip() and not beeld:
            return {"soort": "leeg", "stijl": stijl}
        blok: dict = {"stijl": stijl, "runs": runs, "tekst": tekst}
        if beeld:
            blok["beeld"] = beeld
        niveau = self._kopniveau(p, stijl)
        lijst = self._lijst(p, stijl)
        s = stijl.lower().replace("-", "").replace(" ", "")
        if niveau is not None and tekst.strip():
            blok["soort"] = "titel" if niveau == 0 else "kop"
            blok["niveau"] = max(niveau, 1)
        elif lijst is not None:
            blok["soort"] = "lijst"
            blok["geordend"], blok["niveau"], blok["lijstid"] = lijst
        elif s in CITAATSTIJLEN:
            blok["soort"] = "citaat"
        elif s in BIJSCHRIFTSTIJLEN:
            blok["soort"] = "bijschrift"
        elif beeld and not tekst.strip():
            blok["soort"] = "beeld"
        else:
            blok["soort"] = "alinea"
        return blok

    def _tabel(self, tbl, noten: list) -> dict:
        rijen = []
        for tr in tbl.findall(f"{W}tr"):
            rij = []
            for tc in tr.findall(f"{W}tc"):
                delen = []
                for p in tc.findall(f"{W}p"):
                    runs = self._runs(p, noten)
                    tekst = "".join(r.get("t", "") for r in runs)
                    if tekst.strip():
                        delen.append({"runs": runs, "tekst": tekst})
                span = tc.find(f"{W}tcPr/{W}gridSpan")
                rij.append({"delen": delen,
                            "tekst": " ".join(d["tekst"] for d in delen),
                            "span": int(span.get(f"{W}val")) if span is not None else 1})
            kopregel = tr.find(f"{W}trPr/{W}tblHeader") is not None
            rijen.append({"cellen": rij, "kop": kopregel})
        return {"soort": "tabel", "rijen": rijen}

    # -- de noten -----------------------------------------------------
    def noten(self, ids: list) -> dict:
        uit = {}
        for nid in ids:
            wortel = self.eindnoten_xml if nid.startswith("e") else self.voetnoten_xml
            zoek = nid[1:] if nid.startswith("e") else nid
            tag = "endnote" if nid.startswith("e") else "footnote"
            if wortel is None:
                continue
            for n in wortel.findall(f"{W}{tag}"):
                if n.get(f"{W}id") != zoek:
                    continue
                delen = []
                for p in n.findall(f"{W}p"):
                    runs = self._runs(p, [])
                    delen.append("".join(r.get("t", "") for r in runs))
                tekst = " ".join(d for d in delen if d.strip()).strip()
                # Word zet een tab tussen het nootnummer en de tekst.
                uit[nid] = {"tekst": re.sub(r"^[\s\t]+", "", tekst)}
                break
        return uit

    # -- het geheel ---------------------------------------------------
    def lees(self) -> tuple[list, dict, dict]:
        wortel = ET.fromstring(self.zip.read("word/document.xml"))
        lichaam = wortel.find(f"{W}body")
        blokken, noten = [], []
        for kind in list(lichaam):
            if kind.tag == f"{W}p":
                blok = self._alinea(kind, noten)
                if blok:
                    blokken.append(blok)
            elif kind.tag == f"{W}tbl":
                blokken.append(self._tabel(kind, noten))
        return blokken, self.noten(noten), self.kern()

    def kern(self) -> dict:
        """Titel en auteur uit de bestandseigenschappen, als ze er staan."""
        wortel = self._optioneel("docProps/core.xml")
        if wortel is None:
            return {}
        uit = {}
        for tag, naam in ((f"{DC}title", "titel"), (f"{DC}creator", "auteur"),
                          (f"{DC}subject", "onderwerp")):
            el = wortel.find(tag)
            if el is not None and (el.text or "").strip():
                uit[naam] = el.text.strip()
        return uit

    def beelden(self, doel: Path, gebruikt: set) -> dict:
        """De gebruikte beelden uitpakken naar `beeld/`."""
        doel.mkdir(parents=True, exist_ok=True)
        uit = {}
        for naam in gebruikt:
            pad_in_zip = naam if naam.startswith("word/") else f"word/{naam}"
            try:
                data = self.zip.read(pad_in_zip)
            except KeyError:
                continue
            bestand = doel / Path(naam).name
            bestand.write_bytes(data)
            uit[naam] = {"bestand": f"beeld/{bestand.name}",
                         "bytes": len(data), **_beeldmaat(data)}
        return uit

    def losse_media(self, gebruikt: set) -> list:
        """Wat er in `word/media/` zit en door geen enkel blok wordt genoemd.

        Een tekstvak, een SmartArt, een Word-diagram, een logo in de
        koptekst: het beeld zit wél in het bestand maar niet in de
        tekststroom, en `lees()` loopt de tekststroom af. Zo'n figuur
        komt dus nergens tegen — niet als blok, niet als signaal, en
        straks niet in het rapport.

        Het verschil tussen de zip en de blokken is de enige plek waar
        dat te zien is, en het is een grof verschil: er wordt geteld en
        niet uitgepakt. Waar het beeld vandaan komt weten we niet, en
        wat ermee moet gebeuren is een vraag aan de gebruiker.
        """
        in_gebruik = {n if n.startswith("word/") else f"word/{n}" for n in gebruikt}
        uit = []
        for naam in sorted(self.zip.namelist()):
            if not naam.startswith("word/media/") or naam.endswith("/"):
                continue
            if naam in in_gebruik:
                continue
            uit.append({"naam": naam[len("word/"):],
                        "bytes": self.zip.getinfo(naam).file_size})
        return uit


def _beeldmaat(data: bytes) -> dict:
    """Breedte en hoogte uit de bytes zelf, voor PNG, JPEG en GIF.

    Alleen om te kunnen zeggen of een beeld groot genoeg is voor druk.
    Een foto van 400 px breed die over de volle zetspiegel gaat, komt op
    56 dpi op papier, en dat is zichtbaar. qa_rapport.py rekent dat uit;
    hier wordt alleen gemeten.
    """
    try:
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            w = int.from_bytes(data[16:20], "big")
            h = int.from_bytes(data[20:24], "big")
            return {"breedte": w, "hoogte": h}
        if data[:2] == b"\xff\xd8":
            i = 2
            while i < len(data) - 9:
                if data[i] != 0xFF:
                    i += 1
                    continue
                merk = data[i + 1]
                if merk in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                            0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    h = int.from_bytes(data[i + 5:i + 7], "big")
                    w = int.from_bytes(data[i + 7:i + 9], "big")
                    return {"breedte": w, "hoogte": h}
                i += 2 + int.from_bytes(data[i + 2:i + 4], "big")
        if data[:6] in (b"GIF87a", b"GIF89a"):
            return {"breedte": int.from_bytes(data[6:8], "little"),
                    "hoogte": int.from_bytes(data[8:10], "little")}
    except Exception:
        pass
    return {}


# =====================================================================
#  Markdown en platte tekst — de zijingang
# =====================================================================

def lees_markdown(pad: Path) -> tuple[list, dict, dict]:
    """Genoeg markdown voor een rapport, en geen regel meer.

    Dit bestaat omdat een aangeleverd stuk niet altijd een `.docx` is.
    Wat het niet doet is markdown volledig ondersteunen: geen
    voetnoten, geen definitielijsten, geen HTML erin. Wat er niet in
    zit, komt als gewone alinea door — en dat is beter dan het stil
    verkeerd interpreteren.
    """
    regels = pad.read_text(encoding="utf-8").splitlines()
    blokken: list = []
    i, n = 0, len(regels)
    while i < n:
        regel = regels[i]
        kaal = regel.strip()
        if not kaal:
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", kaal)
        if m:
            blokken.append({"soort": "kop", "niveau": len(m.group(1)),
                            "tekst": m.group(2).strip(),
                            "runs": _md_runs(m.group(2).strip()), "stijl": ""})
            i += 1
            continue
        m = re.match(r"^!\[(.*?)\]\((.+?)\)\s*$", kaal)
        if m:
            blokken.append({"soort": "beeld", "beeld": [m.group(2)],
                            "tekst": "", "runs": [], "stijl": "",
                            "bijschrift": m.group(1) or None})
            i += 1
            continue
        if kaal.startswith("|") and i + 1 < n and re.match(r"^\|[\s:|-]+\|?$", regels[i + 1].strip()):
            rijen, j = [], i
            while j < n and regels[j].strip().startswith("|"):
                cel = [c.strip() for c in regels[j].strip().strip("|").split("|")]
                if not re.match(r"^[\s:|-]+$", regels[j].strip().strip("|")):
                    rijen.append({"cellen": [{"delen": [{"runs": _md_runs(c), "tekst": c}],
                                              "tekst": c, "span": 1} for c in cel],
                                  "kop": len(rijen) == 0})
                j += 1
            blokken.append({"soort": "tabel", "rijen": rijen})
            i = j
            continue
        m = re.match(r"^([-*+]|\d{1,2}[.)])\s+(.*)$", kaal)
        if m:
            geordend = not m.group(1) in ("-", "*", "+")
            inspring = len(regel) - len(regel.lstrip())
            # De doorlopende regels van hetzelfde item erbij. Zonder dit
            # wordt "…en zijn ook het best\n  gedocumenteerd." twee
            # blokken, en dan staat er in de opmaak een lijstregel met een
            # losse alinea eronder. Op de keuzekaart was dat het eerste
            # wat opviel.
            delen = [m.group(2).strip()]
            i += 1
            while i < n and regels[i].strip() and not re.match(
                    r"^\s*(#{1,6}\s|[-*+]\s|\d{1,2}[.)]\s|>|\||!\[)", regels[i]):
                volg_inspring = len(regels[i]) - len(regels[i].lstrip())
                if volg_inspring <= inspring:
                    break
                delen.append(regels[i].strip())
                i += 1
            tekst = " ".join(delen)
            blokken.append({"soort": "lijst", "geordend": geordend,
                            "niveau": 1 if inspring >= 2 else 0,
                            "tekst": tekst,
                            "runs": _md_runs(tekst), "stijl": ""})
            continue
        if kaal.startswith(">"):
            tekst = re.sub(r"^>\s?", "", kaal)
            blokken.append({"soort": "citaat", "tekst": tekst,
                            "runs": _md_runs(tekst), "stijl": ""})
            i += 1
            continue
        stuk = [kaal]
        i += 1
        while i < n and regels[i].strip() and not re.match(
                r"^(#{1,6}\s|[-*+]\s|\d{1,2}[.)]\s|>|\||!\[)", regels[i].strip()):
            stuk.append(regels[i].strip())
            i += 1
        tekst = " ".join(stuk)
        blokken.append({"soort": "alinea", "tekst": tekst,
                        "runs": _md_runs(tekst), "stijl": ""})
    return blokken, {}, {}


def _md_runs(tekst: str) -> list:
    runs, rest = [], tekst
    patroon = re.compile(r"(\*\*|__)(.+?)\1|(\*|_)(.+?)\3")
    pos = 0
    for m in patroon.finditer(rest):
        if m.start() > pos:
            runs.append({"t": rest[pos:m.start()]})
        if m.group(2) is not None:
            runs.append({"t": m.group(2), "vet": True})
        else:
            runs.append({"t": m.group(4), "cursief": True})
        pos = m.end()
    if pos < len(rest):
        runs.append({"t": rest[pos:]})
    return runs or [{"t": tekst}]


# =====================================================================
#  Signalen — waarnemingen, geen ingrepen
# =====================================================================

def signalen(blokken: list, beelden: dict,
             losse_media: list | None = None) -> list:
    """Wat er aan deze brontekst opvalt en wat de vorm in de weg zit.

    Elk signaal draagt het blok-id, wat er aan de hand is, en wat het
    voor de opmaak betekent. Wat het níét draagt is een ingreep. De
    skill maakt hier wijzigingsvóórstellen van en legt die één voor één
    aan de gebruiker voor; pas na een expliciete ja gaat er iets aan de
    tekst veranderen.

    Er zitten twee soorten in de lijst en ze worden op een ander moment
    voorgelegd. Daarom draagt elk signaal een `groep`:

    * **`voorstel`** — een waarneming over één blok, grondstof voor een
      wijzigingsvoorstel in stap 3. Die stap komt ná de vormbesluiten,
      want of een kop van 66 tekens te lang is hangt af van het model.
    * **`vormbesluit`** — een waarneming over het document als geheel,
      die vóór het bouwen vast moet staan. Zie `_documentsignalen`.

    De vormbesluiten staan bovenaan, want ze zijn eerder aan de beurt.
    """
    uit: list = []
    lange_koppen = 0
    for i, b in enumerate(blokken):
        bid = b.get("id", "")
        soort = b.get("soort")
        tekst = b.get("tekst", "")

        if soort == "alinea" and HANDMATIG_TEKEN.match(tekst):
            uit.append({
                "id": bid, "soort": "handmatige-opsomming",
                "tekst": tekst[:120],
                "wat": "Deze alinea begint met een opsommingsteken maar is niet "
                       "als lijst opgemaakt.",
                "voor de vorm": "Als lijst gezet springt hij in en krijgt hij het "
                                "merkteken; als alinea blijft het teken gewoon "
                                "tekst midden in de kolom.",
                "wijziging": "het teken aan het begin vervalt, de tekst zelf niet"})

        if soort == "kop" and len(tekst) > 62:
            lange_koppen += 1
            uit.append({
                "id": bid, "soort": "lange-kop", "tekst": tekst,
                "tekens": len(tekst),
                "wat": f"Kop van {len(tekst)} tekens.",
                "voor de vorm": "Loopt over drie regels of meer en duwt de tekst "
                                "eronder weg. In de inhoudsopgave breekt hij af.",
                "wijziging": "inkorten, of splitsen in een kop en een chapeau"})

        if soort == "alinea":
            woorden = len(tekst.split())
            if woorden > 220:
                uit.append({
                    "id": bid, "soort": "lange-alinea", "woorden": woorden,
                    "tekst": tekst[:120],
                    "wat": f"Alinea van {woorden} woorden.",
                    "voor de vorm": "Vult meer dan een halve pagina zonder ingang. "
                                    "Er is geen plek om een figuur of een kantnoot "
                                    "naast te zetten.",
                    "wijziging": "splitsen op een zinsgrens, zonder woorden te wijzigen"})
            telling = len(re.findall(r"\b(ten eerste|ten tweede|ten derde|"
                                     r"allereerst|vervolgens|tot slot|daarnaast)\b",
                                     tekst, re.I))
            if telling >= 3:
                uit.append({
                    "id": bid, "soort": "opsomming-in-proza", "tekst": tekst[:160],
                    "wat": f"{telling} opsommende signaalwoorden in één alinea.",
                    "voor de vorm": "Dit is een lijst die als proza is opgeschreven. "
                                    "Als 1-2-3 leest hij sneller en kan hij naast "
                                    "een figuur.",
                    "wijziging": "de alinea wordt een genummerde lijst; de "
                                 "signaalwoorden vervallen of blijven staan"})

        if soort == "tabel":
            kolommen = max((sum(c["span"] for c in r["cellen"]) for r in b["rijen"]),
                           default=0)
            if kolommen > 6:
                uit.append({
                    "id": bid, "soort": "brede-tabel", "kolommen": kolommen,
                    "wat": f"Tabel met {kolommen} kolommen.",
                    "voor de vorm": "Past niet in een tekstkolom en nauwelijks over "
                                    "de volle zetspiegel.",
                    "wijziging": "kantelen, splitsen, of als losse bijlage"})
            if not any(r["kop"] for r in b["rijen"]) and len(b["rijen"]) > 1:
                uit.append({
                    "id": bid, "soort": "tabel-zonder-kop",
                    "wat": "Deze tabel heeft geen als kop gemarkeerde rij.",
                    "voor de vorm": "Breekt de tabel over een paginagrens, dan staat "
                                    "het vervolg zonder kolomnamen.",
                    "wijziging": "de eerste rij als kop aanmerken (opmaak, geen tekst)"})

        if soort == "beeld":
            volgend = blokken[i + 1] if i + 1 < len(blokken) else {}
            if volgend.get("soort") != "bijschrift" and not b.get("bijschrift"):
                uit.append({
                    "id": bid, "soort": "beeld-zonder-bijschrift",
                    "wat": "Beeld zonder bijschrift in de bron.",
                    "voor de vorm": "Een figuur zonder bijschrift heeft geen eenheid "
                                    "en geen bron, en is dan niet te lezen.",
                    "wijziging": "een bijschrift toevoegen — dat is nieuwe tekst"})

    for naam, info in beelden.items():
        if info.get("breedte") and info["breedte"] < 900:
            uit.append({
                "id": info["bestand"], "soort": "beeld-te-klein",
                "breedte": info["breedte"],
                "wat": f"Beeld van {info['breedte']} px breed.",
                "voor de vorm": "Over de volle zetspiegel komt dat op "
                                f"{round(info['breedte'] / (650 / 96) )} dpi; "
                                "onder 150 dpi is het op papier zichtbaar zacht.",
                "wijziging": "geen — een beter bestand opvragen"})

    niveaus = [b["niveau"] for b in blokken if b.get("soort") == "kop"]
    for a, b in zip(niveaus, niveaus[1:]):
        if b - a > 1:
            uit.append({
                "id": "", "soort": "kopniveau-sprong",
                "wat": f"Er springt een kopniveau over: van {a} naar {b}.",
                "voor de vorm": "De inhoudsopgave krijgt een gat en de "
                                "hoofdstuknummering klopt niet meer.",
                "wijziging": "een niveau opschuiven (opmaak, geen tekst)"})
            break

    for sig in uit:
        sig.setdefault("groep", "voorstel")
    return _documentsignalen(blokken, beelden, losse_media or []) + uit


def _tel(n: int, enkel: str, meer: str) -> str:
    """"1 kop" of "4 koppen".

    Klein, en het staat er toch. Een lijst die "1 koppen hebben niets
    onder zich" zegt, wordt gelezen als een lijst die niet weet waar hij
    het over heeft, en dan wordt de rest ook niet meer geloofd.
    """
    return f"{n} {enkel if n == 1 else meer}"


def _documentsignalen(blokken: list, beelden: dict, losse_media: list) -> list:
    """Zes waarnemingen over het document als geheel, en niet over een blok.

    Deze zes zijn een ander soort signaal dan de rest. De andere zeggen
    "hier zou een wijzigingsvoorstel kunnen liggen" en komen in stap 3
    langs, ná de vormbesluiten. Deze zes zijn zelf een vormbesluit en ze
    moeten vóór het bouwen vaststaan. Ze komen alle zes uit één echt
    rapport — Engels, 18.043 woorden, 522 blokken, 72 eindnoten, vijf
    bijlagen, zes figuren waarvan vier EMF — en ze waren daar alle zes
    bij het inlezen al te zien. Ze kostten pas tijd toen ze in de
    visuele loop naar boven kwamen, en dat is tachtig gezette pagina's
    later.

    Ze dragen daarom `groep: vormbesluit` en `besluit` waar de andere
    `wijziging` dragen: er valt niets aan de tekst te veranderen, er valt
    iets te besluiten voordat er gebouwd wordt.

    Van elk van de zes komt er hoogstens één in de lijst, hoe vaak het
    geval zich ook voordoet. Over vier EMF-figuren is één besluit te
    nemen; vier losse regels maken van een besluit een lijst, en een
    lijst wordt overgeslagen.
    """
    uit: list = []
    koppen = [b for b in blokken
              if b.get("soort") == "kop" and b.get("tekst", "").strip()]
    niveaus = [b.get("niveau", 1) for b in koppen]

    # -- de taal --------------------------------------------------------
    # Alleen de lopende tekst, niet de tabellen: daar staan getallen en
    # kolomnamen in, en die zeggen niets over de taal waarin geschreven
    # is. Onder de tachtig woorden wordt er niets gemeld — dan is elke
    # uitkomst toeval.
    lopend = " ".join(b.get("tekst", "") for b in blokken
                      if b.get("soort") != "tabel")
    woorden = re.findall(r"[a-zà-öø-ÿ]{1,20}", lopend.lower())
    if len(woorden) >= 80:
        tel = {taal: sum(1 for w in woorden if w in lijst)
               for taal, lijst in _TAALUNIEK.items()}
        top = max(tel, key=lambda t: tel[t])
        # Twee keer zoveel treffers als het Nederlands én minstens vier
        # procent van alle woorden. De eerste eis vangt de Nederlandse
        # tekst met Engelse citaten erin — daar wint het Nederlands
        # ruim. De tweede vangt de tekst die in geen van de vier talen
        # staat: dan is de winnaar toevallig de hoogste van vier lage
        # tellingen, en dan hoort er niets gemeld te worden.
        if (top != "nederlands" and tel[top] >= 2 * tel["nederlands"]
                and tel[top] >= 0.04 * len(woorden)):
            uit.append({
                "id": "", "groep": "vormbesluit", "soort": "bron-niet-nederlands",
                "taal": top,
                "treffers": {t: tel[t] for t in sorted(tel, key=lambda x: -tel[x])},
                "woorden": len(woorden),
                "wat": f"Op {len(woorden)} woorden lopende tekst telt het "
                       f"{top.capitalize()} {tel[top]} functiewoorden en het "
                       f"Nederlands {tel['nederlands']}. De bron is "
                       f"{top.capitalize()}.",
                "voor de vorm": "Alles wat de skill zelf zet staat in het "
                                "Nederlands: 'Bijlage', 'Figuur', 'Inhoud', de "
                                "kopregel, de folio, het bronvermeldingsmodel. "
                                "In een Engels rapport staat dat er straks "
                                "half doorheen.",
                "besluit": "in welke taal het gezette rapport staat, en of de "
                           "vaste woorden en de afbreking meegaan"})

    # -- de koppen een niveau te diep ------------------------------------
    # Word-documenten die uit een sjabloon komen beginnen soms bij Kop 2,
    # omdat Kop 1 voor de omslag was. Dan wordt elk hoofdstuk een sectie,
    # klopt de inhoudsopgave niet en krijgt geen enkele hoofdstukopener
    # een eigen pagina. Vier koppen als ondergrens, want bij twee of drie
    # is een document zonder niveau 1 net zo goed een fragment.
    if len(koppen) >= 4 and min(niveaus) >= 2:
        uit.append({
            "id": "", "groep": "vormbesluit", "soort": "koppen-een-niveau-te-diep",
            "hoogste_niveau": min(niveaus), "koppen": len(koppen),
            "wat": f"{_tel(len(koppen), 'kop', 'koppen')}, en de hoogste staat "
                   f"op niveau {min(niveaus)}. Niveau 1 komt niet voor.",
            "voor de vorm": "Elk hoofdstuk wordt een sectie. De inhoudsopgave "
                            "krijgt geen enkele regel op het bovenste niveau en "
                            "er komt geen hoofdstukopener op de pagina.",
            "besluit": "of alle koppen een niveau omhoog gaan voordat er "
                       "gebouwd wordt (opmaak, geen tekst)"})

    # -- de koppen nummeren zichzelf --------------------------------------
    # Per niveau geteld, en niet over alle koppen samen. Eén kop met een
    # nummer is een uitzondering; een heel kopniveau dat zichzelf nummert
    # is een vormbesluit. Het Nederlandse proefrapport laat zien waarom
    # het onderscheid nodig is: daar dragen twee van de negen koppen op
    # niveau 1 een letter — "Bijlage A" en "Bijlage B" — en dat is
    # precies het geval dat geen signaal hoort te zijn.
    per_niveau: dict = {}
    for b in koppen:
        per_niveau.setdefault(b.get("niveau", 1), []).append(b)
    genummerd = []
    for niveau in sorted(per_niveau):
        groep = per_niveau[niveau]
        raak = [b for b in groep if EIGEN_NUMMER.match(b["tekst"].strip())]
        if len(raak) >= 3 and len(raak) >= 0.6 * len(groep):
            genummerd.append((niveau, len(groep), raak))
    if genummerd:
        zin = "; ".join(f"op niveau {n} dragen {len(raak)} van de {totaal} koppen "
                        f"hun eigen nummer" for n, totaal, raak in genummerd)
        uit.append({
            "id": "", "groep": "vormbesluit", "soort": "kop-nummert-zichzelf",
            "niveaus": [{"niveau": n, "koppen": totaal, "genummerd": len(raak),
                         "voorbeelden": [b["tekst"].strip()[:60] for b in raak[:3]]}
                        for n, totaal, raak in genummerd],
            "wat": zin[:1].upper() + zin[1:] + ".",
            "voor de vorm": "De skill nummert de koppen zelf. Blijft het nummer "
                            "in de tekst staan, dan komt er straks '3 3.2 "
                            "Werkwijze' op de pagina en in de inhoudsopgave.",
            "besluit": "of de skill nummert en het nummer uit de koptekst valt, "
                       "of dat de bronnummering blijft staan en de skill niet "
                       "nummert"})

    # -- beeld dat een browser niet toont ---------------------------------
    onrenderbaar = []
    for naam, info in sorted(beelden.items()):
        ext = Path(naam).suffix.lower().lstrip(".")
        if ext in NIET_RENDERBAAR:
            onrenderbaar.append({"naam": naam, "formaat": NIET_RENDERBAAR[ext],
                                 "bytes": info.get("bytes", 0)})
    if onrenderbaar:
        if len(onrenderbaar) == len(beelden):
            hoeveel = ("Het enige beeldbestand staat" if len(beelden) == 1
                       else f"Alle {len(beelden)} beeldbestanden staan")
        else:
            hoeveel = (f"{len(onrenderbaar)} van de {len(beelden)} beeldbestanden "
                       + ("staat" if len(onrenderbaar) == 1 else "staan"))
        uit.append({
            "id": "", "groep": "vormbesluit", "soort": "beeld-niet-renderbaar",
            "aantal": len(onrenderbaar), "van": len(beelden),
            "bestanden": onrenderbaar,
            "wat": hoeveel + " in een formaat dat een browser niet toont: "
                   + ", ".join(sorted({b["formaat"] for b in onrenderbaar})) + ".",
            "voor de vorm": "Het rapport wordt in Chromium gezet. Zo'n figuur "
                            "komt niet als foutmelding op de pagina maar als een "
                            "leeg vlak, op de plek en in de maat die ervoor "
                            "gereserveerd is.",
            "besluit": "wie ze omzet naar png of svg, en in welke maat — dat "
                       "gebeurt vóór het bouwen en niet erna"})

    # -- beeld dat buiten de tekststroom zit -------------------------------
    if losse_media:
        uit.append({
            "id": "", "groep": "vormbesluit", "soort": "beeld-buiten-de-stroom",
            "aantal": len(losse_media), "bestanden": losse_media[:12],
            "wat": _tel(len(losse_media), "beeldbestand", "beeldbestanden")
                   + " in het .docx "
                   + ("wordt" if len(losse_media) == 1 else "worden")
                   + " door geen enkel blok genoemd.",
            "voor de vorm": "Een tekstvak, een SmartArt, een Word-diagram of een "
                            "figuur in de koptekst zit niet in de tekststroom. "
                            "Het wordt niet ingelezen, het staat niet in "
                            "document.json en het komt dus niet in het rapport.",
            "besluit": "of ze meemoeten, en zo ja achter welk blok — dat staat "
                       "nergens in het bestand en kan alleen gevraagd worden"})

    # -- een kop zonder inhoud ---------------------------------------------
    # Alleen melden als er géén diepere kop volgt. Een hoofdstukkop die
    # direct door zijn eerste sectiekop wordt gevolgd is de gewone vorm en
    # geen fout; zonder die toets gaf het Engelse rapport uit de docstring
    # hierboven zes treffers waarvan er één echt was, en een lijst die vijf
    # keer onzin zegt wordt in zijn geheel niet meer gelezen.
    #
    # Twee koppen op hét bovenste niveau achter elkaar tellen om dezelfde
    # reden niet mee: dat is de deeltitel — "Bijlagen" met "Bijlage A" en
    # "Bijlage B" eronder — en die hoort leeg te zijn.
    bovenste = min(niveaus) if niveaus else 1
    zonder = []
    for i, b in enumerate(blokken):
        if b.get("soort") != "kop" or not b.get("tekst", "").strip():
            continue
        volgend = blokken[i + 1] if i + 1 < len(blokken) else None
        if volgend is None:
            zonder.append(b)
            continue
        if volgend.get("soort") != "kop":
            continue
        n, m = b.get("niveau", 1), volgend.get("niveau", 1)
        if m > n or (m == n and n == bovenste):
            continue
        zonder.append(b)
    if zonder:
        uit.append({
            "id": "", "groep": "vormbesluit", "soort": "kop-zonder-inhoud",
            "aantal": len(zonder),
            "koppen": [{"id": b.get("id", ""), "niveau": b.get("niveau", 1),
                        "tekst": b["tekst"].strip()[:70]} for b in zonder],
            "wat": _tel(len(zonder), "kop heeft", "koppen hebben")
                   + " niets onder zich: geen alinea, geen lijst, geen tabel, "
                     "geen beeld en geen diepere kop.",
            "voor de vorm": "Zo'n kop komt onderaan een pagina te staan met wit "
                            "eronder, of hij krijgt een eigen opener zonder tekst "
                            "erachter. In de inhoudsopgave verwijst hij naar niets.",
            "besluit": "of de kop blijft staan, samengaat met de volgende, of "
                       "eruit valt — dat laatste is een tekstwijziging en gaat "
                       "langs stap 3"})

    return uit


# =====================================================================
#  Samenstellen
# =====================================================================

def apparaat(blokken: list, noten: dict) -> dict:
    """Wat er aan verwijzingsapparaat in de bron zit.

    De skill mag hierna alleen aanbieden wat er werkelijk ligt. Een
    rapport zonder noten hoeft geen keuze tussen voetnoten en eindnoten,
    en een rapport zonder bronnenlijst kan er geen krijgen — die zou
    verzonnen moeten worden, en dat is precies wat deze skill niet doet.

    Wat hier gedetecteerd wordt is de plaats van het apparaat, niet de
    citatiestijl van de auteur. Die stijl staat in de lopende tekst en
    verandert nooit; hij wordt alleen geteld, zodat de skill kan zeggen
    "dit rapport citeert op auteur-jaar" en de gebruiker weet wat voor
    bronnenlijst erbij hoort.
    """
    uit: dict = {"voetnoten": len([n for n in noten if not n.startswith("e")]),
                 "eindnoten": len([n for n in noten if n.startswith("e")])}

    # De bronnenlijst: een kop die er een aankondigt, plus alles tot de
    # eerstvolgende kop van hetzelfde of een hoger niveau.
    lijst = None
    for i, b in enumerate(blokken):
        if b.get("soort") != "kop" or not BRONNENKOP.match(b.get("tekst", "").strip()):
            continue
        niveau = b.get("niveau", 2)
        einde = len(blokken)
        for j in range(i + 1, len(blokken)):
            k = blokken[j]
            if k.get("soort") == "kop" and k.get("niveau", 9) <= niveau:
                einde = j
                break
        regels = [k for k in blokken[i + 1:einde]
                  if k.get("soort") in ("alinea", "lijst") and k.get("tekst", "").strip()]
        if regels:
            lijst = {"kop_id": b["id"], "kop": b["tekst"].strip(),
                     "vanaf": regels[0]["id"], "tot": regels[-1]["id"],
                     "aantal": len(regels)}
    if lijst:
        uit["bronnenlijst"] = lijst

    # De bijlagen: vanaf de eerste kop die er een aankondigt.
    bijlagekoppen = [b for b in blokken
                     if b.get("soort") == "kop"
                     and BIJLAGEKOP.match(b.get("tekst", "").strip())]
    if bijlagekoppen:
        uit["bijlagen"] = {"vanaf": bijlagekoppen[0]["id"],
                           "koppen": [{"id": b["id"], "tekst": b["tekst"].strip(),
                                       "niveau": b.get("niveau", 1)}
                                      for b in bijlagekoppen]}

    # De citatiestijl in de lopende tekst, alleen geteld.
    aj = gn = 0
    for b in blokken:
        t = b.get("tekst", "")
        if not t:
            continue
        aj += len(AUTEUR_JAAR.findall(t))
        gn += len(GENUMMERD.findall(t))
    uit["citaten"] = {"auteur_jaar": aj, "genummerd": gn}
    return uit


def bouw_document(blokken: list, noten: dict, kern: dict,
                  beelden: dict, bron: Path) -> dict:
    schoon: list = []
    nr = 0
    for b in blokken:
        if b.get("soort") == "leeg":
            continue
        nr += 1
        b["id"] = f"b{nr:04d}"
        if b.get("beeld"):
            b["beeldbestanden"] = [beelden[n]["bestand"] for n in b["beeld"]
                                   if n in beelden]
            b["beeldinfo"] = [beelden[n] for n in b["beeld"] if n in beelden]
        schoon.append(b)

    # Een bijschrift dat direct op een beeld volgt, hoort erbij.
    for i, b in enumerate(schoon):
        if b["soort"] == "bijschrift" and i and schoon[i - 1]["soort"] == "beeld":
            schoon[i - 1]["bijschrift"] = b["tekst"]
            # De runs gaan mee en niet alleen de platte tekst. Zonder dit
            # verdwijnt alles wat in het bijschrift cursief staat — een
            # boektitel, een vreemd woord — en, erger, een
            # voetnootverwijzing. Gemeten op het proefrapport: noot 2
            # stond in een bijschrift en kwam nergens in het rapport
            # terecht; `tekstcheck.py` meldde hem als verdwenen.
            schoon[i - 1]["bijschrift_runs"] = b["runs"]
            schoon[i - 1]["bijschrift_id"] = b["id"]
            b["hoort_bij"] = schoon[i - 1]["id"]

    titel = kern.get("titel") or next(
        (b["tekst"] for b in schoon if b["soort"] == "titel"), None) or next(
        (b["tekst"] for b in schoon if b["soort"] == "kop" and b["niveau"] == 1), None)

    tekens = sum(len(normaliseer(b.get("tekst", ""))) for b in schoon)
    return {
        "bron": bron.name,
        "titel": titel,
        "kern": kern,
        "blokken": schoon,
        "voetnoten": noten,
        "beelden": beelden,
        "apparaat": apparaat(schoon, noten),
        "telling": {
            "blokken": len(schoon),
            "koppen": sum(1 for b in schoon if b["soort"] == "kop"),
            "alineas": sum(1 for b in schoon if b["soort"] == "alinea"),
            "lijstregels": sum(1 for b in schoon if b["soort"] == "lijst"),
            "tabellen": sum(1 for b in schoon if b["soort"] == "tabel"),
            "beelden": sum(1 for b in schoon if b.get("beeld")),
            "voetnoten": len(noten),
            "tekens": tekens,
            "woorden": sum(len(b.get("tekst", "").split()) for b in schoon),
        },
    }


def brontekst(doc: dict) -> str:
    """De vingerafdruk: één genormaliseerde regel per blok, in volgorde.

    Tabellen komen als hun cellen achter elkaar, gescheiden door een
    tab, want dat is de leesvolgorde. Voetnoten staan onderaan, want ze
    horen bij het rapport en niet bij de alinea waar ze in staan.
    """
    regels = []
    for b in doc["blokken"]:
        if b["soort"] == "tabel":
            for rij in b["rijen"]:
                cel = [normaliseer(c["tekst"]) for c in rij["cellen"]]
                regels.append(f"{b['id']}\t" + "\t".join(cel))
        else:
            regels.append(f"{b['id']}\t{normaliseer(b.get('tekst', ''))}")
    for nid, noot in sorted(doc["voetnoten"].items()):
        regels.append(f"noot{nid}\t{normaliseer(noot['tekst'])}")
    return "\n".join(regels) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bron", type=Path, help=".docx, .md of .txt")
    ap.add_argument("--uit", type=Path, required=True, help="de werkmap")
    a = ap.parse_args()

    if not a.bron.exists():
        sys.exit(f"niet gevonden: {a.bron}")
    a.uit.mkdir(parents=True, exist_ok=True)

    if a.bron.suffix.lower() in (".docx", ".dotx", ".docm"):
        d = Docx(a.bron)
        blokken, noten, kern = d.lees()
        gebruikt = {n for b in blokken for n in b.get("beeld", [])}
        beelden = d.beelden(a.uit / "beeld", gebruikt)
        los = d.losse_media(gebruikt)
    elif a.bron.suffix.lower() in (".md", ".markdown", ".txt"):
        blokken, noten, kern = lees_markdown(a.bron)
        beelden, los = {}, []
        for b in blokken:
            for naam in b.get("beeld", []):
                p = (a.bron.parent / naam)
                if p.exists():
                    doel = a.uit / "beeld" / p.name
                    doel.parent.mkdir(parents=True, exist_ok=True)
                    doel.write_bytes(p.read_bytes())
                    beelden[naam] = {"bestand": f"beeld/{p.name}",
                                     "bytes": doel.stat().st_size,
                                     **_beeldmaat(doel.read_bytes())}
    else:
        sys.exit(f"onbekend formaat: {a.bron.suffix}. Lever .docx, .md of .txt aan.")

    doc = bouw_document(blokken, noten, kern, beelden, a.bron)
    sig = signalen(doc["blokken"], beelden, los)

    (a.uit / "document.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    (a.uit / "bron-tekst.txt").write_text(brontekst(doc), encoding="utf-8")
    (a.uit / "signalen.json").write_text(
        json.dumps(sig, ensure_ascii=False, indent=1), encoding="utf-8")

    ap = doc["apparaat"]
    print(json.dumps({
        "werkmap": str(a.uit),
        "titel": doc["titel"],
        **doc["telling"],
        "apparaat": {
            "voetnoten": ap["voetnoten"],
            "eindnoten": ap["eindnoten"],
            "bronnenlijst": (f'{ap["bronnenlijst"]["aantal"]} regels onder '
                             f'"{ap["bronnenlijst"]["kop"]}"')
                            if ap.get("bronnenlijst") else "geen gevonden",
            "bijlagen": (f'{len(ap["bijlagen"]["koppen"])} koppen, vanaf '
                         f'{ap["bijlagen"]["vanaf"]}')
                        if ap.get("bijlagen") else "geen gevonden",
            "citaten in de tekst": ap["citaten"],
        },
        "signalen": len(sig),
        "vormbesluiten": [s["soort"] for s in sig if s["groep"] == "vormbesluit"],
        "signaalsoorten": sorted({s["soort"] for s in sig
                                  if s["groep"] == "voorstel"}),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
