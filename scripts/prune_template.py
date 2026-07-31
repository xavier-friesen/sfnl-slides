"""Herbouw `assets/sfnl-sjabloon.potx` uit het onbewerkte merkorigineel.

Usage:
    python prune_template.py                       # herbouwt assets/sfnl-sjabloon.potx
    python prune_template.py --check               # exit 1 als het asset niet klopt
    python prune_template.py --out /tmp/slim.potx
    python prune_template.py --source "../01 SFNL_sjabloon.potx"
    python prune_template.py --drop-layouts 18,23,24 --jpeg-quality 92

Wat het doet, en waarom:

1. **Vier dividerfoto's van RGBA-PNG naar JPEG.** `image9/11/14/15.png` zijn samen
   12,46 MB van de 16,63 MB aan media. Het alfakanaal is exportresidu, geen ontwerp:
   image15 is volledig opaak, en image9/11/14 hebben een volledig transparante strook
   langs de rechterrand (2, 15 en 2 px) plus een antialiasrand van 1–2 px. Die strook
   draagt `(0,0,0)` als RGB — zonder alfa dus een zwarte naad. Hij wordt daarom vóór de
   conversie opgevuld met de laatste opake beeldkolom.

2. **Layouts 18, 23 en 24 eruit** (via `clean.py --drop-layouts`, dat de vier stappen al
   doet: de layout-XML, zijn rels, de `Relationship` in de masterrels, de `sldLayoutId`
   in de master en de `Override` in `[Content_Types].xml`). Het zijn de drie verboden
   layouts uit het layoutbeleid (B11). Er komt geen media mee vrij: hun rels wijzen
   uitsluitend naar `slideMaster2`.

**Er wordt NIET genummerd.** Elk script leidt het layoutnummer uit de bestandsnaam af
(`_deck.layout_number_of`, `add_slide.py`, `fit_title.py`). Het layoutbeleid keyt sinds W2b
op layoutNAAM (`LAYOUT_POLICY` in `_deck.py`), en de nummer-gesleutelde verzamelingen voor
ons eigen bouwpad worden daaruit afgeleid via de sjabloonfeiten in
`reference/layouts.json`. Gaten in de reeks (18, 23, 24 ontbreken) zijn dus onschadelijk;
hernoemen zou elke beleidsset verschuiven én de mapping naam-naar-nummer breken.

`--drop-layouts` noemt bewust NUMMERS: het benoemt de parts die uit dít pakket moeten, en
daar is het sjabloon per definitie bekend.

**Het content-type blijft `presentationml.template.main`.** Het resultaat is een .potx en
`prepare_template.fix_content_type()` rekent daarop.

`--check` vergelijkt **part-voor-part**, niet als zip-bytes: zip-bytes verschillen al door
een timestamp of een andere compressieronde, en zeggen dus niets. Het is de garantie dat
het binaire asset in de repo reproduceerbaar is uit het origineel — hetzelfde idee als
`test_shipped_catalogue_is_current` voor `reference/layouts.md`. Let op: de JPEG-bytes
komen uit Pillow. Een andere Pillow-major kan andere bytes geven; dan is het asset niet
stuk, maar moet het opnieuw gegenereerd en gecommit worden.

Het origineel in de projectroot (`01 SFNL_sjabloon.potx`) blijft de onaangeroerde
merkversie en wordt nooit geschreven.

**Het doel wordt getoetst vóór het werk.** In een geïnstalleerde plugin is `assets/`
read-only, en dan stopt het script meteen met een melding die naar `--out` verwijst — in
plaats van eerst uit te pakken en vier foto's om te zetten en pas op de laatste stap op
een `PermissionError` te stranden. Zelfde beleid als `layout_catalog.py`, zelfde probe
(`_deck.path_is_writable`); alleen wijkt dit script niet uit maar stopt het, want een
sjabloon dat ergens anders belandt is geen herbouwd asset. Herbouwen hoort in de
source-checkout.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "office"))

from _deck import emit, path_is_writable  # noqa: E402
from helpers import rezip, safe_extract  # noqa: E402

PLUGIN_DIR = SCRIPT_DIR.parent
DEFAULT_SOURCE = PLUGIN_DIR.parent / "01 SFNL_sjabloon.potx"
DEFAULT_OUT = PLUGIN_DIR / "assets" / "sfnl-sjabloon.potx"
DEFAULT_DROP = "18,23,24"

# JPEG-kwaliteit, en waarom niet de 95 uit besluit B1.
#
# B1 koos q95 om de fidelity-discussie weg te halen (q88 gaf een maximale kanaalafwijking
# van 56 op een render). Nagemeten op de echte render van een deck met de vier zware
# dividers, PowerPoint COM, 1280 px breed, per pixel gediffed tegen het oude sjabloon:
#
#   q95, 4:2:0 (Pillow-default)  max afwijking 52 / 33 / 25 / 30 per slide
#   q92, 4:4:4                   max afwijking 19 / 31 / 23 / 10 per slide
#
# De afwijking bij q95 zat niet in de luminantie maar in de CHROMA: zeventien losse pixels
# op verzadigd rood en blauw in de foto, precies wat 4:2:0-subsampling doet. Kwaliteit
# verder opschroeven repareert dat niet en kost budget: q97 met 4:2:0 komt op 6,25 MB en
# gaat dus over de 6,2 MB heen. q92 met 4:4:4 haalt de afwijking naar onder de 40 en is
# tegelijk 17 KB KLEINER dan q95 met 4:2:0. Strikt beter op elke as, dus dat is wat er
# gepakt wordt. Zet je hier 95 terug, zet dan ook de subsampling terug, want q95 met
# 4:4:4 komt op 6,38 MB.
DEFAULT_JPEG_QUALITY = 92

# 4:4:4: geen chroma-subsampling. Zie de toelichting bij DEFAULT_JPEG_QUALITY — dit is de
# helft van de reden dat de render binnen de marge blijft.
JPEG_SUBSAMPLING = 0

# Boven deze grootte wordt een PNG met beeldinhoud een JPEG. De vier dividerfoto's zijn
# 2,3 MB en groter; het zwaarste PNG dat blijft staan (een logo, image3/4/7/21) is 8 KB.
# Er is dus geen grensgeval, en dat is precies waarom een drempel hier volstaat in plaats
# van een lijst bestandsnamen die bij de eerste sjabloonwijziging niet meer klopt.
DEFAULT_MIN_PNG_BYTES = 1_000_000


def unpack_source(source: Path, unpacked: Path) -> None:
    """Pak uit met `zipfile` + `safe_extract`, niet met `office/unpack.py`.

    `unpack.py` weigert een .potx én pretty-print elke XML. Dat laatste zou elke part in
    het resultaat herschrijven, terwijl hier maar vijf parts hoeven te veranderen: hoe
    minder er verandert, hoe beter `--check` te lezen is.
    """
    unpacked.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source) as archive:
        safe_extract(archive, unpacked)


def drop_layouts(unpacked: Path, layouts: str) -> list[str]:
    """`clean.py --drop-layouts` als subprocess, zoals prepare_template.py het ook doet."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "clean.py"), str(unpacked),
         "--drop-layouts", layouts],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        sys.stderr.write(result.stdout + result.stderr)
        raise SystemExit("clean.py --drop-layouts failed")
    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.startswith("  ")
    ]


