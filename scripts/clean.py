"""Remove unreferenced files from an unpacked PPTX directory.

Usage:
    python clean.py <unpacked_dir>
    python clean.py <unpacked_dir> --drop-unused-layouts
    python clean.py <unpacked_dir> --drop-layouts 18,23,24

Example:
    python clean.py unpacked/

This script removes:
- Orphaned slides (not in sldIdLst) and their relationships
- [trash] directory (unreferenced files)
- Orphaned .rels files for deleted resources
- Unreferenced media, embeddings, charts, diagrams, drawings, ink files
- Unreferenced theme files
- Unreferenced notes slides
- Content-Type overrides for deleted files

`--drop-unused-layouts` gooit óók de layouts weg waar geen enkele slide op staat, met de
foto's die alleen aan die layouts hingen. Dat is de enige knop die iets doet aan het
gewicht van een opgeleverd deck: het sjabloon draagt 21 mediabestanden (5,79 MB van de
5,80 MB), en die zitten in élk gebouwd deck omdat de masters alle 27 layouts blijven
aanbieden — ook de layouts die je niet gebruikt. Nagemeten op een deck met vier
fotodividers: 5,79 MB → 1,66 MB, en dát is wat er als leave-behind in een mailbox
belandt.

Het is met opzet NIET de default. Wat je opgeeft: een collega die de deck later opent kan
alleen nog de layouts kiezen die erin zitten. Werkwijze: houd `deck.pptx` als werkbestand
compleet, en maak met deze vlag een aparte, lichte versie om te versturen.

`--drop-layouts N,N,N` gooit precies de genoemde layouts weg, ongeacht of er slides op
staan. Dat is de route die `prune_template.py` gebruikt om 18/23/24 uit het sjabloon te
halen: daar zijn géén slides, en `--drop-unused-layouts` doet dan met opzet niets (zonder
slides is elke layout "ongebruikt" en zou die vlag het hele sjabloon slopen).
"""

import sys
from pathlib import Path

import defusedxml.minidom


import re


def get_slides_in_sldidlst(unpacked_dir: Path) -> set[str]:
    pres_path = unpacked_dir / "ppt" / "presentation.xml"
    pres_rels_path = unpacked_dir / "ppt" / "_rels" / "presentation.xml.rels"

    if not pres_path.exists() or not pres_rels_path.exists():
        return set()

    rels_dom = defusedxml.minidom.parse(str(pres_rels_path))
    rid_to_slide = {}
    for rel in rels_dom.getElementsByTagName("Relationship"):
        rid = rel.getAttribute("Id")
        target = rel.getAttribute("Target")
        rel_type = rel.getAttribute("Type")
        if "slide" in rel_type and target.startswith("slides/"):
            rid_to_slide[rid] = target.replace("slides/", "")

    pres_content = pres_path.read_text(encoding="utf-8")
    referenced_rids = set(re.findall(r'<p:sldId[^>]*r:id="([^"]+)"', pres_content))

    return {rid_to_slide[rid] for rid in referenced_rids if rid in rid_to_slide}


def remove_orphaned_slides(unpacked_dir: Path) -> list[str]:
    slides_dir = unpacked_dir / "ppt" / "slides"
    slides_rels_dir = slides_dir / "_rels"
    pres_rels_path = unpacked_dir / "ppt" / "_rels" / "presentation.xml.rels"

    if not slides_dir.exists():
        return []

    referenced_slides = get_slides_in_sldidlst(unpacked_dir)
    removed = []

    for slide_file in slides_dir.glob("slide*.xml"):
        if slide_file.name not in referenced_slides:
            rel_path = slide_file.relative_to(unpacked_dir)
            slide_file.unlink()
            removed.append(rel_path.as_posix())

            rels_file = slides_rels_dir / f"{slide_file.name}.rels"
            if rels_file.exists():
                rels_file.unlink()
                removed.append(rels_file.relative_to(unpacked_dir).as_posix())

    if removed and pres_rels_path.exists():
        rels_dom = defusedxml.minidom.parse(str(pres_rels_path))
        changed = False

        for rel in list(rels_dom.getElementsByTagName("Relationship")):
            target = rel.getAttribute("Target")
            if target.startswith("slides/"):
                slide_name = target.replace("slides/", "")
                if slide_name not in referenced_slides:
                    if rel.parentNode:
                        rel.parentNode.removeChild(rel)
                        changed = True

        if changed:
            with open(pres_rels_path, "wb") as f:
                f.write(rels_dom.toxml(encoding="utf-8"))

    return removed


def remove_trash_directory(unpacked_dir: Path) -> list[str]:
    trash_dir = unpacked_dir / "[trash]"
    removed = []

    if trash_dir.exists() and trash_dir.is_dir():
        for file_path in trash_dir.iterdir():
            if file_path.is_file():
                rel_path = file_path.relative_to(unpacked_dir)
                removed.append(rel_path.as_posix())
                file_path.unlink()
        trash_dir.rmdir()

    return removed


