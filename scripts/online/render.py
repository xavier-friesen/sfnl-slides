#!/usr/bin/env python3
"""De pagina in de browser, in beide thema's, en dan kijken.

Dit is de enige vormbeoordeling die deze skill heeft. Er is geen validator die
een compositie afkeurt voordat iemand hem gezien heeft; er is dit, en er is
`qa_online.py` dat meet wat mechanisch te meten valt.

**In béide thema's, en dat is geen extra.** Een pagina die je alleen in licht
hebt gezien, is half gezien. De helft van wat er op een donkere grond misgaat,
gaat op een lichte grond niet mis: een haarlijn die verdwijnt, een tint die met
zijn grond samenvalt, een SVG met een vaste `fill`, een schaduw die op donker
een vlek is. Geen van die vier meet je; je ziet ze.

**En op meer dan één breedte**, want de breedte groeit. Standaard 1440 en 420 —
een laptop en een telefoon. Wat je op 420 ziet en op 1440 niet: een tabel die
de pagina breder duwt dan het venster, een kop van vier woorden op vier regels,
een kaartenrij die op één kolom valt terwijl de kaarten hun binnenmarge houden.

De donkere stand komt hier uit `prefers-color-scheme` en niet uit een stempel
op de root. Dat is met opzet de ongestempelde stand: als een token alleen
binnen het `[data-theme="dark"]`-blok staat, valt de pagina hier door de mand.
De andere kant — de gestempelde stand — meet `qa_online.py`.

Drie uitvoeren:

* `pagina-<thema>-<breedte>.png` — de volle pagina, per thema en per breedte.
* `contactblad.png` — de thema's naast elkaar, per breedte een rij. Dit is waar
  je naar kijkt: een pagina beoordeel je als paar, want de twee standen horen
  hetzelfde ding te zijn en niet twee ontwerpen.
* een JSON-verslag met de gemeten hoogte, de gemeten grondkleur per thema en of
  het document horizontaal schuift.

Gebruik:

    python render.py werkmap/dashboard.html
    python render.py werkmap/dashboard.html --breedtes 1440,900,420
    python render.py werkmap/dashboard.html --schaal 2 --alleen-contactblad
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WORTEL = Path(__file__).resolve().parent.parent.parent
# De browserlaag is van de drukwerkroute en staat daar. Hij weet Chromium te
# vinden op een machine waar het buildnummer van Playwright niet klopt met wat
# er op schijf staat, en hij wacht op de webfonts. Twee kopieën van die kennis
# gaan een keer uiteenlopen.
sys.path.insert(0, str(WORTEL / "scripts" / "documenten"))
from _browser import browser, wacht_op_letters  # noqa: E402

# Ook het contactblad zelf draagt geen eigen kleurwaarde. Het is een
# hulpmiddel en geen oplevering, maar een hexwaarde in een script is een
# hexwaarde in een script.
sys.path.insert(0, str(WORTEL / "scripts" / "gedeeld"))
from merk import HEX, rgb  # noqa: E402

THEMAS = {"licht": "light", "donker": "dark"}

#: Wat er per stand gemeten wordt naast het beeld. De grondkleur staat erbij
#: omdat een body zonder eigen achtergrond hier zichtbaar wordt: dan meet
#: `licht` en `donker` dezelfde waarde, of `rgba(0, 0, 0, 0)`.
METING = """() => {
  const de = document.documentElement, b = document.body;
  const cs = getComputedStyle(b);
  return {
    hoogte: Math.round(de.scrollHeight),
    breedte: Math.round(de.scrollWidth),
    venster: Math.round(de.clientWidth),
    grond: cs.backgroundColor,
    inkt: cs.color,
    schuift: de.scrollWidth - de.clientWidth
  };
}"""


def render(html: Path, uit: Path, breedtes: list[int], schaal: float = 1.0,
           contactblad: bool = True, losse: bool = True) -> dict:
    uit = uit.resolve()
    uit.mkdir(parents=True, exist_ok=True)
    uri = html.resolve().as_uri()
    standen: list[dict] = []
    geschreven: list[str] = []

    with browser() as b:
        for naam, schema in THEMAS.items():
            ctx = b.new_context(color_scheme=schema,
                                viewport={"width": breedtes[0], "height": 1000},
                                device_scale_factor=schaal)
            page = ctx.new_page()
            page.goto(uri)
            wacht_op_letters(page)
            for breed in breedtes:
                page.set_viewport_size({"width": breed, "height": 1000})
                page.wait_for_timeout(160)
                m = page.evaluate(METING)
                doel = uit / f"pagina-{naam}-{breed}.png"
                if losse:
                    page.screenshot(path=str(doel), full_page=True)
                    geschreven.append(str(doel))
                standen.append({"thema": naam, "breedte": breed, "bestand": doel.name,
                                **m})
            ctx.close()

        if contactblad and losse:
            geschreven += [_contactblad(b, uit, breedtes, schaal)]

    return {"bestand": str(html), "map": str(uit), "standen": standen,
            "bestanden": geschreven}


CONTACT = """<!doctype html>
<html><head><meta charset="utf-8"><style>
  body {{ margin: 0; padding: 26px; background: rgba({navy}, .09);
          font: 600 13px/1.3 -apple-system, system-ui, sans-serif;
          color: {inkt}; }}
  .rij {{ display: flex; gap: 18px; align-items: flex-start; margin-bottom: 34px; }}
  .kolom {{ display: flex; flex-direction: column; gap: 6px; }}
  .kolom p {{ margin: 0; opacity: .62; letter-spacing: .06em; }}
  img {{ display: block; border: 1px solid rgba({navy}, .22); }}
