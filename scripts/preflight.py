"""Report what this machine can do before you start building.

Usage:
    python preflight.py
    python preflight.py --json

Run this FIRST, once per session. It answers three questions in one go:

  1. Are the Python packages the scripts need importable?
  2. Is there a renderer, so the visual loop can actually run?
  3. Staat de merklaag gelijk met zichzelf — `assets/gedeeld/merk.css` zoals
     `scripts/gedeeld/merk.py` hem zou schrijven, en geen merkkleur die ergens
     anders nog als hexwaarde staat?

Output:

    {
      "python":    {"executable": "...", "version": "3.12.x", "platform": "win32"},
      "deps":      {"pptx": true, "lxml": true, "defusedxml": true, ...},
      "renderers": {"powerpoint_com": true, "soffice": null, "soffice_probe": {...},
                    "pdf_to_png": null},
      "merk":      {"klopt": true, "uit_de_pas": [], "hardgecodeerd": [], ...},
      "potx_thema": {"klopt": true, "verouderd": []},
      "verdict":   "full" | "qa-only",
      "missing":   [...],
      "remediation": [...]
    }

`verdict` is the whole point:

* **full** — a renderer works. Build, render, look at the slides, fix what you see.
* **qa-only** — no renderer. You may still build, but you cannot see the result, and
  dan is er geen vormbeoordeling. Dat is het punt van deze vlag, en er komt geen script
  dat het gat vult: wat er nog wél is, is `qa_text.py` voor de hygiëne (restplaceholders,
  Calibri, harde hex, autofit) en `qa_tellingen.py` voor de tellingen (maten per rol,
  bandfrequentie, exhibits bij cijfers, maatsprong, twee families in één alinea, de hoge
  punt). Die twee zien geen overlap, geen contrast, geen dood wit en geen baseline.
  `deck-visual-reviewer` doet dan een structurele XML-review en zegt dat expliciet, en de
  oplevering zegt in zoveel woorden dat de deck niet visueel geverifieerd is. Blind bouwen
  ZONDER dat te zeggen is het defect waarvoor deze vlag bestaat.

Waarom hier geen `qa_fit.py` en `qa_typography.py` staan: die zijn er nooit geweest.
Vijf scripts haalden ze aan als "de poort in QA-only-modus" en de bouwer ging op een
poort vertrouwen die niet bestond. De repo zet zelf "Poorten: twee, en beide zijn een
mens" — het vragenvuur en de outline, geen mechanische poort — dus ze
zijn opgeruimd in plaats van geschreven.

`merk.klopt: false` is een fout en niet een waarschuwing, en hij staat daarom in
`missing`. Twee dingen kunnen hem zetten. `uit_de_pas` betekent dat `merk.css` of het
gestempelde blok in `stijl.css` niet is wat `merk.py` zou schrijven; dan draait er
gerenderd werk op een ander palet dan de merklaag zegt, en `python
scripts/gedeeld/merk.py --css` zet het recht. `hardgecodeerd` betekent dat een script of
een stylesheet een merkkleur als hexwaarde bij zich draagt in plaats van hem uit de
merklaag te halen; dat is de duplicaat waarmee de vijf verkeerde waarden van vóór 27
augustus 2026 hebben kunnen blijven staan, en de remedie is de waarde daar weghalen en
niet hier de melding.

Twee dingen zijn met opzet geen fout. `#FFFFFF` wordt niet geteld: wit is de enige
merkwaarde die geen besluit is, en hij staat in renderinfrastructuur die geen kleur
kiest. En `verouderd` — een hexwaarde die vóór de paletmigratie een merkkleur wás — staat
apart in de remediatie en blokkeert niet: het zijn geen merkwaarden meer, dus de melding
is een vondst en geen eis. Ze zitten in de renderoverlay en in de contactbladen, waar geen
kleur van een oplevering uit komt.

Exit code is ALWAYS 0, including when everything is missing: the JSON is the answer, and
"no renderer" is a valid answer that the caller has to read and act on, not a crash. Do
not gate a pipeline on this exit code — read `verdict`.

Dit script heeft zelf géén van de gecontroleerde pakketten nodig, ook niet indirect.
Zonder python-pptx komt er dus nog steeds geldige JSON uit, met `deps.pptx: false` en
`verdict: "qa-only"` — dat is het antwoord, geen traceback.

Missing packages are installable with:

    <PYEXE> -m pip install -r requirements.txt

Note on `python`: on Windows the bare command is often the Microsoft Store stub, which
prints "Python was not found" and exits non-zero without being a Python at all. Resolve
a real interpreter (python3, python, py -3) and use its full path everywhere; the
`python.executable` field below tells you which one ran this check.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import importlib
import shutil
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# `_deck` NIET op moduleniveau importeren.
#
# `_deck.py` importeert python-pptx bovenaan. Een `from _deck import emit, font_report`
# hier sleepte die eis mee, en dan stierf uitgerekend het script dat moet melden DÁT
# python-pptx ontbreekt aan dat gebrek: exitcode 1, stdout leeg, `check_imports` nooit
# bereikt. Preflight is de eerste stap van elke bouw; die stap stuurde de gebruiker een
# traceback debuggen in plaats van `pip install -r requirements.txt`.
#
# Dus: pas in `main()` ophalen, met een stand-in wanneer de import faalt. `emit` is een
# paar regels json en kan als stand-in niet uit de pas lopen. De fontmeting kán zonder
# `_deck` niet draaien, en zegt dat dan ook — ze doet niet alsof de fonts ontbreken,
# want er is niet gekeken.
# ---------------------------------------------------------------------------

FONT_CHECK_UNAVAILABLE = (
    "de fontmeting kon niet draaien: _deck.py heeft python-pptx nodig en dat ontbreekt. "
    "Over de meetbaarheid van de merkfonts is hiermee niets gezegd — installeer de "
    "requirements en draai preflight opnieuw."
)


def _fallback_emit(payload) -> None:
    """Wat `_deck.emit` doet, zonder `_deck`: UTF-8 JSON in één schrijfactie."""
    import json

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError, ValueError):
            pass
    try:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        sys.stdout.flush()
    except (OSError, ValueError):
        pass


def _fallback_font_report(families) -> dict:
    """Zelfde vorm als `_deck.font_report`, met `measured: False` als eerlijk verschil.

    `missing` blijft leeg: een lege `missing` betekent hier "niet gemeten", niet "alles
    gevonden", en `measured` maakt dat verschil leesbaar voor de caller. Een gevulde
    `missing` zou beweren dat de fonts er niet staan terwijl er niet gekeken is.
    """
    return {
        "pillow": None,
        "measured": False,
        "found": {},
        "missing": [],
        "hint": FONT_CHECK_UNAVAILABLE,
    }


def deck_helpers():
    """`(emit, font_report)` uit `_deck`, of de stand-ins hierboven."""
    try:
        from _deck import emit, font_report

        return emit, font_report
    except ImportError:
        return _fallback_emit, _fallback_font_report


# Import name -> what it is for and how to get it.
REQUIRED = {
    "pptx": ("python-pptx", "elke bouw- en QA-stap"),
    "lxml": ("lxml", "slide-XML lezen en schrijven, XSD-validatie"),
    "defusedxml": ("defusedxml", "veilig XML parsen in clean.py en de validators"),
}

OPTIONAL = {
    "PIL": ("pillow", "thumbnail.py (contactsheet van de renders)"),
    "pytest": ("pytest", "eigen tests; deze repo draagt zelf geen testsuite"),
}

# pdf->png ladder, same order render.py uses.
RASTER_TOOLS = ("pdftoppm", "pdftocairo", "mutool")

# De families die de meting nodig heeft. Titelmaten hangen aan Gotham Bold, body aan Lato
# Light, KPI's aan Montserrat SemiBold, de aanhef binnen een regel aan Lato Semibold.
MEASURED_FAMILIES = ("Gotham Bold", "Montserrat", "Montserrat SemiBold",
                     "Montserrat Light", "Lato Light", "Lato Semibold")

FONTCONFIG_SNIPPET = (
    "~/.config/fontconfig/fonts.conf met een <alias> per merkfont "
    "(Gotham Bold -> Montserrat SemiBold, Montserrat -> een geïnstalleerde sans, "
    "Lato Light -> Lato of Open Sans), daarna `fc-cache -f`. Dat maakt de "
    "LibreOffice-render dichter bij het echte deck; de meting van fit_title.py blijft "
    "een schatting zolang de échte bestanden ontbreken."
)


def check_imports(names: dict) -> dict:
    found = {}
    for module in names:
        try:
            importlib.import_module(module)
            found[module] = True
        except Exception:
            found[module] = False
    return found


def check_powerpoint_com() -> bool:
    """True when PowerPoint COM can actually be driven, not just imported."""
    if sys.platform != "win32":
        return False
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from render import com_available

        return com_available()
    except Exception:
        return False


def check_soffice() -> str | None:
    sys.path.insert(0, str(Path(__file__).resolve().parent / "office"))
    try:
        from soffice import soffice_binary

        return soffice_binary()
    except Exception:
        for name in ("soffice", "libreoffice"):
            found = shutil.which(name)
            if found:
                return found
        return None


# ---------------------------------------------------------------------------
# De renderermelding was ÉÉN KEER fout, en dat is de gevaarlijkste fout die dit script
# kan maken: de bouwer denkt dan visueel te verifiëren terwijl er niets rendert.
#
# Wat er gebeurde: in de meetomgeving stond alleen `libreoffice-core` en niet
# `libreoffice-impress`. `soffice` bestaat dan, staat op PATH, en `shutil.which` vindt
# hem — dus preflight meldde een renderer. Maar zonder Impress is er geen importfilter
# voor een pptx, en `soffice --convert-to pdf` antwoordde `Error: source file could not
# be loaded`, met exitcode 0. Op de aanwezigheid van het binary kun je dus niets bouwen.
#
# Daarom de echte proef, dezelfde soort proef die `render.py` doet met `com_available()`:
# een lege pptx wegschrijven en hem laten omzetten. De uitkomst is niet de exitcode maar
# de vraag of er een pdf staat. Kost hier 1,9 seconde, één keer per sessie.
# ---------------------------------------------------------------------------

PROBE_TIMEOUT = 120

# Wat soffice zegt als er geen importfilter is. Alleen voor de melding: het oordeel hangt
# aan de pdf, niet aan deze tekst.
NO_FILTER_HINT = "source file could not be loaded"


def probe_soffice() -> dict:
    """Laat LibreOffice écht een pptx omzetten. `{"ran", "ok", "detail"}`.

    `ran: False` betekent dat er niet geprobeerd kon worden — geen python-pptx om een
    proefdeck te schrijven, of soffice niet gevonden. Dat is niet hetzelfde als
    `ok: False`, en de JSON houdt die twee gescheiden: "niet geprobeerd" mag nooit lezen
    als "werkt", en ook niet als "werkt niet".
    """
    import glob
    import tempfile

    sys.path.insert(0, str(Path(__file__).resolve().parent / "office"))
    try:
        from pptx import Presentation
    except ImportError:
        return {"ran": False, "ok": None,
                "detail": "niet geprobeerd: zonder python-pptx is er geen proefdeck om "
                          "om te zetten. Het binary is gevonden, maar of het een pptx "
                          "kán openen is hiermee niet vastgesteld."}
    try:
        from soffice import run_soffice
    except ImportError as fout:
        return {"ran": False, "ok": None,
                "detail": f"niet geprobeerd: {fout}"}

    with tempfile.TemporaryDirectory(prefix="preflight_probe_") as tmp:
        deck = Path(tmp) / "probe.pptx"
        try:
            Presentation().save(str(deck))
        except Exception as fout:  # noqa: BLE001 - elk falen is hier "niet geprobeerd"
            return {"ran": False, "ok": None,
                    "detail": f"niet geprobeerd: proefdeck schrijven mislukte ({fout})"}
        try:
            result = run_soffice(
                ["--headless", "--convert-to", "pdf", "--outdir", tmp, str(deck)],
                timeout=PROBE_TIMEOUT, capture_output=True,
            )
        except Exception as fout:  # noqa: BLE001
            return {"ran": True, "ok": False,
                    "detail": f"soffice liep niet af: {fout}"}

        if glob.glob(str(Path(tmp) / "*.pdf")):
            return {"ran": True, "ok": True, "detail": "een lege pptx werd een pdf"}

        melding = " ".join(
            stream.decode("utf-8", "replace").strip()
            for stream in (result.stdout or b"", result.stderr or b"")
        ).strip()
        geen_filter = NO_FILTER_HINT in melding.lower()
        return {
            "ran": True,
            "ok": False,
            "geen_importfilter": geen_filter,
            "returncode": result.returncode,
            "detail": (
                "soffice zette de proef-pptx niet om en er staat geen pdf. "
                + ("De melding is 'source file could not be loaded': er is geen "
                   "importfilter voor pptx, en dat betekent vrijwel altijd dat "
                   "libreoffice-impress ontbreekt naast libreoffice-core. "
                   if geen_filter else "")
                + f"Exitcode was {result.returncode} — die zegt hier niets, soffice "
                  "geeft ook 0 als hij het bestand niet kon laden. "
                  f'Melding: "{melding[:200]}"'
            ),
        }


# ---------------------------------------------------------------------------
# De merklaag: staat ze gelijk met zichzelf?
#
# Dit is de mechanische helft van de toets die `reference/merk.md` bovenaan stelt:
# een kleurwaarde staat één keer. De andere helft — staat er een puntgrootte in
# merk.md — is een leesvraag en die staat hier niet.
#
# De check bestaat omdat het één keer echt is misgegaan. Vijf van de zes accenten
# in deze repo waren andere kleuren dan het themapalet van het Word-sjabloon, en
# ze stonden in zeven bestanden. Wie dat rechtzet vergeet er één, en dan is er
# geen manier om dat te merken: een oranje dat 3 procent afwijkt ziet er op een
# render precies zo uit als een oranje dat klopt. Vandaar: hergenereren en
# vergelijken, en daarnaast grepen naar de waarden zelf.
# ---------------------------------------------------------------------------

#: Waar een merkkleur niet als hexwaarde mag staan: elk script en elke
#: stylesheet. Wat er bewust NIET in staat is gebouwde uitvoer — de `.dc.html`-
#: artboards en de maatstaf-SVG's dragen hun kleuren omdat ze gerenderd zijn, en
#: die renders horen niet bij elke paletwijziging opnieuw gezet te worden.
#: De artboards staan erbij, en dat is een reparatie. Ze vielen buiten de poort
#: omdat ze "gebouwde uitvoer" leken, en dat was maar half waar: een `.dc.html`
#: draagt een gestempelde stylesheet met het `:root`-blok erin, en die veroudert
#: net zo goed als een `.css`. Gemeten na de paletmigratie van 27 augustus 2026:
#: `assets/documenten/voorbeeld-navy/Main.dc.html` droeg nog de vijf oude
#: waarden, en de maatstaf-PNG die eruit komt toont dus het oude navy — een
#: voorbeeld dat de verkeerde kleur leert, en de poort keek er niet naar.
MERK_GEZOCHT = (("scripts", "*.py"), ("assets", "*.css"), ("assets", "*.dc.html"))

#: Wat de grep niet aanrekent. `merk.py` en `merk.css` zijn de bron zelf, en wit
#: is de enige merkwaarde die geen besluit is: hij staat in de renderlaag als
#: achtergrond van een contactblad, en daar kiest niemand een kleur.
MERK_EIGEN = ("merk.py", "merk.css")
MERK_UITGEZONDERD = ("#FFFFFF",)


#: Het themapalet van het `.potx` is de derde plek waar merkkleuren staan, en de
#: poort keek er niet naar. Gemeten na de paletmigratie van 27 augustus 2026:
#: `theme1.xml` en `theme2.xml` droegen alle vijf de oude waarden, dus elk deck
#: uit deze plugin rendeerde in het oude oranje — terwijl `preflight.py`
#: `"klopt": true` meldde, want hij grepte scripts, stylesheets en artboards en
#: niet het thema in een zipbestand. Dat is precies de soort blinde vlek die de
#: merklaag moest opheffen.
#:
#: De slotindeling van het `.potx` is een ANDERE dan die van het Word-sjabloon:
#: hier is navy `accent6` en `dk2`, royal `accent3`, emerald `accent5` en sky
#: `accent4`. Daarom kijkt deze check naar de wáárden en niet naar de slots.
POTX_THEMAS = ("ppt/theme/theme1.xml", "ppt/theme/theme2.xml")


def check_potx_thema() -> dict:
    """Draagt het themapalet van het sjabloon de huidige merkwaarden?

    Alleen de vijf accenten die de migratie raakte; `theme3`/`theme4` zijn de
    Office-standaardthema's en geen merk.
    """
    import re
    import zipfile
    wortel = Path(__file__).resolve().parent.parent
    potx = wortel / "assets" / "sfnl-sjabloon.potx"
    uit: dict = {"bestand": potx.exists(), "verouderd": [], "klopt": None}
    if not potx.exists():
        uit["detail"] = "geen sjabloon om te controleren"
        return uit
    sys.path.insert(0, str(wortel / "scripts" / "gedeeld"))
    try:
        import merk
    except Exception as fout:  # noqa: BLE001
        uit["detail"] = f"merk.py niet te importeren ({fout})"
        return uit
    oud = {h.lstrip("#").upper(): n for h, n in merk.VERVANGEN.items()}
    try:
        with zipfile.ZipFile(potx) as z:
            aanwezig = set(z.namelist())
            for naam in POTX_THEMAS:
                if naam not in aanwezig:
                    continue
                s = z.read(naam).decode("utf-8", "replace")
                m = re.search(r"<a:clrScheme.*?</a:clrScheme>", s, re.S)
                if not m:
                    continue
                for c in re.finditer(r'val="([0-9A-Fa-f]{6})"', m.group(0)):
                    h = c.group(1).upper()
                    if h in oud:
                        uit["verouderd"].append(
                            {"waar": naam, "hex": "#" + h, "kleur": oud[h]})
    except (OSError, zipfile.BadZipFile) as e:
        uit["detail"] = f"sjabloon niet te lezen: {e}"
        return uit
    uit["klopt"] = not uit["verouderd"]
    return uit


def check_merk() -> dict:
    """`{"gemeten", "klopt", "uit_de_pas", "hardgecodeerd", "verouderd"}`.

    `gemeten: False` betekent dat er niet gekeken is — `merk.py` niet
    importeerbaar — en dat is niet hetzelfde als `klopt: True`. Zonder dat
    onderscheid zou een verplaatste merklaag lezen als een merklaag die klopt.
    """
    import re

    wortel = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(wortel / "scripts" / "gedeeld"))
    try:
        import merk
    except Exception as fout:  # noqa: BLE001 - elk falen is hier "niet gemeten"
        return {"gemeten": False, "klopt": None, "uit_de_pas": [],
                "hardgecodeerd": [], "verouderd": [],
                "hint": f"scripts/gedeeld/merk.py was niet te importeren ({fout}). "
                        "Over de merklaag is hiermee niets gezegd."}

    hoort_bij = {h.upper(): n for n, h in merk.HEX.items()
                 if h.upper() not in MERK_UITGEZONDERD}
    oud = {h.upper(): n for h, n in merk.VERVANGEN.items()}
    patroon = re.compile("|".join(re.escape(h) for h in (*hoort_bij, *oud)),
                         re.IGNORECASE)

    hard: list[dict] = []
    verouderd: list[dict] = []
    for map_, glob_ in MERK_GEZOCHT:
        for pad in sorted((wortel / map_).rglob(glob_)):
            if pad.name in MERK_EIGEN:
                continue
            try:
                regels = pad.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError):
                continue
            # Het gestempelde blok is de merklaag zelf, woordelijk. Dat het daar
            # staat is het punt; of het klopt gaat via `merk.verschillen()`, dat
            # het hergenereert in plaats van ernaar te kijken.
            binnen = False
            for nr, regel in enumerate(regels, 1):
                if merk.BEGIN in regel:
                    binnen = True
                elif merk.EINDE in regel:
                    binnen = False
                    continue
                if binnen:
                    continue
                for m in patroon.finditer(regel):
                    h = m.group(0).upper()
                    vondst = {"waar": f"{pad.relative_to(wortel).as_posix()}:{nr}",
                              "hex": m.group(0),
                              "kleur": hoort_bij.get(h) or oud[h]}
                    (hard if h in hoort_bij else verouderd).append(vondst)

    uit_de_pas = merk.verschillen()
    return {"gemeten": True,
            "klopt": not uit_de_pas and not hard,
            "uit_de_pas": uit_de_pas,
            "hardgecodeerd": hard,
            "verouderd": verouderd}


def check_raster() -> str | None:
    for name in RASTER_TOOLS:
        if shutil.which(name):
            return name
    return None


#: Wat een OS-pakketbeheerder moet leveren en pip niet kan. Dit is de lijst die
#: in een container of op een verse Debian ontbreekt, en waarvan het ontbreken
#: zich voordoet als iets anders:
#:
#: * `libreoffice-writer` — zonder deze laadt soffice geen enkele .docx, ook het
#:   sjabloon niet, en meldt `source file could not be loaded` met exitcode 0.
#: * `libreoffice-impress` — zelfde verhaal voor een .pptx. Dit is de fout die
#:   `probe_soffice()` hierboven opving, en de reden dat die proef bestaat.
#: * `poppler-utils` — levert `pdftoppm`. Zonder hem is er een PDF en geen PNG,
#:   dus dan kijk je naar de PDF en dat kan ook; niet blokkerend.
#:
#: Op een laptop met LibreOffice uit de .dmg of .msi is dit alles al aanwezig:
#: die installers leveren de hele suite. Het gesplitste geval bestaat op Debian
#: en Ubuntu, en in containers met een uitgeklede LibreOffice — en dat laatste
#: is precies waar deze plugin vaak draait.
OS_PAKKETTEN = ("libreoffice-writer", "libreoffice-impress", "poppler-utils")


def _pip(*pakketten: str) -> bool:
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                        "--break-system-packages", *pakketten],
                       capture_output=True, text=True)
    return r.returncode == 0


def herstel() -> dict:
    """Zet erbij wat te installeren is, en zeg wat een mens moet doen.

    Twee soorten ontbrekende dingen, en ze vragen iets anders. pip-pakketten
    kan dit script zelf halen. OS-pakketten alleen wanneer er een apt is en
    het script mag installeren; anders is de enige juiste uitkomst een
    opdrachtregel die de gebruiker zelf uitvoert. Nooit stil doorgaan alsof
    het gelukt is.
    """
    uit: dict = {"pip": {}, "os": {}, "handmatig": []}

    mist_pip = [naam for naam, ok in check_imports(REQUIRED).items() if not ok]
    mist_pip += [naam for naam, ok in check_imports(OPTIONAL).items() if not ok]
    if mist_pip:
        uit["pip"] = {"geprobeerd": mist_pip, "gelukt": _pip(*mist_pip)}

    apt = shutil.which("apt-get")
    nodig = []
    if not check_soffice():
        nodig += ["libreoffice-writer", "libreoffice-impress"]
    else:
        probe = probe_soffice()
        if probe.get("ok") is False:
            nodig += ["libreoffice-impress", "libreoffice-writer"]
    if not check_raster():
        nodig.append("poppler-utils")
    nodig = sorted(set(nodig))

    if not nodig:
        uit["os"] = {"nodig": [], "detail": "niets te doen"}
    elif apt:
        r = subprocess.run([apt, "install", "-y", "-qq", *nodig],
                           capture_output=True, text=True)
        uit["os"] = {"nodig": nodig, "gelukt": r.returncode == 0,
                     "detail": (r.stderr or "").strip()[:300]}
        if r.returncode != 0:
            uit["handmatig"].append("sudo apt-get install -y " + " ".join(nodig))
    else:
        uit["os"] = {"nodig": nodig, "gelukt": False,
                     "detail": "geen apt-get op deze machine"}
        uit["handmatig"].append(
            "installeer LibreOffice compleet (de .dmg of .msi levert de hele "
            "suite) en poppler-utils, of hun equivalent voor deze pakketbeheerder: "
            + ", ".join(nodig))
    return uit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="accepted for symmetry with the other scripts; output is always JSON",
    )
    parser.add_argument(
        "--herstel", action="store_true",
        help="zet erbij wat te installeren is, en zeg wat een mens zelf moet doen",
    )
    args = parser.parse_args()

    if args.herstel:
        print(json.dumps({"herstel": herstel()}, indent=2, ensure_ascii=False))
        print(file=sys.stderr)

    emit, font_report = deck_helpers()

    required = check_imports(REQUIRED)
    optional = check_imports(OPTIONAL)

    com = check_powerpoint_com()
    soffice = check_soffice()
    raster = check_raster()
    merk = check_merk()
    potx_thema = check_potx_thema()

    # Het binary vinden is niet hetzelfde als kunnen renderen: zie `probe_soffice`. Bij
    # `ran: False` is er niet geprobeerd, en dan blijft de aanwezigheid van het binary
    # het enige dat we weten — dat staat zo in de JSON en in de remediatie.
    probe = probe_soffice() if soffice else {
        "ran": False, "ok": None, "detail": "geen soffice gevonden om te proberen"}
    soffice_opent_pptx = probe["ok"] is not False

    # LibreOffice on its own renders nothing: it produces a PDF, and something has to
    # turn that into PNG.
    libreoffice_usable = bool(soffice and raster and soffice_opent_pptx)
    can_render = com or libreoffice_usable

    missing: list[str] = []
    remediation: list[str] = []

    for module, (package, purpose) in REQUIRED.items():
        if not required[module]:
            missing.append(package)
            remediation.append(f"{package} ontbreekt ({purpose})")
    for module, (package, purpose) in OPTIONAL.items():
        if not optional[module]:
            missing.append(f"{package} (optioneel)")
            remediation.append(f"{package} ontbreekt — alleen nodig voor {purpose}")

    if missing:
        remediation.append(
            f'"{sys.executable}" -m pip install -r requirements.txt'
        )

    if not can_render:
        missing.append("renderer")
        if soffice and probe["ok"] is False:
            remediation.append(
                "LibreOffice staat er, maar hij kan geen pptx openen: de proefconversie "
                "leverde geen pdf. " + probe["detail"] + " Remedie: installeer "
                "libreoffice-impress naast libreoffice-core (apt: "
                "`apt-get install -y libreoffice-impress`), en voor de png-stap "
                "poppler-utils (pdftoppm) of mupdf-tools (mutool). Meld tot dan dat het "
                "deck niet visueel geverifieerd is — een gevonden binary is geen renderer."
            )
        elif soffice and not raster:
            remediation.append(
                "LibreOffice staat er, maar geen pdf->png-omzetter: installeer "
                "poppler-utils (pdftoppm) of mupdf-tools (mutool)"
            )
        elif sys.platform == "win32":
            remediation.append(
                "geen renderer: installeer pywin32 zodat PowerPoint COM werkt "
                "(pip install pywin32), of LibreOffice met poppler-utils"
            )
        else:
            remediation.append(
                "geen renderer: installeer LibreOffice plus poppler-utils"
            )
        remediation.append(
            "tot dan geldt de QA-only-modus, en die heeft GEEN vormbeoordeling: "
            "qa_text.py toetst de hygiëne en qa_tellingen.py de tellingen, en geen van "
            "de twee ziet overlap, contrast, dood wit of een baseline. Bouw "
            "conservatiever, laat deck-visual-reviewer een structurele XML-review doen, "
            "en meld bij de oplevering dat het deck niet visueel is geverifieerd"
        )

    if soffice and probe["ran"] is False and not com:
        remediation.append(
            "de proefconversie is niet gedraaid, dus van deze LibreOffice is alleen "
            "bekend dát hij bestaat: " + probe["detail"]
        )

    # De merklaag. Dit blokkeert wél, en het staat daarom in `missing`: een
    # gerenderd blad op een ander palet dan de merklaag zegt, is een blad in een
    # huisstijl die niet bestaat, en dat is aan de render niet te zien.
    if merk["gemeten"] and not merk["klopt"]:
        missing.append("merklaag")
        for regel in merk["uit_de_pas"]:
            remediation.append(regel)
        if merk["hardgecodeerd"]:
            plekken = ", ".join(f"{v['waar']} ({v['kleur']})"
                                for v in merk["hardgecodeerd"][:6])
            meer = len(merk["hardgecodeerd"]) - 6
            remediation.append(
                f"{len(merk['hardgecodeerd'])}x een merkkleur als hexwaarde buiten de "
                f"merklaag: {plekken}" + (f" en nog {meer}" if meer > 0 else "")
                + ". Haal de waarde daar weg: een script leest hem uit "
                  "`scripts/gedeeld/merk.py`, een stylesheet uit "
                  "`assets/gedeeld/merk.css`. Zo lang hij op twee plekken staat, "
                  "kan hij op één plek verouderen — dat is precies hoe vijf van de "
                  "zes accenten tot 27 augustus 2026 naast het Word-sjabloon konden "
                  "staan"
            )
    elif not merk["gemeten"]:
        remediation.append(merk["hint"])
    if merk["verouderd"]:
        # Geen `missing`-item: dit zijn geen merkwaarden meer. Wel te weten, want
        # het zijn de resten van de paletmigratie en ze zien eruit als een kleur
        # die klopt.
        remediation.append(
            "hexwaarden van vóór de paletmigratie van 27 augustus 2026, nog aanwezig in "
            + ", ".join(f"{v['waar']} ({v['hex']}, was {v['kleur']})"
                        for v in merk["verouderd"])
            + ". Ze blokkeren niets: er komt geen kleur van een oplevering uit deze "
              "plekken. Wie ze opruimt, laat ze de waarde uit merk.py lezen"
        )

    fonts = font_report(MEASURED_FAMILIES)
    if fonts["missing"]:
        # Geen `missing`-item: dit blokkeert niets. Maar het bepaalt wél hoe je een
        # fit-melding moet lezen, en dat wil je weten vóór de eerste slide.
        remediation.append(
            f"niet te meten fonts: {', '.join(fonts['missing'])} — fit-oordelen "
            "(titelregels, overflow, head-line, fill) zijn dan een schatting, geen "
            "bewijs. Twee remedies, in deze volgorde: zet de fontbestanden in "
            "`assets/fonts/` (Montserrat en Lato staan onder de OFL en mogen mee; Gotham "
            "is commercieel en mag dat niet), of laat het en houd ~10% marge aan bij het "
            "vullen. Voor een render die er dichter bij zit: " + FONTCONFIG_SNIPPET
        )
    elif not fonts.get("measured", True):
        # Er is niet gemeten (geen `_deck`, dus geen python-pptx). Dat hoort in de
        # remediatie, anders leest een lege `missing` als "de fonts zijn in orde".
        remediation.append(fonts["hint"])

    verdict = "full" if can_render and not any(
        not required[m] for m in REQUIRED
    ) else "qa-only"

    emit(
        {
            "python": {
                "executable": sys.executable,
                "version": ".".join(str(v) for v in sys.version_info[:3]),
                "platform": sys.platform,
            },
            "deps": {**required, **optional},
            "renderers": {
                "powerpoint_com": com,
                "soffice": soffice,
                # Niet "is er een soffice" maar "opent deze soffice een pptx". Dat
                # verschil is één keer een foutieve melding "er is een renderer" geweest.
                "soffice_probe": probe,
                "pdf_to_png": raster,
                "preferred": "powerpoint"
                if com
                else ("libreoffice" if libreoffice_usable else None),
                "fonts_substituted": (not com) and libreoffice_usable,
            },
            # Staat de merklaag gelijk met zichzelf: merk.css zoals merk.py hem zou
            # schrijven, en geen merkkleur die ergens anders als hexwaarde staat.
            "merk": merk,
            "potx_thema": potx_thema,
            # Welke merkfonts te MÉTEN zijn op deze machine (niet: wat de renderer ziet).
            # Zonder deze regel las een lege `fonts_measured` in de QA als "de fonts staan
            # er niet", terwijl het ook een ontbrekende Pillow kan zijn — of, op een
            # Office-machine, fonts die alleen in de CloudFonts-cache staan.
            "fonts": fonts,
            "verdict": verdict,
            "missing": missing,
            "remediation": remediation or None,
        }
    )
    # Always 0 — see the module docstring. Read `verdict`, not the exit code.
    sys.exit(0)


if __name__ == "__main__":
    main()
