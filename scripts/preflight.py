"""Report what this machine can do before you start building.

Usage:
    python preflight.py
    python preflight.py --json

Run this FIRST, once per session. It answers two questions in one go:

  1. Are the Python packages the scripts need importable?
  2. Is there a renderer, so the visual loop can actually run?

Output:

    {
      "python":    {"executable": "...", "version": "3.12.x", "platform": "win32"},
      "deps":      {"pptx": true, "lxml": true, "defusedxml": true, ...},
      "renderers": {"powerpoint_com": true, "soffice": null, "soffice_probe": {...},
                    "pdf_to_png": null},
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
    "pytest": ("pytest", "de testsuite"),
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


def check_raster() -> str | None:
    for name in RASTER_TOOLS:
        if shutil.which(name):
            return name
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="accepted for symmetry with the other scripts; output is always JSON",
    )
    parser.parse_args()

    emit, font_report = deck_helpers()

    required = check_imports(REQUIRED)
    optional = check_imports(OPTIONAL)

    com = check_powerpoint_com()
    soffice = check_soffice()
    raster = check_raster()

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
