#!/usr/bin/env python3
"""De tekstregels van `deck-check`: wat er aan een regel tekst verandert, en wat niet.

Dit is de kern van de skill en de enige plek waar hij staat. `reference/voice.md` zegt
wat er op een slide hóórt te staan (titels in kapitalen zonder punt, typografische
aanhalingstekens, het euroteken, de eenheid bij het getal); dit bestand is de
mechanische kant daarvan plus de opschoningsregels die nergens anders staan:
spatiëring rond een slash, interpunctiespatiëring, dubbele spaties, streepjes,
dubbele woorden en een kleine spellinglijst per taal.

Twee dingen zijn hier met opzet zo gebouwd:

**De bescherming staat vóór alles.** Een URL, een e-mailadres, een breuk, een bedrag,
een percentage, een datum en een formule gaan er ongewijzigd door. Zonder die laag
maakt de interpunctieregel van `www.socfin.nl/cases` iets anders en zet de slashregel
spaties in `3/4`. Wat overblijft van een alinea die vrijwel helemaal beschermd is, is
alleen de witruimteopschoning.

**Eén run in, één run uit.** Elke functie hier werkt op de tekst van één run, met de
rol en de taal van het element erbij en met de vraag of het de laatste run van de
alinea is. Daardoor hoeft de toepasstap nooit runs te hertekenen en blijven vet en
cursief per definitie staan — de fout die een fixer maakt is de alinea opnieuw
opbouwen en de opmaak van de tweede helft van de zin verliezen.

Wat hier NIET staat, omdat het al ergens staat:

* restplaceholders, `{{MARKER}}`, sjabloonprompts, Calibri, een harde hex, een titel in
  onderkast, dubbele spaties als bevinding — dat is `scripts/qa_text.py`
* de maten, de kleuren, de letterfamilies en de vier maten per rol — `reference/merk.md`
  en `reference/vormentaal.md`
* de dozen van de titel- en subtitelplaceholder — `reference/sjabloon.md`
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _deck import IN_WORD_APOSTROPHE  # noqa: E402  de enige definitie in de plugin

# ---------------------------------------------------------------------------
# Do Not Touch: wat er ongewijzigd door moet.
# ---------------------------------------------------------------------------

BESCHERMD = re.compile(
    r"""
    (?:https?://\S+)                          # URL met schema
  | (?:www\.[^\s,;]+)                         # URL zonder schema
  | (?:[^\s,;:()]+@[^\s,;:()]+\.[A-Za-z]{2,}) # e-mailadres
  | (?:\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b)     # datum
  | (?:\b\d+/\d+\b)                           # breuk of verhouding
  | (?:€\s?\d[\d.,]*(?:\s?(?:mln|mrd|k))?)     # bedrag
  | (?:\b\d[\d.,]*\s?%)                        # percentage
  | (?:\b\d[\d.,]*\s?(?:[a-zA-Z]{1,4}/[a-zA-Z]{1,4}|fte|uur|dagen|jaar|mnd))
  | (?:\b\d[\d.,]*\b)                          # getal met scheidingstekens
  | (?:[A-Za-z0-9_]+\.(?:xlsx|docx|pptx|pdf|csv|png|jpg|svg|md|py))
  | (?:\S*(?:<=|>=|!=|==|\+\+)\S*)             # formule of code
    """,
    re.VERBOSE,
)

# De voorpas (streepjes) heeft de hele tekst nodig, want een reeks als 2023-2025 valt
# tussen twee beschermde getallen in. Wat daar wél beschermd moet blijven, is de kleine
# groep waarin een koppelteken betekenis heeft: een datum, een URL, een e-mailadres, een
# bestandsnaam en een formule.
BESCHERMD_HARD = re.compile(
    r"""
    (?:https?://\S+)
  | (?:www\.[^\s,;]+)
  | (?:[^\s,;:()]+@[^\s,;:()]+\.[A-Za-z]{2,})
  | (?:\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b)
  | (?:[A-Za-z0-9_]+\.(?:xlsx|docx|pptx|pdf|csv|png|jpg|svg|md|py))
  | (?:\S*(?:<=|>=|!=|==|\+\+)\S*)
    """,
    re.VERBOSE,
)

# Een tekst die vrijwel helemaal beschermd is, krijgt alleen witruimteopschoning.
BESCHERMD_DREMPEL = 0.6

AFKORTINGEN = {
    "etc.", "ca.", "mln.", "mrd.", "e.d.", "o.a.", "d.w.z.", "bijv.", "incl.",
    "excl.", "nl.", "resp.", "t.o.v.", "n.a.v.", "m.b.t.", "i.v.m.", "a.s.",
}
LETTERAFKORTING = re.compile(r"(?:\b[A-Za-z]\.){2,}$")

# ---------------------------------------------------------------------------
# Spelling: een kleine gecureerde lijst per taal, geen NLP.
# ---------------------------------------------------------------------------

SPELLING_NL = {
    "financiele": "financiële", "efficent": "efficiënt", "effcient": "efficiënt",
    "onstaan": "ontstaan", "accomodatie": "accommodatie", "prive": "privé",
    "beinvloeden": "beïnvloeden", "gecoordineerd": "gecoördineerd",
    "reeele": "reële", "cooperatie": "coöperatie", "orginele": "originele",
    "renumeratie": "remuneratie", "kwantitieve": "kwantitatieve",
    "resultaaten": "resultaten", "impakt": "impact", "buurtbewonders": "buurtbewoners",
    "maatschapelijke": "maatschappelijke", "orgnisatie": "organisatie",
    "gemeenete": "gemeente", "orgineel": "origineel",
}

# De lijst is met opzet klein en gecureerd: een spellingcontrole die alles nakijkt,
# corrigeert ook wat geen fout is (jargon, eigennamen, projectnamen), en dan verandert
# er tekst waar niemand om vroeg. Wat hier niet in staat, komt eruit als bevinding van
# het oog en niet van een script.

SPELLING_EN = {
    "recieve": "receive", "seperate": "separate", "occured": "occurred",
    "definately": "definitely", "succesful": "successful", "goverment": "government",
    "wich": "which", "tekst": "text", "adress": "address", "commited": "committed",
    "enviroment": "environment", "publically": "publicly", "responsability":
    "responsibility", "acheive": "achieve", "beleive": "believe",
}

# Woorden die legitiem verdubbelen; die worden gemeld en niet gerepareerd.
DUBBEL_TOEGESTAAN = {
    "dat", "die", "de", "het", "een", "en", "of", "is", "in", "op", "te", "to",
    "that", "had", "the", "van", "voor", "maar", "als", "wat", "er", "heel",
}

VOEGWOORD_EIND = re.compile(
    r"\b(?:en|of|maar|want|omdat|terwijl|and|or|but|because|while)\s*$", re.I
)

# ---------------------------------------------------------------------------
# Taal: stopwoorden, want een deck heeft te weinig tekst voor iets zwaarders.
# ---------------------------------------------------------------------------

NL_WOORDEN = {
    "de", "het", "een", "en", "van", "in", "op", "voor", "met", "dat", "die", "is",
    "zijn", "wordt", "worden", "niet", "aan", "door", "bij", "als", "naar", "per",
    "wij", "we", "hun", "deze", "dit", "ook", "maar", "om", "te", "uit", "over",
    "gemeente", "jaar", "meer", "geen",
}
EN_WOORDEN = {
    "the", "a", "an", "and", "of", "in", "on", "for", "with", "that", "is", "are",
    "was", "were", "not", "to", "by", "at", "as", "from", "per", "we", "our",
    "this", "these", "also", "but", "their", "will", "more", "no", "than",
}

WOORD = re.compile(r"[^\W\d_]+", re.UNICODE)


def taal_van(tekst: str) -> str | None:
    """`nl`, `en`, of None wanneer de tekst te kort of te neutraal is."""
    woorden = [w.lower() for w in WOORD.findall(tekst or "")]
    if len(woorden) < 3:
        return None
    nl = sum(1 for w in woorden if w in NL_WOORDEN)
    en = sum(1 for w in woorden if w in EN_WOORDEN)
    if nl == en:
        return None
    return "nl" if nl > en else "en"


# ---------------------------------------------------------------------------
# De regels, elk op één onbeschermd segment.
# ---------------------------------------------------------------------------

def _witruimte(seg: str) -> tuple[str, list[str]]:
    """Dubbele spaties weg, en een harde ruimte die naast een gewone spatie staat.

    Een losse harde ruimte blijft staan: die houdt in \u20ac\u00a01,04 mln de eenheid bij het
    getal (`reference/voice.md`, Getallen en eenheden) en is daar geen fout maar de
    bedoeling. Wat eruit gaat is de combinatie van twee soorten ruimte naast elkaar,
    want die komt uit een kopieerslag.
    """
    labels = []
    nieuw = re.sub(r"[ ]\u00a0|\u00a0[ ]|\u00a0{2,}", " ", seg)
    if nieuw != seg:
        labels.append("harde-ruimte")
    if re.search(r"[ ]{2,}", nieuw):
        labels.append("dubbele-spatie")
        nieuw = re.sub(r"[ ]{2,}", " ", nieuw)
    return nieuw, labels


def _interpunctie(seg: str) -> tuple[str, list[str]]:
    labels = []
    nieuw = re.sub(r"[ ]+([,.;:!?])", r"\1", seg)
    nieuw = re.sub(r"([,;:!?])(?=[^\W\d_])", r"\1 ", nieuw)
    nieuw = re.sub(r"\([ ]+", "(", nieuw)
    nieuw = re.sub(r"[ ]+\)", ")", nieuw)
    if nieuw != seg:
        labels.append("interpunctie-spatiering")
    return nieuw, labels


SLASH = re.compile(r"(?<![\s/])[ ]?/[ ]?(?![\s/])")


def _slash(seg: str) -> tuple[str, list[str]]:
    """Een slash die twee woorden scheidt krijgt een spatie aan beide zijden.

    Een korte samentrekking blijft staan: `en/of` is één woord in het Nederlands en
    `24/7` is een uitdrukking. De grens is drie tekens per kant; alles daarboven is
    een scheiding tussen twee begrippen en dan is `A / B` de zetting
    (`reference/vormentaal.md` §9).
    """
    labels: list[str] = []

    def vervang(match: re.Match) -> str:
        start, eind = match.start(), match.end()
        links = re.search(r"[^\s]+$", seg[:start])
        rechts = re.match(r"[^\s]+", seg[eind:])
        l_txt = links.group(0) if links else ""
        r_txt = rechts.group(0) if rechts else ""
        if len(l_txt) <= 3 and len(r_txt) <= 3:
            return match.group(0)
        if "/" in l_txt or "/" in r_txt:
            return match.group(0)
        labels.append("slash-spatiering")
        return " / "

    return SLASH.sub(vervang, seg), labels


def _streepjes(seg: str) -> tuple[str, list[str]]:
    labels = []
    nieuw = re.sub(r"(?<=\d)[ ]?-[ ]?(?=\d)", "–", seg)
    if nieuw != seg:
        labels.append("reeks-en-streepje")
    voor = nieuw
    nieuw = re.sub(r"(?<!-)--(?!-)", "–", nieuw)
    if nieuw != voor:
        labels.append("dubbel-koppelteken")
    return nieuw, labels


def _tekens(seg: str) -> tuple[str, list[str]]:
    """Apostrofs, aanhalingstekens en gestapelde interpunctie."""
    labels = []
    nieuw = IN_WORD_APOSTROPHE.sub("’", seg)
    if nieuw != seg:
        labels.append("apostrof")

    voor = nieuw
    nieuw = re.sub(r"\.{3}", "…", nieuw)
    nieuw = re.sub(r"\.{2}(?!\.)", ".", nieuw)
    nieuw = re.sub(r"([!?])\1+", r"\1", nieuw)
    if nieuw != voor:
        labels.append("gestapelde-interpunctie")

    if re.search(r"\"", nieuw):
        labels.append("recht-aanhalingsteken")
    if re.search(r"(?<![^\W\d_])'|'(?![^\W\d_])", nieuw):
        labels.append("rechte-apostrof")
    return nieuw, labels


def _dubbel_woord(seg: str) -> tuple[str, list[str]]:
    labels: list[str] = []

    def vervang(match: re.Match) -> str:
        woord = match.group(1)
        if woord.lower() in DUBBEL_TOEGESTAAN or len(woord) < 4:
            labels.append("dubbel-woord-gemeld")
            return match.group(0)
        labels.append("dubbel-woord")
        return woord

    nieuw = re.sub(r"\b([^\W\d_]+)\s+\1\b", vervang, seg, flags=re.I)
    return nieuw, labels


def _spelling(seg: str, taal: str | None) -> tuple[str, list[str]]:
    kaart = SPELLING_NL if taal == "nl" else SPELLING_EN if taal == "en" else None
    if not kaart:
        return seg, []
    labels: list[str] = []

    def vervang(match: re.Match) -> str:
        woord = match.group(0)
        doel = kaart.get(woord.lower())
        if not doel or doel.lower() == woord.lower():
            return woord
        labels.append(f"spelling-{taal}")
        if woord.isupper():
            return doel.upper()
        if woord[:1].isupper():
            return doel[:1].upper() + doel[1:]
        return doel

    return WOORD.sub(vervang, seg), labels


REGELS_OP_SEGMENT = (_witruimte, _interpunctie, _slash, _tekens, _dubbel_woord)


def _voorpas(tekst: str) -> tuple[str, list[str]]:
    """Regels die de hele regel nodig hebben in plaats van één segment.

    De streepjesregel is er één: `2023-2025` staat tussen twee getallen in, en die zijn
    beschermd, dus per segment ziet de regel het koppelteken zonder zijn buren. Hier
    loopt hij over de hele tekst, met alleen de harde bescherming eromheen — een datum
    houdt zijn koppeltekens.
    """
    labels: list[str] = []
    stukken: list[str] = []
    positie = 0
    for match in BESCHERMD_HARD.finditer(tekst):
        deel, nieuwe = _streepjes(tekst[positie:match.start()])
        stukken.append(deel)
        labels += nieuwe
        stukken.append(match.group(0))
        positie = match.end()
    deel, nieuwe = _streepjes(tekst[positie:])
    stukken.append(deel)
    labels += nieuwe
    return "".join(stukken), labels


def _segmenten(tekst: str) -> list[tuple[str, bool]]:
    """Splits in (stuk, beschermd) zodat de regels de beschermde stukken overslaan."""
    delen: list[tuple[str, bool]] = []
    positie = 0
    for match in BESCHERMD.finditer(tekst):
        if match.start() > positie:
            delen.append((tekst[positie:match.start()], False))
        delen.append((match.group(0), True))
        positie = match.end()
    if positie < len(tekst):
        delen.append((tekst[positie:], False))
    return delen or [(tekst, False)]


def _beschermd_aandeel(delen: list[tuple[str, bool]]) -> float:
    totaal = sum(len(t) for t, _ in delen) or 1
    return sum(len(t) for t, b in delen if b) / totaal


def eindinterpunctie(tekst: str, rol: str, *, lijstitem: bool) -> tuple[str, list[str]]:
    """Haal één afsluitende punt of komma weg waar die niet hoort.

    De regel voor de titel en de subtitel staat in `reference/voice.md` (Titels:
    "Nooit een punt"; de subtitel "zonder punt"). Voor een lijstitem staat hij in
    `reference/vormentaal.md` §9: een losse regel, een label of een lijstitem eindigt
    zonder punt, een volle zin in een prozablok houdt zijn punt.

    Een vraagteken blijft staan, een ellips blijft staan, en een afkorting met punten
    (`o.a.`, `U.S.`) wordt niet afgeknipt.
    """
    kaal = tekst.rstrip()
    staart = tekst[len(kaal):]
    if not kaal or kaal[-1] not in ".,":
        labels = []
        if rol == "title" and kaal.endswith("!"):
            labels.append("uitroepteken-titel-gemeld")
        return tekst, labels
    if kaal.endswith(("…", "?")):
        return tekst, []
    laatste = kaal.split()[-1].lower()
    if laatste in AFKORTINGEN or LETTERAFKORTING.search(kaal):
        return tekst, []
    if rol == "title":
        label = "eindpunt-titel"
    elif rol == "subtitle":
        label = "eindpunt-subtitel"
    elif lijstitem:
        label = "eindpunt-lijstitem"
    else:
        return tekst, []
    return kaal[:-1].rstrip() + staart, [label]


def kapitaliseer(tekst: str, rol: str) -> tuple[str, list[str]]:
    """De titel gaat naar kapitalen; de subtitel gaat er juist niet naartoe.

    `reference/voice.md`: "Altijd in kapitalen" voor de titel, en de subtitel staat in
    zinsvorm met een hoofdletter aan het begin, niet in kapitalen. Een subtitel die
    wél in kapitalen staat wordt daarom gemeld en niet omgezet — terugzetten naar
    zinsvorm raadt naar de eigennamen die erin staan, en dat is werk voor een mens.
    """
    letters = [c for c in tekst if c.isalpha()]
    if not letters:
        return tekst, []
    if rol == "title":
        if all(c.isupper() for c in letters):
            return tekst, []
        # Alleen de HARDE bescherming geldt hier: een URL, een e-mailadres, een
        # bestandsnaam en een formule veranderen van betekenis in kapitalen. Een getal
        # met een eenheid erachter (`39 dagen`) doet dat niet — die eenheid hoort mee
        # naar boven, want anders staat er halve onderkast in de titelrij.
        stukken, positie = [], 0
        for match in BESCHERMD_HARD.finditer(tekst):
            stukken.append(tekst[positie:match.start()].upper())
            stukken.append(match.group(0))
            positie = match.end()
        stukken.append(tekst[positie:].upper())
        return "".join(stukken), ["titel-kapitalen"]
    if rol == "subtitle" and all(c.isupper() for c in letters) and len(letters) > 3:
        return tekst, ["subtitel-in-kapitalen-gemeld"]
    return tekst, []


def schoon_run(tekst: str, *, rol: str = "body", taal: str | None = None,
               laatste: bool = False, lijstitem: bool = False) -> tuple[str, list[str]]:
    """Schoon de tekst van één run op. Geeft (nieuwe tekst, labels).

    Een label dat op `-gemeld` eindigt is een vlag zonder wijziging: de tekst is dan
    ongemoeid gelaten en er hoort een regel in het wijzigingslogboek zonder verschil.
    """
    if not tekst:
        return tekst, []
    tekst, labels = _voorpas(tekst)
    delen = _segmenten(tekst)
    alleen_witruimte = _beschermd_aandeel(delen) > BESCHERMD_DREMPEL

    stukken: list[str] = []
    for deel, beschermd in delen:
        if beschermd:
            stukken.append(deel)
            continue
        if not deel.strip():
            # Een segment van alleen witruimte tussen twee beschermde stukken: dat is
            # precies waar een dubbele spatie zich verstopt (`20 dagen  ` in een
            # tabelcel), dus de witruimteregel geldt er wél.
            deel, nieuwe = _witruimte(deel)
            labels += nieuwe
            stukken.append(deel)
            continue
        huidig = deel
        regels = (_witruimte,) if alleen_witruimte else REGELS_OP_SEGMENT
        for regel in regels:
            huidig, nieuwe = regel(huidig)
            labels += nieuwe
        if not alleen_witruimte:
            huidig, nieuwe = _spelling(huidig, taal)
            labels += nieuwe
        stukken.append(huidig)

    nieuw = "".join(stukken)

    if not alleen_witruimte:
        nieuw, nieuwe = kapitaliseer(nieuw, rol)
        labels += nieuwe
    if laatste:
        kaal = nieuw.rstrip(" \t\u00a0")
        if kaal != nieuw and kaal:
            nieuw = kaal
            labels.append("witruimte-eind")
        nieuw, nieuwe = eindinterpunctie(nieuw, rol, lijstitem=lijstitem)
        labels += nieuwe

    # Volgorde vasthouden en dubbelen eruit, zodat het logboek leesbaar blijft.
    gezien: list[str] = []
    for label in labels:
        if label not in gezien:
            gezien.append(label)
    return nieuw, gezien


def niet_lopende_zin(tekst: str) -> bool:
    """Heuristiek: eindigt op een voegwoord, of draagt gestapelde interpunctie."""
    kaal = (tekst or "").strip().rstrip(".,;:")
    if not kaal:
        return False
    if VOEGWOORD_EIND.search(kaal):
        return True
    if re.search(r"[!?]{2,}", kaal) or re.search(r"\.{2}(?!\.)", kaal):
        return True
    return bool(re.search(r"\b([^\W\d_]{4,})\s+\1\b", kaal, re.I))
