#!/usr/bin/env python3
"""Zoek het .pptx-bestand dat gecontroleerd moet worden, vóór er iets anders gebeurt.

Usage:
    python vind.py
    python vind.py --pad /mnt/user-data/uploads/deck.pptx
    python vind.py --map ./werk

Waarom dit een script is
------------------------
Een deck komt langs drie oppervlakken binnen en op elk staat hij op een andere plek: de
PowerPoint-plugin schrijft het actieve document naar een vaste map (en zet soms
`CLAUDE_PPTX_PATH`), Claude.ai en Cowork zetten een upload in `/mnt/user-data/uploads/`,
en in een projectmap ligt hij gewoon ergens. Wie dat niet in één keer nakijkt, vraagt de
gebruiker om een bestand dat hij al heeft aangeleverd. Dat is de eerste stap van
`deck-check` en de reden dat hij mechanisch is.

De uitkomst is compacte JSON:

    {"pad": "...", "bron": "upload", "kandidaten": [...], "vraag": null}

`bron` is `plugin-env`, `plugin-pad`, `upload`, `map` of `argument`. Staat er meer dan
één kandidaat, dan is `pad` null, staan ze alle in `kandidaten` en zegt `vraag` welke
korte vraag de gebruiker krijgt. Is er niets, dan zegt `vraag` wat je moet vragen —
verschillend per oppervlak, want in de plugin is "sleep het bestand hierheen" geen
bruikbaar antwoord.

Exitcode is 0 zodra er precies één bestand ligt, en 1 bij nul of meer dan één. De JSON
is het antwoord; lees `vraag` en stel die vraag, verzin er geen eigen.
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _deck import emit  # noqa: E402

# De vaste plekken waar de PowerPoint-plugin het actieve document neerzet.
PLUGIN_PADEN = (
    "/mnt/user-data/pptx/active.pptx",
    "/tmp/active_presentation.pptx",
    "/tmp/claude_pptx_input.pptx",
)

UPLOAD_PATRONEN = (
    "/mnt/user-data/uploads/**/*.pptx",
    "/mnt/user-data/uploads/*.pptx",
)

VRAAG_PLUGIN = (
    "De plugin heeft het pad van het actieve document niet doorgegeven. Vraag de "
    "gebruiker het bestand op te slaan en deze chat opnieuw te openen, of met "
    "Bestand > Opslaan als een kopie te maken en die hier aan te leveren."
)

VRAAG_UPLOAD = (
    "Er is geen .pptx gevonden. Vraag de gebruiker het bestand aan te leveren met de "
    "paperclip."
)

VRAAG_KEUZE = (
    "Er liggen meerdere .pptx-bestanden. Stel één korte vraag: welke moet ik "
    "controleren?"
)


def in_plugin() -> bool:
    """Draaien we in de PowerPoint-plugin? Dan is de vervolgvraag een andere."""
    if os.environ.get("CLAUDE_PPTX_PATH"):
        return True
    return Path("/mnt/user-data/pptx").is_dir()


def zoek(map_: str | None) -> tuple[str | None, str | None, list[str]]:
    """Geeft (pad, bron, kandidaten). Pad is None zodra er niet precies één is."""
    env = os.environ.get("CLAUDE_PPTX_PATH", "")
    if env and Path(env).is_file():
        return env, "plugin-env", [env]

    for kandidaat in PLUGIN_PADEN:
        if Path(kandidaat).is_file():
            return kandidaat, "plugin-pad", [kandidaat]

    uploads: list[str] = []
    for patroon in UPLOAD_PATRONEN:
        uploads += glob.glob(patroon, recursive=True)
    uploads = sorted({p for p in uploads if Path(p).is_file()})
    if len(uploads) == 1:
        return uploads[0], "upload", uploads
    if len(uploads) > 1:
        return None, "upload", uploads

    if map_:
        lokaal = sorted(
            str(p) for p in Path(map_).rglob("*.pptx")
            if p.is_file() and not p.name.startswith("~$")
        )
        if len(lokaal) == 1:
            return lokaal[0], "map", lokaal
        if len(lokaal) > 1:
            return None, "map", lokaal

    return None, None, []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pad", help="een bekend pad; slaat het zoeken over")
    parser.add_argument("--map", help="ook deze projectmap doorzoeken")
    args = parser.parse_args()

    if args.pad:
        pad = Path(args.pad)
        if not pad.is_file():
            emit({"pad": None, "bron": "argument", "kandidaten": [],
                  "vraag": f"{args.pad} bestaat niet."})
            return 1
        emit({"pad": str(pad), "bron": "argument", "kandidaten": [str(pad)],
              "vraag": None})
        return 0

    pad, bron, kandidaten = zoek(args.map)
    if pad:
        emit({"pad": pad, "bron": bron, "kandidaten": kandidaten, "vraag": None})
        return 0

    vraag = VRAAG_KEUZE if kandidaten else (
        VRAAG_PLUGIN if in_plugin() else VRAAG_UPLOAD
    )
    emit({"pad": None, "bron": bron, "kandidaten": kandidaten, "vraag": vraag})
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
