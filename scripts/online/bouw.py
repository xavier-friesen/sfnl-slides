#!/usr/bin/env python3
"""Van één fragment naar één pagina: alles ingesloten, niets gelinkt.

Deze route levert **één HTML-bestand** op. Geen buildstap, geen bundler, geen
node_modules, geen backend. Dat is de grens van de skill en dit script is de
plek waar hij mechanisch geldt: wat er niet in dit bestand past, hoort niet in
deze opdracht.

Wat het script doet is stempelen, en verder niets:

1. **De letters.** `assets/documenten/fonts/fonts.css` sluit Montserrat en Lato
   in als data-URI. Geen `<link>` naar Google Fonts: in een artifact blokkeert
   het CSP-beleid elke andere host, en een pagina zonder internet valt anders
   terug op Helvetica — waarna de regelval verandert zonder melding.
2. **De schermstijl.** `assets/online/stijl.css`, ongewijzigd. De merkwaarden
   zitten er al in, tussen `merk:begin` en `merk:einde`, gestempeld door
   `scripts/gedeeld/merk.py --css`. Dit script controleert alleen of dat blok
   nog met `merk.py` in de pas loopt en weigert als het uit de pas is — want
   dan zou de pagina met een oude kleur gebouwd worden en dat ziet niemand.
   Er is met opzet geen `@import`: de CSS-parser laat een `@import` vallen die
   niet vooraan de stylesheet staat, en hieronder komt de stylesheet ná
   `fonts.css` in één `<style>`-blok.
3. **De schil.** Doctype, `lang="nl"`, viewport, de sprongkoppeling en — op de
   losse route — de themaschakelaar met zijn twintig regels JavaScript.

Twee uitvoeren, en het verschil is één ding:

* `<naam>.html` — het losse bestand. Opent in elke browser, werkt zonder
  internet, wordt met `scripts/gedeeld/naar_pdf.py` een PDF. Draagt de
  themaschakelaar.
* `<naam>-artifact.html` — hetzelfde, maar zonder doctype, `<html>`, `<head>`
  en `<body>`, want de Artifact-tool zet die er zelf om heen. En zonder
  schakelaar: in een artifact stempelt de viewer zelf `data-theme` op de root,
  en twee schakelaars op één pagina is er één te veel.

Gebruik:

    python bouw.py werkmap/pagina.frag.html
    python bouw.py werkmap/pagina.frag.html --uit dashboard.html --titel "Fonds 2026"
    python bouw.py werkmap/pagina.frag.html --artifact
    python bouw.py --nieuw werkmap/pagina.frag.html
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
WORTEL = HIER.parent.parent

STIJL = WORTEL / "assets" / "online" / "stijl.css"
FONTS = WORTEL / "assets" / "documenten" / "fonts" / "fonts.css"
MERK_CSS = WORTEL / "assets" / "gedeeld" / "merk.css"
MERK_PY = WORTEL / "scripts" / "gedeeld" / "merk.py"

IMPORT_REGEL = re.compile(r'^\s*@import\s+url\(["\']?\.\./gedeeld/merk\.css["\']?\)\s*;\s*$',
                          re.M)
HEX = re.compile(r"#[0-9a-fA-F]{3}(?:[0-9A-Fa-f]{3})?\b")

#: De namen die deze stijl uit merk.css verwacht. Loopt `merk.py` met andere
#: namen, dan resolveert `var(--oranje)` naar niets en dat is stil: de pagina
#: rendert, alleen zonder kleur. `qa_online.py` meldt elk token dat niet
#: resolveert, dus die controle staat daar en niet hier — maar deze lijst
#: staat er zodat je weet waar je moet kijken.
VERWACHT = ("navy", "oranje", "wit", "grapefruit", "emerald", "royal", "sky",
            "violet", "grijs", "mint-tint", "periwinkel", "oranje-tint",
            "navy-tint", "verloop", "display", "brood")

THEMA_JS = """
/* De themaschakelaar. Twintig regels, geen framework, geen afhankelijkheid.
   De pagina volgt standaard het systeem; klikt iemand, dan stempelt hij
   data-theme op de root en die stempel wint in beide richtingen. De
   localStorage-toegang staat in een try/catch, want in een privévenster en in
   een thumbnailrender gooit de accessor zelf. */