</style></head><body>
{rijen}
</body></html>
"""


def _contactblad(b, uit: Path, breedtes: list[int], schaal: float) -> str:
    """De thema's naast elkaar, per breedte een rij.

    De montage gebeurt in de browser en niet met een beeldbibliotheek: dan is
    er geen afhankelijkheid bij, en de PNG's die erin gaan zijn precies die
    waar je los naar kijkt.
    """
    rijen = []
    for breed in breedtes:
        # 620 px per kolom: twee thema's naast elkaar passen dan op één beeld,
        # en dat is waar dit blad voor is. Een detail kijk je op de losse PNG na.
        toon = 620 if breed >= 620 else breed
        kolommen = "".join(
            f'<div class="kolom"><p>{naam} · {breed} px</p>'
            f'<img src="pagina-{naam}-{breed}.png" width="{toon}"></div>'
            for naam in THEMAS)
        rijen.append(f'<div class="rij">{kolommen}</div>')
    blad = uit / "_contactblad.html"
    blad.write_text(CONTACT.format(rijen="\n".join(rijen),
                                   navy=", ".join(str(k) for k in rgb("navy")),
                                   inkt=HEX["navy"]), encoding="utf-8")

    ctx = b.new_context(viewport={"width": 1360, "height": 1000},
                        device_scale_factor=1)
    page = ctx.new_page()
    page.goto(blad.as_uri())
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(200)
    doel = uit / "contactblad.png"
    page.screenshot(path=str(doel), full_page=True)
    ctx.close()
    blad.unlink(missing_ok=True)
    return str(doel)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=Path)
    ap.add_argument("--uit", type=Path, default=None,
                    help="map voor de PNG's (default: <map van html>/png)")
    ap.add_argument("--breedtes", default="1440,420",
                    help="komma-gescheiden CSS-breedtes; de eerste is de "
                         "hoofdbreedte")
    ap.add_argument("--schaal", type=float, default=1.0,
                    help="device scale factor; 1 is de leesbare stand, 2 om een "
                         "detail na te meten")
    ap.add_argument("--alleen-contactblad", action="store_true")
    ap.add_argument("--alleen-paginas", action="store_true")
    a = ap.parse_args()

    if not a.html.exists():
        sys.exit(f"niet gevonden: {a.html}")
    breedtes = [int(x) for x in a.breedtes.split(",") if x.strip()]
    if not breedtes:
        sys.exit("--breedtes is leeg")

    uit = a.uit or a.html.parent / "png"
    r = render(a.html, uit, breedtes, a.schaal,
               contactblad=not a.alleen_paginas,
               losse=not a.alleen_contactblad)
    print(json.dumps(r, ensure_ascii=False, indent=2))

    # De twee dingen die je uit dit verslag meteen wilt zien.
    gronden = {s["thema"]: s["grond"] for s in r["standen"]}
    if len(set(gronden.values())) < 2:
        print("\nlet op: de grondkleur is in beide thema's dezelfde "
              f"({gronden}). Draagt de body wel een eigen achtergrond? "
              "qa_online.py meet dit als `grond`.", file=sys.stderr)
    schuivend = [s for s in r["standen"] if s["schuift"] > 1]
    if schuivend:
        for s in schuivend:
            print(f"\nlet op: op {s['breedte']} px ({s['thema']}) is het document "
                  f"{s['schuift']} px breder dan het venster — er is een "
                  f"horizontale scrollbalk.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
