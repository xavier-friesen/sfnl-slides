#!/usr/bin/env python3
"""Wat er is en wat er niet is, vóór je een scherm bouwt.

Een dunne wrapper. Drie dingen bepalen hier hoe je bouwt en wat je bij de
oplevering zegt, en alle drie zijn ze van een andere laag:

* **De browser** — zonder Chromium is er geen render, en de render is de enige
  vormbeoordeling die deze route heeft. Je bouwt dan blind en dat meld je. De
  finder komt uit `scripts/documenten/_browser.py`.
* **Het merkblok in de stylesheet** — `assets/online/stijl.css` draagt het
  `:root`-blok van `merk.py` gestempeld tussen `merk:begin` en `merk:einde`.
  Loopt dat uit de pas, dan bouwt de pagina met een kleur die niet meer de
  merkkleur is, en dát ziet niemand op de render.
* **De ingesloten letters** — `assets/documenten/fonts/fonts.css`. Geen
  `<link>` naar Google Fonts: het CSP-beleid van een artifact blokkeert elke
  andere host, en zonder internet valt de pagina terug op Helvetica.

Wat hier met opzet níet in staat: `node` en de canvashelper van de
`design`-skill. Die route hoort bij `ontwerp-documenten`, waar een pagina een
blad is dat je met de muis kunt aanschuiven. Een scherm lever je op als één
bestand of als artifact.

Gebruik:

    python preflight.py
    python preflight.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
WORTEL = HIER.parent.parent

STIJL = WORTEL / "assets" / "online" / "stijl.css"
FONTS = WORTEL / "assets" / "documenten" / "fonts" / "fonts.css"


def _renderer() -> tuple[bool, str]:
    sys.path.insert(0, str(WORTEL / "scripts" / "documenten"))
    try:
        from _browser import browser, zoek_chromium
    except Exception as fout:
        return False, f"kan _browser.py niet laden: {fout}"
    try:
        import playwright  # noqa: F401
    except ImportError:
        return False, "playwright ontbreekt — pip install playwright"
    pad = zoek_chromium()
    try:
        with browser() as b:
            p = b.new_page()
            p.set_content("<p style='font-family:Lato'>x</p>")
            p.evaluate("1")
        return True, pad or "playwright-cache"
    except SystemExit as fout:
        return False, str(fout).splitlines()[0]
    except Exception as fout:  # pragma: no cover
        return False, f"{type(fout).__name__}: {fout}"


def _merkblok() -> dict:
    sys.path.insert(0, str(WORTEL / "scripts" / "gedeeld"))
    try:
        from merk import BEGIN, EINDE, stempel
    except Exception as fout:
        return {"ok": False, "info": f"kan merk.py niet laden: {fout}"}
    if not STIJL.exists():
        return {"ok": False, "info": f"ontbreekt: {STIJL}"}
    tekst = STIJL.read_text(encoding="utf-8")
    if BEGIN not in tekst or EINDE not in tekst:
        return {"ok": False, "info": "geen merktekens in stijl.css — draai "
                                     "`python scripts/gedeeld/merk.py --css`"}
    if stempel(tekst) != tekst:
        return {"ok": False, "info": "het merkblok loopt uit de pas met merk.py — "
                                     "draai `python scripts/gedeeld/merk.py --css`"}
    return {"ok": True, "info": "in de pas met scripts/gedeeld/merk.py"}


def check() -> dict:
    ok_render, info_render = _renderer()
    return {
        "renderer": {"ok": ok_render, "info": info_render},
        "merkblok": _merkblok(),
        "letters": {"ok": FONTS.exists(),
                    "kb": round(FONTS.stat().st_size / 1024) if FONTS.exists() else 0,
                    "pad": str(FONTS)},
        "stijl": {"ok": STIJL.exists(), "pad": str(STIJL)},
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
        print(f"  {'ja ' if ok else 'NEE'}  {naam:<14} {extra}")

    print("preflight — online-design\n")
    regel("renderer", r["renderer"]["ok"], r["renderer"]["info"])
    regel("merkblok", r["merkblok"]["ok"], r["merkblok"]["info"])
    regel("letters", r["letters"]["ok"], f"{r['letters']['kb']} kB ingesloten")
    regel("stijl.css", r["stijl"]["ok"], r["stijl"]["pad"])
    print()
    if not r["renderer"]["ok"]:
        print("  Zonder renderer bouw je blind: geen vormbeoordeling in twee thema's,")
        print("  en qa_online.py meet niets. Lees 'Zonder renderer' in de SKILL.")
    if not r["merkblok"]["ok"]:
        print("  bouw.py weigert te bouwen tot het merkblok klopt, en dat is opzet.")
    if not r["letters"]["ok"]:
        print("  Draai `python scripts/documenten/haal_fonts.py`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
