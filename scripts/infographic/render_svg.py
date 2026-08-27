#!/usr/bin/env python3
"""Render een SVG naar PNG (en optioneel PDF) met Chromium, op ware grootte of groter.

Chromium en niet cairosvg of rsvg-convert, om één reden: alleen een browser zet Montserrat
en Lato met dezelfde metriek als de rest van de keten, dus alleen deze render laat de
regelval zien die de gebruiker straks ook ziet.

    python render_svg.py uitvoer/kaart.svg                 # 2x PNG, doorzichtig
    python render_svg.py uitvoer/kaart.svg --wit --schaal 3
    python render_svg.py uitvoer/*.svg --pdf

TWEE DINGEN KOMEN UIT DE DRUKROUTE VAN DEZE PLUGIN
--------------------------------------------------
**De letters worden ingesloten en niet van Google Fonts gehaald.**
`assets/documenten/fonts/fonts.css` draagt Montserrat en Lato als `@font-face` met een
`data:`-URI, gegenereerd door `scripts/documenten/haal_fonts.py`. Dit script laadde ze
eerder van `fonts.googleapis.com`, en dat gaat op drie manieren stil mis: zonder internet
valt de render terug op Helvetica, en dan beoordeel je de verkeerde regelval en de
verkeerde vorm; de proefrender van de documentenskill kwam er zo uit, en dat is precies
de meting die dat bestand liet maken. Nu is de render offline hetzelfde als online, en
hetzelfde als een SFNL-document -- één lettermetriek voor alle vier de skills.
Ontbreekt `fonts.css`, dan blijft Google Fonts de terugval en zegt het script dat.

**Chromium wordt opgezocht.** `scripts/documenten/_browser.py` doet dat, en het staat er
omdat Playwright in zijn eigen cache kijkt naar een build die bij de pip-versie hoort:
op een machine met `PLAYWRIGHT_BROWSERS_PATH` klopt dat buildnummer bijna nooit en faalt
`launch()` met "Executable doesn't exist" terwijl er een prima Chromium staat. Dit script
liep daar op stuk, en dan lijkt het alsof er geen renderer is en bouw je blind.
"""
from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

PX_PER_PT = 96.0 / 72.0

WORTEL = Path(__file__).resolve().parents[2]
#: De ingesloten huisstijlletters van de drukroute. Zie de moduledocstring.
FONTS_CSS = WORTEL / "assets" / "documenten" / "fonts" / "fonts.css"
#: De terugval als dat bestand er niet is.
GOOGLE = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
          'family=Montserrat:wght@300;600&family=Lato:wght@300;400&display=swap">')


def letters() -> tuple[str, bool]:
    """De `<style>` of `<link>` voor de render, en of de letters ingesloten zijn."""
    if FONTS_CSS.is_file():
        return f"<style>{FONTS_CSS.read_text(encoding='utf-8')}</style>", True
    return GOOGLE, False


def maten(svg: str) -> tuple[float, float]:
    import re
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if not m:
        raise SystemExit("geen viewBox in de SVG; schrijf hem met svg.schrijf()")
    return float(m.group(1)), float(m.group(2))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("svg", nargs="+")
    p.add_argument("--schaal", type=float, default=2.0, help="pixelverhouding, default 2")
    p.add_argument("--wit", action="store_true", help="witte achtergrond in plaats van doorzichtig")
    p.add_argument("--pdf", action="store_true", help="ook een PDF op ware grootte")
    p.add_argument("--knijp", action="store_true",
                   help="ook <naam>-knijp.png op een kwart, voor de kneepoefening")
    p.add_argument("--uit", default=None, help="uitvoermap, default naast de SVG")
    a = p.parse_args()

    paden: list[Path] = []
    for patroon in a.svg:
        paden += [Path(x) for x in sorted(glob.glob(patroon))] or [Path(patroon)]

    try:
        import playwright  # noqa: F401
    except ImportError:
        print("playwright ontbreekt: pip install playwright --break-system-packages")
        return 2

    # De Chromium-zoeker van de documentenroute; zie de moduledocstring.
    sys.path.insert(0, str(WORTEL / "scripts" / "documenten"))
    from _browser import browser as chromium

    kop, ingesloten = letters()
    if not ingesloten:
        print("let op: fonts.css niet gevonden, dus de render haalt de letters bij Google "
              "Fonts. Zonder internet valt hij terug op Helvetica en beoordeel je de "
              "verkeerde regelval.")

    with chromium(args=["--force-color-profile=srgb", "--disable-lcd-text"]) as browser:
        for pad in paden:
            if not pad.is_file():
                print(f"niet gevonden: {pad}")
                continue
            inhoud = pad.read_text(encoding="utf-8")
            w, h = maten(inhoud)
            uitmap = Path(a.uit) if a.uit else pad.parent
            uitmap.mkdir(parents=True, exist_ok=True)
            page = browser.new_page(
                viewport={"width": max(1, round(w * PX_PER_PT)),
                          "height": max(1, round(h * PX_PER_PT))},
                device_scale_factor=a.schaal)
            achter = "#FFFFFF" if a.wit else "transparent"
            page.set_content(
                f'<!doctype html><html><head><meta charset="utf-8">'
                f'{kop}'
                f'<style>html,body{{margin:0;padding:0;background:{achter};}}'
                f'svg{{display:block;width:{w * PX_PER_PT}px;height:{h * PX_PER_PT}px;}}'
                f'</style></head><body>{inhoud}</body></html>',
                wait_until="load")
            try:
                page.wait_for_function("document.fonts.status === 'loaded'", timeout=6000)
            except Exception:
                pass
            png = uitmap / f"{pad.stem}.png"
            page.screenshot(path=str(png), omit_background=not a.wit)
            if a.knijp:
                try:
                    from PIL import Image
                    kn = uitmap / f"{pad.stem}-knijp.png"
                    im = Image.open(png)
                    im.resize((max(1, im.width // 4), max(1, im.height // 4)),
                              Image.LANCZOS).save(kn)
                    print(f"{kn}  kneepversie")
                except ImportError:
                    print("geen Pillow: kneepversie overgeslagen")
            print(f"{png}  {round(w * PX_PER_PT * a.schaal)}x"
                  f"{round(h * PX_PER_PT * a.schaal)}px")
            if a.pdf:
                pdf = uitmap / f"{pad.stem}.pdf"
                page.pdf(path=str(pdf), width=f"{w}pt", height=f"{h}pt",
                         print_background=True, margin={"top": "0", "bottom": "0",
                                                       "left": "0", "right": "0"})
                print(f"{pdf}")
            page.close()
        # Sluiten doet `_browser.browser()` zelf, in zijn `finally`.
    return 0


if __name__ == "__main__":
    sys.exit(main())