(function () {
  var r = document.documentElement;
  var b = document.querySelector('[data-thema]');
  if (!b) return;
  try {
    var keus = localStorage.getItem('sfnl-thema');
    if (keus === 'dark' || keus === 'light') r.setAttribute('data-theme', keus);
  } catch (e) { /* geen opslag: het systeem beslist, en dat is een prima stand */ }
  function donker() {
    var stempel = r.getAttribute('data-theme');
    if (stempel) return stempel === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
  function zet() {
    var d = donker();
    b.setAttribute('aria-pressed', d ? 'true' : 'false');
    b.textContent = d ? 'Licht' : 'Donker';
  }
  b.addEventListener('click', function () {
    r.setAttribute('data-theme', donker() ? 'light' : 'dark');
    try { localStorage.setItem('sfnl-thema', r.getAttribute('data-theme')); }
    catch (e) { /* de stand geldt voor deze sessie en wordt niet onthouden */ }
    zet();
  });
  zet();
})();
"""

SKELET = """<!-- Eén pagina. Componeer hier.
     De schil, de letters, merk.css en stijl.css stempelt bouw.py erin, dus
     schrijf geen <head>, geen <style> en geen doctype.

     De merktekens staan in assets/online/stijl.css §7. Er is geen
     dashboardsjabloon: wat je hieronder bouwt is elke keer opnieuw een
     ontwerpbeslissing. -->

<header class="koprand">
  <div class="dek">
    <div class="rij" style="justify-content: space-between;">
      <p class="logo">
        <span class="logo__vorm"><span class="logo__cirkel"></span><span class="logo__vierkant"></span></span>
        <span class="logo__woord">Social&nbsp;Finance <span class="logo__nl">NL</span></span>
      </p>
      <button class="thema" type="button" data-thema aria-pressed="false">Donker</button>
    </div>
  </div>
</header>

<main class="dek" id="inhoud">
  <p class="kicker">[RUBRIEK]</p>
  <h1 class="titel">[Een kop is een bewering, geen categorie]</h1>
  <hr class="streep" style="margin-top: 16px;">
</main>
"""

DOC = """<!doctype html>
<html lang="nl"{stempel}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titel}</title>
<style>
{css}
</style>
</head>
<body>
<a class="sprong" href="#inhoud">Naar de inhoud</a>
{inhoud}
<script>{js}</script>
</body>
</html>
"""

ARTIFACT = """<title>{titel}</title>
<style>
{css}
</style>
<a class="sprong" href="#inhoud">Naar de inhoud</a>
{inhoud}
"""


# ---------------------------------------------------------------------------
# De merkwaarden
# ---------------------------------------------------------------------------

def merkwaarden(override: Path | None = None) -> tuple[str, str]:
    """Het `:root`-blok met de merkkleuren en -letters, plus waar het vandaan komt.

    De volgorde is niet vrij. `merk.py` is de bron; `merk.css` is er de
    gegenereerde vorm van en staat in de repo omdat een stylesheet geen Python
    kan importeren. Zijn ze beide er, dan wint de bron — dan kan een
    verouderde `merk.css` deze pagina nooit vervuilen.
    """
    if override:
        if not override.exists():
            sys.exit(f"--merk niet gevonden: {override}")
        return override.read_text(encoding="utf-8"), f"--merk {override}"
    if MERK_PY.exists():
        sys.path.insert(0, str(MERK_PY.parent))
        try:
            from merk import css_variabelen  # type: ignore
            return css_variabelen(), "scripts/gedeeld/merk.py"
        except Exception as e:
            print(f"let op: merk.py staat er maar levert niets: {e}", file=sys.stderr)
    if MERK_CSS.exists():
        return MERK_CSS.read_text(encoding="utf-8"), "assets/gedeeld/merk.css"
    sys.exit(
        "geen merkwaarden gevonden. Er zijn drie bronnen, in deze volgorde:\n"
        f"  1. {MERK_PY} — css_variabelen()\n"
        f"  2. {MERK_CSS} — gegenereerd met `merk.py --css`\n"
        "  3. --merk <pad> naar een los :root-blok\n"
        "Zonder een daarvan staat er geen kleurwaarde in de pagina, en een\n"
        "hexwaarde in stijl.css is geen uitweg: die staat één keer, in merk.md.")


def stijlblok(merk: str) -> tuple[str, dict]:
    """merk + letters + schermstijl, in die volgorde, als één CSS-blok."""
    if not STIJL.exists():
        sys.exit(f"schermstijl niet gevonden: {STIJL}")
    stijl = STIJL.read_text(encoding="utf-8")

    # De mechanische toets van `merk.md` §0: een hexwaarde buiten merk.css is
    # een fout. Hier, en niet alleen in preflight, want dit script is de plek
    # waar de stijl de pagina in gaat.
    resten = [h for h in HEX.findall(IMPORT_REGEL.sub("", stijl))]
    if resten:
        sys.exit(f"hexwaarde in {STIJL.name}: {', '.join(sorted(set(resten)))}. "
                 f"Kleuren komen uit merk.md, niet uit een stylesheet.")

    if not IMPORT_REGEL.search(stijl):
        print("let op: geen @import van merk.css in stijl.css — de merkwaarden "
              "worden nu ervóór gezet en dat werkt, maar het bestand klopt niet "
              "meer met de beschrijving erboven.", file=sys.stderr)
        stijl = "@import url(\"../gedeeld/merk.css\");\n" + stijl

    fonts = FONTS.read_text(encoding="utf-8") if FONTS.exists() else ""
    if not fonts:
        sys.exit(
            f"de ingesloten letters ontbreken: {FONTS}\n"
            "Draai `python scripts/documenten/haal_fonts.py`. Een <link> naar "
            "Google Fonts is hier geen terugval: het CSP-beleid van een artifact "
            "blokkeert elke andere host, en zonder internet valt de pagina terug "
            "op Helvetica.")

    css = IMPORT_REGEL.sub(lambda _: merk.strip(), stijl, count=1)
    css = fonts.rstrip() + "\n\n" + css
    return css, {"merk_regels": merk.count("\n") + 1,
                 "letters_kb": round(len(fonts) / 1024),
                 "stijl_regels": stijl.count("\n") + 1}


# ---------------------------------------------------------------------------
# Bouwen
# ---------------------------------------------------------------------------

def _titel_uit(fragment: str, terugval: str) -> str:
    m = re.search(r'<h1[^>]*>(.*?)</h1>', fragment, re.S | re.I)
    if not m:
        return terugval
    ruw = re.sub(r"<[^>]+>", "", m.group(1))
    ruw = re.sub(r"\s+", " ", ruw).strip()
    return ruw or terugval


def bouw(fragment: Path, uit: Path | None = None, titel: str | None = None,
         artifact: bool = False, merk_override: Path | None = None,
         stempel: str | None = None) -> dict:
    if not fragment.exists():
        sys.exit(f"fragment niet gevonden: {fragment}\n"
                 f"Leg er een neer met: python bouw.py --nieuw {fragment}")
    inhoud = fragment.read_text(encoding="utf-8").strip("\n")
    if "<!doctype" in inhoud.lower() or "<body" in inhoud.lower():
        sys.exit(f"{fragment.name} draagt zelf een schil (<doctype> of <body>). "
                 f"Het fragment is alleen de pagina; de schil stempelt dit script "
                 f"erin.")

    merk, bron = merkwaarden(merk_override)
    css, tellingen = stijlblok(merk)

    naam = fragment.name
    for staart in (".frag.html", ".html"):
        if naam.endswith(staart):
            naam = naam[: -len(staart)]
            break
    doel = uit or fragment.parent / f"{naam}.html"
    kop = titel or _titel_uit(inhoud, naam.replace("-", " "))

    los = DOC.format(titel=kop, css=css, inhoud=inhoud, js=THEMA_JS.strip(),
                     stempel=f' data-theme="{stempel}"' if stempel else "")
    doel.write_text(los, encoding="utf-8")
    geschreven = {"los": str(doel), "los_kb": round(len(los.encode()) / 1024)}

    if artifact:
        # De schakelaar gaat eruit: in een artifact stempelt de viewer zelf.
        zonder = re.sub(r'\s*<button[^>]*\bdata-thema\b[^>]*>.*?</button>', "",
                        inhoud, flags=re.S)
        art = ARTIFACT.format(titel=kop, css=css, inhoud=zonder)
        pad = doel.with_name(f"{doel.stem}-artifact.html")
        pad.write_text(art, encoding="utf-8")
        geschreven["artifact"] = str(pad)
        geschreven["artifact_kb"] = round(len(art.encode()) / 1024)
        geschreven["schakelaar_verwijderd"] = zonder != inhoud

    return {"fragment": str(fragment), "titel": kop, "merkbron": bron,
            **tellingen, **geschreven,
            "verwachte_tokens": len(VERWACHT)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fragment", type=Path, nargs="?")
    ap.add_argument("--nieuw", type=Path, default=None,
                    help="leg een leeg fragment neer op dit pad en stop")
    ap.add_argument("--uit", type=Path, default=None)
    ap.add_argument("--titel", default=None,
                    help="de <title>. Zonder dit neemt het script de <h1>")
    ap.add_argument("--artifact", action="store_true",
                    help="schrijf er ook de artifactvariant bij")
    ap.add_argument("--merk", type=Path, default=None,
                    help="pad naar een los :root-blok, als merk.py en merk.css "
                         "er nog niet zijn")
    ap.add_argument("--stempel", choices=("light", "dark"), default=None,
                    help="zet data-theme vast op de <html>. Alleen voor de "
                         "renderloop; de oplevering draagt geen stempel")
    a = ap.parse_args()

    if a.nieuw:
        a.nieuw.parent.mkdir(parents=True, exist_ok=True)
        if a.nieuw.exists():
            sys.exit(f"bestaat al: {a.nieuw}")
        a.nieuw.write_text(SKELET, encoding="utf-8")
        print(json.dumps({"nieuw": str(a.nieuw)}, ensure_ascii=False, indent=2))
        return 0

    if not a.fragment:
        ap.error("geef een fragment, of --nieuw <pad>")
    r = bouw(a.fragment, a.uit, a.titel, a.artifact, a.merk, a.stempel)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
