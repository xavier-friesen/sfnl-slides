#!/usr/bin/env python3
"""Van `document.json` naar een gezet rapport, en de zetmotor aansturen.

Dit script doet vier dingen, in deze volgorde:

1. **De stroom schrijven.** Elk blok uit `document.json` wordt één
   element: een kop, een alinea, een lijst, een tabel, een figuur. De
   tekst gaat er letterlijk in — de runs bepalen alleen waar `<b>` en
   `<i>` staan. Elk element draagt `data-bron` met het blok-id, en dat
   is de draad waarmee `tekstcheck.py` straks terugrekent.

2. **De zetting.** De stroom gaat in een echte browser en
   `paginator.js` giet hem in de kaders van de ene pagina na de andere,
   met splitsing op regelgrens. Dat is de enige manier om te weten waar
   een alinea afbreekt: alleen de browser weet hoe breed een woord is.

3. **De inhoudsopgave, in meer dan één ronde.** De folio's kloppen pas
   als de inhoudsopgave er al in staat, en de inhoudsopgave kan pas
   gevuld worden als de folio's er zijn. Dus: zetten, folio's aflezen,
   inhoudsopgave bouwen, opnieuw zetten, en dat tot de kaart twee
   rondes achter elkaar hetzelfde is. Het loopt in de praktijk in drie.

4. **Het losse bestand schrijven.** Alle pagina's in één HTML, met de
   letters ingesloten, de stijl erin en het beeld als data-URI. Dat is
   wat de gebruiker overhoudt en het werkt zonder internet.

Wat dit script niet doet is de tekst aanraken. Wijzigingen in de inhoud
staan in `wijzigingen.json` en komen daar alleen in nadat de gebruiker
ze stuk voor stuk heeft goedgekeurd; dit script past ze toe en noteert
per stuk dat het is gebeurd.

Gebruik:

    python bouw.py werkmap/
    python bouw.py werkmap/ --uit rapport.html
    python bouw.py werkmap/ --nieuw-ontwerp --model dubbel --register zacht
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
WORTEL = HIER.parent.parent
STIJL = WORTEL / "assets" / "documenten" / "stijl.css"
FONTS = WORTEL / "assets" / "documenten" / "fonts" / "fonts.css"
RAPPORTCSS = WORTEL / "assets" / "rapport" / "rapport.css"
PAGINATOR = HIER / "paginator.js"

sys.path.insert(0, str(HIER))
sys.path.insert(0, str(WORTEL / "scripts" / "documenten"))

#: De bladmaten in px bij 96 dpi. Dezelfde tabel als in `stijl.css` en in
#: `scripts/documenten/bouw.py`; een zevende formaat bestaat niet.
FORMATEN = {
    "sfnl": (794, 1039),
    "a4": (794, 1123),
    "a4-liggend": (1123, 794),
}

MODELLEN = ("breed", "kantlijn", "dubbel", "flexibel")
REGISTERS = ("helder", "diep", "zacht", "contrast")
OPENERS = ("nummer", "band", "blad")
DICHTHEDEN = ("ruim", "gemiddeld", "dicht")

#: Waar de noten komen te staan. Dit is een plaatsingsbesluit en geen
#: inhoudelijk besluit: dezelfde tekst, ergens anders op het blad.
NOTEN = ("geen", "voetnoot", "eindnoot-hoofdstuk", "eindnoot-rapport")

#: Of er een bronnenlijst wordt gezet, en hoe. Los van de noten, want
#: voetnoten mét een volledige bronnenlijst achterin is het gewone geval
#: en niet de uitzondering.
BRONNENLIJSTEN = ("geen", "apa", "genummerd")

#: Wat er aan beeld in het rapport komt. De skill vraagt dit expliciet,
#: want stilzwijgend aannemen dat er geen beeld is, is de reden dat een
#: rapport er kaal uitkomt terwijl de figuren in een aparte map stonden.
BEELDBRONNEN = ("geen", "uit-bron", "aangeleverd")

#: Wat er met de verwijzingen in de lopende tekst gebeurt. Anders dan de
#: rest van deze lijsten raakt dit besluit de tekst zelf, en dat is een
#: vaststelling van de opdrachtgever: een verwijzing gelijktrekken of
#: hernummeren is opmaak. `citaten.py` rekent de omzetting uit en legt
#: elke vervanging vast; `tekstcheck.py` controleert dat er precies dát
#: is veranderd en niets meer.
CITAATSTIJLEN = ("zoals-aangeleverd", "uniform", "genummerd")

STANDAARD_ONTWERP = {
    "model": "breed",
    "register": "helder",
    "formaat": "sfnl",
    "opener": "nummer",
    "dichtheid": "gemiddeld",
    "bandhoogte": 232,
    "dubbelzijdig": True,
    "omslag": True,
    "inhoudsopgave": True,
    "inhoudDiepte": 2,
    "hoofdstuknummers": True,
    "exhibitnummers": True,
    "noten": "voetnoot",
    "bronnenlijst": "geen",
    "citaatstijl": "zoals-aangeleverd",
    "beeld": "uit-bron",
    "beeldmap": None,
    "bijlagen": None,
    "eersteFolio": 1,
    "folioVanaf": 2,
    "rapporttitel": None,
    "ondertitel": None,
    "opdrachtgever": None,
    "datum": None,
    "colofon": None,
}

#: De letters voor de bijlagen. Voorbij Z houdt het op, en een rapport
#: met zesentwintig bijlagen heeft een ander probleem dan opmaak.
BIJLAGELETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


# =====================================================================
#  De stroom
# =====================================================================

def _esc(t: str) -> str:
    return html.escape(t, quote=False)


def runs_naar_html(runs: list, noten_gezien: set, toon_noten: bool = True) -> str:
    """De inline opmaak, en niets erbij.

    Een run wordt `<b>`, `<i>`, `<sup>` of niets. Een voetnootverwijzing
    wordt een `<sup data-noot>` zónder tekst erin — het nummer zet de
    zetmotor erbij, want dat is toegevoegde tekst en die hoort als
    zodanig herkenbaar te zijn.

    Bij `noten: geen` verdwijnt ook het verwijzingscijfer. Een noot die
    er niet is met een bovengezet cijfer ervoor is erger dan geen noot:
    de lezer zoekt naar iets wat nergens staat.
    """
    uit = []
    for run in runs:
        if "voetnoot" in run:
            if not toon_noten:
                continue
            nid = run["voetnoot"]
            noten_gezien.add(nid)
            uit.append(f'<sup data-noot="{_esc(nid)}" data-toevoeging="nootnummer"></sup>')
            continue
        t = _esc(run.get("t", ""))
        if not t:
            continue
        t = t.replace("\n", "<br>").replace("\t", "&#9;")
        if run.get("sup"):
            t = f"<sup>{t}</sup>"
        if run.get("sub"):
            t = f"<sub>{t}</sub>"
        if run.get("cursief"):
            t = f"<i>{t}</i>"
        if run.get("vet"):
            t = f"<b>{t}</b>"
        uit.append(t)
    return "".join(uit)


def _attr(**kw) -> str:
    delen = []
    for k, v in kw.items():
        if v is None or v is False:
            continue
        naam = k.replace("_", "-")
        if v is True:
            delen.append(f' {naam}="ja"')
        else:
            delen.append(f' {naam}="{html.escape(str(v), quote=True)}"')
    return "".join(delen)


class Stroom:
    """Zet `document.json` om in een reeks blokken voor de zetmotor."""

    def __init__(self, doc: dict, ontwerp: dict, werkmap: Path):
        self.doc = doc
        self.o = ontwerp
        self.werkmap = werkmap
        self.noten_gezien: set = set()
        self.hoofdstuk = 0
        self.bijlage = 0
        self.exhibit = 0
        self.titel_op_omslag: str | None = None
        self.in_bijlagen = False
        #: De noten die al in een notenblok zijn uitgeschreven. Wat er
        #: openstaat is het verschil met `noten_gezien`, en dat is
        #: robuuster dan een tweede lijst bijhouden: een noot die twee
        #: keer voorkomt wordt zo één keer gezet.
        self.noten_geplaatst: set = set()
        #: De blokken die in een bronnenlijst vallen, en de blokken die
        #: door een `hoort_bij` of een uitgeschreven notenblok al elders
        #: terechtkomen.
        self.bronregels: set = set()
        self.extra_beeld: dict = {}
        self.beeld_zonder_plek: list = []
        self.toon_noten: bool = ontwerp.get("noten") != "geen"
        self.regels: list[str] = []

    # -- de omslag ----------------------------------------------------
    def omslag(self) -> str:
        """De omslag, en de titel erop komt uit de bron of hij is nieuw.

        Staat de dektitel als titelblok in het brondocument, dan draagt
        hij dat blok-id en is hij dus brontekst die één keer in het
        rapport voorkomt. Heeft de gebruiker in `ontwerp.json` een
        andere titel opgegeven, dan is dat toegevoegde tekst en zegt de
        markup dat — want dan hoort `tekstcheck.py` het titelblok
        érgens anders in het rapport terug te vinden.
        """
        o = self.o
        titelblok = next((b for b in self.doc["blokken"]
                          if b["soort"] == "titel"), None)
        titel = o.get("rapporttitel") or self.doc.get("titel") or ""
        from lees_docx import normaliseer
        if titelblok is not None and normaliseer(titelblok["tekst"]) == normaliseer(titel):
            titelattr = _attr(data_bron=titelblok["id"])
            self.titel_op_omslag = titelblok["id"]
        else:
            titelattr = ' data-toevoeging="omslag"'
            self.titel_op_omslag = None
        boven, onder = [], []
        if o.get("opdrachtgever"):
            boven.append(f'<p class="omslag__regel" data-toevoeging="omslag">'
                         f'{_esc(o["opdrachtgever"])}</p>')
        # De titel uit zijn runs wanneer hij uit de bron komt, en als
        # platte tekst wanneer de gebruiker hem zelf heeft opgegeven.
        titel_html = (self._runs(titelblok["runs"])
                      if self.titel_op_omslag else _esc(titel))
        stuk = [f'<h1 class="omslag__titel"{titelattr}>{titel_html}</h1>']
        if o.get("ondertitel"):
            stuk.append(f'<p class="omslag__onderschrift" data-toevoeging="omslag">'
                        f'{_esc(o["ondertitel"])}</p>')
        if o.get("datum"):
            onder.append(f'<p class="omslag__regel" data-toevoeging="omslag">'
                         f'{_esc(o["datum"])}</p>')
        onder.append(LOGO)
        # De attributen staan op `.omslag` zelf en niet op een omhulsel
        # eromheen. Met een omhulsel is `.omslag` geen flexkind van de
        # zetspiegel meer, groeit hij niet mee, en zakt de hele omslag
        # naar de onderrand — dat was op de eerste gebouwde omslag te
        # zien als een titel die tegen het logo aan stond.
        return (
            '<div class="omslag" data-plek="omslag" data-nieuwe-pagina="ja" '
            'data-opener="blad" data-sjabloon="omslag" data-folio="nee" '
            'data-heel="ja">'
            f'<div class="omslag__boven">{"".join(boven)}</div>'
            f'<div class="omslag__midden">{"".join(stuk)}</div>'
            f'<div class="omslag__onder">{"".join(onder)}</div>'
            '</div>')

    def _runs(self, runs: list) -> str:
        """De inline opmaak van één blok, met de notenstand van dit rapport."""
        return runs_naar_html(runs, self.noten_gezien, self.toon_noten)

    # -- voorbereiding ------------------------------------------------
    def bereid_voor(self, werkmap: Path) -> None:
        """Wat er vóór de blokkenlus vastgesteld moet zijn.

        Drie dingen, en ze hangen alle drie aan besluiten uit
        `ontwerp.json`: welke blokken in de bronnenlijst vallen, waar de
        bijlagen beginnen, en welk aangeleverd beeld waar tussen moet.
        """
        ap = self.doc.get("apparaat", {})

        if self.o.get("bronnenlijst") in ("apa", "genummerd"):
            lijst = ap.get("bronnenlijst")
            if lijst:
                ids = [b["id"] for b in self.doc["blokken"]]
                try:
                    a, z = ids.index(lijst["vanaf"]), ids.index(lijst["tot"])
                    self.bronregels = set(ids[a:z + 1])
                except ValueError:
                    pass

        if self.o.get("beeld") == "aangeleverd":
            pad = werkmap / "beeld.json"
            if pad.exists():
                # `beeldmap` is waar de bestanden staan; in `beeld.json`
                # staan alleen de namen. Een naam die naast de werkmap
                # ligt of absoluut is, wordt met rust gelaten — anders
                # gaat hij door de beeldmap heen. De insluiter verderop
                # rekent alles alsnog af tegen de werkmap, dus wat hier
                # uitkomt hoeft alleen te kloppen, niet mooi te zijn.
                map_ = self.o.get("beeldmap")
                for item in json.loads(pad.read_text(encoding="utf-8")):
                    if not item.get("na"):
                        # Zonder blok-id weet niemand waar dit heen moet, en
                        # ergens neerzetten is raden. Het gaat er niet in en
                        # het wordt gemeld — dat is de eerlijke faalwijze.
                        self.beeld_zonder_plek.append(item.get("bestand", "?"))
                        continue
                    naam = item.get("bestand", "")
                    if map_ and naam and not Path(naam).is_absolute() \
                            and not (werkmap / naam).exists():
                        item = {**item, "bestand": str(Path(map_) / naam)}
                    self.extra_beeld.setdefault(item["na"], []).append(item)

    # -- de blokken ---------------------------------------------------
    def bouw(self) -> str:
        blokken = self.doc["blokken"]
        bijlage_vanaf = (self.o.get("bijlagen") or {}).get("vanaf")
        i = 0
        while i < len(blokken):
            b = blokken[i]
            soort = b["soort"]

            # De overgang naar de bijlagen. Het scheidingsblad komt
            # ervoor; vanaf hier telt de nummering in letters.
            if bijlage_vanaf and b["id"] == bijlage_vanaf and not self.in_bijlagen:
                self.regels.append(self._scheidingsblad(b))
                self.in_bijlagen = True
                if self._is_scheidingskop(b):
                    i += 1          # die kop staat nu op het blad zelf
                    continue
            if soort == "titel":
                # Op de omslag, tenzij die niet bestaat of een andere
                # titel draagt. Dan hoort hij gewoon in de stroom, want
                # anders valt de titel uit het rapport weg.
                if self.titel_op_omslag != b["id"]:
                    self.regels.append(
                        f'<h1 class="hoofdstuktitel"'
                        f'{_attr(data_bron=b["id"], data_kop=1, data_kop_tekst=b["tekst"])}>'
                        f'{self._runs(b["runs"])}</h1>')
                i += 1
                continue
            if b.get("hoort_bij"):
                i += 1
                continue                      # bijschrift zit al bij zijn beeld
            # Een kop van niveau 1 sluit het vorige hoofdstuk af, en in
            # eindnootmodus per hoofdstuk gaan de openstaande noten daar
            # naartoe — vóór de opener, want anders staan ze achter de
            # titel van het volgende hoofdstuk.
            if (soort == "kop" and b.get("niveau") == 1
                    and self.o.get("noten") == "eindnoot-hoofdstuk"):
                self.regels.append(self._notenblok("Noten bij dit hoofdstuk"))

            if b["id"] in self.bronregels:
                i = self._bronnenlijst(blokken, i)
                continue
            if soort == "lijst":
                i = self._lijst(blokken, i)
                continue
            self.regels.append(self._blok(b))
            for extra in self.extra_beeld.get(b["id"], []):
                self.regels.append(self._aangeleverd_beeld(extra))
            i += 1

        # Wat er aan het eind nog open staat.
        if self.o.get("noten") in ("eindnoot-hoofdstuk", "eindnoot-rapport"):
            kop = ("Noten bij dit hoofdstuk"
                   if self.o["noten"] == "eindnoot-hoofdstuk" else "Noten")
            self.regels.append(self._notenblok(kop))
        return "\n".join(r for r in self.regels if r)

    # -- bijlagen -----------------------------------------------------
    @staticmethod
    def _is_scheidingskop(b: dict) -> bool:
        """Is dit een kop die alleen het woord 'Bijlagen' draagt.

        Dan is die kop zelf het scheidingsblad en is er geen toegevoegde
        tekst nodig. Staat er meer — "Bijlage A: methodeverantwoording" —
        dan is dat de eerste bijlage en krijgt het scheidingsblad een
        eigen woord, dat als toevoeging gemarkeerd wordt.
        """
        return (b.get("soort") == "kop"
                and re.fullmatch(r"bijlage[nx]?|appendi(x|ces)|annexe?s?",
                                 b.get("tekst", "").strip(), re.I) is not None)

    def _scheidingsblad(self, b: dict) -> str:
        eigen = self._is_scheidingskop(b)
        woord = (self.o.get("bijlagen") or {}).get("titel") or "Bijlagen"
        if eigen:
            titel = (f'<h1 class="opener__titel"'
                     f'{_attr(data_bron=b["id"], data_kop=1, data_kop_tekst=b["tekst"].strip())}>'
                     f'{self._runs(b["runs"])}</h1>')
        else:
            titel = (f'<h1 class="opener__titel" data-toevoeging="scheiding">'
                     f'{_esc(woord)}</h1>')
        veld = {"diep": "navy", "contrast": "violet",
                "zacht": "mint"}.get(self.o.get("register"), "")
        return (
            f'<div class="opener"'
            f'{_attr(data_nieuwe_pagina=True, data_opener="blad", data_scheiding="bijlagen", data_veld=veld or None, data_heel=True, data_hoofdstuk=woord)}>'
            f'<span class="scheiding__streep" aria-hidden="true"></span>'
            f'{titel}</div>')

    # -- het apparaat -------------------------------------------------
    def _notenblok(self, kop: str) -> str:
        """De openstaande noten als blok in de stroom.

        Levert een lege string wanneer er niets open staat, zodat een
        hoofdstuk zonder noten geen leeg notenblok krijgt.
        """
        openstaand = sorted(self.noten_gezien - self.noten_geplaatst,
                            key=_nootsleutel)
        if not openstaand:
            return ""
        regels = []
        for nid in openstaand:
            noot = self.doc["voetnoten"].get(nid)
            if not noot:
                continue
            regels.append(
                f'<p class="voetnoot" data-bron="noot{_esc(nid)}">'
                f'<span class="nr" data-toevoeging="nootnummer">{_nootlabel(nid)}</span>'
                f'{_esc(noot["tekst"])}</p>')
        self.noten_geplaatst |= set(openstaand)
        if not regels:
            return ""
        return (f'<div class="eindnoten" data-heel="ja">'
                f'<p class="eindnoten__kop" data-toevoeging="notenkop">{_esc(kop)}</p>'
                f'{"".join(regels)}</div>')

    def _bronnenlijst(self, blokken: list, i: int) -> int:
        """De aaneengesloten regels van de bronnenlijst als één blok.

        Bij een genummerde omzetting gaat de lijst op citatievolgorde en
        krijgt elke regel zijn nummer. Wat niet geciteerd wordt, gaat er
        achteraan: weglaten zou tekst laten verdwijnen, en dat mag niet,
        ook niet in een bronnenlijst.
        """
        stijl = self.o.get("bronnenlijst", "apa")
        eigen, j = [], i
        while j < len(blokken) and blokken[j]["id"] in self.bronregels:
            eigen.append(blokken[j])
            j += 1

        plan = self.doc.get("_citaatplan") or {}
        volgorde = plan.get("bronvolgorde") if stijl == "genummerd" else None
        if volgorde:
            # Ontdubbelen bij het herschikken, en niet alleen vertrouwen
            # dat het plan klopt. Een bronregel die twee keer in de
            # volgorde staat, zou anders twee keer gezet worden, en dat
            # is precies het soort fout dat je op een bronnenlijst van
            # zeventig regels niet meer terugvindt.
            op_id = {b["id"]: b for b in eigen}
            gedaan: set = set()
            gesorteerd = []
            for k in volgorde:
                if k in op_id and k not in gedaan:
                    gedaan.add(k)
                    gesorteerd.append(op_id[k])
            gesorteerd += [b for b in eigen if b["id"] not in gedaan]
            eigen = gesorteerd

        regels = []
        for nr, b in enumerate(eigen, start=1):
            nummer = ""
            if volgorde:
                nummer = (f'<span class="bron__nr" data-toevoeging="bronnummer">'
                          f'[{nr}]</span> ')
            regels.append(f'<p{_attr(data_bron=b["id"])}>{nummer}'
                          f'{self._runs(b["runs"])}</p>')
        self.regels.append(
            f'<div class="bronnenlijst" data-stijl="{stijl}">{"".join(regels)}</div>')
        return j

    def _aangeleverd_beeld(self, item: dict) -> str:
        """Een beeld dat de gebruiker apart heeft aangeleverd.

        Het bijschrift komt van de gebruiker en niet uit het rapport, dus
        het draagt `data-toevoeging` — net als de regels op de omslag.
        Zonder bijschrift staat het beeld er zonder, en dat is beter dan
        er een verzinnen.
        """
        bron = _esc(item["bestand"])
        onder = ""
        if item.get("bijschrift"):
            onder = (f'<figcaption data-toevoeging="beeldbijschrift">'
                     f'{_esc(item["bijschrift"])}</figcaption>')
        return (f'<figure class="beeldblok" data-heel="ja">'
                f'<img src="{bron}" alt="">{onder}</figure>')

    def _blok(self, b: dict) -> str:
        soort = b["soort"]
        if soort == "kop":
            return self._kop(b)
        if soort == "alinea":
            return self._alinea(b)
        if soort == "citaat":
            return (f'<blockquote class="citaatblok"{_attr(data_bron=b["id"])}>'
                    f'<p>{self._runs(b["runs"])}</p></blockquote>')
        if soort == "tabel":
            return self._tabel(b)
        if soort == "beeld":
            return self._beeld(b)
        if soort == "bijschrift":
            return (f'<p class="exhibit__bron"{_attr(data_bron=b["id"])}>'
                    f'{self._runs(b["runs"])}</p>')
        return self._alinea(b)

    def _alinea(self, b: dict) -> str:
        inhoud = self._runs(b["runs"])
        klasse = "chapeau--rapport" if b.get("chapeau") else ""
        return (f'<p{" class=" + chr(34) + klasse + chr(34) if klasse else ""}'
                f'{_attr(data_bron=b["id"], data_deel=b.get("deel"))}>{inhoud}</p>')

    def _kop(self, b: dict) -> str:
        niveau = b.get("niveau", 2)
        tekst = self._runs(b["runs"])
        kaal = b.get("tekst", "").strip()
        if niveau == 1:
            if self.in_bijlagen:
                self.bijlage += 1
            else:
                self.hoofdstuk += 1
            return self._opener(b, tekst, kaal)
        if niveau == 2:
            tag, klasse = "h2", "sectiekop"
        elif niveau == 3:
            tag, klasse = "h3", "subkop"
        else:
            tag, klasse = "p", "runinkop"
        return (f'<{tag} class="{klasse}"'
                f'{_attr(data_bron=b["id"], data_kop=niveau, data_kop_tekst=kaal)}>'
                f'{tekst}</{tag}>')

    def _opener(self, b: dict, tekst: str, kaal: str) -> str:
        o = self.o
        if self.in_bijlagen:
            nr = BIJLAGELETTERS[(self.bijlage - 1) % len(BIJLAGELETTERS)]
            woord = "Bijlage"
        else:
            nr = str(self.hoofdstuk)
            woord = "Hoofdstuk"
        kicker = ""
        if o.get("hoofdstuknummers"):
            kicker = (f'<p class="opener__kicker" data-toevoeging="nummer">'
                      f'{woord} {nr}</p>')
        # Het cijfer gaat mee bij alle drie de openers. Waar het komt te
        # staan verschilt per opener en dat regelt de CSS: half achter de
        # titel bij `nummer`, groot onderin bij `blad`, aan de
        # buitenrand van de band bij `band`.
        watermerk = ""
        if o.get("hoofdstuknummers"):
            watermerk = (f'<span class="opener__watermerk" aria-hidden="true" '
                         f'data-toevoeging="nummer">{nr}</span>')
        veld = {"diep": "navy", "contrast": "violet",
                "zacht": "mint"}.get(o.get("register"), "")
        return (
            f'<div class="opener"'
            f'{_attr(data_bron=b["id"], data_kop=1, data_kop_tekst=kaal, data_nummer=nr, data_hoofdstuk=kaal, data_groep="bijlagen" if self.in_bijlagen else None, data_nieuwe_pagina=True, data_opener=o.get("opener", "nummer"), data_veld=veld or None, data_balk=o.get("bandhoogte") if o.get("opener") == "band" else None, data_heel=True)}>'
            f'{watermerk}{kicker}'
            f'<h1 class="opener__titel">{tekst}</h1>'
            f'</div>')

    def _lijst(self, blokken: list, i: int) -> int:
        """Opeenvolgende lijstregels worden één lijst.

        In `document.json` is elke regel een eigen blok, want zo staat
        het in de bron. In de zetting hoort er één `<ul>` of `<ol>`
        omheen, anders springt elke regel apart in en telt een
        genummerde lijst per regel opnieuw vanaf één.
        """
        eerste = blokken[i]
        geordend = eerste.get("geordend", False)
        niveau = eerste.get("niveau", 0)
        tag = "ol" if geordend else "ul"
        items, j = [], i
        while j < len(blokken):
            b = blokken[j]
            if b["soort"] != "lijst" or b.get("geordend", False) != geordend:
                break
            if b.get("niveau", 0) < niveau:
                break
            if b.get("niveau", 0) > niveau:
                # Een dieper niveau hoort in de vorige regel te hangen.
                sub_einde = j
                while (sub_einde < len(blokken)
                       and blokken[sub_einde]["soort"] == "lijst"
                       and blokken[sub_einde].get("niveau", 0) > niveau):
                    sub_einde += 1
                sub = self._lijst_html(blokken[j:sub_einde])
                if items:
                    items[-1] = items[-1][:-len("</li>")] + sub + "</li>"
                j = sub_einde
                continue
            items.append(f'<li{_attr(data_bron=b["id"])}>'
                         f'{self._runs(b["runs"])}</li>')
            j += 1
        self.regels.append(f'<{tag}>{"".join(items)}</{tag}>')
        return j

    def _lijst_html(self, blokken: list) -> str:
        geordend = blokken[0].get("geordend", False)
        tag = "ol" if geordend else "ul"
        items = [f'<li{_attr(data_bron=b["id"])}>'
                 f'{self._runs(b["runs"])}</li>' for b in blokken]
        return f'<{tag}>{"".join(items)}</{tag}>'

    def _tabel(self, b: dict) -> str:
        rijen = b["rijen"]
        kop_rijen = [r for r in rijen if r["kop"]]
        lijf = [r for r in rijen if not r["kop"]]
        if not kop_rijen and b.get("kop_van_eerste_rij") and rijen:
            kop_rijen, lijf = rijen[:1], rijen[1:]
        getalkolom = _getalkolommen(lijf)

        def cel(c, i, th=False):
            tag = "th" if th else "td"
            klasse = ' class="getal"' if getalkolom.get(i) else ""
            span = f' colspan="{c["span"]}"' if c.get("span", 1) > 1 else ""
            inhoud = "<br>".join(self._runs(d["runs"])
                                 for d in c["delen"]) or ""
            return f'<{tag}{klasse}{span}>{inhoud}</{tag}>'

        delen = [f'<table class="tabel--rapport"{_attr(data_bron=b["id"])}>']
        if kop_rijen:
            delen.append("<thead>")
            for r in kop_rijen:
                delen.append("<tr>" + "".join(cel(c, i, True)
                                              for i, c in enumerate(r["cellen"])) + "</tr>")
            delen.append("</thead>")
        delen.append("<tbody>")
        for r in lijf:
            delen.append("<tr>" + "".join(cel(c, i)
                                          for i, c in enumerate(r["cellen"])) + "</tr>")
        delen.append("</tbody></table>")
        return "".join(delen)

    def _beeld(self, b: dict) -> str:
        bestanden = b.get("beeldbestanden") or []
        bijschrift = b.get("bijschrift")
        # Uit de runs en niet uit de platte tekst, anders vallen de
        # cursief gezette woorden en de voetnootverwijzingen eruit.
        bijschrift_html = (self._runs(b["bijschrift_runs"])
                           if b.get("bijschrift_runs") else _esc(bijschrift or ""))
        if self.o.get("beeld") == "geen":
            # Het beeld gaat eruit, het bijschrift niet: dat is tekst van
            # de auteur en die verdwijnt nergens door een vormkeuze. Wat
            # overblijft is een gewone alinea met dezelfde `data-bron`,
            # zodat `tekstcheck.py` hem gewoon terugvindt.
            if not bijschrift:
                return ""
            bron_id = b.get("bijschrift_id", b["id"])
            return f'<p class="bijschrift-los" data-bron="{bron_id}">{bijschrift_html}</p>'
        if not bestanden:
            return (f'<figure class="beeldblok beeldblok--leeg"{_attr(data_bron=b["id"])}>'
                    f'<div>beeld ontbreekt</div></figure>')
        beeld = "".join(f'<img src="{_esc(p)}" alt="">' for p in bestanden)
        if bijschrift and self.o.get("exhibitnummers"):
            self.exhibit += 1
            nr = (f'<p class="exhibit__nr" data-toevoeging="nummer">'
                  f'Figuur {self.exhibit}</p>')
            bron_id = b.get("bijschrift_id", b["id"])
            return (
                f'<figure class="exhibit"{_attr(data_bron=b["id"], data_heel=True)}>'
                f'{nr}'
                f'<p class="exhibit__titel" data-bron="{bron_id}">{bijschrift_html}</p>'
                f'<div class="exhibit__beeld">{beeld}</div>'
                f'</figure>')
        onder = ""
        if bijschrift:
            bron_id = b.get("bijschrift_id", b["id"])
            onder = f'<figcaption data-bron="{bron_id}">{bijschrift_html}</figcaption>'
        return (f'<figure class="beeldblok"{_attr(data_bron=b["id"], data_heel=True)}>'
                f'{beeld}{onder}</figure>')

    # -- de voetnoten -------------------------------------------------
    def voetnoten(self) -> str:
        """De notenbak waar `paginator.js` uit put.

        Leeg in eindnootmodus: dan staan de noten al als blok in de
        stroom, en zou de zetmotor ze een tweede keer op de pagina
        zetten. Dat zou `tekstcheck.py` als dubbele tekst melden, en
        terecht.
        """
        if self.o.get("noten") in ("geen", "eindnoot-hoofdstuk", "eindnoot-rapport"):
            return ""
        uit = []
        for nid in sorted(self.noten_gezien, key=_nootsleutel):
            noot = self.doc["voetnoten"].get(nid)
            if not noot:
                continue
            uit.append(
                f'<p class="voetnoot" id="noot-{_esc(nid)}" data-bron="noot{_esc(nid)}">'
                f'<span class="nr" data-toevoeging="nootnummer">{_nootlabel(nid)}</span>'
                f'{_esc(noot["tekst"])}</p>')
        return "\n".join(uit)


def _nootsleutel(nid: str):
    return (1, int(nid[1:])) if nid.startswith("e") else (0, int(nid))


def _nootlabel(nid: str) -> str:
    return nid[1:] if nid.startswith("e") else nid


def _getalkolommen(rijen: list) -> dict:
    """Welke kolommen zijn getalkolommen, gemeten over de hele tabel.

    Per cel kijken werkt niet: dan lijnt "1.4" rechts uit en "n.v.t." in
    dezelfde kolom links, en dan staat de kolom scheef. En de kopcel is
    nooit een getal, terwijl hij wel boven de cijfers hoort te staan.
    Dus: een kolom is een getalkolom als minstens twee derde van zijn
    gevulde cellen een getal is, en dan lijnt de kop mee.
    """
    tellen: dict = {}
    for rij in rijen:
        for i, c in enumerate(rij["cellen"]):
            if not c["tekst"].strip():
                continue
            heel, getal = tellen.get(i, (0, 0))
            tellen[i] = (heel + 1, getal + (1 if _is_getal(c["tekst"]) else 0))
    return {i: (g >= 2 and g / h >= 2 / 3) for i, (h, g) in tellen.items()}


def _is_getal(t: str) -> bool:
    return bool(re.fullmatch(r"[\s€$%+\-–]*[\d][\d.,\s%]*[\s€$%]*", t.strip())) if t.strip() else False


LOGO = (
    '<svg class="logo" viewBox="0 0 412 104" aria-label="Social Finance NL">'
    '<circle cx="52" cy="52" r="52" fill="currentColor"/>'
    '<rect x="118" y="0" width="104" height="104" fill="currentColor"/>'
    '<text x="248" y="31" font-family="Montserrat, sans-serif" font-weight="700" '
    'font-size="30" letter-spacing="0.4" fill="currentColor">SOCIAL</text>'
    '<text x="248" y="67" font-family="Montserrat, sans-serif" font-weight="700" '
    'font-size="30" letter-spacing="0.4" fill="currentColor">FINANCE</text>'
    '<text x="248" y="103" font-family="Montserrat, sans-serif" font-weight="700" '
    'font-size="30" letter-spacing="0.4" fill="currentColor">NL</text></svg>')


# =====================================================================
#  De paginasjablonen
# =====================================================================

def sjablonen(ontwerp: dict) -> str:
    """De skeletten waar `paginator.js` pagina's uit kloont.

    Ze staan in de HTML en niet in het script, zodat een mens ze kan
    lezen en aanpassen zonder de zetmotor te openen. Het aantal `.kader`
    per sjabloon is wat het model bepaalt: één in breed en kantlijn,
    twee in dubbel.
    """
    model = ontwerp["model"]
    basis = model if model != "flexibel" else "kantlijn"

    def kaders(m: str) -> str:
        if m == "dubbel":
            return ('<div class="kader lopend" data-kader="1"></div>'
                    '<div class="kader lopend" data-kader="2"></div>')
        if m == "kantlijn":
            return ('<div class="kader lopend" data-kader="1"></div>'
                    '<div class="kantlijn"></div>')
        return '<div class="kader lopend" data-kader="1"></div>'

    def pagina(naam: str, m: str, inhoud: str) -> str:
        return f"""<template id="sjabloon-{naam}"><div class="pagina" data-soort="rapport" data-model="{m}">
  <div data-plek="band"></div>
  <p class="rapport-kopregel" data-toevoeging="kopregel"><span data-plek="links"></span><span class="streepje"></span><span data-plek="rechts"></span></p>
  <div class="zetspiegel zetspiegel--rapport">
    <div class="paginakop" data-plek="kop"></div>
    <div class="raster">{inhoud}</div>
    <div class="voetnoten"></div>
  </div>
  <span class="rapport-folio" data-toevoeging="folio"></span>
