"""Add a slide to an unpacked PPTX, built on one of the template layouts.

Usage:
    python add_slide.py <unpacked_dir> slideLayout20.xml
    python add_slide.py <unpacked_dir> slideLayout20.xml --only 0,1,10
    python add_slide.py <unpacked_dir> slideLayout21.xml --at 3
    python add_slide.py <unpacked_dir> slide2.xml            # duplicate a slide
    python add_slide.py <unpacked_dir> slideLayout17.xml --bare
    python add_slide.py <unpacked_dir> slideLayout4.xml --only 10 --no-page-number

`--no-page-number` haalt het paginanummer van de COVERLAYOUT: de cover draagt anders een
"1" terwijl een titelslide niet meetelt. Het paginanummer van dit sjabloon is geen
placeholder maar een getekend tekstvak met een `slidenum`-veld in de master, dus het gaat
via `showMasterSp="0"` op de layout — dat haalt alleen mastervormen weg, en op master 1 is
dat precies dat nummervak (foto, logo en dash zitten in de layout en blijven staan). Op
master 2 zit het logo óók in de master; daar weigert het script, met uitleg. En let op: de
onderdrukking geldt voor elke slide op die layout in dit deck, wat voor een cover de
bedoeling is.

Layout-first: the slide inherits title, subtitle, orange dash, logo and page number
from the master and the layout. None of that is drawn on the slide itself.

By default the new slide gets an empty placeholder shape for every text placeholder
the layout offers, with the right `type`/`idx` and autofit already off, so only the
`<a:t>` text has to be filled in. De JSON noemt per idx de ROL (`role`) en de marker
draagt diezelfde naam — `{{DEKTITEL}}`, `{{HOOFDSTUK}}`, `{{SUBREGEL}}`, `{{LIJST}}` —
in plaats van een nummer. Een `{{TEKST-14}}` op een divider zei niet welke van de twee
regels je vulde; daarvoor moest je terug naar `layouts.md`. Position and size stay unset, which means they are
inherited from the layout — that is the point. Placeholders you do not fill must be
deleted from the slide.

The slide is registered in `[Content_Types].xml`, `presentation.xml.rels` and
`<p:sldIdLst>` right away. Output is compact JSON.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

from lxml import etree

from _deck import (
    AGENDA_LAYOUTS,
    COVER_LAYOUTS,
    DIVIDER_LAYOUTS,
    EMU_PER_INCH,
    emit,
)

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"a": A, "p": P, "r": R}

# Placeholders that carry content. Date, page number and footer come from the master.
TEXT_PH_TYPES = {None, "title", "ctrTitle", "subTitle", "body", "obj"}
SKIP_PH_TYPES = {"dt", "sldNum", "ftr", "hdr", "pic", "chart", "tbl", "dgm", "media", "clipArt"}

SLIDE_SHELL = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
{shapes}    </p:spTree>
  </p:cSld>
  <p:clrMapOvr>
    <a:masterClrMapping/>
  </p:clrMapOvr>
</p:sld>
"""

PH_SHAPE = """      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="{shape_id}" name="{name}"/>
          <p:cNvSpPr>
            <a:spLocks noGrp="1"/>
          </p:cNvSpPr>
          <p:nvPr>
            <p:ph {ph_attrs}/>
          </p:nvPr>
        </p:nvSpPr>
        <p:spPr/>
        <p:txBody>
          <a:bodyPr>
            <a:noAutofit/>
          </a:bodyPr>
          <a:lstStyle/>
          <a:p>
            <a:r>
              <a:rPr lang="nl-NL" dirty="0"/>
              <a:t>{marker}</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>
"""


def layout_number(layout_file: str) -> int | None:
    match = re.search(r"slideLayout(\d+)\.xml", layout_file)
    return int(match.group(1)) if match else None


