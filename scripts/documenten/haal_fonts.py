#!/usr/bin/env python3
"""De huisstijlletters ophalen en insluiten, één keer, als onderhoudsstap.

Waarom dit bestaat. Een document dat zijn letters van Google Fonts haalt, ziet er
op drie plekken anders uit dan bedoeld:

* **In de render.** Chromium in een sandbox heeft lang niet altijd internet. De
  eerste proefdocument van deze skill kwam in Helvetica uit de renderloop, en dan
  meet je de verkeerde regelafbreking en beoordeel je de verkeerde vorm.
* **In de PNG- en PDF-export van het canvas.** Die kan een Google Font niet
  meenemen; geëxporteerde tekst valt terug op de systeemletter.
* **Bij de gebruiker.** Een document dat alleen met internet goed staat, is geen
  bestand maar een verzoek.

Ingesloten `@font-face` met een `data:`-URI lost alle drie tegelijk op. Het kost
ongeveer 180 kB per artboard en dat is de prijs waard.

Montserrat en Lato staan beide onder de SIL Open Font License 1.1, dus
meeleveren mag, met de licentietekst erbij. Gotham Bold niet — dat is
commercieel en het gaat deze repo nooit in. Montserrat ExtraBold is de
substituut, en dat is niet gekozen maar overgenomen: het SFNL-drukwerk zelf
zet zijn display-regels al in Montserrat ExtraBold (gemeten in de casespread).

Alleen de `latin`-subset wordt opgehaald. Dat scheelt ruim de helft en het
Nederlands past erin; wie Grieks of Cyrillisch nodig heeft, heeft een ander
probleem.

Gebruik:

    python haal_fonts.py                 # naar assets/documenten/fonts/
    python haal_fonts.py --controleer    # zeg alleen of het compleet is
"""

from __future__ import annotations

import argparse
import base64
import re
import sys
import urllib.request
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOEL = HIER.parent.parent / "assets" / "documenten" / "fonts"

CSS_URL = ("https://fonts.googleapis.com/css2"
           "?family=Montserrat:wght@300;400;700;800"
           "&family=Lato:ital,wght@0,300;0,400;0,700;1,300;1,400"
           "&display=swap")

# Chromium-UA, anders levert Google een TTF-variant in plaats van woff2.
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/120.0.0.0 Safari/537.36")

OFL = "https://raw.githubusercontent.com/google/fonts/main/ofl/{map}/OFL.txt"

#: De negen sneden die `stijl.css` werkelijk aanspreekt. Meer insluiten is
#: gewicht zonder gebruik; minder is een snede die stil in Arial valt.
NODIG = {
    ("Montserrat", "normal", "300"), ("Montserrat", "normal", "400"),
    ("Montserrat", "normal", "700"), ("Montserrat", "normal", "800"),
    ("Lato", "normal", "300"), ("Lato", "normal", "400"),
    ("Lato", "normal", "700"), ("Lato", "italic", "300"),
    ("Lato", "italic", "400"),
}