def get_slide_referenced_files(unpacked_dir: Path) -> set:
    referenced = set()
    slides_rels_dir = unpacked_dir / "ppt" / "slides" / "_rels"

    if not slides_rels_dir.exists():
        return referenced

    for rels_file in slides_rels_dir.glob("*.rels"):
        dom = defusedxml.minidom.parse(str(rels_file))
        for rel in dom.getElementsByTagName("Relationship"):
            target = rel.getAttribute("Target")
            if not target:
                continue
            target_path = (rels_file.parent.parent / target).resolve()
            try:
                referenced.add(target_path.relative_to(unpacked_dir.resolve()))
            except ValueError:
                pass

    return referenced


def remove_orphaned_rels_files(unpacked_dir: Path) -> list[str]:
    resource_dirs = ["charts", "diagrams", "drawings"]
    removed = []
    slide_referenced = get_slide_referenced_files(unpacked_dir)

    for dir_name in resource_dirs:
        rels_dir = unpacked_dir / "ppt" / dir_name / "_rels"
        if not rels_dir.exists():
            continue

        for rels_file in rels_dir.glob("*.rels"):
            resource_file = rels_dir.parent / rels_file.name.replace(".rels", "")
            try:
                resource_rel_path = resource_file.resolve().relative_to(unpacked_dir.resolve())
            except ValueError:
                continue

            if not resource_file.exists() or resource_rel_path not in slide_referenced:
                rels_file.unlink()
                rel_path = rels_file.relative_to(unpacked_dir)
                removed.append(rel_path.as_posix())

    return removed


def get_referenced_files(unpacked_dir: Path) -> set:
    referenced = set()

    for rels_file in unpacked_dir.rglob("*.rels"):
        dom = defusedxml.minidom.parse(str(rels_file))
        for rel in dom.getElementsByTagName("Relationship"):
            target = rel.getAttribute("Target")
            if not target:
                continue
            target_path = (rels_file.parent.parent / target).resolve()
            try:
                referenced.add(target_path.relative_to(unpacked_dir.resolve()))
            except ValueError:
                pass

    return referenced


def remove_orphaned_files(unpacked_dir: Path, referenced: set) -> list[str]:
    resource_dirs = ["media", "embeddings", "charts", "diagrams", "tags", "drawings", "ink"]
    removed = []

    for dir_name in resource_dirs:
        dir_path = unpacked_dir / "ppt" / dir_name
        if not dir_path.exists():
            continue

        for file_path in dir_path.glob("*"):
            if not file_path.is_file():
                continue
            rel_path = file_path.relative_to(unpacked_dir)
            if rel_path not in referenced:
                file_path.unlink()
                removed.append(rel_path.as_posix())

    theme_dir = unpacked_dir / "ppt" / "theme"
    if theme_dir.exists():
        for file_path in theme_dir.glob("theme*.xml"):
            rel_path = file_path.relative_to(unpacked_dir)
            if rel_path not in referenced:
                file_path.unlink()
                removed.append(rel_path.as_posix())
                theme_rels = theme_dir / "_rels" / f"{file_path.name}.rels"
                if theme_rels.exists():
                    theme_rels.unlink()
                    removed.append(theme_rels.relative_to(unpacked_dir).as_posix())

    notes_dir = unpacked_dir / "ppt" / "notesSlides"
    if notes_dir.exists():
        for file_path in notes_dir.glob("*.xml"):
            if not file_path.is_file():
                continue
            rel_path = file_path.relative_to(unpacked_dir)
            if rel_path not in referenced:
                file_path.unlink()
                removed.append(rel_path.as_posix())

        notes_rels_dir = notes_dir / "_rels"
        if notes_rels_dir.exists():
            for file_path in notes_rels_dir.glob("*.rels"):
                notes_file = notes_dir / file_path.name.replace(".rels", "")
                if not notes_file.exists():
                    file_path.unlink()
                    removed.append(file_path.relative_to(unpacked_dir).as_posix())

    return removed


