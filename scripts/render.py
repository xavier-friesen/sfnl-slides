"""Render slides to PNG with the PowerPoint that is already installed.

Usage:
    python render.py <deck.pptx> <out_dir>
    python render.py <deck.pptx> <out_dir> --slides 1,4,7
    python render.py --check

PowerPoint COM is the preferred renderer: it is the same engine the client will open
the deck in, so Gotham Bold, Montserrat and Lato render exactly as they will look.

Waar PowerPoint niet beschikbaar is (Linux, CI, een sandbox) valt het script terug op
LibreOffice. Die substitueert de huisstijlfonts, dus regelafbrekingen en titelhoogtes
kloppen daar niet op de millimeter. Voor waar het in de visuele loop om gaat is dat
ruim genoeg: overlappende vormen, tekst die buiten zijn kader valt, onleesbaar
contrast, halflege slides en verkeerde kleuren zie je er allemaal in. Blind bouwen is
een veel groter probleem dan een gesubstitueerd font. De JSON-uitvoer meldt met
`renderer` welke van de twee het was, zodat je fontgevoelige bevindingen met een korrel
zout kunt nemen.

Staat er LibreOffice maar geen pdf->png-omzetter, dan stopt het script niet: de
tussen-pdf blijft staan en de JSON meldt `renderer: "libreoffice-pdf"` met het pad in
`pdf`. Een reviewer kan pdf-pagina's lezen; dat is de derde trap van de render-ladder en
een stuk beter dan QA-only. De pdf wordt ook op de PNG-route bewaard (`<out_dir>/
<deck>.pdf`) en hergebruikt zolang hij jonger is dan de deck: `--slides 7` op een deck
van veertig slides kost dan één conversie in plaats van één per aanroep.

If PowerPoint is already running, the existing instance is used and left running
afterwards — quitting it would close whatever the user had open.

Output is compact JSON with the written files, de gebruikte renderer, en de werkelijke
pixelmaat per PNG (afgeleid van het slideformaat uit de deck zelf, niet van een
hardgecodeerde 13.333 x 7.5 in).
"""

from __future__ import annotations

import argparse
import re
import sys
import time
import zipfile
from pathlib import Path

from _deck import emit

# 13.333 x 7.5 in at 144 dpi: small enough to review cheaply, large enough to read
# 12pt body text. Alleen de BOVENGRENS; de werkelijke maat volgt het slideformaat van de
# deck (zie `pixel_size`).
DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1080

EMU_PER_INCH = 914400

# Waar het slideformaat niet uit de deck te lezen is: het formaat van dit sjabloon.
FALLBACK_SLIDE_IN = (13.333, 7.5)

RPC_E_CALL_REJECTED = -2147418111  # 0x80010001


def com_available() -> bool:
    try:
        import pythoncom
        import win32com.client  # noqa: F401
    except Exception:
        return False
    try:
        pythoncom.CoInitialize()
        app, created = _powerpoint()
        if created:
            app.Quit()
        return True
    except Exception:
        return False
    finally:
        try:
            import pythoncom

            pythoncom.CoUninitialize()
        except Exception:
            pass


def _powerpoint() -> tuple[object, bool]:
    """Return (app, created). Attach to a running PowerPoint when there is one."""
    import win32com.client

    try:
        return win32com.client.GetActiveObject("PowerPoint.Application"), False
    except Exception:
        pass
    try:
        return win32com.client.Dispatch("PowerPoint.Application"), True
    except Exception as exc:
        if getattr(exc, "hresult", None) == RPC_E_CALL_REJECTED:
            time.sleep(1)
            return win32com.client.Dispatch("PowerPoint.Application"), True
        raise


