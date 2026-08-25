#!/usr/bin/env python3
"""Een gebouwd HTML-document als PDF, met de maat die het blad zelf zegt.

Van beide drukroutes, en het staat hier omdat de recept-regel in beide
skills woordelijk hetzelfde was en in geen van beide werd uitgevoerd. Het
stond er als proza — "roep `sfnl-html-to-pdf` aan, zet de marges op nul,
gebruik `prefer_css_page_size`" — en proza wordt overgeslagen. Nu is het
een stap.

**Drie instellingen doen het werk, en alle drie om dezelfde reden.**

* `prefer_css_page_size` — het document draagt zijn eigen `@page` met de
  bladmaat erin. Zonder deze vlag drukt Chromium alles op Letter of A4 en
  snijdt hij het SFNL-formaat van 210 × 275 mm af. Dat is de fout die je
  pas op papier ziet.
* marges op nul — de marge zit op de pagina zelf, in de zetspiegel. Een
  printermarge eroverheen telt dubbel en duwt de folio de snijrand in.
* `print_background` — de kleurvelden zijn de vormgeving en geen
  versiering. Zonder dit komt een oranje omslag er wit uit.

Wat er **niet** in zit is afloop en snijtekens; die uitleg staat één keer,
in `reference/documenten-stramien.md` §1a, en geldt voor beide routes.

Gebruik:

    python naar_pdf.py rapport.html
    python naar_pdf.py rapport.html --uit ergens/anders.pdf
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
WORTEL = HIER.parent.parent
sys.path.insert(0, str(WORTEL / "scripts" / "documenten"))


def naar_pdf(html: Path, uit: Path | None = None) -> Path:
    """Print het document en lever het pad van de PDF op."""
    from _browser import browser, wacht_op_letters  # noqa: E402

    html = html.resolve()
    doel = (uit or html.with_suffix(".pdf")).resolve()
    doel.parent.mkdir(parents=True, exist_ok=True)

    with browser() as b:
        p = b.new_page()
        p.goto(html.as_uri())
        # De letters moeten geladen zijn vóór het printen, anders zet
        # Chromium de eerste pagina's in een terugvalletter en de rest in
        # Montserrat. Dat is op één blad niet te zien en over tachtig
        # pagina's wel.
        try:
            wacht_op_letters(p)
        except Exception:
            p.wait_for_timeout(1200)
        p.emulate_media(media="print")
        p.pdf(path=str(doel), margin={"top": "0", "right": "0",
                                      "bottom": "0", "left": "0"},
              print_background=True, prefer_css_page_size=True)
    return doel


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=Path)
    ap.add_argument("--uit", type=Path, default=None)
    a = ap.parse_args()
    if not a.html.exists():
        sys.exit(f"niet gevonden: {a.html}")
    doel = naar_pdf(a.html, a.uit)
    print(json.dumps({"pdf": str(doel),
                      "mb": round(doel.stat().st_size / 1e6, 2)},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
