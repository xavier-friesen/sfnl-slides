"""Validate Office document XML against the ISO-29500 XSD schemas.

Usage:
    python validate.py <path> [--original <file>] [--auto-repair] [--author NAME]

`path` can be:
- an unpacked directory (the usual case mid-build), or
- a packed file (.docx/.pptx/.xlsx, or a .dotx/.potx/.xltx template), unpacked to a
  temporary directory first.

`--original <template>` is the one flag to remember. It baselines the run against the
file you started from: an XSD error that the ORIGINAL already has is not a build error,
so it is reported as pre-existing instead of counted against you. The SFNL template is
a large hand-made .potx and it carries a handful of such quirks. Always pass it when
validating a deck built on the template:

    python validate.py build/unpacked --original ../assets/sfnl-sjabloon.potx

Without `--original` every XSD error is reported, which is the right default for
checking a deck in isolation but noisy on a template-derived deck.

Templates are accepted for `--original` (.potx maps to the pptx family), which is why
the SFNL .potx can be used as the baseline directly, without renaming it first.

Auto-repair fixes:
- paraId/durableId values that exceed OOXML limits
- Missing xml:space="preserve" on w:t elements with whitespace (Word only; DrawingML's
  <a:t> must NOT carry it — see set_text.py)

What this checks beyond the schema: relationships resolve, [Content_Types].xml declares
every part AND every Override points at a part that exists, and chart parts are
schema-checked. The negative `c:axId`/`c:crossAx` values python-pptx writes are
whitelisted in validators/base.py — they are correct and must not be "repaired".
"""

import argparse
import sys
import tempfile
import zipfile
from pathlib import Path

from helpers import OOXML_FAMILY, rezip, safe_extract
from validators import DOCXSchemaValidator, PPTXSchemaValidator, RedliningValidator


def _fail(message: str):
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(2)


def _family_from_directory(unpacked_dir: Path) -> str | None:
    """Infer the document family from an unpacked tree.

    Needed because a directory has no suffix: deriving the type from
    `(original or path).suffix` meant `validate.py build/unpacked` always died on an
    assertion unless --original was supplied, while the docstring advertised
    directories as valid input.
    """
    if (unpacked_dir / "ppt" / "presentation.xml").is_file():
        return "pptx"
    if (unpacked_dir / "word" / "document.xml").is_file():
        return "docx"
    if (unpacked_dir / "xl" / "workbook.xml").is_file():
        return "xlsx"
    return None


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError, ValueError):
            pass

    parser = argparse.ArgumentParser(description="Validate Office document XML files")
    parser.add_argument(
        "path",
        help="unpacked directory, or a packed .docx/.pptx/.xlsx/.dotx/.potx/.xltx file",
    )
    parser.add_argument(
        "--original",
        default=None,
        help="baseline file; errors it already has are reported as pre-existing, not "
        "as build errors. Pass the .potx when validating a template-derived deck.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")
    parser.add_argument(
        "--auto-repair",
        action="store_true",
        help="repair hex IDs and Word whitespace preservation. Modifies the input in "
        "place; repairs to a packed file are written back to it.",
    )
    parser.add_argument(
        "--author",
        default=None,
        help="turns on the tracked-change check (docx only, requires --original)",
    )
    args = parser.parse_args()

    if args.author is not None and not args.original:
        _fail("--author requires --original")

    path = Path(args.path)
    if not path.exists():
        _fail(f"{path} does not exist")

    original_file = None
    if args.original:
        original_file = Path(args.original)
        if not original_file.is_file():
            _fail(f"{original_file} is not a file")
        if original_file.suffix.lower() not in OOXML_FAMILY:
            _fail(f"{original_file} must be one of: {', '.join(sorted(OOXML_FAMILY))}")

    packed_file = None
    temp_dir_ctx = None
    if path.is_file() and path.suffix.lower() in OOXML_FAMILY:
        packed_file = path
        temp_dir_ctx = tempfile.TemporaryDirectory()
        unpacked_dir = Path(temp_dir_ctx.name)
        try:
            with zipfile.ZipFile(path, "r") as zf:
                safe_extract(zf, unpacked_dir)
        except (zipfile.BadZipFile, ValueError, OSError) as e:
            _fail(f"cannot unpack {path}: {e}")
    else:
        if not path.is_dir():
            _fail(f"{path} is not a directory or Office file")
        unpacked_dir = path

    # Suffix wins when there is one; otherwise sniff the tree. --original does not
    # decide the family of the thing being validated, it only supplies the baseline.
    family = OOXML_FAMILY.get(path.suffix.lower()) if path.is_file() else None
    if family is None:
        family = _family_from_directory(unpacked_dir)
    if family is None and original_file is not None:
        family = OOXML_FAMILY.get(original_file.suffix.lower())
    if family is None:
        _fail(
            f"cannot determine the document type of {path}. Give a packed file, an "
            "unpacked tree containing ppt/presentation.xml, word/document.xml or "
            "xl/workbook.xml, or pass --original."
        )

    if args.author is not None and family != "docx":
        _fail(f"--author only applies to docx files, not {family}")

    match family:
        case "docx":
            validators = [
                DOCXSchemaValidator(unpacked_dir, original_file, verbose=args.verbose),
            ]
            if args.author is not None:
                validators.append(
                    RedliningValidator(
                        unpacked_dir,
                        original_file,
                        verbose=args.verbose,
                        author=args.author,
                    )
                )
        case "pptx":
            validators = [
                PPTXSchemaValidator(unpacked_dir, original_file, verbose=args.verbose),
            ]
        case "xlsx":
            print("No XSD schema validation is performed for xlsx-family files.")
            sys.exit(0)
        case _:
            print(f"Error: validation not supported for {family}")
            sys.exit(1)

    if args.auto_repair:
        total_repairs = sum(v.repair() for v in validators)
        if total_repairs:
            print(f"Auto-repaired {total_repairs} issue(s)")
            if packed_file is not None:
                rezip(unpacked_dir, packed_file)
                print(f"Wrote repaired file to {packed_file}")

    success = all([v.validate() for v in validators])

    if temp_dir_ctx is not None:
        temp_dir_ctx.cleanup()

    if success:
        print("All validations PASSED!")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
