#!/usr/bin/env python3
"""Wat er is en wat er niet is, vóór je begint.

Vier dingen bepalen hoe je bouwt en wat je bij de oplevering zegt:

* **Playwright en Chromium** — zonder die twee is er geen render, en dus geen
  vormbeoordeling. Je bouwt dan blind en dat meld je.
* **De design-skill** — de helper `seed-canvas.mjs` wordt per sessie onder een
  versienummer uitgepakt, dus het pad ligt niet vast en je zoekt hem op. Is hij
  er niet, roep de `design`-skill dan één keer aan; blijft hij weg, dan is het
  canvas er niet en lever je alleen het losse HTML-bestand.
* **node** — de helper draait erop.
* **De huisstijlletters** — Montserrat en Lato komen bij de render van Google
  Fonts en dat werkt zolang er internet is. Staan ze lokaal, dan werkt het ook
  offline en meet de regelafbreking hetzelfde.

Gebruik:

    python preflight.py
    python preflight.py --json
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HIER = Path(__file__).resolve().parent
WORTEL = HIER.parent.parent


def zoek_helper() -> str | None:
    """`seed-canvas.mjs` van de design-skill, of None.

    De skill wordt per sessie uitgepakt onder een versienummer, dus dit is een
    zoekopdracht en geen constante.
    """
    for wortel in (tempfile.gettempdir(), str(Path.home()), "/tmp"):
        try:
            tref = sorted(glob.glob(str(Path(wortel) / "**" / "design" / "seed-canvas.mjs"),
                                    recursive=True))
        except OSError:
            continue
        if tref:
            return tref[-1]
    return None


def _chromium() -> tuple[bool, str]:
    sys.path.insert(0, str(HIER))
    try:
        from _browser import zoek_chromium
    except Exception as e:
        return False, f"kan _browser.py niet laden: {e}"
    try:
        import playwright  # noqa: F401
    except ImportError:
        return False, "playwright ontbreekt — pip install playwright"
    pad = zoek_chromium()
    try:
        from _browser import browser
        with browser() as b:
            p = b.new_page()
            p.set_content("<p style='font-family:Lato'>x</p>")
            p.evaluate("1")
        return True, pad or "playwright-cache"
    except SystemExit as e:
        return False, str(e).splitlines()[0]
    except Exception as e:  # pragma: no cover
        return False, f"{type(e).__name__}: {e}"


def _letters() -> dict:
    """Staan Montserrat en Lato lokaal? Niet fataal, wel goed om te weten."""
    mappen = [Path.home() / ".fonts", Path.home() / "Library" / "Fonts",
              Path("/usr/share/fonts"), Path("/Library/Fonts"),
              Path("C:/Windows/Fonts")]
    gevonden = {"Montserrat": False, "Lato": False, "Gotham": False}
    for m in mappen:
        if not m.exists():
            continue
        try:
            namen = " ".join(p.name.lower() for p in m.rglob("*.[to]t[fc]"))
        except OSError:
            continue
        for k in gevonden:
            if k.lower() in namen:
                gevonden[k] = True
    return gevonden


def check() -> dict:
    node = shutil.which("node") or shutil.which("bun")
    node_v = ""
    if node:
        try:
            node_v = subprocess.run([node, "--version"], capture_output=True,
                                    text=True, timeout=10).stdout.strip()
        except Exception:
            pass
    ok_chrome, chrome_info = _chromium()
    helper = zoek_helper()
    stijl = WORTEL / "assets" / "documenten" / "stijl.css"
    return {
        "node": {"ok": bool(node), "pad": node, "versie": node_v},
        "renderer": {"ok": ok_chrome, "info": chrome_info},
        "design_helper": {"ok": bool(helper), "pad": helper},
        "stijl": {"ok": stijl.exists(), "pad": str(stijl)},
        "letters": _letters(),
        "plugin_root": os.environ.get("CLAUDE_PLUGIN_ROOT", str(WORTEL)),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    r = check()
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0

    def regel(naam: str, ok: bool, extra: str = "") -> None:
        print(f"  {'ja ' if ok else 'NEE'}  {naam:<16} {extra}")

    print("preflight — sfnl-design-documents\n")
    regel("node", r["node"]["ok"], f"{r['node']['versie']} {r['node']['pad'] or ''}")
    regel("renderer", r["renderer"]["ok"], r["renderer"]["info"])
    regel("design-helper", r["design_helper"]["ok"], r["design_helper"]["pad"] or
          "roep de design-skill één keer aan; hij wordt per sessie uitgepakt")
    regel("stijl.css", r["stijl"]["ok"], r["stijl"]["pad"])
    lok = ", ".join(k for k, v in r["letters"].items() if v) or "geen"
    regel("letters lokaal", any(r["letters"].values()), f"{lok} (Google Fonts is de terugval)")

    print()
    if not r["renderer"]["ok"]:
        print("  Zonder renderer bouw je blind: geen vormbeoordeling, geen qa_document.")
        print("  Lees 'Zonder renderer' onderaan de SKILL vóór je begint.")
    if not r["design_helper"]["ok"]:
        print("  Zonder de helper is er geen canvas. Het losse HTML-bestand blijft")
        print("  gewoon de oplevering; alleen het aanschuiven in de browser vervalt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