def flatten_alpha(image: Image.Image) -> Image.Image:
    """RGBA naar RGB, met de transparante rechterstrook opgevuld.

    De volledig transparante strook langs de rechterrand draagt `(0,0,0)`. Rechttoe
    `convert("RGB")` levert daar een zwarte naad op, precies op de rand waar de foto in
    de layout tegen de slidekant aanloopt. De laatste opake beeldkolom wordt daarom over
    de hele strook uitgesmeerd.
    """
    if image.mode != "RGBA":
        return image.convert("RGB")

    alpha = image.getchannel("A")
    mask = alpha.point(lambda value: 255 if value < 128 else 0)
    box = mask.getbbox()
    rgb = image.convert("RGB")
    if box is None:
        return rgb

    width, height = image.size
    x0 = max(box[0], 1)
    strip = rgb.crop((x0 - 1, 0, x0, height))
    for x in range(x0, width):
        rgb.paste(strip, (x, 0))
    return rgb


def rewrite_media_references(unpacked: Path, old: str, new: str) -> list[str]:
    """Elke `Target=`-verwijzing naar `old` in élke .rels naar `new`.

    Eén hernoeming die één .rels mist levert een deck op dat PowerPoint repareert of
    weigert, en geen enkele validator in deze plugin controleert media-targets — daarom
    wordt hier over de hele boom gezocht en niet alleen in de rels waar de foto hoort te
    hangen.
    """
    touched = []
    for rels in sorted(unpacked.rglob("*.rels")):
        text = rels.read_text(encoding="utf-8")
        if old not in text:
            continue
        rels.write_text(text.replace(old, new), encoding="utf-8")
        touched.append(rels.relative_to(unpacked).as_posix())
    return touched


