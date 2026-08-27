#!/usr/bin/env python3
"""Zegt of deze machine een infographic kan bouwen, meten en renderen.

    python preflight.py            # kijken
    python preflight.py --herstel  # ontbrekende pakketten erbij zetten

Wat er sinds de plugin niet meer gezocht hoeft te worden: de scripts van `slides`.
Die staan in dezelfde plugin, één map hoger, dus de PowerPoint-route is er altijd. De
eerste versie van dit script zocht ze met een glob over `~/.claude/plugins/**`, en dat is
precies zo betrouwbaar als het klinkt: buiten een geïnstalleerde plugin vond hij niets en
viel de skill terug op alleen de SVG-route, terwijl de scripts ernaast lagen.

Hetzelfde geldt voor de letters. `assets/documenten/fonts/` draagt Montserrat en Lato als
woff2 voor de drukroutes, en `svg.py` leest diezelfde bestanden als metriekbron. De
regelafbreking is dus uit de doos gemeten en niet geschat -- ook zonder netwerk, ook
zonder systeemfonts. `--herstel` haalt daarom geen letters meer op; wat hij nog doet is
`fonttools`, `brotli`, `playwright` en `pillow` bijzetten. `brotli` staat erbij omdat een
woff2 zonder brotli niet uit te pakken is, en dan zakt de meting terug op een schatting
zonder dat er iets ontbreekt om naar te wijzen.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
WORTEL = HIER.parents[1]
sys.path.insert(0, str(HIER))

FAMILIES = ["Montserrat Light", "Montserrat SemiBold", "Lato Light"]


def _pip(*pakketten: str) -> None:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                    "--break-system-packages", *pakketten], check=False)


def main() -> int:
    a = argparse.ArgumentParser()
    a.add_argument("--herstel", action="store_true")
    args = a.parse_args()

    uit: dict[str, object] = {}

    if args.herstel:
        _pip("fonttools", "brotli", "playwright", "pillow")

    ontbreekt_pakket = []
    for mod, pak in (("fontTools", "fonttools"), ("brotli", "brotli"),
                     ("playwright", "playwright"), ("PIL", "pillow")):
        try:
            __import__(mod)
        except ImportError:
            ontbreekt_pakket.append(pak)
    if ontbreekt_pakket and not args.herstel:
        print(f"pakketten ontbreken: {', '.join(ontbreekt_pakket)}  "
              "-> python preflight.py --herstel")
    uit["pakketten_ok"] = not ontbreekt_pakket

    import importlib
    if "svg" in sys.modules:
        importlib.reload(sys.modules["svg"])
    import svg as S

    gevonden = {f: S.vind_font(f) for f in FAMILIES}
    uit["fonts"] = {k: (Path(v).name if v else None) for k, v in gevonden.items()}
    # `meting_echt` is niet "er is een bestand": een woff2 dat je zonder brotli niet
    # openkrijgt, geeft een pad terug en toch een schatting. Vandaar de echte meting.
    uit["meting_echt"] = all(not S._metriek(f).geschat for f in FAMILIES)
    uit["fonts_ingesloten"] = S.INGESLOTEN_MAP.is_dir()

    renderer = None
    try:
        sys.path.insert(0, str(WORTEL / "scripts" / "documenten"))
        from _browser import browser as chromium
        with chromium() as b:
            renderer = b.version
    except Exception as e:                                     # noqa: BLE001
        uit["renderer_fout"] = str(e)[:200]
    uit["renderer"] = renderer

    # De PowerPoint-route van stap 4B loopt op de scripts van slides. Die staan in
    # deze plugin, dus dit is een bestaanscontrole en geen zoekactie.
    slides = WORTEL / "scripts"
    uit["sfnl_slides_scripts"] = str(slides) if (slides / "shapes.py").is_file() else None
    sjabloon = WORTEL / "assets" / "sfnl-sjabloon.potx"
    uit["sjabloon"] = str(sjabloon) if sjabloon.is_file() else None

    # De conceptkeuze in stap 2D gaat op een canvas, en dat vraagt node plus de helper van
    # de design-skill. Die wordt per sessie onder een versienummer uitgepakt, dus zoeken.
    uit["node"] = bool(shutil.which("node") or shutil.which("bun"))
    from schets import seed_helper
    uit["canvas_helper"] = seed_helper()

    print(json.dumps(uit, indent=2, ensure_ascii=False))

    if not uit["meting_echt"]:
        print("\nGeen echte fontmetriek: de afbreking wordt geschat en dus ruim. "
              "Compositie en kleur beoordeel je gewoon op de render, regelval niet. "
              "Draai --herstel; ontbreekt alleen brotli, dan is dát de oorzaak.")
    if not renderer:
        print("\nGeen renderer: dan bouw je blind. Zeg dat bij de oplevering.")
    if not uit["sfnl_slides_scripts"]:
        print("\nDe deckscripts liggen niet naast deze skill. Dat hoort niet te kunnen "
              "binnen de plugin -- controleer of de checkout compleet is. De SVG-route "
              "werkt onverkort.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