# Rol per (layoutfamilie, idx). Dezelfde feiten als de Rol-kolom in `layouts.md`, hier
# in het kort: de JSON van dit script gaf tot nu toe idx, type, marker, layout_name en
# box_in — genoeg om de kolommen niet te verwisselen, maar niet om te weten WAT er in
# idx 13 hoort. Daarvoor moest de agent terug naar layouts.md. Nu staat het erbij, en de
# marker draagt dezelfde naam, zodat een half gevulde slide zichzelf uitlegt.
def placeholder_role(number: int | None, ph_type: str, idx: int) -> tuple[str, str]:
    """(rol, markernaam) voor deze placeholder."""
    if ph_type in {"title", "ctrTitle"}:
        return "titel — de bewering van de slide, ALL CAPS", "TITEL"
    if number in COVER_LAYOUTS:
        if idx == 10:
            return (
                "dektitel van het deck — ALL CAPS, ÉÉN regel (het vak is 0.63 in hoog; "
                "een tweede regel valt over de datumregel). Past het niet: layout 1",
                "DEKTITEL",
            )
        if idx == 14:
            return (
                "dektitel van het deck — ALL CAPS, één regel binnen het budget uit "
                "layouts.md",
                "DEKTITEL",
            )
        if idx == 13:
            return (
                "klant en datum — nooit de organisatienaam als kop",
                "KLANT-EN-DATUM",
            )
    if number in DIVIDER_LAYOUTS:
        if idx == 14:
            return "kopregel — hoofdstuknummer en -naam", "HOOFDSTUK"
        if idx == 13:
            return "ondersteunende regel onder de kop (optioneel)", "SUBREGEL"
        if idx == 11:
            return "hoofdstukoverzicht naast de foto (optioneel)", "OVERZICHT"
    if number in AGENDA_LAYOUTS and idx == 11:
        return "de opsomming zelf — één alinea per punt", "LIJST"
    if idx == 1:
        return (
            "subtitel — één leidende zin, alleen in modus B (anders droppen)",
            "SUBTITEL",
        )
    return "contentzone — zelf componeren of tekst per alinea", f"TEKST-{idx}"


def master_of(layout_path: Path) -> Path | None:
    rels = layout_path.parent / "_rels" / f"{layout_path.name}.rels"
    if not rels.exists():
        return None
    for rel in etree.parse(str(rels)).getroot():
        target = rel.get("Target", "")
        if "slideMasters/" in target:
            return (layout_path.parent.parent / target.replace("../", "")).resolve()
    return None


def _own_shapes(root) -> list:
    """Vormen in een spTree zonder `<p:ph>` — de getekende chrome, niet de placeholders."""
    tree = root.find(".//p:cSld/p:spTree", NS)
    if tree is None:
        return []
    found = []
    for child in tree:
        tag = etree.QName(child).localname
        if tag in {"nvGrpSpPr", "grpSpPr"}:
            continue
        if child.find(".//p:nvPr/p:ph", NS) is not None:
            continue
        found.append(child)
    return found


def _is_slide_number_field(shape) -> bool:
    return any(
        fld.get("type") == "slidenum" for fld in shape.iter(f"{{{A}}}fld")
    )