def convert_photos(unpacked: Path, quality: int, min_bytes: int) -> list[dict]:
    """Grote PNG's naar JPEG, met de rels mee. Alfabetisch, dus reproduceerbaar."""
    media = unpacked / "ppt" / "media"
    if not media.exists():
        return []

    converted: list[dict] = []
    for png in sorted(media.glob("*.png")):
        before = png.stat().st_size
        if before < min_bytes:
            continue

        with Image.open(png) as image:
            mode = image.mode
            rgb = flatten_alpha(image)
        jpeg = png.with_suffix(".jpeg")
        if jpeg.exists():
            raise SystemExit(
                f"{jpeg.name} bestaat al — hernoemen zou een ander part overschrijven"
            )
        rgb.save(jpeg, "JPEG", quality=quality, optimize=True,
                 subsampling=JPEG_SUBSAMPLING)

        after = jpeg.stat().st_size
        png.unlink()
        rels = rewrite_media_references(unpacked, png.name, jpeg.name)
        if not rels:
            raise SystemExit(
                f"{png.name} werd door geen enkele .rels genoemd — niet omgezet, "
                "want dan zou er media in het pakket liggen waar niets naar wijst"
            )
        converted.append(
            {
                "from": png.name,
                "to": jpeg.name,
                "mode": mode,
                "bytes_before": before,
                "bytes_after": after,
                "rels": rels,
            }
        )
    return converted


def count_layouts(unpacked: Path) -> tuple[int, int]:
    masters = len(list((unpacked / "ppt" / "slideMasters").glob("slideMaster*.xml")))
    layouts = len(list((unpacked / "ppt" / "slideLayouts").glob("slideLayout*.xml")))
    return masters, layouts


def build(source: Path, target: Path, layouts: str, quality: int, min_bytes: int) -> dict:
    """Bouw het geslankte sjabloon op `target` en geef de meetgegevens terug."""
    with tempfile.TemporaryDirectory(prefix="prune-template-") as workdir:
        unpacked = Path(workdir) / "unpacked"
        unpack_source(source, unpacked)
        removed = drop_layouts(unpacked, layouts)
        converted = convert_photos(unpacked, quality, min_bytes)
        masters, layout_count = count_layouts(unpacked)

        target.parent.mkdir(parents=True, exist_ok=True)
        rezip(unpacked, target)

    return {
        "source": str(source),
        "out": str(target),
        "bytes_before": source.stat().st_size,
        "bytes_after": target.stat().st_size,
        "converted_media": converted,
        "media_bytes_before": sum(item["bytes_before"] for item in converted),
        "media_bytes_after": sum(item["bytes_after"] for item in converted),
        "layouts_dropped": removed,
        "masters": masters,
        "layouts": layout_count,
    }


