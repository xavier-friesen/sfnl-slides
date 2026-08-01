"""Switch autofit off and size the title placeholder to the chosen title mode.

Usage:
    python fit_title.py <unpacked_dir> --mode a          # titel als volle zin
    python fit_title.py <unpacked_dir> --mode b          # hoofdstuk + subtitel
    python fit_title.py <unpacked_dir> --check           # report only, no writes

Why this exists
---------------
The template puts `<a:normAutofit/>` on the title and subtitle placeholders. Left
alone, PowerPoint silently shrinks a title that does not fit to 22.5pt or 21pt, and
the deck loses its size discipline. So autofit goes off on every text body on the
slide — placeholders and hand-built text boxes alike.

In mode A the title carries the whole message and may run to two lines, so the
placeholder is grown from the layout's single-line height and top-anchored, which
keeps one-line and two-line titles aligned across the deck. In mode B the title is a
chapter name on one line and the layout geometry is left untouched.

Dat groeien gebeurt UITSLUITEND op de contentlayouts 19 t/m 22, dezelfde verzameling
waarop de modus-checks gelden. Eerder groeide het op elke layout met een
titelplaceholder, en dan schoof de titel van een agendaslide (25-30) van 0.55 naar
0.75 in — met zijn onderrand van 2.18 naar 2.38 in, dwars over de ondersteunende regel
op y = 2.20 in. Geen enkele melding wees daarop, want de modus-checks slaan die layouts
juist over. Een layout uitzonderen van de BEVINDINGEN maar niet van de SCHRIJFACTIE is
het slechtste van twee werelden.

The title text is measured with the real Gotham Bold when it is installed, so
`--check` reports the number of lines a title will actually take. Over the maximum
means the title must be written shorter — never a smaller font.

Slide numbers in the output are DECK POSITIONS, the number the reader sees; the file
the finding sits in is reported separately as `file`. The two differ as soon as a slide
was inserted with `add_slide.py --at`.

The mode checks (caps, one-line titles, a filled subtitle in mode A) only apply to the
content layouts 19 t/m 22 — `CONTENT_LAYOUTS` in `_deck.py`, en 18/23/24 horen daar
niet bij want die zijn verboden. Titelslides, sectiedividers, agendaslides, de quote en
het blanco canvas (17, dat helemaal geen titelplaceholder heeft) hebben hun eigen
tekstdiscipline en zijn uitgezonderd — flagging them as mode mixing sends the agent
after a defect that is not there. Autofit gaat wél op élke slide uit: dat is geen
geometrie maar het uitzetten van stil verkleinen.

Output is compact JSON.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from lxml import etree

from _deck import CONTENT_LAYOUTS, deck_positions, emit, find_font_file, font_report

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS = {"a": A, "p": P}

EMU_PER_INCH = 914400
POINTS_PER_INCH = 72

TITLE_PT = 24.0
# PowerPoint's single line spacing is 1.2 x (ascent + descent) of the font itself.
# Gotham Bold measures 0.896 em, so a line is about 1.08 em. Measured from the font
# when it is installed; this is the fallback.
LINE_SPACING_FACTOR = 1.2
FALLBACK_LINE_HEIGHT_EM = 1.08
DEFAULT_MAX_LINES = 2

# slideMaster2's titleStyle sets `<a:lnSpc><a:spcPct val="90000"/></a:lnSpc>`, so a
# title line is 90% of the font's own line height. Without this the grown box is 0.82 in
# where PowerPoint needs 0.75, and the extra 0.07 in eats into the subtitle band.
TITLE_LINE_SPACING_PCT = 0.90

TITLE_PH_TYPES = {"title", "ctrTitle"}

# The mode rules apply to the CONTENT layouts only — 19 (the norm) and 20-22 — which is
# what `CONTENT_LAYOUTS` in _deck.py holds. Everything else is exempt by design:
#
#   1-4    titelslides/covers
#   2-3    the brand outro (no text placeholders at all)
#   5      the quote
#   6-16   sectiedividers (stijl 1, foto)
#   17     the deliberate BLANK CANVAS — it has no title placeholder, so this script
#          must never report a missing title there. A slide that wants a normal title
#          belongs on 19.
#   25-30  agenda/opsomming
#   18/23/24  forbidden (see FORBIDDEN_LAYOUTS); qa_text.py reports the layout itself,
#          and a mode finding on top of that would only bury the real one.
#
# A MISSING or dropped subtitle is NEVER a finding, in either mode: idx 1 is filled only
# when there is genuinely a leading sentence that fits, and in mode B the chapter title
# stays while the subtitle line may simply be absent. Filling it to be consistent is the
# defect, not leaving it out. The only subtitle rule here is the reverse case — a FILLED
# subtitle in mode A, where a two-line title would run over it.
MODE_CHECK_LAYOUTS = CONTENT_LAYOUTS


def find_gotham_bold() -> Path | None:
    """The installed Gotham Bold, or None. Same search as qa_fit.py (see _deck.py)."""
    return find_font_file("Gotham Bold")


class Measurer:
    """Measure title text, with the real font when available."""

    def __init__(self, size_pt: float = TITLE_PT) -> None:
        self.size_pt = size_pt
        self.font = None
        self.font_path = None
        self.line_height_em = FALLBACK_LINE_HEIGHT_EM
        path = find_gotham_bold()
        if path is not None:
            try:
                from PIL import ImageFont

                # Measure at 10x and scale down; TrueType hinting at 24px is coarse.
                self.font = ImageFont.truetype(str(path), int(size_pt * 10))
                self.font_path = path
                ascent, descent = self.font.getmetrics()
                self.line_height_em = (
                    (ascent + descent) / (size_pt * 10) * LINE_SPACING_FACTOR
                )
            except Exception:
                self.font = None

    def width_pt(self, text: str) -> float:
        if self.font is not None:
            return self.font.getlength(text) / 10
        # Fallback: caps in Gotham Bold average ~0.65 em.
        return len(text) * self.size_pt * 0.65

    def lines(self, text: str, usable_pt: float) -> int:
        words = text.split()
        if not words:
            return 1
        count = 1
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if self.width_pt(candidate) <= usable_pt:
                current = candidate
            else:
                count += 1
                current = word
        return count


def placeholder_of(sp: etree._Element) -> tuple[str | None, int | None]:
    ph = sp.find(".//p:nvSpPr/p:nvPr/p:ph", NS)
    if ph is None:
        return None, None
    idx = ph.get("idx")
    return ph.get("type"), int(idx) if idx is not None else None


def text_of(sp: etree._Element) -> str:
    return "".join(t.text or "" for t in sp.findall(".//a:t", NS))


def body_pr(sp: etree._Element) -> etree._Element | None:
    return sp.find("./p:txBody/a:bodyPr", NS)


def set_no_autofit(sp: etree._Element) -> bool:
    bpr = body_pr(sp)
    if bpr is None:
        return False
    changed = False
    for tag in ("normAutofit", "spAutoFit"):
        for node in bpr.findall(f"a:{tag}", NS):
            bpr.remove(node)
            changed = True
    if bpr.find("a:noAutofit", NS) is None:
        # CT_TextBodyProperties orders the autofit choice right after prstTxWarp.
        position = 1 if bpr.find("a:prstTxWarp", NS) is not None else 0
        bpr.insert(position, etree.Element(f"{{{A}}}noAutofit"))
        changed = True
    return changed


def set_anchor_top(sp: etree._Element) -> bool:
    bpr = body_pr(sp)
    if bpr is None:
        return False
    if bpr.get("anchor") == "t":
        return False
    bpr.set("anchor", "t")
    return True


def layout_for(slide_path: Path) -> Path | None:
    rels = slide_path.parent / "_rels" / f"{slide_path.name}.rels"
    if not rels.exists():
        return None
    tree = etree.parse(str(rels))
    for rel in tree.getroot():
        target = rel.get("Target", "")
        if "slideLayouts/" in target:
            return (slide_path.parent.parent / target.replace("../", "")).resolve()
    return None


def layout_number(layout_path: Path | None) -> int | None:
    if layout_path is None:
        return None
    match = re.search(r"slideLayout(\d+)\.xml", layout_path.name)
    return int(match.group(1)) if match else None


def layout_title_box(layout_path: Path | None) -> tuple[int, int, int, int] | None:
    if layout_path is None or not layout_path.exists():
        return None
    tree = etree.parse(str(layout_path))
    for sp in tree.getroot().iter(f"{{{P}}}sp"):
        ph_type, _ = placeholder_of(sp)
        if ph_type not in TITLE_PH_TYPES:
            continue
        off = sp.find("./p:spPr/a:xfrm/a:off", NS)
        ext = sp.find("./p:spPr/a:xfrm/a:ext", NS)
        if off is None or ext is None:
            return None
        return (int(off.get("x")), int(off.get("y")), int(ext.get("cx")), int(ext.get("cy")))
    return None


def set_box(sp: etree._Element, box: tuple[int, int, int, int]) -> bool:
    x, y, cx, cy = box
    sp_pr = sp.find("./p:spPr", NS)
    if sp_pr is None:
        return False
    xfrm = sp_pr.find("a:xfrm", NS)
    if xfrm is None:
        xfrm = etree.Element(f"{{{A}}}xfrm")
        sp_pr.insert(0, xfrm)
    off = xfrm.find("a:off", NS)
    if off is None:
        off = etree.SubElement(xfrm, f"{{{A}}}off")
    ext = xfrm.find("a:ext", NS)
    if ext is None:
        ext = etree.SubElement(xfrm, f"{{{A}}}ext")
    before = (off.get("x"), off.get("y"), ext.get("cx"), ext.get("cy"))
    off.set("x", str(x))
    off.set("y", str(y))
    ext.set("cx", str(cx))
    ext.set("cy", str(cy))
    return before != (str(x), str(y), str(cx), str(cy))


def title_height_emu(lines: int, line_height_em: float) -> int:
    text_pt = lines * TITLE_PT * line_height_em * TITLE_LINE_SPACING_PCT
    insets_pt = 2 * 0.05 * POINTS_PER_INCH  # tIns + bIns, 0.05 in each
    return int((text_pt + insets_pt) / POINTS_PER_INCH * EMU_PER_INCH)


def file_number(path: Path) -> int:
    """The N in slideN.xml. A file number, not a deck position — sort key only."""
    match = re.search(r"slide(\d+)\.xml", path.name)
    return int(match.group(1)) if match else 0


def process(
    unpacked: Path, mode: str, max_lines: int, check_only: bool
) -> dict:
    slides_dir = unpacked / "ppt" / "slides"
    measurer = Measurer()
    positions = deck_positions(unpacked)
    report = []
    problems: list[dict] = []
    changed_files = 0

    def problem(
        slide: int, file_name: str, check: str, message: str, severity: str = "critical"
    ) -> None:
        problems.append(
            {
                "slide": slide,
                "file": file_name,
                "check": check,
                "severity": severity,
                "message": message,
            }
        )

    paths = sorted(slides_dir.glob("slide*.xml"), key=file_number)
    for slide_path in sorted(
        paths, key=lambda p: (positions.get(p.name, 10_000 + file_number(p)))
    ):
        tree = etree.parse(str(slide_path))
        root = tree.getroot()
        position = positions.get(slide_path.name, file_number(slide_path))
        layout_path = layout_for(slide_path)
        number = layout_number(layout_path)
        mode_checked = number in MODE_CHECK_LAYOUTS
        entry: dict = {
            "slide": position,
            "file": slide_path.name,
            "layout": layout_path.name if layout_path else None,
        }
        touched = False

        subtitle_text = ""
        for sp in root.iter(f"{{{P}}}sp"):
            ph_type, idx = placeholder_of(sp)
            # Autofit goes off on every text body, hand-built text boxes included: a
            # <p:sp> without a <p:ph> inherits the layout's autofit just as a
            # placeholder does.
            if not check_only and set_no_autofit(sp):
                touched = True
            if ph_type is None and idx is None:
                continue

            if idx == 1 and ph_type in {"body", "subTitle"}:
                subtitle_text = text_of(sp).strip()

            if ph_type not in TITLE_PH_TYPES:
                continue

            text = text_of(sp).strip()
            box = layout_title_box(layout_path)
            usable_pt = None
            if box is not None:
                usable_pt = box[2] / EMU_PER_INCH * POINTS_PER_INCH - 2 * 0.1 * POINTS_PER_INCH
            lines = measurer.lines(text, usable_pt) if usable_pt else 1

            entry.update(
                {
                    "title": text,
                    "chars": len(text),
                    "lines": lines,
                    "max_lines": max_lines if mode == "a" else 1,
                    "caps": text == text.upper(),
                }
            )
            limit = max_lines if mode == "a" else 1
            if lines > limit:
                problem(
                    position,
                    slide_path.name,
                    "lines",
                    f"titel loopt over {lines} regels, maximaal {limit} — "
                    "schrijf hem korter, verklein het font niet",
                )
            if mode_checked and text and text != text.upper():
                problem(position, slide_path.name, "caps", "titel niet in kapitalen")

            # De groeitak zit op DEZELFDE layoutverzameling als de modus-checks. Op een
            # agendaslide, divider of cover blijft de layoutgeometrie staan; daar zit
            # direct onder de titel een tweede placeholder waar een gegroeide titelbox
            # dwars doorheen loopt (zie de docstring).
            if mode == "a" and box is not None and mode_checked:
                height = title_height_emu(max_lines, measurer.line_height_em)
                grown = (box[0], box[1], box[2], max(box[3], height))
                entry["height_in"] = round(grown[3] / EMU_PER_INCH, 3)
                entry["grown"] = grown[3] > box[3]
                if not check_only:
                    if set_box(sp, grown):
                        touched = True
                    if set_anchor_top(sp):
                        touched = True
            elif box is not None:
                entry["height_in"] = round(box[3] / EMU_PER_INCH, 3)

        if mode_checked:
            # Een subtitel mag in modus A — hij draagt de periode, de afbakening of het
            # scenario (zie de outline-stap in de skill). Wat niet mag is de combinatie
            # die elkaar raakt: een titel van twee regels groeit tot over de subtitel.
            # Een subtitel die nog zijn {{MARKER}} draagt is niet gevuld; clean.py haalt
            # hem weg.
            subtitle_filled = bool(
                subtitle_text and not re.match(r"^\{\{[^{}]+\}\}$", subtitle_text.strip())
            )
            if mode == "a" and subtitle_filled and entry.get("lines", 1) > 1:
                problem(
                    position,
                    slide_path.name,
                    "mode",
                    f"de titel loopt over {entry['lines']} regels en de "
                    f"subtitel-placeholder is gevuld ({subtitle_text!r}) — de gegroeide "
                    "titelbox loopt over de subtitel heen. Schrijf de titel korter of "
                    "haal de subtitel weg.",
                )
            if mode == "b" and entry.get("lines", 1) > 1:
                problem(
                    position,
                    slide_path.name,
                    "mode",
                    "modus B houdt de titel op één regel; deze loopt over "
                    f"{entry['lines']} regels en duwt de subtitel weg",
                )

        if entry.get("title") is not None or touched:
            report.append(entry)
        if touched:
            tree.write(str(slide_path), xml_declaration=True, encoding="UTF-8", standalone=True)
            changed_files += 1

    fonts = font_report(["Gotham Bold"])
    return {
        "mode": mode,
        "font_measured": measurer.font_path.name if measurer.font_path else None,
        # Waarom er niets gemeten kon worden, in dezelfde JSON. `font_measured: null`
        # alleen liet de lezer denken dat de fonts er niet stonden, terwijl het net zo
        # goed een ontbrekende Pillow kan zijn.
        "font_search": fonts,
        "numbering": "slide = deckpositie, file = bestandsnaam",
        "slides_seen": len(report),
        "slides_changed": changed_files,
        "problems": sorted(problems, key=lambda p: (p["slide"], p["check"])),
        "slides": [
            {
                k: v
                for k, v in e.items()
                if k in {"slide", "file", "layout", "title", "lines", "height_in"}
            }
            for e in report
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("unpacked_dir", type=Path)
    parser.add_argument("--mode", choices=["a", "b"], default="a")
    parser.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES)
    parser.add_argument("--check", action="store_true", help="report only, write nothing")
    args = parser.parse_args()

    if not (args.unpacked_dir / "ppt" / "slides").exists():
        raise SystemExit(f"no ppt/slides in {args.unpacked_dir}")

    emit(process(args.unpacked_dir, args.mode, args.max_lines, args.check))


if __name__ == "__main__":
    main()
