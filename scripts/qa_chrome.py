"""Chrome-integriteit op een gebouwde deck: dekt een eigen vorm het logo of het nummer af?

Usage:
    python qa_chrome.py <deck.pptx>
    python qa_chrome.py unpacked            # ook halverwege de bouw
    python qa_chrome.py <deck.pptx> --strict    # ook waarschuwingen geven exit 1

Wat dit script telt, en waarom het een eigen script is
------------------------------------------------------
Het logo linksonder staat niet op de slide. Het is `Picture 4` in `slideMaster2`, en
masterchrome wordt ONDER alles getekend wat de bouwer erop zet. Een opake vorm die tot onder
7,07 loopt wist hem dus stil: de XML is niet fout, geen enkele maat is fout, en tot dit
script bestond zei geen van de drie poorten er iets over. `qa_text.py` gaf op de gemeten
testslide `"verdict": "clean"` terwijl het logo van de render verdwenen was.

`deck-visual-reviewer` heeft chrome-integriteit al als kritiek punt op zijn lijst, maar dat
is een oog op een render — en juist deze fout is op de render niet te zien als een fout: er
staat gewoon een kaart. Wat hier gemeten wordt is de OORZAAK, met de vorm erbij die het doet.

De regel en de uitzondering staan in `chrome.py`; dit script is de CLI eromheen. Kort:
een vorm die de chrome gedeeltelijk afsnijdt is een `critical`, een vol vlak over de héle
slide is een `warn` (dat is het verzadigde register van de uitspraakslide), en een
doorschijnende vulling erover is een `warn`.

Output is compacte JSON. Exit 1 zodra er een `critical` staat, of bij `--strict` ook op een
`warn`.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _deck import emit  # noqa: E402
from chrome import Bron, meet_slide  # noqa: E402


def analyse(doel: Path) -> dict:
    with Bron(doel) as bron:
        slides = bron.slides()
        gemeten = [meet_slide(bron, part) for part in slides]

    findings = []
    for meting in gemeten:
        for bevinding in meting["findings"]:
            findings.append({"slide": meting["slide"], "layout": meting["layout"],
                             **bevinding})

    counts = Counter(f["severity"] for f in findings)
    return {
        "deck": str(doel),
        "slides": len(gemeten),
        "zonder_chrome": [m["slide"] for m in gemeten if not m["chrome"]],
        "findings": findings,
        "counts": {"critical": counts["critical"], "warn": counts["warn"]},
        "verdict": "blocked" if counts["critical"] else "clean" if not findings else "warn",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", help="een .pptx/.potx of een uitgepakte map")
    parser.add_argument("--strict", action="store_true",
                        help="ook een waarschuwing geeft exit 1")
    args = parser.parse_args()

    doel = Path(args.deck)
    if not doel.exists():
        raise SystemExit(f"niet gevonden: {doel}")

    result = analyse(doel)
    emit(result)

    if result["counts"]["critical"] or (args.strict and result["counts"]["warn"]):
        sys.exit(1)


if __name__ == "__main__":
    main()
