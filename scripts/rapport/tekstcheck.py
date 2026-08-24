#!/usr/bin/env python3
"""De tekstintegriteitspoort: staat er nog precies wat er stond.

Dit script bestaat omdat de belofte van deze skill een harde is. Het
rapport is af, de tekst is van de opdrachtgever, en de opmaak mag er
niets aan veranderen. Een belofte die niet te controleren is, is een
voornemen; dit is de controle.

Hoe het werkt. `lees_docx.py` heeft de brontekst vastgelegd in
`bron-tekst.txt`, één genormaliseerde regel per blok met het blok-id
ervoor. `bouw.py` heeft elk element in het gezette rapport het `data-bron`
van zijn blok meegegeven. Dit script leest het gebouwde HTML-bestand,
plakt alle stukken met hetzelfde `data-bron` in documentvolgorde weer aan
elkaar, normaliseert, en vergelijkt regel voor regel.

Vijf uitkomsten, en de eerste vier blokkeren:

* **gewijzigd** — de tekst van een blok is anders dan in de bron. Dit is
  de ernstige: er staat iets anders in het rapport dan de
  opdrachtgever heeft geschreven.
* **verdwenen** — een blok uit de bron komt in het rapport niet voor.
  Meestal is dat een blok dat de zetmotor heeft laten vallen.
* **dubbel** — een blok komt twee keer voor zonder dat het een
  gesplitste alinea is. Dan leest iemand dezelfde alinea twee keer.
* **toegevoegd** — tekst in het rapport die geen `data-bron` heeft en ook
  geen `data-toevoeging`. Dit is per definitie tekst die niemand heeft
  goedgekeurd — een samenvatting die er niet stond, een bijschrift dat
  verzonnen is, een conclusie die de opmaak erbij heeft bedacht — en het
  is precies de fout waar deze skill om heen is gebouwd. Blokkeert.
  Op alle vier de modellen van het proefrapport is dit getal nul, dus
  het is een drempel die je alleen raakt als er echt iets bij is
  geschreven.
* **toevoeging** — de gemarkeerde toevoegingen: folio's, kopregels, de
  inhoudsopgave, hoofdstuknummers, figuurnummers, nootcijfers, de
  herhaalde tabelkop. Die horen erbij en ze worden geteld en genoemd,
  zodat niemand hoeft te raden wat de opmaak heeft toegevoegd.

Goedgekeurde wijzigingen uit `wijzigingen.json` zijn geen afwijking. Ze
worden apart genoemd, met wat er is veranderd en dat de gebruiker
akkoord heeft gegeven.

Geen browser nodig: dit is een tekstvergelijking en die hoort niet aan
een renderer te hangen. Ook zonder Chromium is de tekst dus geverifieerd.

Gebruik:

    python tekstcheck.py werkmap/rapport.html
    python tekstcheck.py werkmap/rapport.html --volledig
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
from lees_docx import normaliseer  # noqa: E402

#: Elementen zonder tekstinhoud die we niet als stapelniveau hoeven te
#: volgen. `br` en `img` sluiten in HTML niet, dus zonder deze lijst
#: raakt de stapel scheef.
LEEG = {"br", "img", "hr", "input", "meta", "link", "source", "col", "wbr"}

#: Tags waarvan de tekst nooit meetelt.
STIL = {"script", "style", "template", "svg", "title"}


class Oogst(HTMLParser):
    """Haalt per `data-bron` de tekst uit het gezette rapport.

    Twee dingen die dit anders doet dan een gewone tekstextractie:

    1. **Een `data-toevoeging` sluit zijn hele deelboom uit.** Het
       hoofdstuknummer, het figuurnummer, de inhoudsopgave en de
       herhaalde tabelkop zijn tekst die de opmaak erbij heeft gezet.
       Ze mogen niet meetellen als brontekst en ze mogen ook niet als
       ongemarkeerde toevoeging opduiken.

    2. **Een tabel wordt per cel geoogst.** Bij lopende tekst worden de
       stukken van een gesplitste alinea aan elkaar geplakt zonder iets
       ertussen; bij een tabel is de celgrens juist wél een grens, want
       anders lijkt "1.4" plus "gehaald" één woord.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stapel: list[dict] = []
        self.bron_stapel: list[str] = []
        self.negeer = 0
        self.stil = 0
        self.stukken: dict[str, list[str]] = {}
        self.soort: dict[str, str] = {}
        self.volgorde: list[str] = []
        self.aantal_elementen: dict[str, int] = {}
        self.toevoegingen: dict[str, list[str]] = {}
        self.toevoeging_nu: list[str] | None = None
        self.los: list[str] = []          # tekst zonder bron en zonder markering
        self.paginas = 0

    # -- de boom ------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in LEEG:
            if tag == "br" and self.bron_stapel and not self.negeer:
                self._voeg(" ")
            return
        niveau = {"tag": tag, "bron": None, "toevoeging": None, "stil": tag in STIL}
        if tag in STIL:
            self.stil += 1
        if "class" in a and "pagina" in (a.get("class") or "").split():
            self.paginas += 1
        toev = a.get("data-toevoeging")
        if toev is not None:
            niveau["toevoeging"] = toev
            self.negeer += 1
            if self.negeer == 1:
                self.toevoeging_nu = self.toevoegingen.setdefault(toev, [])
        bron = a.get("data-bron")
        if bron is not None and not self.negeer:
            niveau["bron"] = bron
            self.bron_stapel.append(bron)
            if bron not in self.stukken:
                self.stukken[bron] = []
                self.volgorde.append(bron)
                self.soort[bron] = "tabel" if tag == "table" else "tekst"
            self.aantal_elementen[bron] = self.aantal_elementen.get(bron, 0) + 1
        if tag in ("td", "th") and self.bron_stapel and not self.negeer:
            if self.soort.get(self.bron_stapel[-1]) == "tabel":
                self.stukken[self.bron_stapel[-1]].append("")
        self.stapel.append(niveau)

    def handle_endtag(self, tag):
        if tag in LEEG:
            return
        for i in range(len(self.stapel) - 1, -1, -1):
            if self.stapel[i]["tag"] == tag:
                for niveau in self.stapel[i:]:
                    if niveau["bron"] is not None and self.bron_stapel:
                        self.bron_stapel.pop()
                    if niveau["toevoeging"] is not None:
                        self.negeer = max(0, self.negeer - 1)
                        if self.negeer == 0:
                            self.toevoeging_nu = None
                    if niveau["stil"]:
                        self.stil = max(0, self.stil - 1)
                del self.stapel[i:]
                return

    def handle_data(self, data):
        if self.stil:
            return
        if self.negeer:
            if self.toevoeging_nu is not None and data.strip():
                self.toevoeging_nu.append(data.strip())
            return
        if not data.strip():
            if self.bron_stapel:
                self._voeg(" ")
            return
        if self.bron_stapel:
            self._voeg(data)
        else:
            self.los.append(data.strip())

    def _voeg(self, data: str) -> None:
        bron = self.bron_stapel[-1]
        lijst = self.stukken[bron]
        if self.soort[bron] == "tabel" and lijst:
            lijst[-1] += data
        else:
            lijst.append(data)