def _haal(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read()


def _ontleed(css: str) -> list[dict]:
    """De @font-face-blokken van de latin-subset, in volgorde."""
    uit = []
    for blok in re.findall(r"@font-face\s*\{(.*?)\}", css, re.S):
        def veld(naam: str) -> str:
            m = re.search(rf"{naam}\s*:\s*([^;]+);", blok)
            return m.group(1).strip().strip("'\"") if m else ""
        src = re.search(r"url\((https://[^)]+\.woff2)\)", blok)
        bereik = veld("unicode-range")
        # De latin-subset is het blok zonder U+0100-02BA aan het begin; het
        # latin-ext-blok begint daar juist mee. Dat is het enige verschil
        # waarop je ze uit elkaar houdt zonder de commentaarregels te lezen.
        if not src or bereik.startswith("U+0100"):
            continue
        if "U+0000-00FF" not in bereik:
            continue
        uit.append({"familie": veld("font-family"), "stijl": veld("font-style"),
                    "gewicht": veld("font-weight"), "url": src.group(1),
                    "bereik": bereik})
    return uit


def haal(doel: Path) -> dict:
    doel.mkdir(parents=True, exist_ok=True)
    css = _haal(CSS_URL).decode("utf-8")
    sneden = _ontleed(css)

    gevonden = {(s["familie"], s["stijl"], s["gewicht"]) for s in sneden}
    mist = NODIG - gevonden
    if mist:
        print(f"let op: niet gevonden in de Google-CSS: {sorted(mist)}", file=sys.stderr)

    regels = [
        "/* SFNL-documentletters, ingesloten.",
        " *",
        " * Gegenereerd door scripts/documenten/haal_fonts.py — niet met de hand bijwerken.",
        " * Montserrat en Lato, SIL Open Font License 1.1, latin-subset.",
        " * De licentietekst staat naast dit bestand in OFL-Montserrat.txt en",
        " * OFL-Lato.txt en hoort mee te reizen met elke kopie.",
        " */",
        "",
    ]
    # Montserrat komt als één variabel bestand terug dat álle gewichten draagt:
    # Google serveert voor 300, 400, 700 en 800 dezelfde URL. Vier keer
    # insluiten is dan 114 kB weggegooid, en het is een echte val — de eerste
    # versie van dit script deed het en kwam op 258 kB uit waar 148 kB volstaat.
    # Eén URL wordt dus één @font-face met een gewichtsbereik.
    groepen: dict[tuple[str, str, str], list[str]] = {}
    for s in sneden:
        if (s["familie"], s["stijl"], s["gewicht"]) not in NODIG:
            continue
        groepen.setdefault((s["url"], s["familie"], s["stijl"]), []).append(s["gewicht"])

    totaal = 0
    for (url, familie, stijl), gewichten in groepen.items():
        data = _haal(url)
        totaal += len(data)
        g = sorted(int(x) for x in gewichten)
        merk = f"{g[0]}-{g[-1]}" if len(g) > 1 else str(g[0])
        naam = f"{familie}-{merk}{'i' if stijl == 'italic' else ''}.woff2"
        (doel / naam).write_bytes(data)
        b64 = base64.b64encode(data).decode("ascii")
        regels += [
            f"/* {familie} {stijl} {merk}"
            + (" — variabel bestand, dekt het hele bereik */" if len(g) > 1 else " */"),
            "@font-face {",
            f"  font-family: '{familie}';",
            f"  font-style: {stijl};",
            f"  font-weight: {g[0]} {g[-1]};" if len(g) > 1 else f"  font-weight: {g[0]};",
            "  font-display: block;",
            f"  src: url(data:font/woff2;base64,{b64}) format('woff2');",
            "}",
        ]
    (doel / "fonts.css").write_text("\n".join(regels) + "\n", encoding="utf-8")

    for familie, mapnaam in (("Montserrat", "montserrat"), ("Lato", "lato")):
        try:
            tekst = _haal(OFL.format(map=mapnaam)).decode("utf-8")
            (doel / f"OFL-{familie}.txt").write_text(tekst, encoding="utf-8")
        except Exception as e:  # pragma: no cover
            print(f"let op: OFL voor {familie} niet opgehaald ({e}). "
                  f"Zet hem er met de hand bij — meeleveren zonder licentie mag niet.",
                  file=sys.stderr)

    kb = (doel / "fonts.css").stat().st_size / 1024
    return {"sneden": len(NODIG) - len(mist), "woff2_bytes": totaal,
            "fonts_css_kb": round(kb, 1), "map": str(doel)}


def controleer(doel: Path) -> int:
    css = doel / "fonts.css"
    if not css.exists():
        print(f"NEE  {css} ontbreekt — draai `python haal_fonts.py`")
        return 1
    tekst = css.read_text(encoding="utf-8")
    n = tekst.count("@font-face")
    # Niet tellen tegen NODIG: een variabel bestand dekt meerdere gewichten in
    # één face, dus het aantal faces is kleiner dan het aantal sneden. Wat je
    # wél kunt toetsen is of beide families erin zitten en of er een cursieve
    # snede is — dat zijn de drie manieren waarop dit stil kapot gaat.
    families = [f for f in ("Montserrat", "Lato") if f"'{f}'" in tekst]
    cursief = "font-style: italic" in tekst
    licenties = [p.name for p in doel.glob("OFL-*.txt")]
    print(f"ja   {css} — {n} faces, {css.stat().st_size / 1024:.0f} kB")
    print(f"{'ja  ' if len(families) == 2 else 'NEE '} families: "
          f"{', '.join(families) or 'geen'}")
    print(f"{'ja  ' if cursief else 'NEE '} cursief aanwezig")
    print(f"{'ja  ' if len(licenties) == 2 else 'NEE '} licenties: "
          f"{', '.join(licenties) or 'geen'}")
    return 0 if len(families) == 2 and cursief and len(licenties) == 2 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--doel", type=Path, default=DOEL)
    ap.add_argument("--controleer", action="store_true")
    a = ap.parse_args()
    if a.controleer:
        return controleer(a.doel)
    r = haal(a.doel)
    print(f"{r['sneden']} sneden ingesloten, "
          f"{r['woff2_bytes'] / 1024:.0f} kB woff2 → {r['fonts_css_kb']} kB CSS")
    print(f"in {r['map']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
