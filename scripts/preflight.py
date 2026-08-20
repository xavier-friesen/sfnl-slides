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
      "renderers": {"powerpoint_com": true, "soffice": null, "pdf_to_png": null},
      "verdict":   "full" | "qa-only",
      "missing":   [...],
      "remediation": [...]
    }

`verdict` is the whole point:

* **full** — a renderer works. Build, render, look at the slides, fix what you see.
* **qa-only** — no renderer. You may still build, but you cannot see the result, so
  qa_fit.py, qa_text.py and qa_typography.py become the gate instead of your eyes, the
  reviewer does a structural XML review rather than a visual one, and the delivery says
  in so many words that the deck was not visually verified. Building blind WITHOUT
  saying so is the defect this flag exists to prevent.

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
    "LibreOffice-render dichter bij het echte deck; de meting van qa_fit blijft een "
    "schatting zolang de échte bestanden ontbreken."
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

    # LibreOffice on its own renders nothing: it produces a PDF, and something has to
    # turn that into PNG.
    libreoffice_usable = bool(soffice and raster)
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
        if soffice and not raster:
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
            "tot dan geldt de QA-only-modus: qa_fit/qa_text/qa_typography zijn de "
            "poort, en de oplevering meldt dat het deck niet visueel is geverifieerd"
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