def suppress_page_number(unpacked_dir: Path, layout_file: str) -> tuple[bool, str | None]:
    """Zet `showMasterSp="0"` op de LAYOUT, zodat het paginanummer eraf gaat.

    Waarom zo, en waarom niet anders — dit is geverifieerd op een echte render:

    * Het paginanummer van dit sjabloon is GEEN sldNum-placeholder maar een gewoon
      tekstvak in de master met een `<a:fld type="slidenum">` erin (`userDrawn="1"`).
      `<p:hf sldNum="0"/>` staat er al op master 1 en doet dus niets, en een eigen
      sldNum-placeholder op de slide kan niets overschrijven wat niet bestaat.
    * `showMasterSp="0"` op de SLIDE haalt behalve het nummer ook alle vormen van de
      layout weg — op een cover dus de foto én het logo. Gemeten: fotoinkt 466560 -> 0.
    * `showMasterSp="0"` op de LAYOUT haalt alleen de mastervormen weg. Op master 1 is
      dat precies dat ene nummervak; foto en logo zitten in de layout zelf en blijven
      staan. Gemeten: nummerinkt 0, logo 3291, foto 466560, en de andere slides houden
      hun nummer.

    Daarom weigert dit alleen wanneer de master méér getekende vormen heeft dan het
    nummer — dat is master 2, waar ook het logo in de master zit.

    Let op: dit geldt voor ELKE slide op die layout in dit deck. Voor een coverlayout is
    dat de bedoeling (er is één cover); op een contentlayout is het dat niet.
    """
    layout_path = unpacked_dir / "ppt" / "slideLayouts" / layout_file
    master_path = master_of(layout_path)
    if master_path is None or not master_path.exists():
        return False, f"geen master gevonden bij {layout_file}"

    master_root = etree.parse(str(master_path)).getroot()
    extra = [s for s in _own_shapes(master_root) if not _is_slide_number_field(s)]
    if extra:
        names = ", ".join(
            (s.find(".//p:cNvPr", NS).get("name") if s.find(".//p:cNvPr", NS) is not None else "?")
            for s in extra
        )
        return False, (
            f"{master_path.name} draagt naast het paginanummer ook {names} — die zou je "
            "hiermee ook weghalen. Onderdruk het nummer alleen op de master-1-layouts "
            "(covers, quote, dividers), waar de master niets anders draagt dan het "
            "nummer."
        )

    tree = etree.parse(str(layout_path))
    root = tree.getroot()
    if root.get("showMasterSp") == "0":
        return True, None
    root.set("showMasterSp", "0")
    tree.write(str(layout_path), xml_declaration=True, encoding="UTF-8", standalone=True)
    return True, None


def get_next_slide_number(slides_dir: Path) -> int:
    existing = [
        int(m.group(1))
        for f in slides_dir.glob("slide*.xml")
        if (m := re.match(r"slide(\d+)\.xml", f.name))
    ]
    return max(existing) + 1 if existing else 1


def layout_placeholders(layout_path: Path) -> list[dict]:
    """Read the layout's text placeholders, sorted the way the slide reads.

    Sorted by GEOMETRY (top, then left), not by idx. idx order is not reading order:
    on layout 22 idx 12 is the RIGHT column head and idx 13 the LEFT one, while idx 14
    is the LEFT body and 15 the RIGHT — so "12 and 14 are the left pair" is exactly
    backwards, and an idx sort put the left column's heading on the right. Each entry
    carries `box_in` so the caller can see which column an idx belongs to instead of
    having to guess.
    """
    tree = etree.parse(str(layout_path))
    found = []
    for sp in tree.getroot().iter(f"{{{P}}}sp"):
        ph = sp.find(".//p:nvSpPr/p:nvPr/p:ph", NS)
        if ph is None:
            continue
        ph_type = ph.get("type")
        if ph_type in SKIP_PH_TYPES or ph_type not in TEXT_PH_TYPES:
            continue
        idx = ph.get("idx")
        cnv = sp.find(".//p:nvSpPr/p:cNvPr", NS)
        off = sp.find(".//a:xfrm/a:off", NS)
        ext = sp.find(".//a:xfrm/a:ext", NS)
        left = int(off.get("x")) if off is not None else None
        top = int(off.get("y")) if off is not None else None
        width = int(ext.get("cx")) if ext is not None else None
        height = int(ext.get("cy")) if ext is not None else None
        found.append(
            {
                "type": ph_type or "obj",
                "idx": int(idx) if idx is not None else 0,
                "layout_name": cnv.get("name", "") if cnv is not None else "",
                "box_in": (
                    [round(v / EMU_PER_INCH, 2) for v in (left, top, width, height)]
                    if None not in (left, top, width, height)
                    else None
                ),
                "_top": top,
                "_left": left,
            }
        )
    # Title first, then top to bottom, then left to right. Rounded to 0.01 in so two
    # boxes on the same visual row sort by their left edge rather than by a stray EMU.
    found.sort(
        key=lambda p: (
            0 if p["type"] in {"title", "ctrTitle"} else 1,
            round((p["_top"] or 0) / EMU_PER_INCH, 2),
            round((p["_left"] or 0) / EMU_PER_INCH, 2),
        )
    )
    for entry in found:
        entry.pop("_top", None)
        entry.pop("_left", None)
    return found


