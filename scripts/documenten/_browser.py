"""Chromium opzoeken, want het pad is nergens hetzelfde.

Playwright kijkt standaard in zijn eigen cache naar een build die bij de
geïnstalleerde versie hoort. Op een machine waar de browser vooraf is neergezet
(`PLAYWRIGHT_BROWSERS_PATH`) klopt dat buildnummer bijna nooit met de
pip-versie, en dan faalt `launch()` met "Executable doesn't exist" terwijl er
een prima Chromium staat. Dit zoekt hem alsnog op.

Gemeten aanleiding: een omgeving met `chromium-1194` op schijf en een
Playwright die om build 1234 vroeg. De renderloop viel daar stil op een
foutmelding die eruitzag alsof er geen browser wás.
"""

from __future__ import annotations

import glob
import os
from contextlib import contextmanager
from pathlib import Path


def zoek_chromium() -> str | None:
    """Pad naar een bruikbare Chromium, of None als Playwright zelf het weet."""
    kandidaten: list[str] = []
    wortel = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if wortel:
        kandidaten.append(str(Path(wortel) / "chromium"))
        kandidaten += sorted(glob.glob(str(Path(wortel) / "chromium-*" / "chrome-linux" / "chrome")))
        kandidaten += sorted(glob.glob(str(Path(wortel) / "chromium-*" / "chrome-mac" / "Chromium.app"
                                            / "Contents" / "MacOS" / "Chromium")))
    for env in ("CHROME_PATH", "CHROMIUM_PATH"):
        if os.environ.get(env):
            kandidaten.insert(0, os.environ[env])
    for k in kandidaten:
        p = Path(k)
        if p.exists() and (p.is_file() or p.is_symlink()):
            return str(p)
    return None


@contextmanager
def browser(**kw):
    """`with browser() as b:` — Chromium, waar hij ook staat."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:  # pragma: no cover
        raise SystemExit(
            "playwright ontbreekt. Installeer het met:\n"
            "  pip install playwright\n"
            "en zet er een browser bij als die er niet al staat:\n"
            "  python3 -m playwright install chromium")
    pad = zoek_chromium()
    with sync_playwright() as pw:
        try:
            b = pw.chromium.launch(executable_path=pad, **kw) if pad \
                else pw.chromium.launch(**kw)
        except Exception as e:  # pragma: no cover
            raise SystemExit(
                f"Chromium start niet: {e}\n"
                "Zet PLAYWRIGHT_BROWSERS_PATH of draai "
                "`python3 -m playwright install chromium`.")
        try:
            yield b
        finally:
            b.close()


def wacht_op_letters(page, ms: int = 1200) -> None:
    """Wacht tot de webfonts er zijn.

    Zonder dit rendert de eerste pagina in de fallback en meet je de verkeerde
    regelafbreking. `document.fonts.ready` is de harde toets; de extra pauze is
    er voor de gevallen waarin Chromium de belofte al inlost terwijl de laatste
    weight nog binnenkomt.
    """
    page.wait_for_load_state("networkidle")
    try:
        page.evaluate("document.fonts.ready")
    except Exception:
        pass
    page.wait_for_timeout(ms)
