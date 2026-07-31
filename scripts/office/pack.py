"""Pack a directory into a DOCX, PPTX, or XLSX file.

Validates with auto-repair, condenses XML formatting, and creates the Office file.

Usage:
    python pack.py <input_directory> <output_file> [--original <file>] [--validate true|false]

Examples:
    python pack.py unpacked/ output.docx --original input.docx
    python pack.py unpacked/ output.pptx --validate false
"""

import argparse
import sys
import shutil
import tempfile
import zipfile
from pathlib import Path

import defusedxml.minidom

from validators import DOCXSchemaValidator, PPTXSchemaValidator, RedliningValidator

TEMPLATE_CONTENT_TYPE = "presentationml.template.main"


def pack(
    input_directory: str,
    output_file: str,
    original_file: str | None = None,
    validate: bool = True,
    infer_author_func=None,
) -> tuple[bool, str]:
    """Pack an unpacked tree into an Office file. Returns (ok, message).

    Returns an explicit boolean rather than letting the caller look for "Error" in the
    message: an output path that merely CONTAINED the substring "Error" used to exit 1
    on a perfectly successful pack.
    """
    input_dir = Path(input_directory)
    output_path = Path(output_file)
    suffix = output_path.suffix.lower()

    if not input_dir.is_dir():
        return False, f"Error: {input_dir} is not a directory"

    if suffix not in {".docx", ".pptx", ".xlsx"}:
        return False, f"Error: {output_file} must be a .docx, .pptx, or .xlsx file"

    # A .potx unpacked directly with unpack.py still declares the TEMPLATE content type.
    # Packing that to .pptx yields a zip python-pptx refuses with a bare "is not a
    # PowerPoint file, content type is ...". prepare_template.py fixes the content type;
    # this catches the path that skipped it, while the answer is still cheap.
    if suffix == ".pptx":
        content_types = input_dir / "[Content_Types].xml"
        if content_types.exists():
            declared = content_types.read_bytes().decode("utf-8", errors="replace")
            if TEMPLATE_CONTENT_TYPE in declared:
                return False, (
                    f"Error: {input_dir} still declares the .potx template content "
                    "type, so the packed .pptx will not open — run "
                    "prepare_template.py first (it rewrites [Content_Types].xml), or "
                    "pack to a .potx"
                )

    if validate:
        # Deliberately NOT gated on original_file. With the documented default
        # --validate true and no --original, this used to validate nothing at all while
        # still printing "Successfully packed"; every caller in the plugin omits
        # --original. base.py handles original_file=None, so a baseline-free structural
        # validation is exactly what we want as the floor.
        original_path = Path(original_file) if original_file else None
        if original_path is not None and not original_path.exists():
            original_path = None
        success, output = _run_validation(
            input_dir, original_path, suffix, infer_author_func
        )
        if output:
            print(output)
        if not success:
            return False, f"Error: Validation failed for {input_dir}"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_content_dir = Path(temp_dir) / "content"
        shutil.copytree(input_dir, temp_content_dir)

        for pattern in ["*.xml", "*.rels"]:
            for xml_file in temp_content_dir.rglob(pattern):
                _condense_xml(xml_file)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in temp_content_dir.rglob("*"):
                if f.is_file():
                    zf.write(f, f.relative_to(temp_content_dir))

    return True, f"Successfully packed {input_dir} to {output_file}"


def _run_validation(
    unpacked_dir: Path,
    original_file: Path | None,
    suffix: str,
    infer_author_func=None,
) -> tuple[bool, str | None]:
    output_lines = []
    validators = []

    if suffix == ".docx":
        author = "Claude"
        if infer_author_func:
            try:
                author = infer_author_func(unpacked_dir, original_file)
            except ValueError as e:
                print(f"Warning: {e} Using default author 'Claude'.", file=sys.stderr)

        validators = [
            DOCXSchemaValidator(unpacked_dir, original_file),
            RedliningValidator(unpacked_dir, original_file, author=author),
        ]
    elif suffix == ".pptx":
        validators = [PPTXSchemaValidator(unpacked_dir, original_file)]

    if not validators:
        return True, None

    total_repairs = sum(v.repair() for v in validators)
    if total_repairs:
        output_lines.append(f"Auto-repaired {total_repairs} issue(s)")

    success = all(v.validate() for v in validators)

    if success:
        output_lines.append("All validations PASSED!")

    return success, "\n".join(output_lines) if output_lines else None


def _condense_xml(xml_file: Path) -> None:
    try:
        with open(xml_file, encoding="utf-8") as f:
            dom = defusedxml.minidom.parse(f)

        for element in dom.getElementsByTagName("*"):
            if element.tagName.endswith(":t"):
                continue

            for child in list(element.childNodes):
                if (
                    child.nodeType == child.TEXT_NODE
                    and child.nodeValue
                    and child.nodeValue.strip() == ""
                ) or child.nodeType == child.COMMENT_NODE:
                    element.removeChild(child)

        # standalone="yes" to match what every other writer in the toolchain emits
        # (lxml's tree.write(..., standalone=True) and PowerPoint itself);
        # dom.toxml(encoding=...) alone drops it, so packing silently rewrote the
        # declaration of every part it touched.
        body = dom.toxml(encoding="UTF-8")
        body = body.replace(
            b'<?xml version="1.0" encoding="UTF-8"?>',
            b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            1,
        )
        xml_file.write_bytes(body)
    except Exception as e:
        print(f"ERROR: Failed to parse {xml_file.name}: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    # The Windows console is cp1252 and mangles the em dashes in these messages.
    # scripts/_deck.py does this for the toolkit; office/ does not import it.
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError, ValueError):
            pass

    parser = argparse.ArgumentParser(
        description="Pack a directory into a DOCX, PPTX, or XLSX file"
    )
    parser.add_argument("input_directory", help="Unpacked Office document directory")
    parser.add_argument("output_file", help="Output Office file (.docx/.pptx/.xlsx)")
    parser.add_argument(
        "--original",
        help="Original file for validation comparison",
    )
    parser.add_argument(
        "--validate",
        type=lambda x: x.lower() == "true",
        default=True,
        metavar="true|false",
        help="Run validation with auto-repair (default: true)",
    )
    args = parser.parse_args()

    ok, message = pack(
        args.input_directory,
        args.output_file,
        original_file=args.original,
        validate=args.validate,
    )
    print(message)

    if not ok:
        sys.exit(1)