def build_placeholder_shapes(placeholders: list[dict], number: int | None) -> str:
    shapes = []
    for offset, ph in enumerate(placeholders):
        attrs = []
        if ph["type"] != "obj":
            attrs.append(f'type="{ph["type"]}"')
        if ph["idx"]:
            attrs.append(f'idx="{ph["idx"]}"')
        label = {"title": "Title", "ctrTitle": "Title", "subTitle": "Subtitle"}.get(
            ph["type"], "Placeholder"
        )
        role, marker_name = placeholder_role(number, ph["type"], ph["idx"])
        if ph["idx"] == 1:
            # In this template the body placeholder at idx 1 is the subtitle line.
            label = "Subtitle"
        marker = f"{{{{{marker_name}}}}}"
        ph["marker"] = marker
        ph["role"] = role
        shapes.append(
            PH_SHAPE.format(
                shape_id=2 + offset,
                name=f"{label} {ph['idx']}",
                ph_attrs=" ".join(attrs) or 'idx="1"',
                marker=marker,
            )
        )
    return "".join(shapes)


def create_slide_from_layout(
    unpacked_dir: Path,
    layout_file: str,
    only: set[int] | None,
    bare: bool,
    no_page_number: bool = False,
) -> tuple[str, list[dict], bool]:
    slides_dir = unpacked_dir / "ppt" / "slides"
    rels_dir = slides_dir / "_rels"
    layout_path = unpacked_dir / "ppt" / "slideLayouts" / layout_file

    if not layout_path.exists():
        raise SystemExit(f"{layout_path} not found")

    slides_dir.mkdir(parents=True, exist_ok=True)
    rels_dir.mkdir(parents=True, exist_ok=True)

    placeholders = [] if bare else layout_placeholders(layout_path)
    if only is not None:
        placeholders = [p for p in placeholders if p["idx"] in only]

    shapes_xml = build_placeholder_shapes(placeholders, layout_number(layout_file))

    suppressed: bool | str = False
    if no_page_number:
        ok, reason = suppress_page_number(unpacked_dir, layout_file)
        if not ok:
            raise SystemExit(f"--no-page-number kan hier niet: {reason}")
        suppressed = True

    dest = f"slide{get_next_slide_number(slides_dir)}.xml"
    (slides_dir / dest).write_text(
        SLIDE_SHELL.format(shapes=shapes_xml),
        encoding="utf-8",
    )
    (rels_dir / f"{dest}.rels").write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        f'  <Relationship Id="rId1" Type="{R}/slideLayout" '
        f'Target="../slideLayouts/{layout_file}"/>\n'
        "</Relationships>\n",
        encoding="utf-8",
    )
    return dest, placeholders, suppressed


def duplicate_slide(unpacked_dir: Path, source: str) -> str:
    slides_dir = unpacked_dir / "ppt" / "slides"
    rels_dir = slides_dir / "_rels"
    source_slide = slides_dir / source

    if not source_slide.exists():
        raise SystemExit(f"{source_slide} not found")

    dest = f"slide{get_next_slide_number(slides_dir)}.xml"
    shutil.copy2(source_slide, slides_dir / dest)

    source_rels = rels_dir / f"{source}.rels"
    if source_rels.exists():
        dest_rels = rels_dir / f"{dest}.rels"
        shutil.copy2(source_rels, dest_rels)
        # A duplicated slide must not point at the original's notes slide.
        content = dest_rels.read_text(encoding="utf-8")
        content = re.sub(r'\s*<Relationship[^>]*Type="[^"]*notesSlide"[^>]*/>\s*', "\n", content)
        dest_rels.write_text(content, encoding="utf-8")

    return dest


def _add_to_content_types(unpacked_dir: Path, dest: str) -> None:
    path = unpacked_dir / "[Content_Types].xml"
    content = path.read_text(encoding="utf-8")
    if f"/ppt/slides/{dest}" in content:
        return
    override = (
        f'<Override PartName="/ppt/slides/{dest}" '
        'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
    )
    path.write_text(content.replace("</Types>", f"  {override}\n</Types>"), encoding="utf-8")