# =====================================================================

def lees_bron(pad: Path) -> tuple[dict, list]:
    """`bron-tekst.txt` -> id naar cellen, plus de volgorde."""
    uit: dict[str, list[str]] = {}
    volgorde: list[str] = []
    for regel in pad.read_text(encoding="utf-8").splitlines():
        if not regel.strip():
            continue
        delen = regel.split("\t")
        bid, cellen = delen[0], delen[1:]
        if bid not in uit:
            uit[bid] = []
            volgorde.append(bid)
        uit[bid].extend(cellen)
    return uit, volgorde


def verschil(a: str, b: str, marge: int = 46) -> str:
    """Het eerste stuk waar twee teksten uiteenlopen, met wat eromheen.

    Een diff van twee alinea's van 900 tekens is onleesbaar; wat je wilt
    weten is waar het misgaat en wat er staat in plaats van wat er
    stond.
    """
    matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        voor = a[max(0, i1 - marge):i1]
        return (f"…{voor}[bron: {a[i1:i2][:90]!r} → rapport: {b[j1:j2][:90]!r}]"
                f"{a[i2:i2 + marge]}…")
    return ""


def check(html_pad: Path, werkmap: Path, volledig: bool = False) -> dict:
    bron, bron_volgorde = lees_bron(werkmap / "bron-tekst.txt")
    oogst = Oogst()
    oogst.feed(html_pad.read_text(encoding="utf-8"))

    akkoord = {}
    wpad = werkmap / "wijzigingen.json"
    if wpad.exists():
        for w in json.loads(wpad.read_text(encoding="utf-8")):
            if w.get("akkoord"):
                for bid in ([w["id"]] if w.get("id") else []) + list(w.get("ids", [])):
                    akkoord[bid] = w

    gewijzigd, verdwenen, dubbel, goedgekeurd = [], [], [], []

    for bid in bron_volgorde:
        verwacht = bron[bid]
        if bid not in oogst.stukken:
            (goedgekeurd if bid in akkoord else verdwenen).append({
                "id": bid,
                "bron": " ".join(verwacht)[:120],
                "wat": "komt in het rapport niet voor",
                **({"besluit": akkoord[bid].get("soort")} if bid in akkoord else {}),
            })
            continue
        gevonden = oogst.stukken[bid]
        if oogst.soort[bid] == "tabel":
            a = [normaliseer(c) for c in verwacht]
            b = [normaliseer(c) for c in gevonden]
            gelijk = a == b
            bron_str, rapport_str = " | ".join(a), " | ".join(b)
        else:
            bron_str = normaliseer(" ".join(verwacht))
            rapport_str = normaliseer("".join(gevonden))
            gelijk = bron_str == rapport_str
        if gelijk:
            continue
        melding = {
            "id": bid,
            "tekens_bron": len(bron_str),
            "tekens_rapport": len(rapport_str),
            "waar": verschil(bron_str, rapport_str),
        }
        if volledig:
            melding["bron"] = bron_str
            melding["rapport"] = rapport_str
        if bid in akkoord:
            melding["besluit"] = akkoord[bid].get("soort")
            melding["reden"] = akkoord[bid].get("reden", "")
            goedgekeurd.append(melding)
        else:
            gewijzigd.append(melding)

    # Een blok dat uit meer elementen bestaat dan zijn splitsingen
    # rechtvaardigen, staat er twee keer. Een gesplitste alinea is één
    # blok in twee stukken en de tekst klopt dan nog; een gekopieerd
    # blok verdubbelt de tekst en dat is bij de vergelijking hierboven
    # al opgevallen. Dit vangt het geval waarin de bron zelf twee keer
    # identiek voorkomt.
    for bid, n in oogst.aantal_elementen.items():
        if n > 6:
            dubbel.append({"id": bid, "elementen": n,
                           "wat": "dit blok staat in meer dan zes stukken in het rapport"})

    onbekend = [t for t in oogst.los if len(t) > 2 and not _mag_los(t)]

    return {
        "bestand": str(html_pad),
        "paginas": oogst.paginas,
        "blokken_bron": len(bron_volgorde),
        "blokken_gevonden": len(oogst.stukken),
        "gewijzigd": gewijzigd,
        "verdwenen": verdwenen,
        "dubbel": dubbel,
        "goedgekeurd": goedgekeurd,
        "ongemarkeerd_toegevoegd": onbekend,
        "toevoegingen": {k: {"aantal": len(v), "voorbeeld": v[:4]}
                         for k, v in sorted(oogst.toevoegingen.items())},
    }


