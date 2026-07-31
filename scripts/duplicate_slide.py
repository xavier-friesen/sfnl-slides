"""Duplicate an existing slide, with all the package bookkeeping done.

Usage:
    python duplicate_slide.py <unpacked_dir | deck.pptx> slide2.xml
    python duplicate_slide.py unpacked/ slide2.xml --after slide2.xml
    python duplicate_slide.py deck.pptx slide2.xml -o out.pptx

Vendored from the official Anthropic pptx skill (snapshot in
`vendor/pptx-official-2026-07-29/`, where it is `add_slide.py`). Renamed here because
our own `add_slide.py` does something different: it INSTANTIATES A LAYOUT, with the
placeholder shapes, `--only`, `--bare` and the {{MARKER}} scaffolding. Use that one to
start a new slide. Use this one only to copy a slide that already exists.

    new slide from a layout        -> add_slide.py unpacked/ slideLayout19.xml
    copy of an existing slide      -> duplicate_slide.py unpacked/ slide4.xml

What it takes care of, so the deck stays openable:
  - writes ppt/slides/slideN.xml and its .rels, MINUS any notesSlide reference, so the
    copy does not share the source's speaker notes
  - registers the part in [Content_Types].xml
  - adds a slide relationship with a fresh rId to presentation.xml.rels
  - inserts <p:sldId> with a fresh id into <p:sldIdLst>, at the end or after --after

Works on an unpacked directory (during a build) or straight on a .pptx/.potx, which is
extracted to a temp dir and rezipped atomically. In that case the temp dir is discarded,
so unpack the output again if you still need to edit the new slide.

CAVEAT — CHARTS AND SMARTART ARE SHARED, NOT COPIED. A duplicated slide REFERENCES the
same chart, diagram, OLE or embedded package part as its source. Editing the chart on
the copy therefore also changes the original, and deleting one slide can strip the part
from under the other. The tool reports which shared parts it saw in `shared_parts`. When
the copy needs its own chart: delete the copy's chart shape and add a fresh one with
add_chart.py (which writes a new chart part), rather than editing the shared one.

The copy still holds the source's TEXT as well — that is the point — so edit
ppt/slides/slideN.xml (reported in the output) to change it.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import NoReturn

sys.path.insert(0, str(Path(__file__).resolve().parent / "office"))

from _deck import emit  # noqa: E402

SHARED_PART_TYPES = ("chart", "diagramData", "oleObject", "package")

NOTES_SLIDE_TYPE_RE = re.compile(r"""Type=["'][^"']*/relationships/notesSlide["']""")
RELATIONSHIP_RE = re.compile(
    r"<Relationship\b[^>]*?(?:/>|>.*?</Relationship\s*>)", re.DOTALL
)

SLIDE_ID_MIN = 256
SLIDE_ID_MAX = 2147483647


def _die(msg: str) -> NoReturn:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def get_next_slide_number(slides_dir: Path) -> int:
    existing = [
        int(m.group(1))
        for f in slides_dir.glob("slide*.xml")
        if (m := re.match(r"slide(\d+)\.xml", f.name))
    ]
    return max(existing) + 1 if existing else 1


def duplicate_slide(
    unpacked_dir: Path, source: str, after: str | None = None
) -> tuple[str, list[str], int, int]:
    slides_dir = unpacked_dir / "ppt" / "slides"
    rels_dir = slides_dir / "_rels"
    source_slide = slides_dir / source

    if not source_slide.exists():
        _die(f"{source_slide} not found")

    next_num = get_next_slide_number(slides_dir)
    dest = f"slide{next_num}.xml"
    after_rid = _precheck_registration(unpacked_dir, after, dest)

    shutil.copy2(source_slide, slides_dir / dest)

    source_rels = rels_dir / f"{source}.rels"
    shared_parts: list[str] = []
    if source_rels.exists():
        dest_rels = rels_dir / f"{dest}.rels"
        shutil.copy2(source_rels, dest_rels)
        rels_content = dest_rels.read_text(encoding="utf-8")
        rels_content = RELATIONSHIP_RE.sub(
            lambda m: "" if NOTES_SLIDE_TYPE_RE.search(m.group(0)) else m.group(0),
            rels_content,
        )
        dest_rels.write_text(rels_content, encoding="utf-8")
        shared_parts = sorted(
            {
                t
                for t in re.findall(r'Type="[^"]*/relationships/(\w+)"', rels_content)
                if t in SHARED_PART_TYPES
            }
        )

    position, total = _register_slide(unpacked_dir, dest, after_rid)
    return dest, shared_parts, position, total


def _precheck_registration(
    unpacked_dir: Path, after: str | None, dest: str
) -> str | None:
    pres_path = unpacked_dir / "ppt" / "presentation.xml"
    if not pres_path.exists():
        _die(f"{pres_path} not found — is this an unpacked PPTX?")
    xml = pres_path.read_text(encoding="utf-8")

    has_slot = (
        "</p:sldIdLst>" in xml
        or re.search(r"<p:sldIdLst\s*/>", xml)
        or "</p:sldMasterIdLst>" in xml
    )
    if not has_slot:
        _die(
            "presentation.xml has no <p:sldIdLst> (or <p:sldMasterIdLst> to anchor a new one)"
        )

    stale = []
    content_types = unpacked_dir / "[Content_Types].xml"
    if (
        content_types.exists()
        and f'PartName="/ppt/slides/{dest}"'
        in content_types.read_text(encoding="utf-8")
    ):
        stale.append("[Content_Types].xml")
    pres_rels = unpacked_dir / "ppt" / "_rels" / "presentation.xml.rels"
    if pres_rels.exists() and _find_slide_relationship(
        pres_rels.read_text(encoding="utf-8"), dest
    ):
        stale.append("presentation.xml.rels")
    if stale:
        _die(
            f"{dest} is still registered in {' and '.join(stale)} but absent from "
            f"ppt/slides/ — run clean.py first"
        )

    if not after:
        return None
    after_rid = _rid_for_slide(unpacked_dir, after)
    if not re.search(rf'<p:sldId\b[^>]*r:id="{re.escape(after_rid)}"[^>]*>', xml):
        _die(f"{after} ({after_rid}) is not listed in <p:sldIdLst>")
    return after_rid


def _register_slide(
    unpacked_dir: Path, dest: str, after_rid: str | None
) -> tuple[int, int]:
    _add_to_content_types(unpacked_dir, dest)
    rid = _add_to_presentation_rels(unpacked_dir, dest)
    slide_id = _get_next_slide_id(unpacked_dir)
    return _insert_into_sld_id_lst(unpacked_dir, slide_id, rid, after_rid)


def _add_to_content_types(unpacked_dir: Path, dest: str) -> None:
    content_types_path = unpacked_dir / "[Content_Types].xml"
    content_types = content_types_path.read_text(encoding="utf-8")

    new_override = (
        f'<Override PartName="/ppt/slides/{dest}" '
        'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
    )
    if f'PartName="/ppt/slides/{dest}"' not in content_types:
        content_types = content_types.replace("</Types>", f"  {new_override}\n</Types>")
        content_types_path.write_text(content_types, encoding="utf-8")


def _add_to_presentation_rels(unpacked_dir: Path, dest: str) -> str:
    pres_rels_path = unpacked_dir / "ppt" / "_rels" / "presentation.xml.rels"
    pres_rels = pres_rels_path.read_text(encoding="utf-8")

    existing = _find_slide_relationship(pres_rels, dest)
    if existing:
        return existing

    pres_xml = (unpacked_dir / "ppt" / "presentation.xml").read_text(encoding="utf-8")
    used = {int(n) for n in re.findall(r'\bId="rId(\d+)"', pres_rels)}
    used |= {int(n) for n in re.findall(r'\br:id="rId(\d+)"', pres_xml)}
    rid = f"rId{max(used) + 1 if used else 1}"

    new_rel = (
        f'<Relationship Id="{rid}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" '
        f'Target="slides/{dest}"/>'
    )
    pres_rels = pres_rels.replace("</Relationships>", f"  {new_rel}\n</Relationships>")
    pres_rels_path.write_text(pres_rels, encoding="utf-8")
    return rid


def _find_slide_relationship(pres_rels: str, slide_name: str) -> str | None:
    for m in re.finditer(r"<Relationship\b[^>]*>", pres_rels):
        element = m.group(0)
        if re.search(rf'Target="(?:/ppt/)?slides/{re.escape(slide_name)}"', element):
            id_match = re.search(r'\bId="([^"]+)"', element)
            if id_match:
                return id_match.group(1)
    return None


def _get_next_slide_id(unpacked_dir: Path) -> int:
    pres_content = (unpacked_dir / "ppt" / "presentation.xml").read_text(
        encoding="utf-8"
    )
    used = {int(m) for m in re.findall(r'<p:sldId[^>]*\bid="(\d+)"', pres_content)}

    candidate = (
        max((i for i in used if i >= SLIDE_ID_MIN), default=SLIDE_ID_MIN - 1) + 1
    )
    if candidate <= SLIDE_ID_MAX and candidate not in used:
        return candidate
    for i in range(SLIDE_ID_MIN, SLIDE_ID_MAX + 1):
        if i not in used:
            return i
    _die("no slide id available in [256, 2147483647] — the deck is full")


def _insert_into_sld_id_lst(
    unpacked_dir: Path, slide_id: int, rid: str, after_rid: str | None = None
) -> tuple[int, int]:
    pres_path = unpacked_dir / "ppt" / "presentation.xml"
    xml = pres_path.read_text(encoding="utf-8")
    entry = f'<p:sldId id="{slide_id}" r:id="{rid}"/>'

    if f'r:id="{rid}"' in xml:
        _die(f"presentation.xml already references {rid}; refusing to add a duplicate")

    if after_rid:
        open_tag = re.search(
            rf'<p:sldId\b[^>]*r:id="{re.escape(after_rid)}"[^>]*>', xml
        )
        if not open_tag:
            _die(f"{after_rid} is not listed in <p:sldIdLst>")
        end = open_tag.end()
        if not open_tag.group(0).endswith("/>"):
            close = xml.find("</p:sldId>", end)
            if close == -1:
                _die(f"unclosed <p:sldId> for {after_rid} in presentation.xml")
            end = close + len("</p:sldId>")
        xml = xml[:end] + entry + xml[end:]
    elif "</p:sldIdLst>" in xml:
        xml = xml.replace("</p:sldIdLst>", f"{entry}</p:sldIdLst>", 1)
    elif re.search(r"<p:sldIdLst\s*/>", xml):
        xml = re.sub(
            r"<p:sldIdLst\s*/>", f"<p:sldIdLst>{entry}</p:sldIdLst>", xml, count=1
        )
    elif "</p:sldMasterIdLst>" in xml:
        xml = xml.replace(
            "</p:sldMasterIdLst>",
            f"</p:sldMasterIdLst><p:sldIdLst>{entry}</p:sldIdLst>",
            1,
        )
    else:
        _die("presentation.xml has no <p:sldIdLst>")

    pres_path.write_text(xml, encoding="utf-8")

    lst = re.search(r"<p:sldIdLst>(.*)</p:sldIdLst>", xml, re.DOTALL)
    entries = re.findall(r"<p:sldId\b[^>]*>", lst.group(1)) if lst else []
    position = next(
        (i for i, e in enumerate(entries, 1) if f'r:id="{rid}"' in e), len(entries)
    )
    return position, len(entries)


def _rid_for_slide(unpacked_dir: Path, slide_name: str) -> str:
    pres_rels_path = unpacked_dir / "ppt" / "_rels" / "presentation.xml.rels"
    rid = _find_slide_relationship(
        pres_rels_path.read_text(encoding="utf-8"), slide_name
    )
    if not rid:
        _die(f"{slide_name} has no relationship in presentation.xml.rels")
    return rid


def duplicate_in_package(
    package: Path, source: str, after: str | None, output: Path | None
) -> dict:
    from helpers import rezip, safe_extract

    out = output or package
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(package) as zf:
            safe_extract(zf, tmp_path)
        dest, shared, position, total = duplicate_slide(tmp_path, source, after)
        rezip(tmp_path, out)
    return {
        "deck": str(out),
        "slide": dest,
        "position": position,
        "of": total,
        "shared_parts": shared,
        "note": f"unpack {out} opnieuw om de inhoud van {dest} te bewerken",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="unpacked PPTX directory OR a .pptx/.potx file")
    parser.add_argument(
        "source",
        help="slideN.xml to duplicate. For a NEW slide from a layout use add_slide.py.",
    )
    parser.add_argument(
        "--after",
        metavar="SLIDE",
        help="insert after this slide, e.g. slide2.xml (default: append)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="output file (.pptx/.potx target only; default: rewrite in place)",
    )
    args = parser.parse_args()

    if args.source.startswith("slideLayout"):
        _die(
            f"{args.source} is a layout. duplicate_slide.py copies an EXISTING slide; "
            "to start a new slide from a layout use: add_slide.py <unpacked> "
            f"{args.source}"
        )

    target = Path(args.target)
    if target.is_dir():
        if args.output:
            parser.error(
                "--output is only valid for a .pptx/.potx target; a directory is "
                "modified in place"
            )
        dest, shared, position, total = duplicate_slide(
            target, args.source, args.after
        )
        payload = {
            "unpacked": str(target),
            "slide": dest,
            "path": str(target / "ppt" / "slides" / dest),
            "position": position,
            "of": total,
            "shared_parts": shared,
        }
    elif target.is_file() and target.suffix.lower() in (".pptx", ".potx"):
        try:
            payload = duplicate_in_package(
                target,
                args.source,
                args.after,
                Path(args.output) if args.output else None,
            )
        except (OSError, ValueError, zipfile.BadZipFile) as e:
            _die(str(e))
    else:
        _die(f"{target} is neither a directory nor a .pptx/.potx file")

    if payload.get("shared_parts"):
        payload["warning"] = (
            f"deelt {', '.join(payload['shared_parts'])}-part(s) met {args.source} — "
            "die zijn gerefereerd, niet gekopieerd; bewerk je ze, dan verandert ook de "
            "bronslide. Geef de kopie een eigen grafiek via add_chart.py."
        )
    emit(payload)


if __name__ == "__main__":
    main()