def update_content_types(unpacked_dir: Path, removed_files: list[str]) -> None:
    """Drop the Override for every part we deleted.

    `removed_files` MUST hold forward-slash paths — every remover appends
    `rel_path.as_posix()`. A `str(rel_path)` there yields `ppt\\slides\\slide4.xml` on
    Windows, which can never equal the `ppt/slides/slide4.xml` an OPC PartName carries,
    so no Override was ever removed and `changed` stayed False. That stayed invisible
    in the happy path (the .potx ships one slide with one Override, and add_slide.py
    early-returns when the PartName is already declared) but shipped a package pointing
    at a missing part the moment a slide or chart was dropped mid-build.
    """
    ct_path = unpacked_dir / "[Content_Types].xml"
    if not ct_path.exists():
        return

    dom = defusedxml.minidom.parse(str(ct_path))
    changed = False

    for override in list(dom.getElementsByTagName("Override")):
        part_name = override.getAttribute("PartName").lstrip("/")
        if part_name in removed_files:
            if override.parentNode:
                override.parentNode.removeChild(override)
                changed = True

    if changed:
        with open(ct_path, "wb") as f:
            f.write(dom.toxml(encoding="utf-8"))


def layouts_in_use(unpacked_dir: Path) -> set[str]:
    """De layoutbestanden waar minstens één slide op staat."""
    used = set()
    rels_dir = unpacked_dir / "ppt" / "slides" / "_rels"
    if not rels_dir.exists():
        return used
    for rels_file in rels_dir.glob("slide*.xml.rels"):
        dom = defusedxml.minidom.parse(str(rels_file))
        for rel in dom.getElementsByTagName("Relationship"):
            target = rel.getAttribute("Target")
            if "slideLayouts/" in target:
                used.add(target.split("/")[-1])
    return used


def remove_unused_layouts(unpacked_dir: Path) -> list[str]:
    """Layouts zonder slide eraf, met hun rels en hun plek in de sldLayoutIdLst.

    De foto's die alleen aan die layouts hingen worden daarna door de gewone
    media-opruiming meegenomen, want er verwijst niets meer naar.
    """
    layouts_dir = unpacked_dir / "ppt" / "slideLayouts"
    if not layouts_dir.exists():
        return []

    used = layouts_in_use(unpacked_dir)
    if not used:
        # Geen slides, geen informatie: dan is elke layout "ongebruikt" en zou dit het
        # hele sjabloon slopen. Niets doen. Wie een sjabloon wil uitdunnen noemt de
        # layouts expliciet, via remove_layouts() / `--drop-layouts`.
        return []

    doomed = {
        path.name
        for path in layouts_dir.glob("slideLayout*.xml")
        if path.name not in used
    }
    return remove_layouts(unpacked_dir, doomed)


def layout_file_names(numbers) -> set[str]:
    """`[18, 23, 24]` → `{"slideLayout18.xml", ...}`."""
    return {f"slideLayout{int(number)}.xml" for number in numbers}


def remove_layouts(unpacked_dir: Path, doomed: set[str]) -> list[str]:
    """De genoemde layoutbestanden eraf, met hun rels en hun plek in de sldLayoutIdLst.

    `doomed` draagt bestandsnamen (`slideLayout18.xml`). Wie ze aanwijst is niet aan deze
    functie: `remove_unused_layouts()` leidt ze af uit de slides, `--drop-layouts` krijgt
    ze van de aanroeper. Dat onderscheid is er omdat een sjabloon géén slides heeft en de
    afgeleide route daar per definitie niets vindt.

    De masters blijven staan: die hangen aan `sldMasterIdLst` in presentation.xml en een
    master weghalen raakt het thema en de tekststijlen waar de overgebleven slides op
    leunen.
    """
    layouts_dir = unpacked_dir / "ppt" / "slideLayouts"
    if not layouts_dir.exists() or not doomed:
        return []

    removed: list[str] = []

    # 1. De verwijzingen uit elke master weg: eerst de rId's opzoeken in de masterrels,
    #    dan die rId's uit de sldLayoutIdLst halen, dan de rels zelf.
    masters_dir = unpacked_dir / "ppt" / "slideMasters"
    for master in masters_dir.glob("slideMaster*.xml"):
        rels_path = masters_dir / "_rels" / f"{master.name}.rels"
        if not rels_path.exists():
            continue
        rels_dom = defusedxml.minidom.parse(str(rels_path))
        drop_rids = set()
        for rel in list(rels_dom.getElementsByTagName("Relationship")):
            target = rel.getAttribute("Target")
            if target.split("/")[-1] in doomed and "slideLayouts" in target:
                drop_rids.add(rel.getAttribute("Id"))
                if rel.parentNode:
                    rel.parentNode.removeChild(rel)
        if not drop_rids:
            continue
        with open(rels_path, "wb") as handle:
            handle.write(rels_dom.toxml(encoding="utf-8"))

        master_xml = master.read_text(encoding="utf-8")
        for rid in drop_rids:
            # Attribuutvolgorde is niet gegarandeerd (`id` vóór of ná `r:id`), dus geen
            # aanname dat r:id het laatste attribuut is: dan blijft er een sldLayoutId
            # staan die naar een verwijderde relatie wijst, en dát maakt een deck stuk.
            master_xml = re.sub(
                rf'\s*<p:sldLayoutId\b[^>]*\br:id="{rid}"[^>]*/>', "", master_xml
            )
            master_xml = re.sub(
                rf'\s*<p:sldLayoutId\b[^>]*\br:id="{rid}"[^>]*>.*?</p:sldLayoutId>',
                "",
                master_xml,
                flags=re.DOTALL,
            )
            if f'r:id="{rid}"' in master_xml:
                raise SystemExit(
                    f"kon {rid} niet uit {master.name} verwijderen — de sldLayoutIdLst "
                    "zou naar een weggegooide layout blijven wijzen. Niets weggegooid."
                )
        master.write_text(master_xml, encoding="utf-8")

    # 2. De layoutbestanden en hun rels.
    for name in sorted(doomed):
        path = layouts_dir / name
        if path.exists():
            path.unlink()
            removed.append(path.relative_to(unpacked_dir).as_posix())
        rels = layouts_dir / "_rels" / f"{name}.rels"
        if rels.exists():
            rels.unlink()
            removed.append(rels.relative_to(unpacked_dir).as_posix())

    return removed