def slide_size_in(pptx_path: str | Path) -> tuple[float, float]:
    """Slideformaat in inch, uit `ppt/presentation.xml` van de deck zelf.

    Het formaat stond hardgecodeerd op 13.333 x 7.5 in. Dat is het SFNL-sjabloon, maar
    niet elke deck die hier langskomt: een 4:3-deck kreeg daardoor een verkeerde dpi en
    een uitgerekte PNG, zonder melding.
    """
    try:
        with zipfile.ZipFile(str(pptx_path)) as archive:
            xml = archive.read("ppt/presentation.xml").decode("utf-8", "replace")
    except (OSError, KeyError, zipfile.BadZipFile):
        return FALLBACK_SLIDE_IN

    match = re.search(r"<p:sldSz\b[^>]*>", xml)
    if not match:
        return FALLBACK_SLIDE_IN
    tag = match.group(0)
    cx = re.search(r'cx="(\d+)"', tag)
    cy = re.search(r'cy="(\d+)"', tag)
    if not cx or not cy:
        return FALLBACK_SLIDE_IN
    width_in = int(cx.group(1)) / EMU_PER_INCH
    height_in = int(cy.group(1)) / EMU_PER_INCH
    if width_in <= 0 or height_in <= 0:
        return FALLBACK_SLIDE_IN
    return round(width_in, 4), round(height_in, 4)


def pixel_size(slide_in: tuple[float, float], width: int, height: int) -> tuple[int, int]:
    """De grootste pixelmaat die in `width` x `height` past ZONDER te vervormen.

    `--width` en `--height` zijn dus een kader, niet twee losse getallen: op een
    16:9-deck met de defaults komt daar precies 1920 x 1080 uit, op een 4:3-deck
    1440 x 1080. Eerder werd --height op de LibreOffice-route genegeerd en op de
    COM-route letterlijk doorgegeven, wat een deck met een ander formaat uitrekte.
    """
    slide_w, slide_h = slide_in
    scale = min(width / slide_w, height / slide_h)
    return max(1, round(slide_w * scale)), max(1, round(slide_h * scale))


def render_deck(
    pptx_path: str | Path,
    out_dir: str | Path,
    slides: list[int] | None = None,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
) -> list[Path]:
    """Export slides to PNG. `slides` is a list of 1-based slide numbers."""
    import pythoncom

    deck = Path(pptx_path).resolve()
    out = Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    pythoncom.CoInitialize()
    app, created = _powerpoint()
    images: list[Path] = []
    try:
        presentation = app.Presentations.Open(str(deck), WithWindow=False)
        try:
            total = presentation.Slides.Count
            targets = list(range(1, total + 1)) if slides is None else slides
            for number in targets:
                if number < 1 or number > total:
                    continue
                dest = out / f"slide_{number:02d}.png"
                presentation.Slides(number).Export(str(dest), "PNG", width, height)
                images.append(dest)
        finally:
            presentation.Close()
    finally:
        if created:
            app.Quit()
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass
    return images


def soffice_binary() -> str | None:
    """Pad naar LibreOffice, of None."""
    sys.path.insert(0, str(Path(__file__).resolve().parent / "office"))
    from soffice import soffice_binary as resolve

    return resolve()


def pdf_to_png_tool() -> str | None:
    """Eerste beschikbare pdf->png-omzetter, of None.

    De ladder is pdftoppm -> pdftocairo -> mutool. pdftoppm en pdftocairo komen beide
    uit poppler-utils maar worden niet altijd samen gepakt; mutool (mupdf-tools) is de
    derde onafhankelijke bron. Eerder stond alleen pdftoppm in de weg, en dat is precies
    het gat waardoor een machine met LibreOffice toch niets kon renderen.
    """
    import shutil

    for name in ("pdftoppm", "pdftocairo", "mutool"):
        if shutil.which(name):
            return name
    return None


