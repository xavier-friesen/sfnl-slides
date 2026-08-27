#!/usr/bin/env python3
"""Het rapport renderen en er als spreads naar kijken.

Dit is de enige vormbeoordeling die deze skill heeft. `qa_rapport.py`
meet ernaast wat mechanisch te meten valt, maar of een pagina goed staat,
zie je alleen door ernaar te kijken.

Een rapport is te lang om pagina voor pagina te bekijken, dus er zijn
drie uitvoeren en ze horen in deze volgorde gebruikt te worden:

* **`contactblad-01.png` en verder** — alle spreads als kleine beelden,
  twaalf per blad. Hier zie je het ritme: waar de hoofdstukken openen,
  waar het te vol wordt, waar drie pagina's achter elkaar hetzelfde
  eruitzien. Dit is het eerste waar je naar kijkt en meestal het enige.
* **`spread-NN.png`** — één spread op leesmaat, om iets na te kijken dat
  op het contactblad opviel.
* **`pagina-NN.png`** — één pagina op ware maat, om een detail na te
  meten.

Een rapport wordt per spread gelezen en niet per pagina: pagina 12 en 13
liggen tegenover elkaar en botsen of ze botsen niet. Daarom staan de
pagina's ook op het contactblad als paren, met de omslag alleen rechts.

Gebruik:

    python render.py werkmap/rapport.html
    python render.py werkmap/rapport.html --spread 6
    python render.py werkmap/rapport.html --pagina 12 --schaal 2
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER.parent / "documenten"))
from _browser import browser, wacht_op_letters  # noqa: E402

sys.path.insert(0, str(HIER.parent / "gedeeld"))
from merk import HEX, rgb  # noqa: E402

#: De chroom van het contactblad draagt de merkinkt en hoort dus uit de
#: merklaag te komen. Stond hier tot 27 augustus 2026 hardgecodeerd, en dat
#: was ná de paletmigratie de navy uit `merk.VERVANGEN`: het contactblad
#: waarop je de kleur beoordeelt, gaf zelf de oude waarde af.
_NAVY = HEX["navy"]
_NAVY_RGB = ", ".join(str(k) for k in rgb(_NAVY))

TAFEL = "#E7E6EA"
PER_BLAD = 12          # spreads per contactblad


def _spreads(aantal: int) -> list[list[int]]:
    """De pagina's als paren, met de omslag alleen rechts.

    Zo gaat een gedrukt rapport open: blad 1 staat alleen, daarna 2-3,
    4-5. Wie de pagina's per twee vanaf één groepeert, beoordeelt paren
    die in het echt nooit naast elkaar liggen.
    """
    uit: list[list[int]] = [[0]]
    i = 1
    while i < aantal:
        uit.append([i, i + 1] if i + 1 < aantal else [i])
        i += 2
    return uit


def render(html: Path, uit: Path, schaal: float = 1.0,
           spread: int | None = None, pagina: int | None = None) -> dict:
    uit.mkdir(parents=True, exist_ok=True)
    geschreven: list[str] = []

    with browser() as b:
        page = b.new_page(viewport={"width": 1800, "height": 1200},
                          device_scale_factor=schaal)
        page.goto(html.resolve().as_uri())
        wacht_op_letters(page)

        aantal = page.evaluate("() => document.querySelectorAll('.pagina').length")
        if not aantal:
            sys.exit(f"geen .pagina gevonden in {html}")
        paren = _spreads(aantal)

        if pagina is not None:
            if not 1 <= pagina <= aantal:
                sys.exit(f"pagina {pagina} bestaat niet; er zijn er {aantal}")
            doel = uit / f"pagina-{pagina:02d}.png"
            page.locator(".pagina").nth(pagina - 1).screenshot(path=str(doel))
            geschreven.append(str(doel))
            return {"paginas": aantal, "bestanden": geschreven, "map": str(uit)}

        _tafel(page)
        if spread is not None:
            if not 1 <= spread <= len(paren):
                sys.exit(f"spread {spread} bestaat niet; er zijn er {len(paren)}")
            doel = uit / f"spread-{spread:02d}.png"
            _bouw_spreads(page, [paren[spread - 1]], 1, groot=True)
            page.screenshot(path=str(doel), full_page=True)
            geschreven.append(str(doel))
            return {"paginas": aantal, "spreads": len(paren),
                    "bestanden": geschreven, "map": str(uit)}

        bladen = math.ceil(len(paren) / PER_BLAD)
        for nr in range(bladen):
            deel = paren[nr * PER_BLAD:(nr + 1) * PER_BLAD]
            _bouw_spreads(page, deel, nr * PER_BLAD + 1, groot=False)
            doel = uit / f"contactblad-{nr + 1:02d}.png"
            page.screenshot(path=str(doel), full_page=True)
            geschreven.append(str(doel))
            page.reload()
            wacht_op_letters(page, 400)
            _tafel(page)

    return {"paginas": aantal, "spreads": len(paren), "bladen": bladen,
            "bestanden": geschreven, "map": str(uit)}


def _tafel(page) -> None:
    page.add_style_tag(content=f"""
      body {{ background: {TAFEL}; margin: 0; padding: 24px; }}
      .vel {{ display: block !important; padding: 0 !important; }}
      .contact {{ display: flex; flex-wrap: wrap; gap: 26px 22px;
                  align-items: flex-start; justify-content: flex-start; }}
      .kaart {{ display: flex; flex-direction: column; gap: 5px; }}
      .spread {{ display: flex; gap: 2px; box-shadow: 0 2px 12px rgba({_NAVY_RGB},.22);
                 background: #fff; }}
      .spread .pagina {{ box-shadow: none !important; margin: 0 !important; }}
      .merk {{ font: 600 12px/1 -apple-system, system-ui, sans-serif;
               color: {_NAVY}; opacity: .6; letter-spacing: .05em; }}
    """)


def _bouw_spreads(page, paren: list[list[int]], eerstenr: int, groot: bool) -> None:
    """De spreads naast elkaar zetten, geschaald.

    Het schalen gebeurt met `zoom` op de spread zelf en niet met
    `transform`, want een transform laat de doos op zijn oude maat staan
    en dan valt het contactblad uit elkaar met gaten ertussen.
    """
    factor = 1.0 if groot else 0.28
    page.evaluate("""([paren, eerstenr, factor]) => {
        const paginas = Array.from(document.querySelectorAll('.pagina'));
        const houder = document.createElement('div');
        houder.className = 'contact';
        let nr = eerstenr;
        for (const paar of paren) {
          const kaart = document.createElement('div');
          kaart.className = 'kaart';
          const merk = document.createElement('p');
          merk.className = 'merk';
          const nrs = paar.map(i => i + 1);
          merk.textContent = nrs.length === 2 ? `${nrs[0]}\\u2013${nrs[1]}` : `${nrs[0]}`;
          const rij = document.createElement('div');
          rij.className = 'spread';
          rij.style.zoom = factor;
          for (const i of paar) if (paginas[i]) rij.appendChild(paginas[i]);
          kaart.appendChild(rij); kaart.appendChild(merk);
          houder.appendChild(kaart);
          nr += paar.length;
        }
        document.body.innerHTML = '';
        document.body.appendChild(houder);
    }""", [paren, eerstenr, factor])
    page.wait_for_timeout(260)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=Path)
    ap.add_argument("--uit", type=Path, default=None)
    ap.add_argument("--schaal", type=float, default=1.0)
    ap.add_argument("--spread", type=int, default=None,
                    help="één spread op leesmaat")
    ap.add_argument("--pagina", type=int, default=None,
                    help="één pagina op ware maat")
    a = ap.parse_args()

    if not a.html.exists():
        sys.exit(f"niet gevonden: {a.html}")
    uit = a.uit or a.html.parent / "png"
    res = render(a.html, uit, a.schaal, a.spread, a.pagina)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
