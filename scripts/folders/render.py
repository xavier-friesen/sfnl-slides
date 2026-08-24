#!/usr/bin/env python3
"""De folder renderen en er als spreads naar kijken.

Dit is de enige vormbeoordeling die deze skill heeft. Er is geen validator die
een compositie afkeurt voordat iemand hem gezien heeft; er is dit, en er is
`qa_folder.py` dat meet wat mechanisch te meten valt.

Twee uitvoeren:

* **losse pagina's** — `pagina-01.png` en verder, op ware maat, om een detail
  na te kijken.
* **het contactblad** — alle spreads onder elkaar, want een folder wordt per
  spread gelezen en niet per pagina. Twee pagina's die los allebei kloppen en
  naast elkaar botsen, zie je alleen zo. De omslag staat alleen, daarna 2-3,
  4-5, zoals het gedrukte ding opengaat.

Gebruik:

    python render.py werkmap/folder.html
    python render.py werkmap/folder.html --uit png --schaal 2
    python render.py werkmap/folder.html --alleen-contactblad
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _browser import browser, wacht_op_letters  # noqa: E402

TAFEL = "#E7E6EA"


def render(html: Path, uit: Path, schaal: float = 1.5,
           contactblad: bool = True, losse: bool = True) -> dict:
    uit.mkdir(parents=True, exist_ok=True)
    geschreven: list[str] = []

    with browser() as b:
        page = b.new_page(viewport={"width": 1700, "height": 1200},
                          device_scale_factor=schaal)
        page.goto(html.resolve().as_uri())
        wacht_op_letters(page)

        maten = page.evaluate("""() => Array.from(document.querySelectorAll('.pagina'))
            .map((el, i) => {
              const r = el.getBoundingClientRect();
              return {i, w: Math.round(r.width), h: Math.round(r.height),
                      formaat: el.dataset.formaat || 'sfnl',
                      folio: el.dataset.folio || '',
                      kopregel: el.dataset.kopregel || ''};
            })""")
        if not maten:
            sys.exit(f"geen .pagina gevonden in {html}")

        if losse:
            for m in maten:
                el = page.locator(".pagina").nth(m["i"])
                doel = uit / f"pagina-{m['i'] + 1:02d}.png"
                el.screenshot(path=str(doel))
                geschreven.append(str(doel))

        if contactblad:
            geschreven += _spreads(page, maten, uit, schaal)

    return {"paginas": len(maten), "maten": maten, "bestanden": geschreven,
            "map": str(uit)}


def _spreads(page, maten: list[dict], uit: Path, schaal: float) -> list[str]:
    """Zet de pagina's als spreads in één beeld: 1 alleen, dan 2-3, 4-5.

    De opzet gebeurt in de browser zelf, op een kloon van de pagina's, zodat
    de spread precies zo meet als de echte pagina — een montage buiten de
    browser om zou de webfonts opnieuw moeten oplossen.
    """
    css = """
      body { background: %s; margin: 0; padding: 26px; }
      .vel { display: block !important; padding: 0 !important; }
      .contact { display: flex; flex-direction: column; gap: 30px; align-items: center; }
      .spread { display: flex; gap: 2px; box-shadow: 0 2px 16px rgba(32,27,92,.20); }
      .spread .pagina { box-shadow: none !important; }
      .merk { font: 600 13px/1 -apple-system, system-ui, sans-serif;
              color: #201B5C; opacity: .62; letter-spacing: .06em;
              margin: 0 0 -18px; align-self: flex-start; }
    """ % TAFEL
    page.add_style_tag(content=css)
    page.evaluate("""(n) => {
        const paginas = Array.from(document.querySelectorAll('.pagina'));
        const houder = document.createElement('div');
        houder.className = 'contact';
        const groepen = [];
        for (let i = 0; i < paginas.length; i++) {
          const breed = paginas[i].getBoundingClientRect().width > 1100;
          if (i === 0 || breed) { groepen.push([paginas[i]]); continue; }
          const vorige = groepen[groepen.length - 1];
          if (vorige.length === 1 && vorige[0].getBoundingClientRect().width <= 1100
              && groepen.length > 1) { vorige.push(paginas[i]); }
          else { groepen.push([paginas[i]]); }
        }
        let nr = 1;
        for (const g of groepen) {
          const wrap = document.createElement('div');
          const merk = document.createElement('p');
          merk.className = 'merk';
          merk.textContent = g.length === 2 ? `spread ${nr}\\u2013${nr + 1}` : `pagina ${nr}`;
          const rij = document.createElement('div');
          rij.className = 'spread';
          g.forEach(p => rij.appendChild(p));
          wrap.appendChild(merk); wrap.appendChild(rij);
          houder.appendChild(wrap);
          nr += g.length;
        }
        document.body.innerHTML = '';
        document.body.appendChild(houder);
    }""", len(maten))
    page.wait_for_timeout(220)
    doel = uit / "contactblad.png"
    page.screenshot(path=str(doel), full_page=True)
    return [str(doel)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=Path)
    ap.add_argument("--uit", type=Path, default=None,
                    help="map voor de PNG's (default: <map van html>/png)")
    ap.add_argument("--schaal", type=float, default=1.5,
                    help="device scale factor; 1.5 is genoeg om naar te kijken, "
                         "2 om een detail na te meten")
    ap.add_argument("--alleen-contactblad", action="store_true")
    ap.add_argument("--alleen-paginas", action="store_true")
    a = ap.parse_args()

    if not a.html.exists():
        sys.exit(f"niet gevonden: {a.html}")
    uit = a.uit or a.html.parent / "png"
    res = render(a.html, uit, a.schaal,
                 contactblad=not a.alleen_paginas,
                 losse=not a.alleen_contactblad)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