def _rasterise_pdf(
    tool: str,
    pdf: Path,
    tmp: Path,
    dpi: int,
    pages: list[int] | None,
) -> list[Path]:
    """Zet de pdf om naar page-*.png met `tool`, alleen de gevraagde pagina's."""
    import subprocess

    first_last: list[str] = []
    if pages:
        # Alleen het gevraagde bereik rasteren. Bij een deck van 40 slides en
        # --slides 7 scheelt dat het overige werk volledig.
        first_last = [str(min(pages)), str(max(pages))]

    if tool in ("pdftoppm", "pdftocairo"):
        command = [tool, "-png", "-r", str(dpi)]
        if first_last:
            command += ["-f", first_last[0], "-l", first_last[1]]
        command += [str(pdf), str(tmp / "page")]
    else:
        command = [
            "mutool", "draw", "-r", str(dpi),
            "-o", str(tmp / "page-%d.png"), str(pdf),
        ]
        if first_last:
            command.append(f"{first_last[0]}-{first_last[1]}")

    subprocess.run(command, check=True, capture_output=True, timeout=600)
    return sorted(tmp.glob("page-*.png"))


def _page_number(path: Path) -> int:
    """Paginanummer uit `page-7.png` / `page-07.png`."""
    digits = "".join(ch for ch in path.stem.split("-")[-1] if ch.isdigit())
    return int(digits) if digits else 0


