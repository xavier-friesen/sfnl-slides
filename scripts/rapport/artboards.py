#!/usr/bin/env python3
"""Het gezette rapport uit elkaar halen tot artboards voor het designcanvas.

De zetmotor levert één HTML-bestand met alle pagina's erin. Dat is de
oplevering — het opent overal en het reist per mail — maar het is niet
iets waar iemand nog iets aan kan verschuiven. Het designcanvas werkt met
`.dc.html`-artboards: één bestand per pagina, naast elkaar op een canvas,
en daar kun je een figuur verplaatsen of een kop anders zetten zonder de
zetmotor te openen.

Dit script maakt van het ene het andere. Elke `.pagina` uit het gebouwde
rapport wordt een artboard in precies dezelfde vorm die
`ontwerp-documenten` gebruikt — dezelfde `<x-dc>`-omhulling, dezelfde
`<helmet>` met de stijl erin, dezelfde `canvas.json`. Dat is met opzet:
de twee routes leveren hetzelfde soort ding op en een pagina uit een
rapport hoort in hetzelfde canvas te kunnen liggen als een pagina uit een
uitnodiging.

**De opmaak staat in elk artboard, de letters staan ernaast.** De
documentenroute stempelt allebei in elk bestand, en op vijf pagina's kan
dat: 200 kB aan ingesloten letters per artboard is dan 1 MB. Een rapport
van tweeënvijftig pagina's zou zo op 16 MB uitkomen, waarvan tien
dezelfde letters. Daarom gaat `fonts.css` één keer naast de artboards en
linkt elk artboard ernaar, terwijl de opmaak zelf wél in elk bestand
staat. De faalwijze is daarmee ook de zachte: kan het canvas de sibling
niet vinden, dan valt de letter terug op de systeemletter en staat de
rest van de vorm er nog. Het opgeleverde HTML-bestand en de PDF houden
hun letters gewoon ingesloten; daar verandert niets aan.

**Wat dit script níét is: een tweede bron.** De artboards zijn afgeleid.
Verschuif je er iets in en bouw je daarna opnieuw uit `document.json`,
dan is je wijziging weg. Wie in het canvas werkt, werkt dáár verder — en
dan is het gebouwde HTML-bestand het oude.

Gebruik:

    python artboards.py werkmap/rapport.html
    python artboards.py werkmap/rapport.html --uit werkmap/canvas/
"""

from __future__ import annotations

import argparse
import html as _html
import json
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
WORTEL = HIER.parent.parent
sys.path.insert(0, str(WORTEL / "scripts" / "gedeeld"))
sys.path.insert(0, str(WORTEL / "scripts" / "documenten"))

from canvas import manifest  # noqa: E402

#: Dezelfde omhulling als `scripts/documenten/bouw.py`. Hij staat hier
#: overgeschreven en niet geïmporteerd omdat die module bij het importeren
#: naar artboards in een werkmap zoekt; één sjabloon van twintig regels
#: dupliceren is goedkoper dan dat ontwarren.
SJABLOON = """<!doctype html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <link rel="stylesheet" href="./fonts.css">
  <style>
{stijl}
  </style>
</helmet>
{inhoud}
</x-dc>
</body>
</html>
"""

#: De `@font-face`-regels met hun data-URI's. Ze gaan naar `fonts.css`
#: naast de artboards in plaats van in elk bestand.
FONTBLOK = re.compile(r"@font-face\s*\{[^}]*\}", re.S)

PAGINA = re.compile(r'<div class="pagina"([^>]*)>', re.I)


def _attr(tag: str, naam: str) -> str:
    m = re.search(rf'{naam}="([^"]*)"', tag)
    return m.group(1) if m else ""


def _titel(tag: str, inhoud: str, nr: int) -> str:
    """Hoe deze pagina op het canvas heet.

    De naamstrip boven een artboard is het enige wat je ziet als je
    uitzoomt, dus hij moet zeggen wáár je bent. De folio erbij, want dat
    is het nummer waarop iemand naar een pagina verwijst — behalve op de
    pagina's die geen folio dragen, want daar zegt een cijfer niets.

    Het onderscheid komt uit de inhoud en niet uit de attributen. De
    omslag en het achterblad dragen allebei `data-opener` en allebei een
    `data-folio`, want de zetmotor zet dat nummer op élke pagina als
    gegeven — ook waar het niet gedrukt wordt. Wat ze uit elkaar houdt is
    de klasse op het blok erbinnen.
    """
    if "data-blanco" in tag:
        return f"{nr} · blanco"
    if "omslag--achter" in inhoud:
        return "Achterblad"
    if _attr(tag, "data-opener") == "omslag" or 'class="omslag"' in inhoud:
        return "Omslag"
    folio = _attr(tag, "data-folio")
    voor = folio if folio and folio != "nee" else str(nr)
    kop = _attr(tag, "data-kopregel")
    if not kop and 'class="inhoud' in inhoud:
        kop = "Inhoudsopgave"
    if not kop:
        m = re.search(r'<h1[^>]*class="(?:opener__titel|extra__titel)"[^>]*>(.*?)</h1>',
                      inhoud, re.S)
        if m:
            kop = re.sub(r"<[^>]+>", "", m.group(1))
    kop = _html.unescape(kop).strip()
    return f"{voor} · {kop}" if kop else voor


