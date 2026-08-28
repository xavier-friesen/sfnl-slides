#!/usr/bin/env python3
"""Zegt of deze machine een SFNL-Word-document kan bouwen en bekijken.

Vier vragen, en de vierde is de enige die een vormbesluit oplevert:

1. **Een interpreter met de stdlib.** Er is geen `python-docx` en geen `lxml`
   voor nodig — een `.docx` is een zip met XML erin en `zipfile` plus
   `xml.etree` doen het. Dat is geen zuinigheid: het maakt navertelbaar uit
   welk onderdeel welk stuk komt. Zie `requirements.txt` bij
   `scripts/rapport/lees_docx.py`.
2. **Het sjabloon.** `assets/word/SFNL_Word_sjabloon.dotx` is de bron van de
   stijlen, het thema, de kop- en voetteksten en het logo. Zonder dat bestand
   is er geen route: alles wordt geërfd en niets nagebouwd.
3. **Een renderer.** LibreOffice, om het document één keer naar PDF te
   drukken en er echt naar te kijken. Een document dat je niet hebt gezien is
   niet af. Ontbreekt hij, dan bouw je blind, en dat hoort bij de oplevering
   te worden gezegd.
4. **Gotham.** `Kop1` vraagt `Gotham Bold Regular`, commercieel en niet in de
   plugin. Staat hij er niet, dan zet `bouw.py` de kop expliciet in
   Montserrat SemiBold in plaats van het aan Word over te laten. Dit script
   meldt alleen wat het aantreft; het besluit valt in `bouw.py`.

En één ding erbij, omdat het je een ronde scheelt: `merk.py`. De
letterfamilies komen daaruit en nergens anders, dus zonder dat bestand kan
`bouw.py` het Gotham-besluit niet nemen.

    python preflight.py
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import subprocess
import sys
import zipfile
from pathlib import Path

HIER = Path(__file__).resolve().parent
WORTEL = HIER.parents[1]
SJABLOON = WORTEL / "assets" / "word" / "SFNL_Word_sjabloon.dotx"

sys.path.insert(0, str(HIER))
sys.path.insert(0, str(WORTEL / "scripts" / "gedeeld"))

#: De onderdelen waar de route op leunt. Ontbreekt er een, dan is het sjabloon
#: geen sjabloon meer en heeft nameten geen zin.
NODIG = ("word/styles.xml", "word/theme/theme1.xml", "word/numbering.xml",
         "word/settings.xml", "word/header2.xml", "word/footer2.xml",
         "word/media/image2.png")


GEEN_FILTER = "source file could not be loaded"


def _proef_writer(exe: str | None) -> dict:
    """Zet het sjabloon echt om naar PDF. `{"ran", "ok", "detail"}`.

    Het oordeel hangt aan de vraag of er een PDF staat, en niet aan de
    exitcode: die is 0 ook wanneer LibreOffice niets heeft omgezet. Kost hier
    ongeveer twee seconden, een keer per sessie.
    """
    if not exe:
        return {"ran": False, "ok": False, "detail": "geen soffice gevonden"}
    if not SJABLOON.is_file():
        return {"ran": False, "ok": False,
                "detail": "geen sjabloon om de proef mee te doen"}
    with tempfile.TemporaryDirectory() as tmp:
        doel = Path(tmp) / "proef"
        doel.mkdir()
        try:
            r = subprocess.run(
                [exe, "-env:UserInstallation=file://" + str(Path(tmp) / "profiel"),
                 "--headless", "--convert-to", "pdf", "--outdir", str(doel),
                 str(SJABLOON)],
                capture_output=True, text=True, timeout=180)
        except (OSError, subprocess.SubprocessError) as e:
            return {"ran": False, "ok": False, "detail": f"soffice liep niet af: {e}"}
        pdfs = list(doel.glob("*.pdf"))
        if pdfs:
            return {"ran": True, "ok": True, "detail": "het sjabloon werd een pdf"}
        melding = ((r.stdout or "") + (r.stderr or "")).strip()
        hint = ("libreoffice-writer ontbreekt naast libreoffice-core"
                if GEEN_FILTER in melding else
                "geen pdf en geen bekende melding")
        return {"ran": True, "ok": False,
                "detail": f"soffice zette het sjabloon niet om: {hint}. "
                          f"Exitcode {r.returncode} zegt hier niets."}


def main() -> int:
    argparse.ArgumentParser(description=__doc__,
                            formatter_class=argparse.RawDescriptionHelpFormatter
                            ).parse_args()

    uit: dict[str, object] = {"python": sys.version.split()[0]}

    # 2. Het sjabloon.
    if SJABLOON.is_file():
        with zipfile.ZipFile(SJABLOON) as z:
            namen = set(z.namelist())
        mist = [n for n in NODIG if n not in namen]
        uit["sjabloon"] = str(SJABLOON)
        uit["sjabloon_kb"] = round(SJABLOON.stat().st_size / 1024, 1)
        uit["sjabloon_onderdelen"] = len(namen)
        uit["sjabloon_mist"] = mist
    else:
        uit["sjabloon"] = None
        uit["sjabloon_mist"] = list(NODIG)

    # 3. De renderer, en die wordt geprobeerd en niet aangenomen.
    #
    # `shutil.which("soffice")` is hier geen antwoord, en dat is een keer duur
    # geweest. Op Debian en Ubuntu kan `libreoffice-core` alleen geinstalleerd
    # staan, zonder `libreoffice-writer`. Dan bestaat `soffice`, staat hij op
    # PATH, en meldt een which-check een renderer -- maar er is geen
    # importfilter voor een .docx, en `--convert-to pdf` antwoordt
    # `Error: source file could not be loaded` MET EXITCODE 0. Op de
    # aanwezigheid van het binary kun je dus niets bouwen.
    #
    # `scripts/preflight.py` had dit al opgelost voor de deckroute, met
    # `probe_soffice()` en een lege pptx. Die les was niet meegereisd naar deze
    # route, en dat kostte een halve dag zoeken op een sjabloon dat "niet
    # geladen" kon worden terwijl er niets mee was. Dus: hier dezelfde proef,
    # met het echte sjabloon, want dat is precies het bestand dat straks
    # omgezet moet worden.
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    uit["renderer_gevonden"] = exe
    if exe:
        try:
            r = subprocess.run([exe, "--version"], capture_output=True,
                               text=True, timeout=90)
            uit["renderer_versie"] = (r.stdout or r.stderr).strip().split("\n")[0]
        except (OSError, subprocess.SubprocessError) as e:
            uit["renderer_versie"] = f"niet op te vragen: {e}"
    uit["renderer_proef"] = _proef_writer(exe)
    # `renderer` is voortaan het antwoord op "kan deze machine een document
    # omzetten", en niet op "staat er een binary". Een consument die hierop
    # keek, keek op het verkeerde.
    uit["renderer"] = exe if uit["renderer_proef"].get("ok") else None
    # pdftoppm is geen eis maar het scheelt: zonder een PDF-naar-PNG-stap kijk
    # je naar de PDF zelf, en dat kan ook.
    uit["pdf_naar_png"] = shutil.which("pdftoppm")

    # 4. Gotham, en de terugval.
    letter: dict[str, object] = {}
    try:
        from bouw import gothamnaam, letter_aanwezig, terugvalletter
        if SJABLOON.is_file():
            with zipfile.ZipFile(SJABLOON) as z:
                styles = z.read("word/styles.xml").decode("utf-8")
            gevraagd = gothamnaam(styles)
            letter["kop1_vraagt"] = gevraagd
            letter["kop1_aanwezig"] = (letter_aanwezig(gevraagd)
                                       if gevraagd else None)
        letter["terugval"] = terugvalletter()
        # De families komen uit merk.py en staan niet in dit script. Wat daar
        # `mag_mee: False` heeft, is de licentieletter: die hoort hier niet te
        # staan en krijgt zijn eigen melding via kop1_aanwezig.
        from bouw import _letterfamilies
        for fam, waarde in _letterfamilies().items():
            if isinstance(waarde, dict) and waarde.get("mag_mee") is False:
                continue
            letter[f"{fam.lower()}_aanwezig"] = letter_aanwezig(fam)
        uit["merk_py"] = True
    except SystemExit as e:
        letter["fout"] = str(e).split("\n")[0]
        uit["merk_py"] = False
    uit["letters"] = letter

    print(json.dumps(uit, indent=2, ensure_ascii=False))

    if not uit["sjabloon"]:
        print(f"\nGeen sjabloon op {SJABLOON}. Er is geen route: deze skill "
              "erft alles uit dat bestand en bouwt niets na.", file=sys.stderr)
    if uit.get("sjabloon_mist"):
        print("\nHet sjabloon mist onderdelen: "
              f"{', '.join(uit['sjabloon_mist'])}. Controleer of de checkout "
              "compleet is.", file=sys.stderr)
    if not uit["renderer"]:
        proef = uit.get("renderer_proef", {})
        print("\nGeen werkende LibreOffice: dan bouw je blind. Het document is "
              "dan niet visueel geverifieerd, en dat hoort bij de oplevering te "
              f"worden gezegd.\n  {proef.get('detail', '')}", file=sys.stderr)
        if uit.get("renderer_gevonden"):
            print("  Let op: soffice staat er WEL. Dat is de val -- het binary "
                  "bestaat en converteert niets. Op Debian of Ubuntu: "
                  "`apt-get install libreoffice-writer`, of draai "
                  "`python scripts/preflight.py --herstel`.", file=sys.stderr)
    if not uit["merk_py"]:
        print("\nGeen merk.py: de letterfamilies staan daar en nergens anders "
              "(reference/merk.md §5). Zonder hem valt het Gotham-besluit "
              "niet te nemen.", file=sys.stderr)
    elif letter.get("kop1_aanwezig") is False:
        print(f"\nGotham staat niet op deze machine. Kop1 gaat in "
              f"{letter.get('terugval')}, expliciet in het bestand, en dat "
              "hoort bij de oplevering te worden genoemd.", file=sys.stderr)
    mist = sorted(k[:-9] for k, v in letter.items()
                  if k.endswith("_aanwezig") and v is False and k != "kop1_aanwezig")
    if mist:
        print(f"\nNiet op deze machine: {', '.join(mist)}. De render "
              "substitueert dan óók de broodletter of de koppen, dus de "
              "regelval die je ziet is niet de regelval die de lezer krijgt. "
              "Zeg dat bij de oplevering.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
