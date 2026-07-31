"""Build a labelled contact sheet of a deck, so the visual loop can be staged.

Usage:
    python thumbnail.py <deck.pptx | renders_dir> <output_prefix> [--cols N]

The prefix is REQUIRED — the sheet is a working artefact you will make several of per
deck, and a default name silently overwrites the previous round.

Two inputs, because this project renders two ways:

    python thumbnail.py deck.pptx raster-v1
    python thumbnail.py build/renders/v1 raster-v1     <- a directory of PNGs

A DIRECTORY is the normal case here: render.py drives PowerPoint COM and writes
slide_01.png, slide_02.png, ... and those are the font-accurate renders. Passing the
.pptx instead makes this script call LibreOffice itself, which substitutes Gotham,
Montserrat and Lato — fine for composition, not for fit. Prefer the directory when you
already rendered.

Why bother: reviewing a 20-slide deck slide by slide burns a lot of context. Read the
sheet first, and open only the slides that look wrong at full size. Labels carry the
slide's XML file name so a finding maps straight onto the file to edit.

Hidden slides get a crossed-out placeholder rather than being skipped, so the numbering
in the sheet cannot drift from the numbering in the deck.
"""

from __future__ import annotations

import argparse
import posixpath
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import defusedxml.minidom
from defusedxml import ElementTree
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent / "office"))

from _deck import emit  # noqa: E402

THUMBNAIL_WIDTH = 300
CONVERSION_DPI = 100
MAX_COLS = 6
DEFAULT_COLS = 3
JPEG_QUALITY = 95
GRID_PADDING = 20
BORDER_WIDTH = 2
FONT_SIZE_RATIO = 0.10
LABEL_PADDING_RATIO = 0.4

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}


def _natural_key(path: Path):
    """Sort slide_2.png before slide_10.png."""
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", path.name)
    ]


def images_from_directory(source: Path) -> list[tuple[Path, str]]:
    """Existing renders, labelled by the slide number in the file name."""
    files = sorted(
        (p for p in source.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES),
        key=_natural_key,
    )
    if not files:
        raise RuntimeError(f"geen PNG/JPG gevonden in {source}")

    slides = []
    for index, path in enumerate(files, start=1):
        digits = "".join(ch for ch in path.stem if ch.isdigit())
        number = int(digits) if digits else index
        slides.append((path, f"slide{number}.xml"))
    return slides


def _is_hidden(zf: zipfile.ZipFile, part: str) -> bool:
    try:
        with zf.open(part) as f:
            for _, root in ElementTree.iterparse(f, events=("start",)):
                return root.get("show") in ("0", "false")
    except (KeyError, ElementTree.ParseError):
        return False
    return False


def get_slide_info(pptx_path: Path) -> list[dict]:
    from helpers import SLIDE_REL_TYPE, opc_target

    with zipfile.ZipFile(pptx_path, "r") as zf:
        rels_content = zf.read("ppt/_rels/presentation.xml.rels").decode("utf-8")
        rels_dom = defusedxml.minidom.parseString(rels_content)

        rid_to_part = {}
        for rel in rels_dom.getElementsByTagName("Relationship"):
            if rel.getAttribute("Type") != SLIDE_REL_TYPE:
                continue
            part = opc_target(
                rel.getAttribute("Target"),
                "ppt/presentation.xml",
                rel.getAttribute("TargetMode"),
            )
            if part is not None:
                rid_to_part[rel.getAttribute("Id")] = part

        pres_dom = defusedxml.minidom.parseString(
            zf.read("ppt/presentation.xml").decode("utf-8")
        )
        present = set(zf.namelist())

        slides = []
        for sld_id in pres_dom.getElementsByTagName("p:sldId"):
            part = rid_to_part.get(sld_id.getAttribute("r:id"))
            if part is not None and part in present:
                slides.append(
                    {"name": posixpath.basename(part), "hidden": _is_hidden(zf, part)}
                )
        return slides