</div></template>"""

    delen = [pagina("tekst", basis, kaders(basis))]
    if model == "flexibel":
        for m in ("breed", "dubbel"):
            delen.append(pagina(m, m, kaders(m)))
    delen.append(f"""<template id="sjabloon-opener"><div class="pagina" data-soort="rapport" data-model="{basis}">
  <div class="zetspiegel zetspiegel--rapport" data-plek="opener"></div>
  <span class="rapport-folio" data-toevoeging="folio"></span>
</div></template>""")
    delen.append(f"""<template id="sjabloon-omslag"><div class="pagina" data-soort="rapport" data-model="{basis}">
  <div class="zetspiegel zetspiegel--rapport" data-plek="opener"></div>
</div></template>""")
    delen.append(f"""<template id="sjabloon-leeg"><div class="pagina" data-soort="rapport" data-model="{basis}">
  <div class="zetspiegel zetspiegel--rapport"></div>
</div></template>""")
    return "\n".join(delen)


# =====================================================================
#  De werkpagina en de eindpagina
# =====================================================================

WERK = """<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<title>{titel} — zetten</title>
<style>
{stijl}
</style>
</head>
<body class="rapport" data-model="{model}">
{sjablonen}
<div id="stroom" hidden>
{stroom}
</div>
<div id="noten" hidden>
{noten}
</div>
<div class="vel" id="rapport"></div>
<script>
{paginator}
</script>
</body>
</html>
"""

EIND = """<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titel}</title>
<style>
{stijl}