def deck_to_pdf(deck: Path, out: Path) -> tuple[Path, bool]:
    """pptx -> pdf via LibreOffice, met de pdf als cache in `out`.

    Returns (pdf, cached). De pdf blijft staan: hij is het bewijsstuk waarop de reviewer
    terugvalt als er geen pdf->png-omzetter is, en hij is de cache voor een tweede
    aanroep. Hergebruikt zolang hij jonger is dan de deck — dus na een fixronde en
    herpack wordt hij opnieuw gemaakt, en `--slides 7` op een deck van veertig slides
    kost geen tweede conversie.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent / "office"))
    from soffice import run_soffice, soffice_binary as resolve

    if not resolve():
        raise RuntimeError("LibreOffice niet gevonden en PowerPoint COM niet beschikbaar")

    out.mkdir(parents=True, exist_ok=True)
    pdf = out / (deck.stem + ".pdf")
    if pdf.exists() and pdf.stat().st_mtime >= deck.stat().st_mtime:
        return pdf, True

    result = run_soffice(
        ["--headless", "--convert-to", "pdf", "--outdir", str(out), str(deck)],
        capture_output=True,
    )
    if result.returncode != 0 or not pdf.exists():
        detail = result.stderr or b""
        if isinstance(detail, bytes):
            detail = detail.decode("utf-8", errors="replace")
        raise RuntimeError(f"LibreOffice leverde geen pdf op: {detail.strip()[:300]}")
    return pdf, False


def render_deck_soffice(
    pptx_path: str | Path,
    out_dir: str | Path,
    slides: list[int] | None = None,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
) -> dict:
    """Export slides via LibreOffice: pptx -> pdf -> png.

    Fonts worden gesubstitueerd. Gebruik dit om compositie te controleren (overlap,
    lege vlakken, uitlijning), niet om regelafbrekingen op de millimeter na te meten:
    Gotham, Montserrat en Lato krijgen hier een vervanger met andere metriek.

    De pptx->pdf-stap gaat door `office/soffice.py` (eigen profielmap, timeout,
    sandbox-shim), de pdf->png-stap door de pdftoppm/pdftocairo/mutool-ladder.

    Is er geen omzetter, dan is het resultaat de pdf: `renderer` wordt
    `libreoffice-pdf`, `images` blijft leeg. Dat is de toestand waarop de reviewer en
    SKILL.md al jaren wijzen ("komt er alleen een pdf terug, lees dan de pdf-pagina's")
    en die dit script eerder nooit produceerde — het gooide een RuntimeError en de agent
    kreeg QA-only te horen terwijl er wel degelijk iets te zien was.
    """
    import shutil
    import tempfile

    deck = Path(pptx_path).resolve()
    out = Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    pdf, cached = deck_to_pdf(deck, out)
    tool = pdf_to_png_tool()
    if tool is None:
        return {
            "images": [],
            "renderer": "libreoffice-pdf",
            "pdf": pdf,
            "pdf_cached": cached,
            "remediation": (
                "geen pdf->png-omzetter gevonden — de pdf staat er wel: lees de "
                "pagina's daarvan. Wil je PNG's, installeer poppler-utils (pdftoppm of "
                "pdftocairo) of mupdf-tools (mutool)."
            ),
        }

    slide_in = slide_size_in(deck)
    pixels = pixel_size(slide_in, width, height)
    dpi = max(1, round(pixels[0] / slide_in[0]))

    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        pages = _rasterise_pdf(tool, pdf, tmp, dpi, slides)

        images: list[Path] = []
        for page in pages:
            number = _page_number(page)
            if slides is not None and number not in slides:
                continue
            dest = out / f"slide_{number:02d}.png"
            shutil.copy(page, dest)
            images.append(dest)
    return {
        "images": images,
        "renderer": "libreoffice",
        "pdf": pdf,
        "pdf_cached": cached,
        "pixels": pixels,
        "dpi": dpi,
        "raster_tool": tool,
    }


def render(
    pptx_path: str | Path,
    out_dir: str | Path,
    slides: list[int] | None = None,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    renderer: str = "auto",
) -> dict:
    """Render met PowerPoint waar dat kan, anders met LibreOffice.

    Geeft een dict terug in plaats van (images, renderer): de LibreOffice-route kan ook
    alleen een pdf opleveren, en die derde uitkomst was in een tuple van twee niet te
    melden.
    """
    slide_in = slide_size_in(pptx_path)
    if renderer in ("auto", "powerpoint") and com_available():
        pixels = pixel_size(slide_in, width, height)
        images = render_deck(pptx_path, out_dir, slides, pixels[0], pixels[1])
        return {
            "images": images,
            "renderer": "powerpoint",
            "pdf": None,
            "pixels": pixels,
            "slide_size_in": list(slide_in),
        }
    if renderer == "powerpoint":
        raise RuntimeError("PowerPoint COM niet beschikbaar")
    result = render_deck_soffice(pptx_path, out_dir, slides, width, height)
    result.setdefault("slide_size_in", list(slide_in))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", nargs="?", type=Path)
    parser.add_argument("out_dir", nargs="?", type=Path)
    parser.add_argument("--slides", help="comma-separated 1-based slide numbers")
    parser.add_argument(
        "--width",
        type=int,
        default=DEFAULT_WIDTH,
        help="breedte van het KADER in pixels; het slideformaat wordt erin gepast",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=DEFAULT_HEIGHT,
        help="hoogte van het kader in pixels; de JSON meldt de werkelijke pixelmaat",
    )
    parser.add_argument("--check", action="store_true", help="report whether COM works")
    parser.add_argument(
        "--renderer",
        choices=("auto", "powerpoint", "libreoffice"),
        default="auto",
        help="auto neemt PowerPoint waar dat kan en anders LibreOffice",
    )
    args = parser.parse_args()

    if args.check:
        com = com_available()
        soffice = soffice_binary()
        raster = pdf_to_png_tool()
        # Het binary vinden is niet hetzelfde als kunnen renderen. Een installatie met
        # alleen `libreoffice-core`, zonder `libreoffice-impress`, heeft geen importfilter
        # voor pptx: soffice start, zegt "Error: source file could not be loaded" en geeft
        # exit 0. Deze check meldde dan `mode: full` terwijl er niets rendert, en dat is de
        # gevaarlijkste melding die dit script kan geven -- de bouwer denkt visueel te
        # verifieren. Dus dezelfde proefconversie als in `preflight.py`.
        probe = {"ran": False, "ok": None, "detail": "niet geprobeerd: geen soffice"}
        if soffice and not com:
            try:
                from preflight import probe_soffice
                probe = probe_soffice()
            except Exception as fout:                          # noqa: BLE001
                probe = {"ran": False, "ok": None,
                         "detail": f"niet geprobeerd: {fout}"}
        soffice_werkt = soffice and probe.get("ok") is not False

        # LibreOffice alleen is niet genoeg voor PNG's, maar wel voor een pdf: dat is de
        # derde trap van de render-ladder, geen QA-only.
        if com:
            renderer, mode = "powerpoint", "full"
        elif soffice_werkt and raster:
            renderer, mode = "libreoffice", "full"
        elif soffice_werkt:
            renderer, mode = "libreoffice-pdf", "pdf"
        else:
            renderer, mode = None, "qa-only"

        if mode == "full":
            remediation = None
        elif mode == "pdf":
            remediation = (
                "LibreOffice staat er wel, maar er is geen pdf->png-omzetter — je krijgt "
                "een pdf en leest de pagina's daarvan. Wil je PNG's en een contactsheet: "
                "installeer poppler-utils (pdftoppm) of mupdf-tools (mutool)"
            )
        elif soffice and probe.get("ok") is False:
            remediation = (
                "soffice staat er, maar kan geen pptx openen: er is geen importfilter, "
                "dus vrijwel zeker is alleen libreoffice-core geinstalleerd. Installeer "
                "libreoffice-impress ernaast (apt-get install -y libreoffice-impress), en "
                "voor de png-stap poppler-utils (pdftoppm) of mupdf-tools (mutool)"
            )
        else:
            remediation = (
                "installeer PowerPoint met pywin32, of LibreOffice met poppler-utils"
            )

        emit(
            {
                "powerpoint_com": com,
                "libreoffice": soffice,
                "pdf_to_png": raster,
                "renderer": renderer,
                # full = PNG per slide, pdf = alleen pdf-pagina's, qa-only = niets te zien
                "mode": mode,
                "fonts_substituted": renderer in ("libreoffice", "libreoffice-pdf"),
                "remediation": remediation,
            }
        )
        # ALTIJD 0. De JSON is het antwoord: `--check` beantwoordt de vraag "kan ik
        # renderen", en "nee" is een geldig antwoord, geen scriptfout. Een exit 1 liet
        # een `set -e`-pipeline of een gehaaste caller de hele bouw afbreken terwijl de
        # QA-only-modus juist de bedoelde route is.
        sys.exit(0)

    if args.deck is None or args.out_dir is None:
        parser.error("deck en out_dir zijn verplicht (of gebruik --check)")

    slides = None
    if args.slides:
        slides = [int(part) for part in args.slides.replace(" ", "").split(",") if part]

    result = render(
        args.deck, args.out_dir, slides, args.width, args.height, args.renderer
    )
    images = result["images"]
    used = result["renderer"]
    payload = {
        "deck": str(args.deck),
        "out_dir": str(Path(args.out_dir).resolve()),
        "renderer": used,
        "fonts_substituted": used in ("libreoffice", "libreoffice-pdf"),
        "slide_size_in": result.get("slide_size_in"),
        # De werkelijke pixelmaat per PNG, niet de gevraagde: --width/--height zijn een
        # kader waarin het slideformaat past.
        "pixels": result.get("pixels"),
        "dpi": result.get("dpi"),
        "count": len(images),
        "images": [str(p) for p in images],
        "pdf": str(result["pdf"]) if result.get("pdf") else None,
        "pdf_cached": result.get("pdf_cached"),
    }
    if result.get("remediation"):
        payload["remediation"] = result["remediation"]
    if used == "libreoffice-pdf":
        payload["note"] = (
            "geen PNG's: lees de pdf-pagina's. Compositie-oordelen zijn geldig, "
            "fit-oordelen indicatief (fonts gesubstitueerd)."
        )
    emit(payload)


if __name__ == "__main__":
    main()