def convert_to_images(pptx_path: Path, temp_dir: Path) -> list[Path]:
    """pptx -> pdf -> jpg via LibreOffice, through the soffice wrapper."""
    from soffice import run_soffice

    pdf_path = temp_dir / f"{pptx_path.stem}.pdf"
    result = run_soffice(
        ["--headless", "--convert-to", "pdf", "--outdir", str(temp_dir), str(pptx_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not pdf_path.exists():
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"pdf-conversie mislukte: {detail}" if detail else "pdf-conversie mislukte")

    # Same ladder as render.py, for the same reason: pdftoppm is not everywhere.
    import shutil

    tool = next(
        (t for t in ("pdftoppm", "pdftocairo", "mutool") if shutil.which(t)), None
    )
    if tool is None:
        raise RuntimeError(
            "geen pdf->png-omzetter gevonden — installeer poppler-utils of mupdf-tools, "
            "of render eerst met render.py en geef die map als invoer"
        )

    if tool == "mutool":
        command = ["mutool", "draw", "-r", str(CONVERSION_DPI),
                   "-o", str(temp_dir / "slide-%d.png"), str(pdf_path)]
    else:
        command = [tool, "-jpeg", "-r", str(CONVERSION_DPI),
                   str(pdf_path), str(temp_dir / "slide")]

    result = subprocess.run(command, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"beeldconversie mislukte met {tool}")

    found = sorted(
        (p for p in temp_dir.glob("slide-*") if p.suffix.lower() in IMAGE_SUFFIXES),
        key=_natural_key,
    )
    return found


def build_slide_list(
    slide_info: list[dict], visible_images: list[Path], temp_dir: Path
) -> list[tuple[Path, str]]:
    visible_count = sum(1 for info in slide_info if not info["hidden"])
    rendered_hidden = len(visible_images) == len(slide_info) != visible_count

    if not rendered_hidden and visible_count != len(visible_images):
        raise ValueError(
            f"de renderer leverde {len(visible_images)} pagina('s) voor "
            f"{visible_count} zichtbare slide(s) van {len(slide_info)}; de labels "
            "zouden dan niet meer kloppen"
        )

    if visible_images:
        with Image.open(visible_images[0]) as img:
            placeholder_size = img.size
    else:
        placeholder_size = (1920, 1080)

    slides: list[tuple[Path, str]] = []
    visible_idx = 0
    for info in slide_info:
        if info["hidden"] and not rendered_hidden:
            placeholder_path = temp_dir / f"hidden-{info['name']}.jpg"
            create_hidden_placeholder(placeholder_size).save(placeholder_path, "JPEG")
            slides.append((placeholder_path, f"{info['name']} (verborgen)"))
        else:
            label = f"{info['name']} (verborgen)" if info["hidden"] else info["name"]
            slides.append((visible_images[visible_idx], label))
            visible_idx += 1
    return slides


def create_hidden_placeholder(size: tuple[int, int]) -> Image.Image:
    img = Image.new("RGB", size, color="#F0F0F0")
    draw = ImageDraw.Draw(img)
    line_width = max(5, min(size) // 100)
    draw.line([(0, 0), size], fill="#CCCCCC", width=line_width)
    draw.line([(size[0], 0), (0, size[1])], fill="#CCCCCC", width=line_width)
    return img


def create_grid(slides: list[tuple[Path, str]], cols: int, width: int) -> Image.Image:
    font_size = int(width * FONT_SIZE_RATIO)
    label_padding = int(font_size * LABEL_PADDING_RATIO)

    with Image.open(slides[0][0]) as img:
        aspect = img.height / img.width
    height = int(width * aspect)

    rows = (len(slides) + cols - 1) // cols
    grid_w = cols * width + (cols + 1) * GRID_PADDING
    grid_h = rows * (height + font_size + label_padding * 2) + (rows + 1) * GRID_PADDING

    grid = Image.new("RGB", (grid_w, grid_h), "white")
    draw = ImageDraw.Draw(grid)

    try:
        font = ImageFont.load_default(size=font_size)
    except Exception:
        font = ImageFont.load_default()

    for i, (img_path, slide_name) in enumerate(slides):
        row, col = i // cols, i % cols
        x = col * width + (col + 1) * GRID_PADDING
        y_base = row * (height + font_size + label_padding * 2) + (row + 1) * GRID_PADDING

        bbox = draw.textbbox((0, 0), slide_name, font=font)
        text_w = bbox[2] - bbox[0]
        draw.text(
            (x + (width - text_w) // 2, y_base + label_padding),
            slide_name,
            fill="black",
            font=font,
        )

        y_thumbnail = y_base + label_padding + font_size + label_padding
        with Image.open(img_path) as img:
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
            w, h = img.size
            tx = x + (width - w) // 2
            ty = y_thumbnail + (height - h) // 2
            grid.paste(img, (tx, ty))
            if BORDER_WIDTH > 0:
                draw.rectangle(
                    [
                        (tx - BORDER_WIDTH, ty - BORDER_WIDTH),
                        (tx + w + BORDER_WIDTH - 1, ty + h + BORDER_WIDTH - 1),
                    ],
                    outline="gray",
                    width=BORDER_WIDTH,
                )
    return grid


def create_grids(
    slides: list[tuple[Path, str]], cols: int, width: int, output_path: Path
) -> list[str]:
    max_per_grid = cols * (cols + 1)
    grid_files = []

    for chunk_idx, start_idx in enumerate(range(0, len(slides), max_per_grid)):
        chunk = slides[start_idx : start_idx + max_per_grid]
        grid = create_grid(chunk, cols, width)

        if len(slides) <= max_per_grid:
            grid_filename = output_path
        else:
            grid_filename = (
                output_path.parent
                / f"{output_path.stem}-{chunk_idx + 1}{output_path.suffix}"
            )

        grid_filename.parent.mkdir(parents=True, exist_ok=True)
        grid.save(str(grid_filename), quality=JPEG_QUALITY)
        grid_files.append(str(grid_filename))

    return grid_files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="deck.pptx, or a directory of rendered PNGs")
    parser.add_argument(
        "output_prefix",
        help="output prefix, without extension (required, so rounds do not overwrite)",
    )
    parser.add_argument(
        "--cols",
        type=int,
        default=DEFAULT_COLS,
        help=f"columns (default {DEFAULT_COLS}, max {MAX_COLS})",
    )
    args = parser.parse_args()

    cols = min(args.cols, MAX_COLS)
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"{input_path} bestaat niet")

    output_path = Path(f"{args.output_prefix}.jpg")

    if input_path.is_dir():
        slides = images_from_directory(input_path)
        source = "renders"
        grid_files = create_grids(slides, cols, THUMBNAIL_WIDTH, output_path)
    else:
        if input_path.suffix.lower() not in {".pptx", ".potx"}:
            raise SystemExit(f"geen .pptx en geen map: {input_path}")
        slide_info = get_slide_info(input_path)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            visible_images = convert_to_images(input_path, temp_path)
            if not visible_images and not any(s["hidden"] for s in slide_info):
                raise SystemExit("geen slides gevonden")
            slides = build_slide_list(slide_info, visible_images, temp_path)
            source = "libreoffice"
            grid_files = create_grids(slides, cols, THUMBNAIL_WIDTH, output_path)

    emit(
        {
            "input": str(input_path),
            "source": source,
            "fonts_substituted": source == "libreoffice",
            "slides": len(slides),
            "cols": cols,
            "sheets": grid_files,
        }
    )


if __name__ == "__main__":
    main()
