#!/usr/bin/env python3
"""Welk fontbestand hoort bij een familienaam. Eén keer, voor alle routes.

    python fonts.py "Lato Light" "Montserrat SemiBold"

Waarom dit script bestaat
-------------------------
Er stonden twee fontvinders in deze plugin: `find_font_file()` in
`scripts/_deck.py` voor de deckmeting, en `vind_font()` in
`scripts/infographic/svg.py` voor de SVG-meting. Ze zochten in bijna dezelfde
mappen en ze kozen anders, en de tweede koos fout.

**Het defect, gemeten.** `vind_font("Lato Light")` globde op
`*LatoLight*.ttf` en nam het eerste resultaat uit `sorted()`. In een map met
`LatoLight-Italic.ttf` en `LatoLight-Regular.ttf` sorteert `Italic` vóór
`Regular`, dus de meting liep op de cursief. Die is 6,3 procent smaller dan de
romein — meer dan de veiligheidsmarge van 3,5 procent waarmee de regelschatter
werkt, en met het teken de verkeerde kant op: de meting zegt dat er meer op een
regel past dan er werkelijk past. En `preflight.py` meldde er `meting_echt:
true` bij, dus het gaf een schatting de status van bewijs.

Dat is de gevaarlijkste soort fout die deze plugin kan maken, want hij is
onzichtbaar: er staat een fontbestand, de meting draait, er komt een getal uit,
en niets klaagt. Alleen op de render zie je een regel die net niet valt waar de
meting hem zette.

`_deck.py` had dit al goed opgelost — "de bestandsnaam die het minst aan de
familie toevoegt wint, `Regular` telt als niets, en cursief matcht alleen als de
familie erom vraagt" — en die logica staat nu hier, zodat er één antwoord is.

Wat hier NIET in staat
----------------------
De zoekmappen per route, en de terugval. De deckroute wil een volledige statische
snede en valt terug op schatten; de SVG-route valt terug op het ingesloten woff2
dat de plugin zelf meedraagt. Dat verschil is echt en blijft bij de route.
Gedeeld is alleen de vraag: *welke van deze bestanden is de familie die ik
vroeg?*
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

#: De cursiefstraf. Hoog genoeg dat een cursief nooit van een romein wint, ook
#: niet wanneer zijn bestandsnaam korter is — `LatoIt.ttf` tegen
#: `LatoLight-Regular.ttf` was precies dat geval.
CURSIEF_STRAF = 100

#: Wat in een bestandsnaam als "niets toegevoegd" telt. `Regular` en `Book` zijn
#: de twee namen die drukkers voor de romein gebruiken.
GEEN_TOEVOEGING = ("", "regular", "book")

SNEDES = ("ttf", "otf", "ttc")


def kaal(naam: str) -> str:
    """Alleen letters en cijfers, in onderkast. `Lato Light` -> `latolight`."""
    return "".join(c for c in naam.lower() if c.isalnum())


def score(bestandsnaam: str, familie: str) -> int | None:
    """Hoe goed past dit bestand bij deze familie? Lager is beter, None is niet.

    De regel: het bestand dat het mínst aan de gevraagde familie toevoegt wint.
    Matchen op "bevat" alleen kiest `Montserrat-Black` voor `Montserrat`, en
    Black is aanzienlijk breder dan Regular — genoeg om een regel die past als
    overloop te melden.

    >>> score("LatoLight-Regular", "latolight")
    0
    >>> score("LatoLight-Italic", "latolight") > CURSIEF_STRAF
    True
    >>> score("Montserrat-Black", "montserrat")
    5
    >>> score("Roboto-Regular", "latolight") is None
    True

    En de cursief verliest ook als zijn naam korter is:

    >>> score("LatoIt", "lato") > score("Lato-Regular", "lato")
    True
    """
    stam = kaal(bestandsnaam)
    if familie not in stam:
        return None
    rest = stam.replace(familie, "", 1)
    punten = 0 if rest in GEEN_TOEVOEGING else len(rest)
    if "italic" in rest or "oblique" in rest or rest.endswith("it"):
        punten += CURSIEF_STRAF
    return punten


def kies_beste(paden, familie: str) -> Path | None:
    """Het beste bestand uit `paden` voor `familie`, of None.

    Bij gelijke score wint de alfabetisch eerste stam, zodat de uitkomst niet
    van de mapvolgorde afhangt — twee runs op dezelfde machine moeten hetzelfde
    bestand kiezen, anders is de meting niet reproduceerbaar.
    """
    gevraagd = kaal(familie)
    if not gevraagd:
        return None
    beste: tuple[int, str] | None = None
    beste_pad: Path | None = None
    for pad in paden:
        pad = Path(pad)
        punten = score(pad.stem, gevraagd)
        if punten is None:
            continue
        sleutel = (punten, kaal(pad.stem))
        if beste is None or sleutel < beste:
            beste, beste_pad = sleutel, pad
    return beste_pad


def in_mappen(familie: str, mappen) -> Path | None:
    """`kies_beste` over elk fontbestand in `mappen`, recursief."""
    kandidaten: list[Path] = []
    gezien: set[str] = set()
    for wortel in mappen:
        wortel = Path(wortel)
        if not wortel.exists():
            continue
        for snede in SNEDES:
            for patroon in (f"*.{snede}", f"*.{snede.upper()}",
                            f"**/*.{snede}", f"**/*.{snede.upper()}"):
                for kand in glob.glob(str(wortel / patroon), recursive=True):
                    sleutel = kand.lower()
                    if sleutel not in gezien:
                        gezien.add(sleutel)
                        kandidaten.append(Path(kand))
    return kies_beste(kandidaten, familie)


def systeemmappen() -> list[Path]:
    """Waar een geïnstalleerde snede staat, per platform."""
    import os
    import platform
    if platform.system() == "Windows":
        lok = os.environ.get("LOCALAPPDATA", "")
        return [Path(r"C:\Windows\Fonts"),
                Path(lok) / "Microsoft" / "FontCache" / "4" / "CloudFonts"]
    return [Path("/usr/share/fonts"), Path("/usr/local/share/fonts"),
            Path.home() / ".fonts", Path.home() / ".local" / "share" / "fonts",
            Path("/Library/Fonts"), Path.home() / "Library" / "Fonts"]


def main() -> int:
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("familie", nargs="+")
    args = a.parse_args()
    uit = {}
    for fam in args.familie:
        pad = in_mappen(fam, systeemmappen())
        uit[fam] = str(pad) if pad else None
    print(json.dumps(uit, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