/* -- Drukwerk. De pagina draagt zijn eigen marge, dus @page staat op nul. -- */
@page {{ size: {breedte} {hoogte}; margin: 0; }}
</style>
</head>
<body{lichaamattr}>
<div class="vel">
{paginas}
</div>
</body>
</html>
"""


def _mm(px: float) -> str:
    return f"{px / 96 * 25.4:.4g}mm"


def lees_stijl() -> str:
    delen = []
    if FONTS.exists():
        delen.append(FONTS.read_text(encoding="utf-8"))
    else:
        print("let op: de ingesloten letters ontbreken. Draai "
              "`python scripts/documenten/haal_fonts.py`.", file=sys.stderr)
    for p in (STIJL, RAPPORTCSS):
        if not p.exists():
            sys.exit(f"ontbreekt: {p}")
        delen.append(p.read_text(encoding="utf-8"))
    return "\n".join(delen)


def sluit_beeld_in(markup: str, werkmap: Path) -> tuple[str, int]:
    """`<img src="beeld/x.png">` wordt een data-URI.

    De oplevering is één bestand. Een rapport dat naast zich een map met
    plaatjes nodig heeft, is er geen: het reist per mail, het wordt
    doorgestuurd, en dan is de map weg en staan er kruisjes.
    """
    gezien: dict = {}
    aantal = 0

    def vervang(m):
        nonlocal aantal
        pad = m.group(1)
        if pad.startswith("data:"):
            return m.group(0)
        if pad not in gezien:
            bestand = (werkmap / pad).resolve()
            if not bestand.exists():
                return m.group(0)
            soort = mimetypes.guess_type(bestand.name)[0] or "image/png"
            data = base64.b64encode(bestand.read_bytes()).decode("ascii")
            gezien[pad] = f"data:{soort};base64,{data}"
            aantal += 1
        return f'src="{gezien[pad]}"'

    return re.sub(r'src="([^"]+)"', vervang, markup), aantal


# =====================================================================
#  Zetten
# =====================================================================

def zet(werk_html: Path, ontwerp: dict, rondes: int = 4) -> tuple[str, dict]:
    """De stroom in een browser laten vallen, tot de folio's kloppen."""
    from _browser import browser, wacht_op_letters  # noqa: E402

    breedte, hoogte = FORMATEN[ontwerp["formaat"]]
    cfg = {
        "model": ontwerp["model"],
        # Een pagina draagt nooit `flexibel` als model: dat is een
        # eigenschap van het rapport en niet van het blad. Zonder deze
        # regel valt de pagina terug op geen enkel model en wordt het
        # kader de volle zetspiegel breed — 97 tekens per regel, en dat
        # was op de keuzekaart precies te zien.
        "paginamodel": "kantlijn" if ontwerp["model"] == "flexibel" else ontwerp["model"],
        "register": ontwerp["register"],
        "formaat": ontwerp["formaat"],
        "dubbelzijdig": bool(ontwerp.get("dubbelzijdig")),
        "bandhoogte": ontwerp.get("bandhoogte", 232),
        "eersteFolio": ontwerp.get("eersteFolio", 1),
        "folioVanaf": ontwerp.get("folioVanaf", 2),
        "inhoudDiepte": ontwerp.get("inhoudDiepte", 2),
        "dichtheid": ontwerp.get("dichtheid", "gemiddeld"),
        # Alleen in voetnootmodus zet de zetmotor noten op de pagina. In
        # eindnootmodus staan ze al als blok in de stroom.
        "notenOpPagina": ontwerp.get("noten") == "voetnoot",
        "rapporttitel": ontwerp.get("rapporttitel") or "",
        "minRegelsBoven": 2,
        "minRegelsOnder": 2,
        "minRegelsNaKop": 2,
    }

    verslagen = []
    with browser() as b:
        page = b.new_page(viewport={"width": breedte + 120, "height": 1200})
        page.goto(werk_html.resolve().as_uri())
        wacht_op_letters(page)

        afbreking = page.evaluate(PROEF_AFBREKING)
        if not afbreking:
            page.evaluate("() => document.body.setAttribute('data-afbreking', 'nee')")

        inhoud: list = []
        verslag = {}
        for ronde in range(rondes):
            cfg["inhoud"] = inhoud if ontwerp.get("inhoudsopgave") else []
            verslag = page.evaluate("(c) => window.zet(c)", cfg)
            verslagen.append({"ronde": ronde + 1, "paginas": verslag["paginas"],
                              "klachten": len(verslag["klachten"])})
            nieuw = [r for r in verslag["inhoud"] if r["niveau"] <= cfg["inhoudDiepte"]]
            if not ontwerp.get("inhoudsopgave"):
                break
            if _zelfde(inhoud, nieuw):
                break
            inhoud = nieuw
        markup = page.evaluate("() => document.getElementById('rapport').innerHTML")
    verslag["rondes"] = verslagen
    verslag["afbreking"] = bool(afbreking)
    return markup, verslag


