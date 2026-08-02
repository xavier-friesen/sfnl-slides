"""Fill the placeholders of a slide from JSON.

Usage:
    python set_text.py <slide.xml> --json '{"title": "...", "10": ["...", "..."]}'
    python set_text.py <slide.xml> --file slide2.json
    python set_text.py <slide.xml> --json '{...}' --drop-empty

Keys are placeholder indices as strings, or the aliases `title` (idx 0) and
`subtitle` (idx 1). Values are:

    "one paragraph"
    ["first paragraph", "second paragraph"]
    [[{"t": "Label: ", "b": true}, {"t": "rest of the line"}]]     one paragraph, two runs
    {"runs": [{"t": "Label: ", "b": true}, {"t": "rest"}]}         the same, one paragraph
    [{"runs": [...], "lvl": 1}]                                    indent level 1
    [{"t": "eerste vraag", "num": true}, {"t": "tweede", "num": true}]   genummerde lijst
    {"runs": [{"t": "Intake: ", "b": true, "u": true}, {"t": "de rest"}], "align": "c"}

`num: true` zet `<a:buAutoNum type="arabicPeriod"/>` op die alinea: PowerPoint nummert
dan zelf. Typ nooit "1." "2." in de tekst zelf — dan lijnt de vervolgregel onder het
nummer door in plaats van erlangs, en een tussengevoegd punt hernummert niets.
`qa_text.py` meldt handgetypte nummers als `manual-numbering`.

Een run kent `t`, `b` (vet), `u` (onderstreept) en `lang`; een alinea kent `lvl`, `num` en
`align` (`l`, `c`, `r`). Dat is dezelfde vorm als een tekstblok in `parameters`, waar
`compose.py` hem uitvoert — zie `reference/deck-spec.md`.

`u` en `align` volgen V6 (30 juli 2026): onderstreping mag voor een **inline label** en
centreren mag waar de kolom smal is. Ze stonden al in de spec en werden al door
`deck_spec.py` gevalideerd, maar dit script schreef alleen `b`, `lvl` en `num` — dus een
onderstreept label in een placeholder verdween stil bij de bouw. Twee grenzen blijven
staan: een alinea die in haar **geheel** onderstreept is is een fout (dat is de
hyperlinklook, en dat is precies waarvoor onderstreping eerst helemaal verboden was), en
`align` neemt alleen `l`, `c` of `r` — hetzelfde vocabulaire als
`tabel.data.columns[].align`, zodat er één woord voor uitlijning in de spec staat.

Note the nesting on the two-run form. A flat list of run objects —
`[{"t": "a"}, {"t": "b"}]` — is a list of PARAGRAPHS of one run each, so the bold label
lands on its own bullet. Wrap the runs in their own list, or use the `{"runs": [...]}`
form.

Why a script instead of editing the XML by hand: filling placeholders is the bulk of
building a deck, and doing it this way keeps slide XML out of the conversation, keeps
the run properties consistent, and cannot put text in the wrong placeholder.

Font, size and colour are inherited from the layout and the master — that is
layout-first. Nothing here writes a typeface. Bold is the normal inline emphasis;
underline is allowed for an inline label only (V6, see below).

Straight apostrophes inside a word are rewritten to the typographic ’ (`risico's` →
`risico’s`); `--keep-apostrophes` switches that off. A straight quotation mark around a
quote is left alone — turning it into ’ would be wrong — and `qa_typography.py` reports
it so it can be fixed by hand.

`--drop-empty` removes placeholder shapes that got no text, so no unfilled prompt is
left on the slide.

Output is compact JSON.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from lxml import etree

from _deck import emit, normalise_apostrophes

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS = {"a": A, "p": P}

ALIASES = {"title": 0, "titel": 0, "subtitle": 1, "subtitel": 1}

# V6: alineauitlijning. Zelfde vocabulaire als `deck_spec.UITLIJNINGEN` en als
# `tabel.data.columns[].align`; `c` is het woord in de spec, `ctr` is het woord in OOXML.
ALIGN = {"l": "l", "c": "ctr", "ctr": "ctr", "r": "r"}


def placeholder_idx(sp: etree._Element) -> int | None:
    ph = sp.find(".//p:nvSpPr/p:nvPr/p:ph", NS)
    if ph is None:
        return None
    ph_type = ph.get("type")
    if ph_type in {"title", "ctrTitle"}:
        return 0
    idx = ph.get("idx")
    return int(idx) if idx is not None else 0


def normalise(value) -> list[dict]:
    """Return a list of paragraphs, each {'runs': [{'t':..,'b':..}], 'lvl': int}.

    A dict has to be wrapped too. Iterating a bare dict walks its KEYS, so
    `{"runs": [...]}` passed straight through used to put the literal strings "runs" and
    "lvl" on the slide, with exit code 0 and a `filled` list that looked right.
    """
    if isinstance(value, (str, dict)):
        value = [value]
    if not isinstance(value, list):
        raise SystemExit(
            f"kan waarde niet lezen: {value!r} — geef een string, een dict met "
            '"runs", of een lijst van paragrafen'
        )
    paragraphs = []
    for item in value:
        if isinstance(item, str):
            paragraphs.append({"runs": [{"t": item}], "lvl": 0, "num": False, "align": None})
        elif isinstance(item, dict) and "runs" in item:
            paragraphs.append(
                {
                    "runs": item["runs"],
                    "lvl": int(item.get("lvl", 0)),
                    "num": bool(item.get("num")),
                    "align": item.get("align"),
                }
            )
        elif isinstance(item, dict):
            paragraphs.append(
                {
                    "runs": [item],
                    "lvl": int(item.get("lvl", 0)),
                    "num": bool(item.get("num")),
                    "align": item.get("align"),
                }
            )
        elif isinstance(item, list):
            paragraphs.append({"runs": item, "lvl": 0, "num": False, "align": None})
        else:
            raise SystemExit(f"kan waarde niet lezen: {item!r}")
    for paragraph in paragraphs:
        _check_align(paragraph)
        _check_underline(paragraph)
    return paragraphs


def _check_align(paragraph: dict) -> None:
    align = paragraph.get("align")
    if align is None:
        return
    if align not in ALIGN:
        raise SystemExit(
            f"onbekende uitlijning {align!r} — kies l, c of r (V6: centreren mag waar de "
            "kolom smal is, bijvoorbeeld de tekst onder een icoontegel)"
        )


def _check_underline(paragraph: dict) -> None:
    """Een alinea die in haar GEHEEL onderstreept is blijft een fout.

    V6 staat onderstreping toe voor een **inline label**: "Communicatie:" onderstreept met
    de zin erachter. Een hele alinea onderstrepen leest als een hyperlink, en dat is precies
    het defect waarvoor onderstreping eerst helemaal verboden was. Het verschil is te
    tellen: een label heeft tekst achter zich, dus staat er in dezelfde alinea nog een run
    zonder `u`.
    """
    runs = [run for run in paragraph["runs"] if isinstance(run, dict)]
    gevuld = [run for run in runs if str(run.get("t", "")).strip()]
    if not gevuld:
        return
    onderstreept = [run for run in gevuld if run.get("u")]
    if onderstreept and len(onderstreept) == len(gevuld):
        tekst = "".join(str(run.get("t", "")) for run in gevuld)[:50]
        raise SystemExit(
            f'de hele alinea "{tekst}" is onderstreept, en dat leest als een hyperlink. '
            "V6 staat onderstreping toe voor een INLINE LABEL: zet het label in zijn eigen "
            'run ({"t": "Label: ", "b": true, "u": true}) met de zin erachter in een '
            "tweede run zonder `u`"
        )


def write_paragraphs(
    sp: etree._Element, paragraphs: list[dict], fix_apostrophes: bool = True
) -> int:
    """Write the paragraphs into the shape. Returns how many apostrophes were fixed."""
    body = sp.find("./p:txBody", NS)
    if body is None:
        raise SystemExit("placeholder zonder txBody")
    fixed = 0

    # Autofit staat nooit aan: zonder expliciete <a:noAutofit/> erft de placeholder de
    # normAutofit uit de layout en mag PowerPoint de tekst stil krimpen. Liever tekst
    # die zichtbaar te lang is en een mens die beslist. qa_text.py keurt het ook af.
    body_pr = body.find("a:bodyPr", NS)
    if body_pr is None:
        body_pr = etree.Element(f"{{{A}}}bodyPr")
        body.insert(0, body_pr)
    for tag in ("a:noAutofit", "a:normAutofit", "a:spAutoFit"):
        for el in body_pr.findall(tag, NS):
            body_pr.remove(el)
    etree.SubElement(body_pr, f"{{{A}}}noAutofit")

    for para in body.findall("a:p", NS):
        body.remove(para)

    for paragraph in paragraphs:
        node = etree.SubElement(body, f"{{{A}}}p")
        level = paragraph.get("lvl", 0)
        align = paragraph.get("align")
        ppr = None
        if level or align:
            ppr = etree.SubElement(node, f"{{{A}}}pPr")
        if level:
            ppr.set("lvl", str(level))
        if align:
            # `algn` is een ATTRIBUUT van a:pPr, niet een kind, dus de sequence-volgorde
            # binnen pPr raakt het niet.
            ppr.set("algn", ALIGN[align])
        if paragraph.get("num"):
            if ppr is None:
                ppr = etree.SubElement(node, f"{{{A}}}pPr")
            # CT_TextParagraphProperties is een sequence: de bullet-keuze komt ná
            # lnSpc/spcBef/spcAft en vóór defRPr. Er staat hier niets anders in, dus
            # aanhangen is de juiste plek.
            etree.SubElement(ppr, f"{{{A}}}buAutoNum").set("type", "arabicPeriod")
        for run in paragraph["runs"]:
            text = run.get("t", "")
            if fix_apostrophes:
                repaired = normalise_apostrophes(text)
                if repaired != text:
                    fixed += 1
                    text = repaired
            # De eenheid blijft bij het getal (voice.md): een non-breaking space na
            # het euroteken, anders blijft "€" op de vorige regel achter zodra de
            # regel daar breekt.
            text = text.replace("€ ", "€ ")
            r = etree.SubElement(node, f"{{{A}}}r")
            rpr = etree.SubElement(r, f"{{{A}}}rPr")
            rpr.set("lang", run.get("lang", "nl-NL"))
            rpr.set("dirty", "0")
            if run.get("b"):
                rpr.set("b", "1")
            if run.get("u"):
                rpr.set("u", "sng")
            t = etree.SubElement(r, f"{{{A}}}t")
            t.text = text
            # No xml:space="preserve" here. That belongs on Word's <w:t> (CT_Text
            # declares the attribute); DrawingML's <a:t> is ST_Xstring, a simple type
            # that allows no attributes at all, so the strict pml/dml schema rejects it
            # and every deck with a padded run failed validation. Leading and trailing
            # spaces in <a:t> are significant and preserved without it — verified
            # against the template, which never writes the attribute either.

    return fixed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slide", type=Path)
    parser.add_argument("--json", dest="payload", help="JSON object with the content")
    parser.add_argument("--file", type=Path, help="read the JSON object from a file")
    parser.add_argument(
        "--drop-empty",
        action="store_true",
        help="remove placeholder shapes that were not given text",
    )
    parser.add_argument(
        "--keep-apostrophes",
        action="store_true",
        help="leave straight apostrophes alone (default: risico's -> risico’s)",
    )
    args = parser.parse_args()

    if not args.slide.exists():
        raise SystemExit(f"{args.slide} not found")
    if not args.payload and not args.file:
        raise SystemExit("geef --json of --file")

    raw = args.file.read_text(encoding="utf-8") if args.file else args.payload
    content = json.loads(raw)

    wanted: dict[int, list[dict]] = {}
    for key, value in content.items():
        idx = ALIASES.get(str(key).lower())
        if idx is None:
            try:
                idx = int(key)
            except ValueError:
                raise SystemExit(f"onbekende placeholder-key: {key!r}") from None
        wanted[idx] = normalise(value)

    tree = etree.parse(str(args.slide))
    root = tree.getroot()
    tree_parent = root.find(".//p:cSld/p:spTree", NS)

    filled, dropped, missing = [], [], []
    apostrophes = 0
    seen = set()
    for sp in list(tree_parent.iter(f"{{{P}}}sp")):
        idx = placeholder_idx(sp)
        if idx is None:
            continue
        seen.add(idx)
        if idx in wanted:
            apostrophes += write_paragraphs(
                sp, wanted[idx], fix_apostrophes=not args.keep_apostrophes
            )
            filled.append(idx)
        elif args.drop_empty:
            parent = sp.getparent()
            parent.remove(sp)
            dropped.append(idx)

    missing = sorted(set(wanted) - seen)
    if missing:
        raise SystemExit(
            f"placeholder(s) {missing} staan niet op {args.slide.name}; "
            "voeg ze toe met add_slide.py of kies een andere layout"
        )

    tree.write(str(args.slide), xml_declaration=True, encoding="UTF-8", standalone=True)
    emit(
        {
            "slide": args.slide.name,
            "filled": sorted(filled),
            "dropped": sorted(dropped),
            "apostrophes_fixed": apostrophes,
        }
    )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(__doc__)
        sys.exit(1)
    main()