def clean_unused_files(
    unpacked_dir: Path,
    drop_unused_layouts: bool = False,
    drop_layouts: set[str] | None = None,
) -> list[str]:
    all_removed = []

    slides_removed = remove_orphaned_slides(unpacked_dir)
    all_removed.extend(slides_removed)

    if drop_layouts:
        missing = sorted(
            name for name in drop_layouts
            if not (unpacked_dir / "ppt" / "slideLayouts" / name).exists()
        )
        if missing:
            # Stil niets doen zou een typfout in `--drop-layouts 8,23,24` laten passeren
            # en een sjabloon opleveren dat er goed uitziet en de layout nog draagt.
            raise SystemExit(
                "deze layouts staan niet in de boom: " + ", ".join(missing)
            )
        all_removed.extend(remove_layouts(unpacked_dir, set(drop_layouts)))

    if drop_unused_layouts:
        all_removed.extend(remove_unused_layouts(unpacked_dir))

    trash_removed = remove_trash_directory(unpacked_dir)
    all_removed.extend(trash_removed)

    while True:
        removed_rels = remove_orphaned_rels_files(unpacked_dir)
        referenced = get_referenced_files(unpacked_dir)
        removed_files = remove_orphaned_files(unpacked_dir, referenced)

        total_removed = removed_rels + removed_files
        if not total_removed:
            break

        all_removed.extend(total_removed)

    if all_removed:
        update_content_types(unpacked_dir, all_removed)

    return all_removed


def parse_layout_numbers(raw: str) -> set[str]:
    """`"18,23,24"` → layoutbestandsnamen. Alles wat geen nummer is, is een fout."""
    numbers = []
    for chunk in raw.replace(" ", "").split(","):
        if not chunk:
            continue
        if not chunk.isdigit():
            raise SystemExit(
                f"--drop-layouts verwacht layoutNUMMERS, gescheiden door komma's; "
                f"{chunk!r} is er geen (dus niet 'slideLayout18.xml', wel '18')"
            )
        numbers.append(int(chunk))
    if not numbers:
        raise SystemExit("--drop-layouts kreeg geen enkel nummer")
    return layout_file_names(numbers)


if __name__ == "__main__":
    argv = sys.argv[1:]
    args = []
    drop_unused = False
    drop_layouts: set[str] | None = None
    unknown = []

    index = 0
    while index < len(argv):
        token = argv[index]
        if token == "--drop-unused-layouts":
            drop_unused = True
        elif token == "--drop-layouts" or token.startswith("--drop-layouts="):
            if "=" in token:
                value = token.split("=", 1)[1]
            else:
                index += 1
                if index >= len(argv):
                    print("Error: --drop-layouts needs a value", file=sys.stderr)
                    sys.exit(1)
                value = argv[index]
            drop_layouts = parse_layout_numbers(value)
        elif token.startswith("--"):
            unknown.append(token)
        else:
            args.append(token)
        index += 1

    if len(args) != 1 or unknown:
        print(
            "Usage: python clean.py <unpacked_dir> [--drop-unused-layouts] "
            "[--drop-layouts N,N,N]",
            file=sys.stderr,
        )
        print("Example: python clean.py unpacked/", file=sys.stderr)
        sys.exit(1)

    unpacked_dir = Path(args[0])

    if not unpacked_dir.exists():
        print(f"Error: {unpacked_dir} not found", file=sys.stderr)
        sys.exit(1)

    removed = clean_unused_files(
        unpacked_dir,
        drop_unused_layouts=drop_unused,
        drop_layouts=drop_layouts,
    )

    if removed:
        print(f"Removed {len(removed)} unreferenced files:")
        for f in removed:
            print(f"  {f}")
    else:
        print("No unreferenced files found")