#: Werkt de Nederlandse afbreking in deze browser.
#:
#: Uitvullen zonder afbreking geeft gaten van vier spaties in een kolom
#: van 50 tekens, en dat is op elke pagina te zien. Chromium heeft de
#: woordenboeken niet altijd aan boord — in een kale container ontbreken
#: ze meestal — en dan hoort het uitvullen te vervallen in plaats van
#: stil verkeerd te gaan.
#:
#: De proef: een lang Nederlands woord in een doos van 60 px. Breekt hij
#: af, dan wordt het meer dan één regel hoog.
PROEF_AFBREKING = """() => {
  const d = document.createElement('div');
  d.lang = 'nl';
  d.style.cssText = 'position:absolute;visibility:hidden;left:-9999px;width:62px;' +
    "font:300 13.33px/17.33px Lato,sans-serif;hyphens:auto;-webkit-hyphens:auto;" +
    'hyphenate-limit-chars:6 3 3';
  d.textContent = 'schuldhulpverleningstraject';
  document.body.appendChild(d);
  const regels = d.getClientRects().length ? d.offsetHeight : 0;
  document.body.removeChild(d);
  return regels > 26;
}"""


def _zelfde(a: list, b: list) -> bool:
    if len(a) != len(b):
        return False
    return all(x.get("folio") == y.get("folio") and x.get("tekst") == y.get("tekst")
               for x, y in zip(a, b))