def _mag_los(t: str) -> bool:
    """Losse tekst die er zonder markering mag staan.

    Er is er precies één soort: de leestekens en scheidingstekens die de
    opmaak zelf tussen elementen zet. Alles wat op een woord lijkt, mag
    er niet los staan.
    """
    return bool(re.fullmatch(r"[\s|·—–\-•/,.:;()\[\]]+", t))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=Path)
    ap.add_argument("--werkmap", type=Path, default=None)
    ap.add_argument("--volledig", action="store_true",
                    help="de hele bron- en rapporttekst bij elke afwijking")
    a = ap.parse_args()

    if not a.html.exists():
        sys.exit(f"niet gevonden: {a.html}")
    werkmap = a.werkmap or a.html.parent
    if not (werkmap / "bron-tekst.txt").exists():
        sys.exit(f"geen bron-tekst.txt in {werkmap}. Draai eerst lees_docx.py.")

    res = check(a.html, werkmap, a.volledig)
    (werkmap / "tekstcheck.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    blokkeert = bool(res["gewijzigd"] or res["verdwenen"] or res["dubbel"]
                     or res["ongemarkeerd_toegevoegd"])
    if res["gewijzigd"] or res["verdwenen"] or res["dubbel"]:
        uitkomst = "TEKST GEWIJZIGD"
    elif res["ongemarkeerd_toegevoegd"]:
        uitkomst = "TEKST TOEGEVOEGD"
    else:
        uitkomst = "tekst ongewijzigd"
    samenvatting = {
        "uitkomst": uitkomst,
        "paginas": res["paginas"],
        "blokken": f"{res['blokken_gevonden']} van {res['blokken_bron']}",
        "gewijzigd": len(res["gewijzigd"]),
        "verdwenen": len(res["verdwenen"]),
        "dubbel": len(res["dubbel"]),
        "goedgekeurd": len(res["goedgekeurd"]),
        "ongemarkeerd_toegevoegd": len(res["ongemarkeerd_toegevoegd"]),
        "toevoegingen": {k: v["aantal"] for k, v in res["toevoegingen"].items()},
    }
    print(json.dumps(samenvatting, ensure_ascii=False, indent=2))
    for soort in ("gewijzigd", "verdwenen", "dubbel"):
        for m in res[soort][:8]:
            print(f"\n  {soort.upper()}  {m['id']}", file=sys.stderr)
            print(f"    {m.get('waar') or m.get('wat') or m.get('bron', '')}",
                  file=sys.stderr)
    if res["ongemarkeerd_toegevoegd"]:
        print("\n  ONGEMARKEERD TOEGEVOEGD:", file=sys.stderr)
        for t in res["ongemarkeerd_toegevoegd"][:8]:
            print(f"    {t[:100]!r}", file=sys.stderr)
    print(f"\nvolledig verslag: {werkmap / 'tekstcheck.json'}", file=sys.stderr)
    return 1 if blokkeert else 0


if __name__ == "__main__":
    raise SystemExit(main())
