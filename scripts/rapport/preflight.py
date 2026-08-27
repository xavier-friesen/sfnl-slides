#!/usr/bin/env python3
"""Staat alles klaar om een rapport te zetten.

Vier dingen, en ze zijn niet allemaal even hard:

* **Chromium** — hard nodig. Zonder browser is er geen zetting: het
  splitsen van een alinea op een regelgrens kan alleen een engine die
  weet hoe breed een woord is. Anders dan bij `sfnl-documenten`
  is er hier dus geen "zonder renderer bouw je blind"-route — er is
  helemaal geen route.
* **De ingesloten letters** — zonder die valt het rapport terug op
  Google Fonts, en dan meet de zetting straks op een andere letter dan
  waarin hij gedrukt wordt. Dat verschuift elke regelafbreking.
* **De stijlbestanden** — `stijl.css` uit de documentenskill en
  `rapport.css` uit deze.
* **De Nederlandse afbreking** — zacht. Ontbreekt het woordenboek in
  deze Chromium, dan vervalt het uitvullen in het dubbele model en
  wordt alles vlaggend links. Dat is geen fout maar het is wel iets om
  te weten voordat je een model kiest.

Gebruik:

    python preflight.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
WORTEL = HIER.parent.parent
sys.path.insert(0, str(WORTEL / "scripts" / "documenten"))

PROEF = """() => {
  const d = document.createElement('div');
  d.lang = 'nl';
  d.style.cssText = 'position:absolute;visibility:hidden;left:-9999px;width:62px;' +
    'font:300 13.33px/17.33px Lato,sans-serif;hyphens:auto;-webkit-hyphens:auto;' +
    'hyphenate-limit-chars:6 3 3';
  d.textContent = 'schuldhulpverleningstraject';
  document.body.appendChild(d);
  const h = d.offsetHeight;
  document.body.removeChild(d);
  return {hoogte: h, breekt: h > 26};
}"""


def main() -> int:
    uit: dict = {"in orde": True, "meldingen": []}

    def meld(hard: bool, tekst: str) -> None:
        uit["meldingen"].append(("BLOKKEERT" if hard else "let op") + ": " + tekst)
        if hard:
            uit["in orde"] = False

    # -- python en playwright ----------------------------------------
    uit["python"] = sys.version.split()[0]
    try:
        import playwright  # noqa: F401
        uit["playwright"] = True
    except ImportError:
        uit["playwright"] = False
        meld(True, "playwright ontbreekt. `pip install playwright` en daarna "
                   "`python3 -m playwright install chromium`.")

    # -- de bestanden ------------------------------------------------
    for naam, pad, hard in (
        ("stijl.css", WORTEL / "assets" / "documenten" / "stijl.css", True),
        ("rapport.css", WORTEL / "assets" / "rapport" / "rapport.css", True),
        ("paginator.js", HIER / "paginator.js", True),
        ("fonts.css", WORTEL / "assets" / "documenten" / "fonts" / "fonts.css", False),
    ):
        bestaat = pad.exists()
        uit[naam] = str(pad) if bestaat else None
        if not bestaat:
            meld(hard, f"{naam} ontbreekt op {pad}"
                 + ("" if hard else ". Draai `python scripts/documenten/haal_fonts.py`; "
                                   "zonder dit meet de zetting op de verkeerde letter."))

    # -- de browser --------------------------------------------------
    if uit["playwright"]:
        try:
            from _browser import browser, zoek_chromium
            uit["chromium"] = zoek_chromium() or "playwright kiest zelf"
            with browser() as b:
                page = b.new_page()
                page.set_content("<div lang='nl'>x</div>")
                proef = page.evaluate(PROEF)
            uit["afbreking nl"] = proef["breekt"]
            if not proef["breekt"]:
                meld(False, "deze Chromium heeft geen Nederlands afbreekwoordenboek. "
                            "Uitvullen vervalt, ook in het dubbele model, en de "
                            "lopende tekst wordt vlaggend links. Dat is de zetting "
                            "van Bain, BMC en MGI, dus het is geen noodgreep — maar "
                            "het is wel een andere zetting dan het SFNL-drukwerk.")
        except SystemExit as e:
            uit["chromium"] = None
            meld(True, f"Chromium start niet: {e}")
        except Exception as e:  # pragma: no cover
            uit["chromium"] = None
            meld(True, f"Chromium start niet: {e!r}")

    print(json.dumps(uit, ensure_ascii=False, indent=2))
    return 0 if uit["in orde"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