def snij(markup: str) -> tuple[str, list[dict]]:
    """De stijl en de losse pagina's uit het gebouwde bestand."""
    m = re.search(r"<style>(.*?)</style>", markup, re.S | re.I)
    stijl = m.group(1).strip() if m else ""

    treffers = list(PAGINA.finditer(markup))
    if not treffers:
        sys.exit("geen pagina's gevonden. Is dit een gebouwd rapport?")

    paginas = []
    for i, t in enumerate(treffers):
        eind = treffers[i + 1].start() if i + 1 < len(treffers) else len(markup)
        stuk = markup[t.start():eind]
        # Het staartje van het bestand hangt aan de laatste pagina; knip
        # het af op de sluitende divs die erbij horen.
        stuk = re.split(r"\n</div>\s*</body>", stuk)[0]
        if not stuk.rstrip().endswith("</div>"):
            stuk = stuk.rstrip() + "\n</div>"
        paginas.append({"tag": t.group(0), "attrs": t.group(1), "html": stuk})
    return stijl, paginas


def maten(stijl: str, tag: str) -> tuple[int, int]:
    """De bladmaat in px, uit de `@page`-regel of uit het formaat."""
    m = re.search(r"@page\s*{[^}]*size:\s*([\d.]+)mm\s+([\d.]+)mm", stijl)
    if m:
        mm_naar_px = 96 / 25.4
        return round(float(m.group(1)) * mm_naar_px), round(float(m.group(2)) * mm_naar_px)
    formaten = {"sfnl": (794, 1039), "a4": (794, 1123), "a4-liggend": (1123, 794)}
    return formaten.get(_attr(tag, "data-formaat"), (794, 1039))


def bouw(html_pad: Path, uit: Path | None = None) -> dict:
    markup = html_pad.read_text(encoding="utf-8")
    stijl, paginas = snij(markup)
    doel = uit or (html_pad.parent / "canvas")
    doel.mkdir(parents=True, exist_ok=True)

    # Wat er van een vorige ronde staat gaat eerst weg. Een rapport dat
    # korter wordt, laat anders artboards van de oude lengte staan en die
    # blijven gewoon in het canvas hangen.
    for oud in doel.glob("*.dc.html"):
        oud.unlink()

    # De letters eruit en één keer ernaast. Zie de kop van dit bestand.
    fonts = "\n".join(FONTBLOK.findall(stijl))
    (doel / "fonts.css").write_text(fonts, encoding="utf-8")
    kaal = FONTBLOK.sub("", stijl)
    stijl_ingesprongen = "\n".join("    " + r if r.strip() else r
                                   for r in kaal.splitlines() if r.strip())
    lijst = []
    for i, p in enumerate(paginas, start=1):
        naam = "Main" if i == 1 else f"p{i:03d}"
        breedte, hoogte = maten(stijl, p["tag"])
        (doel / f"{naam}.dc.html").write_text(
            SJABLOON.format(stijl=stijl_ingesprongen, inhoud=p["html"]),
            encoding="utf-8")
        lijst.append({"bestand": f"{naam}.dc.html",
                      "breedte": breedte, "hoogte": hoogte,
                      "titel": _titel(p["tag"], p["html"], i)})

    (doel / "canvas.json").write_text(
        json.dumps(manifest(lijst), ensure_ascii=False, indent=1), encoding="utf-8")

    mb = sum(f.stat().st_size for f in doel.iterdir()) / 1e6
    return {"map": str(doel), "artboards": len(lijst),
            "canvas": str(doel / "canvas.json"), "mb": round(mb, 1)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=Path)
    ap.add_argument("--uit", type=Path, default=None)
    a = ap.parse_args()
    if not a.html.exists():
        sys.exit(f"niet gevonden: {a.html}")
    print(json.dumps(bouw(a.html, a.uit), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
