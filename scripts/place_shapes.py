"""Verplaats of herschaal vormen op een slide, op naam, in inch.

Usage:
    python place_shapes.py <slide.xml> --file boxes.json
    python place_shapes.py <slide.xml> --json '{"Kaart 2*": {"dx": -2.1}}'
    python place_shapes.py <slide.xml> --json '{"Kaart 1*": {"w": 6.14}}' --list

De JSON is `{doel: aanpassing}`. Een doel is een vormnaam zoals `inspect_deck.py` en
`retext_slide.py --list` hem rapporteren, eventueel met een `*` aan het eind:
`"Kaart 2*"` raakt `Kaart 2`, `Kaart 2 label`, `Kaart 2 getal` en `Kaart 2 toelichting`
in één keer. Dat is de eenheid waarin een kaart beweegt.

Een aanpassing is een object met wat je wilt zetten of verschuiven, alles in inch:

    {"x": 4.75}              linkerkant absoluut
    {"y": 1.93, "h": 2.3}    bovenkant en hoogte absoluut
    {"dx": -2.13}            verschuiven ten opzichte van waar de vorm nu staat
    {"dy": -0.4, "dw": 1.2}  verschuiven én meerekken

`x/y/w/h` zetten, `dx/dy/dw/dh` verschuiven. Beide voor dezelfde as in één aanpassing is
een fout, want dan is de uitkomst een kwestie van volgorde.

Waarom dit bestaat
------------------
De snelste route naar een nieuwe slide in de stijl van de deck is een bestaande slide
dupliceren en opnieuw vullen. Zodra de nieuwe inhoud een ander AANTAL elementen heeft dan
het voorbeeld — twee kaarten waar er drie stonden — is hertekstueren niet genoeg: de derde
kaart verdwijnt en laat een gat aan de rechterkant achter. Dat gat is precies het soort
defect dat op de render als "halfleeg" terugkomt.

Met dit script herverdeel je de rij in één aanroep: de kaarten breder maken en de tweede
opschuiven. Het rekenwerk blijft bij de aanroeper, want dat is één regel: bij n kaarten
over de contentbreedte van 12.52 in met 0.28 in tussenruimte is de breedte
`(12.52 - 0.28 * (n - 1)) / n` en staat kaart i op `0.48 + i * (breedte + 0.28)`.

Groepen worden doorlopen, maar let op: verplaats je een vorm BINNEN een `<p:grpSp>`, dan
werkt PowerPoint met de kindcoördinaten van die groep en niet met de slidecoördinaten. Het
script meldt dat per geraakte vorm met `in_group: true`, zodat je een groep als geheel
verplaatst in plaats van zijn kinderen los.

Er wordt niets aan de tekst gedaan — dat is `retext_slide.py`. Output is compacte JSON met
de oude en de nieuwe doos per vorm, zodat de wijziging na te rekenen is zonder de XML te
openen.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from lxml import etree

from _deck import EMU_PER_INCH, emit
from set_text import A, NS, P

AXES = {
    "x": ("off", "x", "dx"),
    "y": ("off", "y", "dy"),
    "w": ("ext", "cx", "dw"),
    "h": ("ext", "cy", "dh"),
}


def shape_name(sp: etree._Element) -> str:
    node = sp.find(".//p:nvSpPr/p:cNvPr", NS)
    if node is None:
        node = sp.find(".//p:cNvPr", NS)
    return (node.get("name") if node is not None else "") or ""


def matches(name: str, pattern: str) -> bool:
    if pattern.endswith("*"):
        return name.startswith(pattern[:-1])
    return name == pattern


def xfrm_of(sp: etree._Element) -> etree._Element:
    """De `<a:xfrm>` van de vorm, aangemaakt als hij nog geërfd werd.

    Een placeholder heeft normaal géén eigen xfrm: positie en maat komen uit de layout, en
    dat hoort zo. Wie er hier toch een op zet, bevriest die maat op de slide. Daarom
    gebeurt dat alleen wanneer de aanroeper de vorm expliciet noemt.
    """
    sp_pr = sp.find("./p:spPr", NS)
    if sp_pr is None:
        raise SystemExit(f"vorm zonder spPr: {shape_name(sp)!r}")
    xfrm = sp_pr.find("a:xfrm", NS)
    if xfrm is None:
        # a:xfrm is het eerste kind van CT_ShapeProperties, vóór de geometrie.
        xfrm = etree.Element(f"{{{A}}}xfrm")
        sp_pr.insert(0, xfrm)
    return xfrm


def read_box(xfrm: etree._Element) -> dict[str, float | None]:
    box: dict[str, float | None] = {}
    off = xfrm.find("a:off", NS)
    ext = xfrm.find("a:ext", NS)
    box["x"] = int(off.get("x")) / EMU_PER_INCH if off is not None else None
    box["y"] = int(off.get("y")) / EMU_PER_INCH if off is not None else None
    box["w"] = int(ext.get("cx")) / EMU_PER_INCH if ext is not None else None
    box["h"] = int(ext.get("cy")) / EMU_PER_INCH if ext is not None else None
    return box


def write_box(xfrm: etree._Element, box: dict[str, float | None]) -> None:
    off = xfrm.find("a:off", NS)
    if off is None:
        off = etree.SubElement(xfrm, f"{{{A}}}off")
    ext = xfrm.find("a:ext", NS)
    if ext is None:
        ext = etree.SubElement(xfrm, f"{{{A}}}ext")
    off.set("x", str(int(round((box["x"] or 0) * EMU_PER_INCH))))
    off.set("y", str(int(round((box["y"] or 0) * EMU_PER_INCH))))
    ext.set("cx", str(int(round((box["w"] or 0) * EMU_PER_INCH))))
    ext.set("cy", str(int(round((box["h"] or 0) * EMU_PER_INCH))))


def apply(box: dict[str, float | None], change: dict, name: str) -> dict[str, float | None]:
    unknown = set(change) - set(AXES) - {"dx", "dy", "dw", "dh"}
    if unknown:
        raise SystemExit(
            f"onbekende sleutel(s) {sorted(unknown)} voor {name!r} — gebruik "
            "x/y/w/h (zetten) of dx/dy/dw/dh (verschuiven)"
        )
    new = dict(box)
    for axis, (_kind, _attr, delta_key) in AXES.items():
        absolute = change.get(axis)
        delta = change.get(delta_key)
        if absolute is not None and delta is not None:
            raise SystemExit(
                f"{name!r}: geef {axis} of {delta_key}, niet beide — de uitkomst zou van "
                "de volgorde afhangen"
            )
        if absolute is not None:
            new[axis] = float(absolute)
        elif delta is not None:
            if box[axis] is None:
                raise SystemExit(
                    f"{name!r} heeft geen eigen {axis} (die wordt geërfd), dus "
                    f"{delta_key} heeft niets om vanaf te rekenen. Zet {axis} absoluut."
                )
            new[axis] = box[axis] + float(delta)
    return new


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("slide", type=Path)
    parser.add_argument("--json", dest="payload", help="JSON-object met de aanpassingen")
    parser.add_argument("--file", type=Path, help="lees het JSON-object uit een bestand")
    parser.add_argument(
        "--list",
        action="store_true",
        help="alleen de vormen met hun huidige doos tonen; niets schrijven",
    )
    args = parser.parse_args()

    if not args.slide.exists():
        raise SystemExit(f"{args.slide} niet gevonden")

    tree = etree.parse(str(args.slide))
    sp_tree = tree.getroot().find(".//p:cSld/p:spTree", NS)
    every = [
        node
        for node in sp_tree.iter()
        if node.tag in {f"{{{P}}}sp", f"{{{P}}}grpSp", f"{{{P}}}pic", f"{{{P}}}graphicFrame"}
    ]

    if args.list:
        listed = []
        for node in every:
            # Geen `or`: een leeg `<p:spPr/>` is falsy in lxml, dus dan viel dit door naar
            # grpSpPr en werd None. Dat gaf toevallig het juiste antwoord ("geërfd"), met
            # een FutureWarning erbij, en zou stilletjes fout gaan zodra lxml zijn
            # truth-testing verandert.
            sp_pr = node.find("./p:spPr", NS)
            if sp_pr is None:
                sp_pr = node.find("./p:grpSpPr", NS)
            xfrm = sp_pr.find("a:xfrm", NS) if sp_pr is not None else None
            if xfrm is None:
                xfrm = node.find("./p:xfrm", NS)
            box = read_box(xfrm) if xfrm is not None else {}
            listed.append({"name": shape_name(node), "box": box or "geërfd"})
        emit({"slide": args.slide.name, "shapes": listed})
        return

    if not args.payload and not args.file:
        raise SystemExit("geef --json, --file of --list")

    raw = args.file.read_text(encoding="utf-8") if args.file else args.payload
    changes: dict[str, dict] = json.loads(raw)

    moved = []
    hit: set[str] = set()
    for node in every:
        name = shape_name(node)
        for pattern, change in changes.items():
            if not matches(name, pattern):
                continue
            hit.add(pattern)
            xfrm = xfrm_of(node) if node.tag == f"{{{P}}}sp" else node.find(".//a:xfrm", NS)
            if xfrm is None:
                raise SystemExit(
                    f"{name!r} heeft geen xfrm die dit script kan zetten (groep, plaatje "
                    "of grafiekframe zonder eigen transform)"
                )
            before = read_box(xfrm)
            after = apply(before, change, name)
            write_box(xfrm, after)
            in_group = any(
                parent.tag == f"{{{P}}}grpSp" for parent in node.iterancestors()
            )
            moved.append(
                {
                    "name": name,
                    "from": {key: round(value, 2) if value is not None else None for key, value in before.items()},
                    "to": {key: round(value, 2) if value is not None else None for key, value in after.items()},
                    **({"in_group": True} if in_group else {}),
                }
            )
            break

    missing = sorted(set(changes) - hit)
    if missing:
        available = ", ".join(repr(shape_name(node)) for node in every)
        raise SystemExit(
            f"niet gevonden op {args.slide.name}: {', '.join(missing)}. "
            f"Op deze slide staan: {available}. Niets geschreven."
        )

    tree.write(str(args.slide), xml_declaration=True, encoding="UTF-8", standalone=True)
    emit({"slide": args.slide.name, "moved": moved})


if __name__ == "__main__":
    main()
