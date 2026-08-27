#!/usr/bin/env python3
"""De pagina's op het canvas neerleggen zoals een lezer ze ziet.

Van beide drukroutes. `ontwerp-documenten` componeert zijn artboards
met de hand en `rapport-deliverable` leidt ze af uit een gezet rapport,
maar de vraag waar ze op het canvas komen te liggen is dezelfde, en het
antwoord ook: **in spreads.**

Dat is geen ordeningskwestie. Een spread is de eenheid waarop editorial
ontwerp beoordeeld wordt — de lezer ziet twee pagina's tegelijk, dus de
linker en de rechter moeten samen kloppen. Wie de pagina's in een rij van
vier neerlegt, kan dat niet zien, en wie ze in één kolom zet ziet het ook
niet. Pagina 1 hangt daarom alleen en aan de rechterkant, zoals een
omslag op een rechterpagina ligt; daarna gaat het 2-3, 4-5.

De maten hieronder komen uit de designskill: tussen twee pagina's van
dezelfde spread hoort de rug (klein), tussen twee spreads hoort de
naamstrip van het frame plus de tweakchips (ruim).
"""

from __future__ import annotations

from pathlib import Path

#: Tussen twee pagina's van dezelfde spread: de rug.
KIER_SPREAD = 24

#: Tussen twee spreads onder elkaar. De naamstrip en de tweakchips staan
#: bóven elk frame, dus hier moet meer lucht dan tussen twee frames
#: naast elkaar.
KIER_RIJ = 150

#: Boven deze breedte staat een pagina altijd alleen op zijn rij: een
#: liggend of dubbelbreed formaat is zelf al een spread.
BREED = 1100


def leg_neer(paginas: list[dict],
             kier_spread: int = KIER_SPREAD,
             kier_rij: int = KIER_RIJ) -> list[dict]:
    """De artboardlijst voor `canvas.json`.

    Elke pagina in ``paginas`` is een woordenboek met ``bestand``,
    ``breedte``, ``hoogte`` en ``titel``. Wat eruit komt is de lijst die
    onder ``artboards`` in het manifest gaat, met ``x``, ``y``, ``w``,
    ``h`` en ``print`` erbij.

    >>> leg_neer([{"bestand": "a.dc.html", "breedte": 794, "hoogte": 1039,
    ...            "titel": "Omslag"}])[0]["x"]
    0
    """
    uit: list[dict] = []
    y = 0
    i = 0
    while i < len(paginas):
        p = paginas[i]
        alleen = (i == 0) or p["breedte"] > BREED
        groep = [p]
        if not alleen and i + 1 < len(paginas):
            volgende = paginas[i + 1]
            if volgende["breedte"] == p["breedte"] and volgende["breedte"] <= BREED:
                groep.append(volgende)
        # Pagina 1 hangt rechts: een omslag ligt op een rechterpagina, en
        # dan valt de eerste spread er onder als 2-3 zoals in het boek.
        x = p["breedte"] + kier_spread if (i == 0 and len(paginas) > 1) else 0
        for q in groep:
            uit.append({
                "file": q["bestand"],
                "x": x, "y": y, "w": q["breedte"], "h": q["hoogte"],
                "title": q.get("titel") or q["bestand"],
                "print": "fixed",
            })
            x += q["breedte"] + kier_spread
        y += max(q["hoogte"] for q in groep) + kier_rij
        i += len(groep)
    return uit


def manifest(paginas: list[dict], **kier) -> dict:
    """Hetzelfde, maar als het hele `canvas.json`."""
    return {"artboards": leg_neer(paginas, **kier), "launch": {"view": "canvas"}}


def zoek_helper() -> str | None:
    """Pad naar `seed-canvas.mjs` van de design-skill, of None.

    Van alle vier de skills, want alle vier leggen hun werk op een canvas voor en alle
    vier hebben hetzelfde probleem: de design-skill wordt per sessie onder een
    versienummer uitgepakt, dus het pad ligt niet vast en dit is een zoekopdracht.

    **En zoeken is niet genoeg -- kiezen is het punt.** Er staan er vaak meer dan een:
    dezelfde skillversie komt onder wisselende hashmappen terecht en er kunnen oudere
    versies naast staan. De eerste versie hiervan nam de alfabetisch laatste, en dat
    kiest niets: van `3b10cbb2` en `ea784c4b` wint de tweede op zijn eerste letter en
    niet omdat hij bij deze sessie hoort. Een oude payload betekent een canvas op een
    verouderde editor, en dat merk je pas als de gebruiker erin klikt. Daarom: hoogste
    skillversie eerst, en daarbinnen de meest recent uitgepakte.
    """
    import glob
    import re
    import tempfile

    def sleutel(p: str) -> tuple:
        m = re.search(r"bundled-skills[\\/]+([0-9][0-9.]*)", p)
        versie = tuple(int(x) for x in m.group(1).split(".")) if m else ()
        try:
            gewijzigd = Path(p).stat().st_mtime
        except OSError:
            gewijzigd = 0.0
        return (versie, gewijzigd)

    wortels = (tempfile.gettempdir(), str(Path.home()), "/tmp")
    for patroon in ("**/bundled-skills/*/*/design/seed-canvas.mjs",
                    "**/design/seed-canvas.mjs"):
        tref: list[str] = []
        for w in wortels:
            try:
                tref += glob.glob(str(Path(w) / patroon), recursive=True)
            except OSError:
                continue
        if tref:
            return max(tref, key=sleutel)
    return None
