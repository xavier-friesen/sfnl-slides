#!/usr/bin/env python3
"""Meet aan een gebouwd `.docx` wat stil misgaat en op de render niet te zien is.

Dit is geen poort en geen vormoordeel. De vorm beoordeel je door naar het
document te kijken; hier staan negen dingen die je juist *niet* ziet doordat
het bestand er precies zo uitziet als bedoeld terwijl er iets anders in staat.

**Vier ervan blokkeren**, en dat zijn precies de vier waar geen interpretatie
aan te pas komt:

* `sjabloon` — de bladmaat, de marges, `titlePg` of een van de vijf kop- en
  voetverwijzingen wijkt af van het sjabloon. Dan is er niet geërfd maar
  nagebouwd, en het document is een ander document dan het lijkt.
* `contenttype` — `/word/document.xml` staat nog op `template.main`. Het
  bestand heet `.docx` en Word behandelt het als sjabloon.
* `onbekende-stijl` — een `pStyle`, `rStyle` of `tblStyle` die niet in
  `styles.xml` staat. Word meldt dat niet: de alinea valt terug op
  `Standaard` en je ziet het aan de regelval, drie ronden later. Dit is de
  fout die je maakt door `Heading1` te schrijven waar `Kop1` moet staan,
  want de stijl-id's in dit sjabloon zijn Nederlands.
* `onbekende-nummering` — een `numId` die niet in `numbering.xml` staat. Dan
  is er geen opsommingsteken en geen indent.

**Vijf zijn een waarneming**: kijk ernaar en beslis.

* `harde-kleur` — een `w:color` in de body. Elke kleur hoort uit een stijl te
  komen; staat hij op de run, dan overleeft hij geen stijlwijziging. Drie
  verdicten, want dat zijn drie verschillende fouten: de waarde is een
  merkkleur (dan is alleen de plek fout), de waarde staat in
  `merk.VERVANGEN` (dan is het de kleur die de plugin tot 27 augustus 2026
  rendeerde, en dat is een preciezere aanwijzing dan "fout"), of de waarde is
  geen merkkleur.
* `harde-letter` — een `w:rFonts` in de body. De letters hangen in dit
  sjabloon aan de stijlen en niet aan het thema (`majorFont` en `minorFont`
  zijn béide Lato Light), dus een `rFonts` op een run is de manier om
  Montserrat kwijt te raken.
* `harde-maat` — een `w:sz` in de body. Zelfde verhaal, en het is hoe de
  kopladder scheef gaat staan.
* `plaatshouder` — `[DATUM]`, `[BEDRAG]`: iets wat de gebruiker moest
  invullen en nog in het bestand staat. Dit hoort niet stil te blijven staan.
* `letter` — de letter die `Kop1` in `styles.xml` vraagt, staat niet op deze
  machine. Dan substitueert Word bij het openen, zonder melding, en verandert
  de regelval van de kop. In de praktijk is dat Gotham; zie het
  Gotham-besluit in `bouw.py`. De letternaam staat niet in dit script maar
  wordt uit het bestand gelezen, want de naam is `Gotham Bold Regular` en
  niet `Gotham Bold`.

En één telling die geen fout is maar wel iets zegt: `lijst-niveau2`, het
aantal opsommingspunten op niveau 2. Niveau 2 van elke bulletdefinitie in dit
sjabloon is een `o` in Courier New, dus dat is een tweede letter op de pagina.

Gebruik:

    python qa_word.py werkmap/notitie.docx
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

HIER = Path(__file__).resolve().parent
WORTEL = HIER.parents[1]
SJABLOON = WORTEL / "assets" / "word" / "SFNL_Word_sjabloon.dotx"

sys.path.insert(0, str(WORTEL / "scripts" / "gedeeld"))
sys.path.insert(0, str(HIER))

#: Wat er in de `sectPr` gelijk moet zijn aan het sjabloon. Dit is de
#: mechanische vorm van "erven, niet herdefiniëren": als een van deze vijf
#: verschilt, is de bladmaat, de zetspiegel of het logo niet meer die van het
#: sjabloon.
SECTIE = ("pgSz", "pgMar", "titlePg", "headerReference", "footerReference")

BLOKKEREND = {"sjabloon", "contenttype", "onbekende-stijl",
              "onbekende-nummering"}


def _kaal(waarde) -> str:
    """Eén hexwaarde uit `merk.py`, in hoofdletters en zonder `#`."""
    h = waarde
    if isinstance(waarde, dict):
        h = waarde.get("hex") or waarde.get("hexwaarde") or ""
    elif hasattr(waarde, "hex"):
        h = waarde.hex
    h = str(h).lstrip("#").upper()
    return h if re.fullmatch(r"[0-9A-F]{6}", h) else ""


def _merkkleuren() -> tuple[dict[str, str], dict[str, str]]:
    """De merkkleuren en de achterhaalde waarden, uit `merk.py`.

    Twee dingen, want een harde kleur in de body is niet één fout maar drie
    verschillende. Een willekeurige rode waarde is geen merkkleur. De navy
    uit `KLEUREN` is dat wel, maar hoort uit de stijl te komen. En de navy
    uit `VERVANGEN` is de waarde die de plugin tot 27 augustus 2026
    rendeerde, en die aanwijzing is preciezer dan "geen merkkleur".

    De waarden staan hier met opzet niet als hexcijfers in de tekst. De
    grep-check van `preflight.py` kijkt naar het bestand en niet naar de
    Python-structuur, dus een hexwaarde in een docstring is voor die check
    niet van een hexwaarde in code te onderscheiden — en dat hoort zo, want
    anders is de volgende die er één in een commentaar zet ook vrij.
    """
    hex_naar_naam: dict[str, str] = {}
    achterhaald: dict[str, str] = {}
    try:
        from merk import KLEUREN                              # noqa: PLC0415
        for naam, waarde in KLEUREN.items():
            h = _kaal(waarde)
            if h:
                hex_naar_naam[h] = naam
    except ImportError:
        pass
    try:
        from merk import VERVANGEN                            # noqa: PLC0415
        for oud, naam in VERVANGEN.items():
            h = _kaal(oud)
            if h:
                achterhaald[h] = str(naam)
    except ImportError:
        pass
    return hex_naar_naam, achterhaald


def _sectie(document_xml: str) -> dict[str, list[str]]:
    """De vijf sectie-eigenschappen als vergelijkbare tekst."""
    m = re.search(r"<w:sectPr\b.*?</w:sectPr>", document_xml, re.S)
    if not m:
        return {}
    blok = m.group(0)
    uit: dict[str, list[str]] = {}
    for naam in SECTIE:
        uit[naam] = sorted(re.findall(rf"<w:{naam}\b[^>]*/?>", blok))
    return uit


def meet(docx: Path, sjabloon: Path = SJABLOON) -> dict:
    with zipfile.ZipFile(docx) as z:
        namen = set(z.namelist())
        doc = z.read("word/document.xml").decode("utf-8")
        styles = z.read("word/styles.xml").decode("utf-8")
        ct = z.read("[Content_Types].xml").decode("utf-8")
        numbering = (z.read("word/numbering.xml").decode("utf-8")
                     if "word/numbering.xml" in namen else "")

    bevindingen: list[dict] = []

    def zeg(soort: str, wat: str, **rest) -> None:
        bevindingen.append({"soort": soort, "wat": wat, **rest})

    # --- contenttype -----------------------------------------------------
    if "wordprocessingml.template.main+xml" in ct:
        zeg("contenttype",
            "/word/document.xml staat nog op template.main; Word ziet een "
            "sjabloon en niet een document")

    # --- de sectie tegen het sjabloon ------------------------------------
    if sjabloon.is_file():
        with zipfile.ZipFile(sjabloon) as z:
            sj = z.read("word/document.xml").decode("utf-8")
        a, b = _sectie(doc), _sectie(sj)
        for naam in SECTIE:
            if a.get(naam) != b.get(naam):
                zeg("sjabloon", f"w:{naam} wijkt af van het sjabloon",
                    gebouwd=a.get(naam), sjabloon=b.get(naam))
        for onderdeel in ("word/header1.xml", "word/header2.xml",
                          "word/footer2.xml", "word/media/image2.png"):
            if onderdeel not in namen:
                zeg("sjabloon", f"{onderdeel} zit niet in het bestand; "
                                "dan is de kop- of voettekst niet geërfd")
    else:
        zeg("waarschuwing", f"sjabloon niet gevonden op {sjabloon}; "
                            "de sectiecontrole is niet gedaan")

    # --- stijlen ----------------------------------------------------------
    bekend = set(re.findall(r'w:styleId="([^"]+)"', styles))
    for soort in ("pStyle", "rStyle", "tblStyle"):
        for sid in sorted(set(re.findall(rf'<w:{soort} w:val="([^"]+)"', doc))):
            if sid not in bekend:
                zeg("onbekende-stijl",
                    f"{soort} '{sid}' staat niet in styles.xml; de alinea "
                    "valt stil terug op Standaard")

    # --- nummering --------------------------------------------------------
    beschikbaar = set(re.findall(r'<w:num w:numId="([^"]+)"', numbering))
    for nid in sorted(set(re.findall(r'<w:numId w:val="([^"]+)"', doc))):
        if nid != "0" and nid not in beschikbaar:
            zeg("onbekende-nummering",
                f"numId {nid} staat niet in numbering.xml")

    # --- directe opmaak in de body ---------------------------------------
    merk, achterhaald = _merkkleuren()
    for hexv in sorted(set(re.findall(r'<w:color w:val="([0-9A-Fa-f]{6})"',
                                      doc))):
        h = hexv.upper()
        naam = merk.get(h)
        if naam:
            staart = f"; dat is {naam}, maar die hoort uit de stijl te komen"
        elif h in achterhaald:
            staart = (f"; dat is de waarde die de plugin tot 27 augustus 2026 "
                      f"voor {achterhaald[h]} rendeerde en niet de merkwaarde")
        else:
            staart = " en is geen merkkleur"
        zeg("harde-kleur",
            f"#{h} staat als directe opmaak in de body" + staart,
            merkkleur=bool(naam))
    for fam in sorted(set(re.findall(r'<w:rFonts w:ascii="([^"]+)"', doc))):
        zeg("harde-letter", f"'{fam}' staat als directe opmaak in de body")
    for sz in sorted(set(re.findall(r"<w:sz w:val=\"(\d+)\"", doc))):
        zeg("harde-maat",
            f"corps {int(sz) / 2:g} pt staat als directe opmaak in de body")

    # --- plaatshouders ----------------------------------------------------
    from bouw import PLAATSHOUDER                             # noqa: PLC0415
    tekst = " ".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", doc, re.S))
    for p in sorted(set(PLAATSHOUDER.findall(tekst))):
        zeg("plaatshouder", f"[{p}] staat nog in het document")

    # --- de letter van Kop1 ----------------------------------------------
    # Geen letternaam in dit script: wat Kop1 vraagt staat in styles.xml en
    # wordt daaruit gelezen. De vraag is niet "is het Gotham" maar "staat de
    # letter die er in het bestand staat op deze machine" -- want elke
    # familie die ontbreekt wordt stil gesubstitueerd, niet alleen die ene.
    from bouw import gothamnaam, letter_aanwezig               # noqa: PLC0415
    gevraagd = gothamnaam(styles)
    if gevraagd and not letter_aanwezig(gevraagd):
        zeg("letter",
            f"Kop1 vraagt '{gevraagd}' en die letter staat niet op deze "
            "machine; Word substitueert bij het openen zonder melding, en "
            "dan verandert de regelval van de kop")

    niveau2 = len(re.findall(r'<w:ilvl w:val="[1-9]"/>', doc))

    telling: dict[str, int] = {}
    for b in bevindingen:
        telling[b["soort"]] = telling.get(b["soort"], 0) + 1

    return {
        "docx": str(docx),
        "blokkeert": sorted(t for t in telling if t in BLOKKEREND),
        "telling": telling,
        "lijst_niveau2": niveau2,
        "kop1_letter": gevraagd,
        "bevindingen": bevindingen,
    }


def main() -> int:
    a = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("docx", type=Path)
    a.add_argument("--sjabloon", type=Path, default=SJABLOON)
    args = a.parse_args()
    if not args.docx.is_file():
        raise SystemExit(f"niet gevonden: {args.docx}")

    uit = meet(args.docx, args.sjabloon)
    print(json.dumps(uit, indent=2, ensure_ascii=False))
    if uit["blokkeert"]:
        print("\nblokkeert: " + ", ".join(uit["blokkeert"]), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