def _add_to_presentation_rels(unpacked_dir: Path, dest: str) -> str:
    path = unpacked_dir / "ppt" / "_rels" / "presentation.xml.rels"
    content = path.read_text(encoding="utf-8")
    existing = re.search(rf'Id="(rId\d+)"[^>]*Target="slides/{dest}"', content)
    if existing:
        return existing.group(1)

    rids = [int(m) for m in re.findall(r'Id="rId(\d+)"', content)]
    rid = f"rId{max(rids) + 1 if rids else 1}"
    rel = f'<Relationship Id="{rid}" Type="{R}/slide" Target="slides/{dest}"/>'
    path.write_text(
        content.replace("</Relationships>", f"  {rel}\n</Relationships>"), encoding="utf-8"
    )
    return rid


def _register_in_sldidlst(unpacked_dir: Path, rid: str, at: int | None) -> int:
    """Insert the slide in the slide list. `at` is 1-based; None appends."""
    path = unpacked_dir / "ppt" / "presentation.xml"
    tree = etree.parse(str(path))
    root = tree.getroot()

    lst = root.find("p:sldIdLst", NS)
    if lst is None:
        lst = etree.Element(f"{{{P}}}sldIdLst")
        size = root.find("p:sldSz", NS)
        root.insert(list(root).index(size) if size is not None else 0, lst)

    ids = [int(node.get("id")) for node in lst]
    node = etree.Element(f"{{{P}}}sldId")
    node.set("id", str(max(ids) + 1 if ids else 256))
    node.set(f"{{{R}}}id", rid)

    if at is None or at > len(lst):
        lst.append(node)
        position = len(lst)
    else:
        lst.insert(max(at - 1, 0), node)
        position = max(at, 1)

    tree.write(str(path), xml_declaration=True, encoding="UTF-8", standalone=True)
    return position


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("unpacked_dir", type=Path)
    parser.add_argument("source", help="slideLayoutN.xml to build on, or slideN.xml to duplicate")
    parser.add_argument("--at", type=int, help="1-based position in the deck (default: append)")
    parser.add_argument("--only", help="comma-separated placeholder idx list to emit")
    parser.add_argument(
        "--bare", action="store_true", help="no placeholder shapes at all (custom composition)"
    )
    parser.add_argument(
        "--no-page-number",
        action="store_true",
        help="onderdruk het geërfde paginanummer op deze slide (voor de cover)",
    )
    args = parser.parse_args()

    if not args.unpacked_dir.exists():
        raise SystemExit(f"{args.unpacked_dir} not found")

    only = None
    if args.only:
        only = {int(part) for part in args.only.replace(" ", "").split(",") if part}

    page_number_suppressed = False
    if args.source.startswith("slideLayout") and args.source.endswith(".xml"):
        dest, placeholders, page_number_suppressed = create_slide_from_layout(
            args.unpacked_dir, args.source, only, args.bare, args.no_page_number
        )
    else:
        dest = duplicate_slide(args.unpacked_dir, args.source)
        placeholders = []

    _add_to_content_types(args.unpacked_dir, dest)
    rid = _add_to_presentation_rels(args.unpacked_dir, dest)
    position = _register_in_sldidlst(args.unpacked_dir, rid, args.at)

    emit(
        {
            "slide": dest,
            "path": str(args.unpacked_dir / "ppt" / "slides" / dest),
            "source": args.source,
            "position": position,
            "page_number_suppressed": page_number_suppressed,
            "placeholders": [
                {
                    "idx": p["idx"],
                    "type": p["type"],
                    # Wat er in deze placeholder hoort. Zelfde feiten als de Rol-kolom in
                    # layouts.md, zodat het vullen niet langs dat bestand hoeft.
                    "role": p.get("role"),
                    "marker": p.get("marker"),
                    "layout_name": p["layout_name"],
                    # x, y, w, h in inches, from the layout. Listed in reading order
                    # (top, then left), which is NOT idx order on layouts 21/22.
                    "box_in": p.get("box_in"),
                }
                for p in placeholders
            ],
            "note": "vervang elke {{MARKER}} door tekst; verwijder placeholders die je niet vult",
        }
    )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(__doc__)
        sys.exit(1)
    main()
