#!/usr/bin/env python3
"""Wat er verandert wanneer een document naar de drukker gaat.

Dit bestand is van twee skills tegelijk. `sfnl-design-documents` maakt
kort drukwerk en `sfnl-rapport-opmaak` maakt lange rapporten, en op dit
punt stellen ze dezelfde vraag: het aantal pagina's moet uitkomen. De
rekensom stond tot nu toe alleen in proza in
`reference/documenten-stramien.md`, en werd door geen van beide routes
uitgerekend — dus stond er in het ene verslag "45 pagina's" en moest de
gebruiker zelf bedenken dat dat op de pers niet bestaat.

**Waarom een veelvoud van vier.** Een gebonden of geniet drukwerk wordt
niet per pagina gedrukt maar per vel, en een vel dat je dubbelvouwt
levert vier pagina's op: twee aan de voorkant, twee aan de achterkant.
Een rapport van 45 pagina's wordt dus 48 pagina's papier, en die laatste
drie zijn er hoe dan ook. De vraag is alleen of jij bepaalt wat erop
staat of dat de drukker er iets van maakt.

**Wat dit bestand niet doet.** Het rekent, het beslist niet. Er zijn drie
uitwegen uit een aantal dat niet uitkomt — pagina's erbij, pagina's eraf,
of het bij een PDF houden — en welke de goede is hangt af van wat het
document is. Stilzwijgend afronden is het defect; dat staat al zo in de
documentenskill en het geldt hier net zo hard.

Afloop en snijtekens zitten er bewust **niet** in. In beide routes is de
snijrand `overflow: hidden` op `.pagina` en is er geen gebied buiten het
blad; een echte afloop van 3 mm verandert de bladmaat en raakt de
formatentabel op drie plekken. Dat is een aparte ingreep en geen vlag.
"""

from __future__ import annotations

#: Het gebruikelijke katern. Vier pagina's uit één dubbelgevouwen vel.
KATERN = 4

#: Wat er op de pers bestaat en wat niet, bij kleine oplagen. Uit
#: `reference/documenten-stramien.md`: één vel enkelzijdig is 1 pagina,
#: dubbelzijdig 2, en 3 bestaat niet op papier.
LOSSE_VELLEN = (1, 2)


def _pag(n: int) -> str:
    """"1 pagina" en "2 pagina's". De zin gaat naar de gebruiker."""
    return f"{n} pagina" if n == 1 else f"{n} pagina's"


def katern(paginas: int, gedrukt: bool = True, maat: int = KATERN) -> dict:
    """Wat er met dit aantal pagina's moet gebeuren voor de pers.

    Levert altijd hetzelfde woordenboek, ook wanneer er niets hoeft:

    * ``klopt`` — komt het aantal uit
    * ``maat`` — het katern waarop gerekend is
    * ``tekort`` — hoeveel pagina's erbij moeten om naar boven uit te komen
    * ``teveel`` — hoeveel eraf moeten om naar beneden uit te komen
    * ``naar_boven`` / ``naar_beneden`` — de twee aantallen zelf
    * ``uitleg`` — één zin die je kunt teruggeven aan de gebruiker

    >>> katern(45)["tekort"]
    3
    >>> katern(48)["klopt"]
    True
    >>> katern(2, gedrukt=True)["klopt"]
    True
    """
    paginas = max(0, int(paginas))
    maat = max(1, int(maat))

    if not gedrukt:
        return {"klopt": True, "maat": maat, "paginas": paginas,
                "tekort": 0, "teveel": 0,
                "naar_boven": paginas, "naar_beneden": paginas,
                "uitleg": "blijft een PDF, dus het aantal pagina's is vrij"}

    # Een los vel is geen katern. Twee pagina's zijn de voor- en
    # achterkant van één vel en die hoeven niet naar vier.
    if paginas in LOSSE_VELLEN:
        return {"klopt": True, "maat": maat, "paginas": paginas,
                "tekort": 0, "teveel": 0,
                "naar_boven": paginas, "naar_beneden": paginas,
                "uitleg": f"{_pag(paginas)} is één vel en hoeft niet naar {maat}"}

    rest = paginas % maat
    if rest == 0:
        return {"klopt": True, "maat": maat, "paginas": paginas,
                "tekort": 0, "teveel": 0,
                "naar_boven": paginas, "naar_beneden": paginas,
                "uitleg": f"{_pag(paginas)} is een veelvoud van {maat}"}

    tekort = maat - rest
    boven, beneden = paginas + tekort, paginas - rest
    # Naar beneden is alleen een uitweg als er een document overblijft.
    # Bij drie pagina's is "er drie af" nul pagina's, en dat is geen
    # advies maar een rekenfout die eruitziet als een advies.
    omlaag_kan = beneden >= maat
    uitleg = (f"{_pag(paginas)} komt niet uit op een katern van {maat}: "
              f"er moeten er {tekort} bij (naar {boven})")
    uitleg += f" of {rest} af (naar {beneden})" if omlaag_kan else ""
    return {
        "klopt": False, "maat": maat, "paginas": paginas,
        "tekort": tekort, "teveel": rest if omlaag_kan else 0,
        "naar_boven": boven, "naar_beneden": beneden if omlaag_kan else boven,
        "uitleg": uitleg,
    }


def opvulling(paginas: int, gedrukt: bool = True, maat: int = KATERN) -> int:
    """Hoeveel blanco pagina's er achteraan moeten. Nul als het uitkomt."""
    return katern(paginas, gedrukt, maat)["tekort"]


if __name__ == "__main__":
    import json
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 45
    print(json.dumps(katern(n), ensure_ascii=False, indent=2))