# =====================================================================

def laad_ontwerp(werkmap: Path, overschrijf: dict | None = None) -> dict:
    pad = werkmap / "ontwerp.json"
    o = dict(STANDAARD_ONTWERP)
    if pad.exists():
        o.update(json.loads(pad.read_text(encoding="utf-8")))
    if overschrijf:
        o.update({k: v for k, v in overschrijf.items() if v is not None})
    if o["model"] not in MODELLEN:
        sys.exit(f"onbekend model: {o['model']}. Kies uit {', '.join(MODELLEN)}.")
    if o["register"] not in REGISTERS:
        sys.exit(f"onbekend register: {o['register']}. Kies uit {', '.join(REGISTERS)}.")
    if o["opener"] not in OPENERS:
        sys.exit(f"onbekende opener: {o['opener']}. Kies uit {', '.join(OPENERS)}.")
    if o["formaat"] not in FORMATEN:
        sys.exit(f"onbekend formaat: {o['formaat']}. Kies uit {', '.join(FORMATEN)}.")
    for sleutel, geldig in (("dichtheid", DICHTHEDEN), ("noten", NOTEN),
                            ("bronnenlijst", BRONNENLIJSTEN), ("beeld", BEELDBRONNEN),
                            ("citaatstijl", CITAATSTIJLEN)):
        if o.get(sleutel) not in geldig:
            sys.exit(f"onbekende {sleutel}: {o.get(sleutel)}. "
                     f"Kies uit {', '.join(geldig)}.")
    return o


