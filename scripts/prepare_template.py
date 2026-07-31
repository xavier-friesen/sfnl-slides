"""Turn the SFNL .potx template into a working .pptx build directory.

Usage:
    python prepare_template.py <build_dir> [--template <path.potx>] [--keep-slides]

What it does:
  1. Unpacks the template into <build_dir>/unpacked/
  2. Rewrites the template content type to the presentation content type
     (without this, python-pptx and PowerPoint treat the result as a template)
  3. Drops the placeholder slide the template ships with, so the deck starts empty
  4. Drops `ppt/authors.xml`, an unschema'd extension part that trips validate.py
  5. Prints a compact JSON summary

The content-type fix is not optional. A .potx carries
`presentationml.template.main+xml` in [Content_Types].xml, and renaming the file
does not change it. PowerPoint then opens the deck in template mode and
python-pptx refuses the file outright.

**Windows: houd de builddir kort.** De uitgepakte boom gaat 53 tekens diep
(`unpacked/ppt/slideLayouts/_rels/slideLayout30.xml.rels`), dus boven een builddir van
ongeveer 200 tekens loopt het uitpakken tegen MAX_PATH aan. Dit script rekent dat vóóraf
na en zegt het met zoveel woorden in plaats van te stoppen op `[Errno 2] No such file or
directory`, waar niemand padlengte in leest. Een korte map (`C:/w/deck`) en het
eindbestand daarna op zijn plek zetten is de route.

Examples:
    python prepare_template.py build/
    python prepare_template.py build/ --template ../assets/sfnl-sjabloon.potx
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

from _deck import emit

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_TEMPLATE = SCRIPT_DIR.parent / "assets" / "sfnl-sjabloon.potx"

TEMPLATE_CT = "presentationml.template.main"
PRESENTATION_CT = "presentationml.presentation.main"

# Het langste pad dat in de uitgepakte boom voorkomt, geteld vanaf de builddir:
#   unpacked/ppt/slideLayouts/_rels/slideLayout30.xml.rels
LONGEST_INNER_PATH = len("unpacked/ppt/slideLayouts/_rels/slideLayout30.xml.rels")

# Windows MAX_PATH. Zonder de long-path-optie (en die staat zelden aan) faalt elke
# bestandsoperatie boven 260 tekens, met `[Errno 2] No such file or directory` — een
# melding die nergens zegt dat het om padlengte gaat. Er is één marge bijgeteld voor
# `template.pptx` en de tijdelijke bestanden.
MAX_PATH = 260


def check_path_budget(build_dir: Path) -> str | None:
    """Waarschuwing (of None) over de padlengte van deze builddir op Windows.

    Dit is een echte blokkade, geen theorie: `output/<YYYY-MM-DD>-<slug>/` — precies wat
    SKILL.md voorschrijft — kwam vanuit een werkmap van 186 tekens uit op 265 tekens voor
    `unpacked/ppt/slideLayouts/_rels/slideLayout4.xml.rels`, en het uitpakken stopte
    zonder één woord over padlengte.
    """
    if sys.platform != "win32":
        return None
    root = str(build_dir.resolve())
    if len(root) + 1 + LONGEST_INNER_PATH <= MAX_PATH:
        return None
    room = MAX_PATH - 1 - LONGEST_INNER_PATH
    return (
        f"de builddir is {len(root)} tekens ({root}); op Windows past daar de uitgepakte "
        f"boom niet in — `unpacked/ppt/slideLayouts/_rels/slideLayout30.xml.rels` komt "
        f"boven MAX_PATH ({MAX_PATH}) uit en het uitpakken faalt met een melding die "
        f"niets over padlengte zegt. Kies een pad van maximaal {room} tekens: een korte "
        "map dicht bij de wortel (bijvoorbeeld C:/w/deck of <scratchpad>/d) en zet het "
        "eindbestand daarna op zijn plek."
    )


def unpack(template: Path, unpacked: Path) -> None:
    """Unpack via the vendored office toolchain, on a .pptx copy of the template.

    The copy is needed because office/unpack.py only accepts .docx/.pptx/.xlsx, and it
    is deleted again afterwards: it is 5,5 MB, and leaving it behind put a stray
    template.pptx next to deck.pptx in every single build directory.
    """
    staged = unpacked.parent / "template.pptx"
    staged.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(template, staged)

    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "office" / "unpack.py"), str(staged), str(unpacked)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            sys.stderr.write(result.stdout + result.stderr)
            hint = ""
            if sys.platform == "win32" and (
                "No such file or directory" in (result.stdout + result.stderr)
                or "Errno 2" in (result.stdout + result.stderr)
            ):
                hint = (
                    " — dit is op Windows bijna altijd de padlengte: de uitgepakte boom "
                    f"gaat {LONGEST_INNER_PATH} tekens diep en de builddir is "
                    f"{len(str(unpacked.parent.resolve()))} tekens. Kies een kortere "
                    "werkmap."
                )
            raise SystemExit(f"unpack failed for {template}{hint}")
    finally:
        staged.unlink(missing_ok=True)


def fix_content_type(unpacked: Path) -> bool:
    """Rewrite the template content type. Returns True when something changed."""
    ct_path = unpacked / "[Content_Types].xml"
    text = ct_path.read_text(encoding="utf-8")
    if TEMPLATE_CT not in text:
        return False
    ct_path.write_text(text.replace(TEMPLATE_CT, PRESENTATION_CT), encoding="utf-8")
    return True


def verify_content_type(unpacked: Path) -> None:
    text = (unpacked / "[Content_Types].xml").read_text(encoding="utf-8")
    if TEMPLATE_CT in text:
        raise SystemExit("content type still says template.main — fix before packing")


def strip_slides(unpacked: Path) -> list[str]:
    """Remove every slide the template ships with, leaving masters and layouts intact."""
    pres_path = unpacked / "ppt" / "presentation.xml"
    pres = pres_path.read_text(encoding="utf-8")
    pres = re.sub(r"<p:sldIdLst>.*?</p:sldIdLst>", "<p:sldIdLst/>", pres, flags=re.DOTALL)
    pres = pres.replace("<p:sldIdLst></p:sldIdLst>", "<p:sldIdLst/>")
    pres_path.write_text(pres, encoding="utf-8")

    slides_dir = unpacked / "ppt" / "slides"
    before = (
        {slide.name for slide in slides_dir.glob("slide*.xml")}
        if slides_dir.exists()
        else set()
    )

    clean = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "clean.py"), str(unpacked)],
        capture_output=True,
        text=True,
    )
    if clean.returncode != 0:
        sys.stderr.write(clean.stdout + clean.stderr)
        raise SystemExit("clean.py failed while stripping template slides")

    # Report what clean.py actually removed, by comparing before and after. Listing the
    # glob from before the subprocess reported files as dropped whether or not they were.
    after = (
        {slide.name for slide in slides_dir.glob("slide*.xml")}
        if slides_dir.exists()
        else set()
    )
    return sorted(before - after)


def drop_comment_authors(unpacked: Path) -> bool:
    """Remove `ppt/authors.xml`, with its relationship and content-type override.

    It is a Microsoft 2018 extension part with no ISO-29500 schema, so `validate.py`
    reports it on every deck we build. It only holds the comment authors the template
    happened to ship with, and PowerPoint writes a fresh one the moment someone adds a
    comment — so dropping it costs nothing and keeps validation clean.
    """
    authors = unpacked / "ppt" / "authors.xml"
    if not authors.exists():
        return False
    authors.unlink()

    rels_path = unpacked / "ppt" / "_rels" / "presentation.xml.rels"
    rels = rels_path.read_text(encoding="utf-8")
    rels_path.write_text(
        re.sub(r"<Relationship[^>]*Target=\"authors\.xml\"[^>]*/>", "", rels),
        encoding="utf-8",
    )

    ct_path = unpacked / "[Content_Types].xml"
    types = ct_path.read_text(encoding="utf-8")
    ct_path.write_text(
        re.sub(r"<Override[^>]*PartName=\"/ppt/authors\.xml\"[^>]*/>", "", types),
        encoding="utf-8",
    )
    return True


def count_layouts(unpacked: Path) -> tuple[int, int]:
    masters = len(list((unpacked / "ppt" / "slideMasters").glob("slideMaster*.xml")))
    layouts = len(list((unpacked / "ppt" / "slideLayouts").glob("slideLayout*.xml")))
    return masters, layouts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build_dir", type=Path, help="directory to prepare (created if absent)")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument(
        "--keep-slides",
        action="store_true",
        help="keep the placeholder slide(s) the template ships with",
    )
    args = parser.parse_args()

    template: Path = args.template
    if not template.exists():
        raise SystemExit(f"template not found: {template}")

    build_dir: Path = args.build_dir
    too_long = check_path_budget(build_dir)
    if too_long:
        raise SystemExit(f"padlengte: {too_long}")

    unpacked = build_dir / "unpacked"
    if unpacked.exists():
        shutil.rmtree(unpacked)

    unpack(template, unpacked)
    changed = fix_content_type(unpacked)
    verify_content_type(unpacked)
    dropped = [] if args.keep_slides else strip_slides(unpacked)
    authors_dropped = drop_comment_authors(unpacked)
    masters, layouts = count_layouts(unpacked)

    emit(
        {
            "unpacked": str(unpacked),
            "template": str(template),
            "content_type_fixed": changed,
            "slides_dropped": dropped,
            "authors_dropped": authors_dropped,
            "masters": masters,
            "layouts": layouts,
        }
    )


if __name__ == "__main__":
    main()