def parts_of(package: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(package) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def compare(fresh: Path, shipped: Path) -> list[str]:
    """Part-voor-part verschillen. Leeg betekent: hetzelfde pakket."""
    if not shipped.exists():
        return [f"{shipped} bestaat niet"]

    mine = parts_of(fresh)
    theirs = parts_of(shipped)
    problems = []
    for name in sorted(set(theirs) - set(mine)):
        problems.append(f"alleen in {shipped.name}: {name}")
    for name in sorted(set(mine) - set(theirs)):
        problems.append(f"alleen opnieuw gegenereerd: {name}")
    for name in sorted(set(mine) & set(theirs)):
        if mine[name] != theirs[name]:
            problems.append(
                f"verschilt: {name} ({len(theirs[name])} → {len(mine[name])} bytes)"
            )
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE,
                        help="het onbewerkte merkorigineel (.potx)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help="waar het geslankte sjabloon heen gaat")
    parser.add_argument("--drop-layouts", default=DEFAULT_DROP,
                        help=f"layoutnummers, komma-gescheiden (default {DEFAULT_DROP})")
    parser.add_argument("--jpeg-quality", type=int, default=DEFAULT_JPEG_QUALITY,
                        help=f"JPEG-kwaliteit (default {DEFAULT_JPEG_QUALITY}, met 4:4:4 "
                             "chroma — zie de toelichting in dit bestand)")
    parser.add_argument("--min-png-bytes", type=int, default=DEFAULT_MIN_PNG_BYTES,
                        help="PNG's hierboven worden JPEG")
    parser.add_argument("--check", action="store_true",
                        help="niets schrijven; vergelijken met --out en exit 1 bij verschil")
    args = parser.parse_args()

    source: Path = args.source
    if not source.exists():
        raise SystemExit(
            f"bron niet gevonden: {source} — het onbewerkte merkorigineel staat in de "
            "projectroot en wordt niet met de plugin meegeleverd; geef hem met --source"
        )

    # Het doel wordt getoetst VÓÓR het werk, niet erna. Zonder deze toets deed het script
    # in een geïnstalleerde plugin eerst de volledige unpack plus de vier
    # JPEG-conversies en viel het daarna om op een kale `PermissionError` uit `rezip()`,
    # zonder JSON en zonder aanwijzing. Het gaat niet om de seconden (de hele bouw duurt
    # er ruim één) maar om de melding: al het werk zat vóór de enige schrijfactie, dus
    # de fout kwam er op het laatst uit en zei niets. Dat is dezelfde faalwijze waarvoor
    # `layout_catalog.writable_target()` bestaat en die de README als plugin-beleid
    # opschrijft; de probe is daarom gedeeld (`_deck.path_is_writable`).
    #
    # `via_tempfile=True`, want `rezip()` schrijft via `tempfile.mkstemp(dir=...)` naast
    # het doel: de MAP moet open zijn, niet alleen het bestand.
    #
    # Er wordt hier NIET uitgeweken zoals `layout_catalog.py` dat doet. Een catalogus die
    # in de huidige map landt is nog steeds te lezen; een sjabloon van 5,8 MB dat
    # stilletjes ergens anders komt te staan is geen herbouwd asset maar een kopie die
    # niemand vroeg — en dan is `--out` precies de vlag die je wilde geven.
    #
    # Alleen op de schrijfroute: `--check` bouwt in een tempdir en LEEST `--out`.
    if not args.check and not path_is_writable(args.out, via_tempfile=True):
        raise SystemExit(
            f"doel niet beschrijfbaar: {args.out} — de map eromheen laat geen schrijven "
            "toe (geïnstalleerde plugin?). Herbouw het sjabloon in de source-checkout, "
            "of geef zelf een schrijfbaar pad met `--out <pad>`. Er is nog niets "
            "uitgepakt."
        )

    if not args.check:
        result = build(source, args.out, args.drop_layouts,
                       args.jpeg_quality, args.min_png_bytes)
        result["checked"] = False
        emit(result)
        return

    with tempfile.TemporaryDirectory(prefix="prune-check-") as workdir:
        fresh = Path(workdir) / args.out.name
        result = build(source, fresh, args.drop_layouts,
                       args.jpeg_quality, args.min_png_bytes)
        problems = compare(fresh, args.out)

    result["out"] = str(args.out)
    result["checked"] = True
    result["differences"] = problems
    emit(result)
    if problems:
        print(
            f"{args.out} wijkt af van wat prune_template.py uit {source} maakt:",
            file=sys.stderr,
        )
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
