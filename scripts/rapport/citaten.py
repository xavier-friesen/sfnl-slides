#!/usr/bin/env python3
"""Verwijzingen in de lopende tekst gelijktrekken, en dat opschrijven.

Dit is het enige script in deze skill dat de tekst van de gebruiker
aanraakt buiten de toestemmingspoort om, en dat is een besluit van de
opdrachtgever: een verwijzing omzetten of gelijktrekken telt als opmaak
en niet als herschrijven. De prijs die daarbij hoort is dat elke
omzetting wordt vastgelegd — welk blok, wat er stond, wat er komt te
staan — en dat `tekstcheck.py` ze allemaal apart uitschrijft bij de
oplevering. Wat er verandert blijft dus zichtbaar; het gaat alleen niet
meer per geval langs de gebruiker.

Drie doelen:

* **`zoals-aangeleverd`** — er verandert niets. De default.
* **`uniform`** — auteur-jaarverwijzingen krijgen overal dezelfde vorm:
  `et al.` in plaats van `e.a.` of `et. al.`, en een komma voor het
  jaartal. Dit is wat "consistente opmaak van verwijzingen" meestal
  betekent: het systeem klopt al, de uitvoering niet.

  Wat er bewust **niet** gebeurt is `en` vervangen door `&`. Dat lijkt
  dezelfde soort ingreep en is het niet: in een verwijzing naar het
  "Ministerie van Sociale Zaken en Werkgelegenheid" hoort dat `en` bij
  de naam. Op de eerste proef maakte de regel daar "Sociale Zaken &
  Werkgelegenheid" van, en dat is een organisatie die niet bestaat.
  Er is geen manier om aan de tekst te zien of een `en` twee auteurs
  scheidt of in een naam staat, dus blijft hij staan.
* **`genummerd`** — auteur-jaarverwijzingen worden `[3]`, en de
  bronnenlijst wordt op citatievolgorde genummerd. Alleen mogelijk
  wanneer er een bronnenlijst is: het nummer moet ergens naar wijzen.

Wat er **niet** in zit en waarom: omzetten naar voetnootverwijzingen.
Dat vraagt een noottekst per verwijzing, en die moet uit de bronregel
worden gemaakt — dan staat dezelfde regel twee keer in het rapport, één
keer in de noot en één keer in de lijst, en dat is een inhoudelijk
besluit over hoe het rapport zijn bronnen presenteert en niet langer een
kwestie van vorm. Kies daarvoor `noten: voetnoot` met een bronnenlijst
erbij; dat is hetzelfde resultaat zonder dat er tekst wordt aangemaakt.

Een verwijzing die niet aan een bronregel te koppelen is, **blijft staan
zoals hij stond** en wordt gemeld. Dat is de eerlijke faalwijze: liever
één verwijzing die uit de toon valt dan een nummer dat nergens naar
wijst.

Gebruik:

    python citaten.py werkmap/ --naar uniform
    python citaten.py werkmap/ --naar genummerd
    python citaten.py werkmap/ --naar zoals-aangeleverd     # gooit de omzetting weg
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
from lees_docx import AUTEUR_JAAR, normaliseer  # noqa: E402

DOELEN = ("zoals-aangeleverd", "uniform", "genummerd")

#: De achternaam en het jaartal uit een bronregel. De achternaam is wat
#: er vóór de eerste komma staat; het jaartal is het eerste viercijferige
#: getal tussen 1800 en 2099. Dat is grof, en het is precies grof genoeg:
#: een bronnenlijst die anders is opgebouwd levert geen koppeling op, en
#: dan blijft de verwijzing staan zoals hij stond.
BRONREGEL = re.compile(
    r"^\s*(?P<naam>[^,(]{2,60}?)\s*[,(].{0,200}?(?P<jaar>1[89]\d{2}|20\d{2})[a-z]?\b")

#: De achternaam en het jaartal uit een verwijzing in de tekst.
IN_TEKST = re.compile(
    r"\((?:zie\s+)?(?P<naam>[A-ZÀ-Þ][\w'’-]+)(?P<rest>[^)]*?)"
    r"(?P<jaar>1[89]\d{2}|20\d{2})[a-z]?(?P<staart>[^)]*)\)")


def sleutel(naam: str, jaar: str) -> tuple:
    return (re.sub(r"[^\w]", "", naam).lower(), jaar)


def sleutels_van(naam: str, jaar: str) -> list:
    """Alle sleutels waaronder een naam gevonden mag worden.

    Twee, en de tweede is er voor de organisaties. "Boogers" vindt
    "Boogers, M., P-J. Klok e.a. (2016)" op de eerste sleutel. Het
    "Ministerie van Sociale Zaken en Werkgelegenheid" vindt zichzelf
    alleen op de volledige naam, want de eerste sleutel zou "Ministerie"
    zijn en dat is de helft van de rijksoverheid. Dus allebei.
    """
    kaal = re.sub(r"\b(et\s+al\.?|e\.?\s?a\.?)\b", "", naam, flags=re.I)
    kaal = kaal.strip(" ,;&").strip()
    uit = [sleutel(kaal, jaar)]
    eerste = re.split(r"[\s,;&]+", kaal)[0] if kaal else ""
    if eerste and sleutel(eerste, jaar) not in uit:
        uit.append(sleutel(eerste, jaar))
    return uit


def lees_bronnen(doc: dict) -> dict:
    """De bronregels op (achternaam, jaar), plus hun blok-id."""
    ap = doc.get("apparaat", {})
    lijst = ap.get("bronnenlijst")
    if not lijst:
        return {}
    ids = [b["id"] for b in doc["blokken"]]
    try:
        a, z = ids.index(lijst["vanaf"]), ids.index(lijst["tot"])
    except ValueError:
        return {}
    uit = {}
    for b in doc["blokken"][a:z + 1]:
        m = BRONREGEL.match(b.get("tekst", ""))
        if not m:
            continue
        waarde = {"id": b["id"], "regel": b["tekst"].strip()}
        for sl in sleutels_van(m.group("naam"), m.group("jaar")):
            uit.setdefault(sl, waarde)
    return uit


def uniform(m: re.Match) -> str:
    """Eén auteur-jaarverwijzing in de standaardvorm.

    Wat er gelijkgetrokken wordt: `e.a.` en `et. al.` worden `et al.`,
    en er komt een komma voor het jaartal. Wat er niet gebeurt: namen
    aanvullen, een ontbrekend jaartal verzinnen, de volgorde van auteurs
    veranderen, of `en` vervangen door `&` — zie de kop van dit bestand.
    """
    rest = m.group("rest")
    rest = re.sub(r"\be\.?\s?a\.?(?=\s|,|$)", "et al.", rest)
    rest = re.sub(r"\bet\.?\s+al\.?", "et al.", rest)
    rest = re.sub(r"\s*[,;]?\s*$", "", rest).strip()
    staart = m.group("staart").strip()
    kern = m.group("naam") + (" " + rest if rest else "")
    uit = f"({kern}, {m.group('jaar')}"
    if staart:
        uit += (staart if staart.startswith((",", ";", ":")) else ", " + staart)
    return uit + ")"


def bereken(doc: dict, naar: str) -> dict:
    bronnen = lees_bronnen(doc)
    vervangingen, ongekoppeld, volgorde = [], [], []

    for b in doc["blokken"]:
        tekst = b.get("tekst", "")
        if not tekst or "(" not in tekst:
            continue
        for m in IN_TEKST.finditer(tekst):
            oud = m.group(0)
            naam = (m.group("naam") + m.group("rest")).strip()
            bron = None
            for sl in sleutels_van(naam, m.group("jaar")):
                if sl in bronnen:
                    bron = bronnen[sl]
                    break

            if naar == "uniform":
                nieuw = uniform(m)
                if nieuw != oud:
                    vervangingen.append({"id": b["id"], "van": oud, "naar": nieuw,
                                         "bron": bron["id"] if bron else None})
                continue

            if naar == "genummerd":
                if not bron:
                    ongekoppeld.append({"id": b["id"], "citaat": oud,
                                        "waarom": "geen bronregel met deze naam en dit jaar"})
                    continue
                if bron["id"] not in volgorde:
                    volgorde.append(bron["id"])
                nieuw = f"[{volgorde.index(bron['id']) + 1}]"
                vervangingen.append({"id": b["id"], "van": oud, "naar": nieuw,
                                     "bron": bron["id"]})

    uit = {"naar": naar, "vervangingen": vervangingen,
           "niet_gekoppeld": ongekoppeld,
           "bronnen_gevonden": len(bronnen)}
    if naar == "genummerd":
        # De bronnenlijst gaat op citatievolgorde en krijgt nummers. Wat
        # er niet geciteerd wordt, komt er achteraan in de volgorde
        # waarin het stond — weglaten zou tekst laten verdwijnen.
        # `bronnen` staat onder twee sleutels per regel — de volledige
        # naam en het eerste woord — dus `values()` levert dezelfde regel
        # twee keer. Zonder deze ontdubbeling komt hij twee keer in de
        # volgorde en dus twee keer in de gezette bronnenlijst.
        # Gemeten op de proef: twee van de zeven regels stonden dubbel.
        gezien = set(volgorde)
        rest = []
        for w in bronnen.values():
            if w["id"] not in gezien:
                gezien.add(w["id"])
                rest.append(w["id"])
        uit["bronvolgorde"] = volgorde + rest
    return uit


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("werkmap", type=Path)
    ap.add_argument("--naar", choices=DOELEN, required=True)
    a = ap.parse_args()

    docpad = a.werkmap / "document.json"
    if not docpad.exists():
        sys.exit(f"geen document.json in {a.werkmap}. Draai eerst lees_docx.py.")
    doc = json.loads(docpad.read_text(encoding="utf-8"))

    doel = a.werkmap / "citaten.json"
    if a.naar == "zoals-aangeleverd":
        if doel.exists():
            doel.unlink()
        print(json.dumps({"naar": "zoals-aangeleverd",
                          "wat": "er wordt niets omgezet"}, ensure_ascii=False, indent=2))
        return 0

    plan = bereken(doc, a.naar)
    doel.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")

    print(json.dumps({
        "naar": plan["naar"],
        "bronregels gekoppeld": plan["bronnen_gevonden"],
        "verwijzingen omgezet": len(plan["vervangingen"]),
        "niet gekoppeld": len(plan["niet_gekoppeld"]),
        "voorbeeld": plan["vervangingen"][:3],
        "blijft staan": plan["niet_gekoppeld"][:3],
        "plan": str(doel),
    }, ensure_ascii=False, indent=2))
    if not plan["vervangingen"] and a.naar != "zoals-aangeleverd":
        print("\nlet op: er is niets omgezet. Ofwel staan de verwijzingen al in de "
              "gevraagde vorm, ofwel citeert dit rapport niet op auteur-jaar — dat is "
              "het enige systeem dat dit script kan koppelen aan een bronnenlijst.",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