def pas_wijzigingen_toe(doc: dict, werkmap: Path) -> list:
    """Goedgekeurde inhoudelijke wijzigingen doorvoeren.

    `wijzigingen.json` is een lijst besluiten van de gebruiker. Elk
    besluit noemt het blok, wat er verandert, en dat het is goedgekeurd.
    Zonder `"akkoord": true` gebeurt er niets — dat is de hele
    bestaansreden van dit bestand.

    Vier soorten, en meer bestaan er niet:

      knip      een alinea splitsen op een zinsgrens, tekst gelijk
      lijst     opeenvolgende alinea's worden een lijst; het teken aan
                het begin van elke regel vervalt
      kop       de tekst van een kop wordt vervangen
      tekst     de tekst van een blok wordt vervangen
    """
    pad = werkmap / "wijzigingen.json"
    if not pad.exists():
        return []
    besluiten = json.loads(pad.read_text(encoding="utf-8"))
    index = {b["id"]: b for b in doc["blokken"]}
    gedaan = []
    for w in besluiten:
        if not w.get("akkoord"):
            continue
        soort, bid = w.get("soort"), w.get("id")
        blok = index.get(bid)
        if blok is None and soort != "lijst":
            gedaan.append({**w, "resultaat": "blok niet gevonden"})
            continue
        if soort == "tekst" or soort == "kop":
            blok["tekst"] = w["naar"]
            blok["runs"] = [{"t": w["naar"]}]
            gedaan.append({**w, "resultaat": "toegepast"})
        elif soort == "chapeau":
            blok["chapeau"] = True
            gedaan.append({**w, "resultaat": "toegepast"})
        elif soort == "knip":
            plek = blok["tekst"].find(w["op"])
            if plek <= 0:
                gedaan.append({**w, "resultaat": "knippunt niet gevonden"})
                continue
            if blok.get("deel"):
                gedaan.append({**w, "resultaat": "dit blok is al eerder geknipt"})
                continue
            # Beide helften houden hetzelfde blok-id, en de spatie bij het
            # knippunt blijft aan het kopstuk hangen. Daardoor plakt
            # `tekstcheck.py` ze weer aan elkaar tot precies de brontekst,
            # en dan is een knip wat hij is: geen verandering van de tekst
            # maar van de vorm. Zonder deze twee dingen — een eigen id
            # voor de staart, of een `rstrip()` op het kopstuk — is de
            # staart nergens tegen te controleren en zou er stil tekst uit
            # kunnen vallen.
            kop, staart = blok["tekst"][:plek], blok["tekst"][plek:]
            blok["tekst"], blok["runs"] = kop, [{"t": kop}]
            blok["deel"] = 1
            nieuw = {"id": bid, "soort": "alinea", "tekst": staart,
                     "runs": [{"t": staart}], "stijl": "", "deel": 2}
            doc["blokken"].insert(doc["blokken"].index(blok) + 1, nieuw)
            gedaan.append({**w, "resultaat": "toegepast"})
        elif soort == "lijst":
            for lid in w["ids"]:
                b = index.get(lid)
                if b is None:
                    continue
                b["soort"] = "lijst"
                b["geordend"] = bool(w.get("geordend"))
                b["niveau"] = 0
                if w.get("teken_vervalt"):
                    kaal = re.sub(r"^\s*([-–—•*·▪◦o]|\(?\d{1,2}[.)]|[a-z][.)])\s+",
                                  "", b["tekst"])
                    b["tekst"] = kaal
                    b["runs"] = [{"t": kaal}]
            gedaan.append({**w, "resultaat": "toegepast"})
        elif soort == "tabelkop":
            blok["kop_van_eerste_rij"] = True
            gedaan.append({**w, "resultaat": "toegepast"})
        else:
            gedaan.append({**w, "resultaat": f"onbekende soort: {soort}"})
    return gedaan


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("werkmap", type=Path)
    ap.add_argument("--uit", default=None, help="naam van het HTML-bestand")
    ap.add_argument("--model", choices=MODELLEN)
    ap.add_argument("--register", choices=REGISTERS)
    ap.add_argument("--opener", choices=OPENERS)
    ap.add_argument("--formaat", choices=list(FORMATEN))
    ap.add_argument("--dichtheid", choices=DICHTHEDEN)
    ap.add_argument("--noten", choices=NOTEN)
    ap.add_argument("--bronnenlijst", choices=BRONNENLIJSTEN)
    ap.add_argument("--nieuw-ontwerp", action="store_true",
                    help="schrijf ontwerp.json met de defaults en stop")
    ap.add_argument("--los-beeld", action="store_true",
                    help="beeld niet insluiten maar naast het bestand laten staan")
    ap.add_argument("--alleen-stroom", action="store_true",
                    help="alleen de werkpagina schrijven, niet zetten")
    a = ap.parse_args()

    werkmap = a.werkmap
    if not (werkmap / "document.json").exists():
        sys.exit(f"geen document.json in {werkmap}. Draai eerst lees_docx.py.")

    overschrijf = {"model": a.model, "register": a.register,
                   "opener": a.opener, "formaat": a.formaat,
                   "dichtheid": a.dichtheid, "noten": a.noten,
                   "bronnenlijst": a.bronnenlijst}
    ontwerp = laad_ontwerp(werkmap, overschrijf)
    if a.nieuw_ontwerp:
        (werkmap / "ontwerp.json").write_text(
            json.dumps(ontwerp, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"geschreven: {werkmap / 'ontwerp.json'}")
        return 0

    doc = json.loads((werkmap / "document.json").read_text(encoding="utf-8"))
    citaatplan = pas_citaten_toe(doc, werkmap)
    gedaan = pas_wijzigingen_toe(doc, werkmap)
    ontwerp.setdefault("rapporttitel", None)
    if not ontwerp.get("rapporttitel"):
        ontwerp["rapporttitel"] = doc.get("titel") or ""

    stroom = Stroom(doc, ontwerp, werkmap)
    stroom.bereid_voor(werkmap)
    _waarschuw_over_apparaat(doc, ontwerp)
    voor = []
    if ontwerp.get("omslag"):
        voor.append(stroom.omslag())
    lichaam = stroom.bouw()
    if ontwerp.get("inhoudsopgave"):
        voor.append('<div data-plek="inhoudsopgave"></div>')

    titel = ontwerp.get("rapporttitel") or doc.get("titel") or werkmap.name
    werk_html = werkmap / "_zetten.html"
    werk_html.write_text(WERK.format(
        titel=_esc(titel), stijl=lees_stijl(), model=ontwerp["model"],
        sjablonen=sjablonen(ontwerp),
        stroom="\n".join(voor) + "\n" + lichaam,
        noten=stroom.voetnoten(),
        paginator=PAGINATOR.read_text(encoding="utf-8"),
    ), encoding="utf-8")

    if a.alleen_stroom:
        print(json.dumps({"werkpagina": str(werk_html)}, ensure_ascii=False, indent=2))
        return 0

    markup, verslag = zet(werk_html, ontwerp)

    ingesloten = 0
    if not a.los_beeld:
        markup, ingesloten = sluit_beeld_in(markup, werkmap)

    breedte, hoogte = FORMATEN[ontwerp["formaat"]]
    uit = werkmap / (a.uit or _bestandsnaam(titel))
    # De afbrekingsvlag moet mee naar het eindbestand. Zonder dit staat
    # de tekst in het gezette rapport wél uitgevuld terwijl er tijdens
    # het zetten vlaggend links is gemeten — en dan klopt geen enkele
    # regelafbreking meer met wat er gemeten is. Dat was op de eerste
    # gezette proef in het dubbele model als gaten in de kolom te zien.
    lichaamattr = "" if verslag["afbreking"] else ' data-afbreking="nee"'
    uit.write_text(EIND.format(
        titel=_esc(titel), stijl=lees_stijl(), lichaamattr=lichaamattr,
        breedte=_mm(breedte), hoogte=_mm(hoogte), paginas=markup,
    ), encoding="utf-8")

    (werkmap / "zetverslag.json").write_text(
        json.dumps({"ontwerp": ontwerp, "verslag": verslag,
                    "wijzigingen": gedaan, "citaten": citaatplan,
                    "beeld_ingesloten": ingesloten},
                   ensure_ascii=False, indent=1), encoding="utf-8")

    print(json.dumps({
        "bestand": str(uit),
        "paginas": verslag["paginas"],
        "rondes": verslag["rondes"],
        "klachten": verslag["klachten"][:12],
        "aantal_klachten": len(verslag["klachten"]),
        "vulling_laatste_pagina": verslag["vullingLaatste"],
        "afbreking": verslag["afbreking"],
        "wijzigingen_toegepast": len(gedaan),
        "citaten_omgezet": citaatplan.get("toegepast", 0),
        "citaten_niet_gekoppeld": len(citaatplan.get("niet_gekoppeld", [])),
        "beeld_ingesloten": ingesloten,
        "beeld_zonder_plek": stroom.beeld_zonder_plek,
        "mb": round(uit.stat().st_size / 1e6, 2),
    }, ensure_ascii=False, indent=2))
    return 0


def vervang_in_runs(runs: list, van: str, naar: str) -> tuple[list, bool]:
    """Een stuk tekst vervangen zonder de inline opmaak kwijt te raken.

    Word knipt een alinea in tientallen runs, dus een verwijzing van
    twintig tekens kan over drie runs verdeeld staan. Vervangen op de
    platte tekst en er één run van maken zou al het vet en cursief in die
    alinea wegvagen. Daarom wordt de vervanging op de samengevoegde tekst
    gezocht en daarna teruggerekend naar de runs: alles vóór en ná de
    treffer houdt zijn eigen opmaak, en de vervanging erft de opmaak van
    de run waar hij begint.
    """
    tekst = "".join(r.get("t", "") for r in runs)
    i = tekst.find(van)
    if i < 0:
        return runs, False
    j = i + len(van)
    uit, pos = [], 0
    for r in runs:
        t = r.get("t", "")
        start, eind = pos, pos + len(t)
        pos = eind
        if eind <= i or start >= j:
            uit.append(r)
            continue
        voor = t[:max(0, i - start)]
        na = t[max(0, j - start):] if eind > j else ""
        if voor:
            uit.append({**r, "t": voor})
        if start <= i < eind:
            uit.append({**r, "t": naar})
        if na:
            uit.append({**r, "t": na})
    return uit, True


def pas_citaten_toe(doc: dict, werkmap: Path) -> dict:
    """De citatieomzetting uit `citaten.json` doorvoeren.

    Anders dan `wijzigingen.json` staat hier geen `akkoord` bij, en dat
    is met opzet: de opdrachtgever heeft vastgesteld dat een verwijzing
    omzetten opmaak is en geen herschrijving. Wat er wél gebeurt is
    vastleggen: elke vervanging staat in het plan, `tekstcheck.py`
    controleert dat er precies dát is veranderd en niets meer, en het
    aantal gaat mee bij de oplevering.
    """
    pad = werkmap / "citaten.json"
    if not pad.exists():
        return {}
    plan = json.loads(pad.read_text(encoding="utf-8"))
    index = {b["id"]: b for b in doc["blokken"]}
    gelukt = mislukt = 0
    for v in plan.get("vervangingen", []):
        blok = index.get(v["id"])
        if blok is None:
            mislukt += 1
            continue
        runs, ok = vervang_in_runs(blok.get("runs", []), v["van"], v["naar"])
        if not ok:
            mislukt += 1
            continue
        blok["runs"] = runs
        blok["tekst"] = "".join(r.get("t", "") for r in runs)
        gelukt += 1
    plan["toegepast"] = gelukt
    plan["mislukt"] = mislukt
    doc["_citaatplan"] = plan
    return plan


def _waarschuw_over_apparaat(doc: dict, ontwerp: dict) -> None:
    """Zeggen wanneer een besluit niet bij de bron past.

    Dit blokkeert niet, want de gebruiker mag een bronnenlijst willen die
    er nog niet is — dan komt hij er later in. Maar stil doorbouwen zou
    betekenen dat er een besluit is genomen dat niets doet, en dat merkt
    niemand tot de oplevering.
    """
    ap = doc.get("apparaat", {})
    if ontwerp.get("noten") != "geen" and not ap.get("voetnoten") and not ap.get("eindnoten"):
        print(f"let op: notenplaatsing staat op '{ontwerp['noten']}' maar het "
              f"brondocument heeft geen noten. Er verandert niets.", file=sys.stderr)
    if ontwerp.get("noten") == "geen" and (ap.get("voetnoten") or ap.get("eindnoten")):
        print(f"let op: notenplaatsing staat op 'geen' terwijl het brondocument "
              f"{ap.get('voetnoten', 0) + ap.get('eindnoten', 0)} noten heeft. Die "
              f"tekst komt dan nergens terecht en tekstcheck.py blokkeert erop.",
              file=sys.stderr)
    if ontwerp.get("bronnenlijst") != "geen" and not ap.get("bronnenlijst"):
        print(f"let op: bronnenlijst staat op '{ontwerp['bronnenlijst']}' maar er is "
              f"in het brondocument geen kop gevonden die er een aankondigt. Er "
              f"wordt niets als bronnenlijst gezet; een lijst verzinnen doet deze "
              f"skill niet.", file=sys.stderr)
    if ontwerp.get("bijlagen") and not ap.get("bijlagen"):
        print("let op: er is een bijlagegrens opgegeven die niet uit de bron komt. "
              "Controleer of het blok-id klopt.", file=sys.stderr)
    if ap.get("bijlagen") and not ontwerp.get("bijlagen"):
        n = len(ap["bijlagen"]["koppen"])
        print(f"let op: het brondocument heeft {n} kop(pen) die met 'Bijlage' of "
              f"'Appendix' beginnen, maar er is geen bijlagegrens ingesteld. Ze "
              f"worden als gewone hoofdstukken gezet.", file=sys.stderr)


def _bestandsnaam(titel: str) -> str:
    kaal = re.sub(r"[^\w\s-]", "", titel, flags=re.U).strip().lower()
    kaal = re.sub(r"[\s_]+", "-", kaal)[:60] or "rapport"
    return kaal + ".html"


if __name__ == "__main__":
    raise SystemExit(main())
