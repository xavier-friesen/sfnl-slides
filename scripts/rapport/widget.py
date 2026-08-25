#!/usr/bin/env python3
"""De ontwerpwidget: alle vormbesluiten op één pagina, met een preview.

Het vragenvuur van deze skill is met vijftien besluiten te lang geworden
voor een gesprek. Vier per keer door een keuzewidget betekent vier
rondes, en na de tweede weet niemand meer wat er in de eerste is
gekozen. Dus: één pagina, alles zichtbaar, en een schematische preview
die meebeweegt.

Wat deze widget anders maakt dan een formulier: hij wordt **per rapport
gegenereerd**. Hij leest `document.json` en biedt alleen aan wat er
werkelijk ligt. Geen bronnenlijst in het brondocument betekent geen keuze
tussen apa en genummerd; geen bijlagekoppen betekent geen bijlagevraag;
zijn er geen noten, dan vervalt de vraag waar ze moeten staan. Dat is
belangrijker dan het lijkt — de meest gestelde vraag in een intake is er
een die de gebruiker niet kan beantwoorden omdat hij over iets gaat wat
er niet is.

De preview is een **schema en geen zetproef**: het laat de marges, de
kolommen, de band en de folio zien, en het reageert op elke knop. De
echte zetting staat in de drie keuzekaarten in
`assets/rapport/keuzekaarten/`; die stuur je ernaast mee.

De uitvoer is een `ontwerp.json` die de gebruiker kopieert en
terugplakt. Dat is de eenvoudigste route die overal werkt — een widget
die zelf naar de werkmap schrijft, kan dat alleen in een omgeving die
dat toestaat.

Gebruik:

    python widget.py werkmap/
    python widget.py werkmap/ --uit ontwerpwidget.html
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
WORTEL = HIER.parent.parent
FONTS = WORTEL / "assets" / "documenten" / "fonts" / "fonts.css"


def _esc(t) -> str:
    return html.escape(str(t or ""), quote=True)


SJABLOON = """<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ontwerp — {titel}</title>
<style>
{fonts}
:root {{
  --navy: #201B5C; --oranje: #F87F4F; --emerald: #6AC6BA; --violet: #6B5DAE;
  --mint: #E0F4F1; --tint: #F4F3F7; --lijn: rgba(32,27,92,.16);
  --display: 'Montserrat', system-ui, sans-serif;
  --brood: 'Lato', system-ui, sans-serif;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; padding: 28px 30px 60px; background: #EFEEF2; color: var(--navy);
  font-family: var(--brood); font-weight: 300; font-size: 15px; line-height: 1.5;
}}
h1 {{ font-family: var(--display); font-weight: 800; font-size: 27px;
     letter-spacing: -.015em; margin: 0 0 4px; }}
h1 + p {{ margin: 0 0 22px; opacity: .72; max-width: 62ch; }}
h2 {{ font-family: var(--display); font-weight: 800; font-size: 13px;
     letter-spacing: .13em; text-transform: uppercase; color: var(--oranje);
     margin: 0 0 12px; padding-top: 12px; border-top: 3px solid var(--oranje);
     display: inline-block; }}
.blad {{ display: grid; grid-template-columns: minmax(0,1fr) 330px; gap: 34px;
        align-items: start; max-width: 1180px; }}
.kaart {{ background: #fff; padding: 20px 22px 22px; margin-bottom: 16px;
         box-shadow: 0 1px 3px rgba(32,27,92,.10); }}
.rij {{ display: grid; grid-template-columns: 150px minmax(0,1fr); gap: 12px 16px;
       align-items: start; margin-bottom: 14px; }}
.rij:last-child {{ margin-bottom: 0; }}
.rij > label {{ font-weight: 700; font-size: 13.5px; padding-top: 5px; }}
.opties {{ display: flex; flex-wrap: wrap; gap: 7px; }}
.opt {{ position: relative; }}
.opt input {{ position: absolute; opacity: 0; pointer-events: none; }}
.opt span {{
  display: block; padding: 6px 12px; border: 1px solid var(--lijn);
  font-size: 13.5px; cursor: pointer; background: #fff; user-select: none;
}}
.opt input:checked + span {{ background: var(--navy); color: #fff; border-color: var(--navy); }}
.opt input:focus-visible + span {{ outline: 2px solid var(--oranje); outline-offset: 2px; }}
.uitleg {{ grid-column: 2; font-size: 12.5px; opacity: .68; margin: -8px 0 0; }}
input[type=text] {{
  width: 100%; padding: 7px 10px; border: 1px solid var(--lijn);
  font-family: var(--brood); font-size: 14px; color: var(--navy); background: #fff;
}}
.aan {{ display: flex; align-items: center; gap: 9px; font-size: 13.5px; }}
.aan input {{ width: 17px; height: 17px; accent-color: var(--navy); }}
select {{ padding: 7px 10px; border: 1px solid var(--lijn); font-family: var(--brood);
         font-size: 14px; color: var(--navy); background: #fff; max-width: 100%; }}

/* --- de preview --------------------------------------------------- */
.zij {{ position: sticky; top: 24px; }}
.preview {{ background: #fff; padding: 18px; box-shadow: 0 1px 3px rgba(32,27,92,.10); }}
.blad-schets {{ position: relative; width: 100%; aspect-ratio: 794 / 1039;
               background: #fff; border: 1px solid var(--lijn); overflow: hidden; }}
.blad-schets.a4 {{ aspect-ratio: 794 / 1123; }}
.band {{ position: absolute; top: 0; left: 0; right: 0; height: 22%;
        background: var(--oranje); }}
.band::after {{ content: ""; position: absolute; width: 150%; height: 150%;
               left: -60%; top: -95%; border-radius: 50%;
               background: rgba(32,27,92,.10); }}
.zetspiegel {{ position: absolute; inset: 7.3% 5.9% 9.3% 7.8%; display: flex; gap: 3.8%; }}
.kolom {{ background: repeating-linear-gradient(
            transparent 0 3px, rgba(32,27,92,.30) 3px 4px); flex: 1; }}
.kant {{ flex: 0 0 21.5%; background: repeating-linear-gradient(
           transparent 0 4px, rgba(32,27,92,.14) 4px 5px); }}
.folio {{ position: absolute; bottom: 3.6%; right: 5.9%; width: 8%; height: 1.4%;
         background: var(--oranje); }}
.meting {{ margin-top: 12px; font-size: 12.5px; line-height: 1.45; }}
.meting b {{ font-family: var(--display); font-weight: 700; }}
.let {{ margin-top: 10px; padding: 9px 11px; background: var(--tint);
       font-size: 12.5px; line-height: 1.45; }}

/* --- de uitvoer ---------------------------------------------------- */
.uit {{ margin-top: 16px; }}
pre {{ background: var(--navy); color: #EDECF4; padding: 15px 17px; margin: 0;
      font: 400 12.5px/1.55 ui-monospace, 'SF Mono', Menlo, monospace;
      overflow-x: auto; white-space: pre-wrap; word-break: break-word; }}
button {{ font-family: var(--display); font-weight: 700; font-size: 13px;
         letter-spacing: .04em; padding: 10px 18px; border: 0; cursor: pointer;
         background: var(--oranje); color: var(--navy); margin-top: 10px; }}
button:active {{ transform: translateY(1px); }}
.klaar {{ margin-left: 10px; font-size: 13px; color: var(--emerald); font-weight: 700; }}
</style>
</head>
<body>

<h1>Ontwerp van het rapport</h1>
<p>{intro}</p>

<div class="blad">
  <div>
{secties}
  </div>

  <div class="zij">
    <div class="preview">
      <h2 style="border-color: var(--navy); color: var(--navy)">Schets</h2>
      <div class="blad-schets" id="schets">
        <div class="band" id="p-band" hidden></div>
        <div class="zetspiegel" id="p-zet">
          <div class="kolom"></div>
        </div>
        <div class="folio"></div>
      </div>
      <p class="meting" id="p-meting"></p>
      <p class="let">Dit is een schema en geen zetproef: het laat de marges, de
        kolommen en de band zien. Hoe het er écht uitziet staat in de drie
        keuzekaarten die hierbij horen.</p>
    </div>

    <div class="uit">
      <h2 style="border-color: var(--navy); color: var(--navy)">ontwerp.json</h2>
      <pre id="uit"></pre>
      <button type="button" id="kopieer">Kopieer en plak terug in het gesprek</button>
      <span class="klaar" id="klaar" hidden>gekopieerd</span>
    </div>
  </div>
</div>

<script>
const MAAT = {maten};

function lees() {{
  const o = {{}};
  document.querySelectorAll('[data-veld]').forEach(el => {{
    const naam = el.dataset.veld;
    if (el.type === 'radio') {{ if (el.checked) o[naam] = el.value; }}
    else if (el.type === 'checkbox') {{ o[naam] = el.checked; }}
    else if (el.value !== '') {{ o[naam] = el.value; }}
  }});
  if (o.inhoudDiepte) o.inhoudDiepte = +o.inhoudDiepte;
  if (o.bijlageVanaf) {{
    o.bijlagen = o.bijlageVanaf === 'geen' ? null : {{ vanaf: o.bijlageVanaf }};
  }}
  delete o.bijlageVanaf;
  if (o.bijlagen === undefined) o.bijlagen = null;
  for (const k of ['rapporttitel','ondertitel','opdrachtgever','datum','beeldmap']) {{
    if (!o[k]) o[k] = null;
  }}
  return o;
}}

function ververs() {{
  const o = lees();
  const m = MAAT[o.model] || MAAT.breed;
  const schets = document.getElementById('schets');
  schets.classList.toggle('a4', o.formaat === 'a4');

  const zet = document.getElementById('p-zet');
  zet.innerHTML = '';
  const n = m.kolommen;
  for (let i = 0; i < n; i++) {{
    const k = document.createElement('div'); k.className = 'kolom'; zet.appendChild(k);
  }}
  if (m.kantlijn) {{
    const k = document.createElement('div'); k.className = 'kant'; zet.appendChild(k);
  }}

  const band = document.getElementById('p-band');
  band.hidden = o.opener !== 'band';
  const kleur = {{helder: 'var(--oranje)', diep: 'var(--navy)',
                 zacht: 'var(--mint)', contrast: 'var(--violet)'}};
  band.style.background = kleur[o.register] || 'var(--oranje)';
  zet.style.paddingTop = o.opener === 'band' ? '17%' : '0';

  const per = {{ruim: 0.88, gemiddeld: 1, dicht: 1.12}}[o.dichtheid] || 1;
  document.getElementById('p-meting').innerHTML =
    '<b>' + m.tekens + '</b> tekens per regel &middot; brood op <b>' + m.brood +
    '</b> &middot; ongeveer <b>' + Math.round(m.woorden * per) +
    '</b> woorden per pagina bij dichtheid <b>' + o.dichtheid + '</b>';

  document.getElementById('uit').textContent = JSON.stringify(o, null, 1);
}}

document.addEventListener('input', ververs);
document.addEventListener('change', ververs);
document.getElementById('kopieer').addEventListener('click', () => {{
  const t = document.getElementById('uit').textContent;
  const klaar = () => {{
    const k = document.getElementById('klaar');
    k.hidden = false; setTimeout(() => {{ k.hidden = true; }}, 2200);
  }};
  if (navigator.clipboard && navigator.clipboard.writeText) {{
    navigator.clipboard.writeText(t).then(klaar, klaar);
  }} else {{
    const ta = document.createElement('textarea');
    ta.value = t; document.body.appendChild(ta); ta.select();
    try {{ document.execCommand('copy'); }} catch (e) {{}}
    ta.remove(); klaar();
  }}
}});
ververs();
</script>
</body>
</html>
"""

#: Wat de preview per model laat zien. De getallen komen uit
#: `reference/rapport-stramien.md` §3 en zijn daar gemeten op een gezet
#: rapport; ze staan hier alleen om de gebruiker te laten zien wat een
#: keuze kost.
MATEN = {
    "breed":    {"kolommen": 1, "kantlijn": False, "tekens": 77,
                 "brood": "11 pt", "woorden": 330},
    "kantlijn": {"kolommen": 1, "kantlijn": True, "tekens": 76,
                 "brood": "10 pt", "woorden": 400},
    "dubbel":   {"kolommen": 2, "kantlijn": False, "tekens": 48,
                 "brood": "10 pt", "woorden": 540},
    "flexibel": {"kolommen": 1, "kantlijn": True, "tekens": 76,
                 "brood": "10 pt", "woorden": 400},
}


def keuze(veld: str, label: str, opties: list, gekozen: str, uitleg: str = "") -> str:
    knoppen = []
    for waarde, tekst in opties:
        aan = " checked" if waarde == gekozen else ""
        knoppen.append(
            f'<label class="opt"><input type="radio" name="{veld}" '
            f'data-veld="{veld}" value="{_esc(waarde)}"{aan}>'
            f'<span>{_esc(tekst)}</span></label>')
    hulp = f'<p class="uitleg">{_esc(uitleg)}</p>' if uitleg else ""
    return (f'<div class="rij"><label>{_esc(label)}</label>'
            f'<div class="opties">{"".join(knoppen)}</div>{hulp}</div>')


def vinkje(veld: str, label: str, tekst: str, aan: bool) -> str:
    c = " checked" if aan else ""
    return (f'<div class="rij"><label>{_esc(label)}</label>'
            f'<label class="aan"><input type="checkbox" data-veld="{veld}"{c}>'
            f'<span>{_esc(tekst)}</span></label></div>')


def tekstveld(veld: str, label: str, waarde, plaatshouder: str = "") -> str:
    return (f'<div class="rij"><label>{_esc(label)}</label>'
            f'<input type="text" data-veld="{veld}" value="{_esc(waarde)}" '
            f'placeholder="{_esc(plaatshouder)}"></div>')


def keuzelijst(veld: str, label: str, opties: list, gekozen: str,
               uitleg: str = "") -> str:
    regels = []
    for waarde, tekst in opties:
        aan = " selected" if waarde == gekozen else ""
        regels.append(f'<option value="{_esc(waarde)}"{aan}>{_esc(tekst)}</option>')
    hulp = f'<p class="uitleg">{_esc(uitleg)}</p>' if uitleg else ""
    return (f'<div class="rij"><label>{_esc(label)}</label>'
            f'<select data-veld="{veld}">{"".join(regels)}</select>{hulp}</div>')


def bouw_secties(doc: dict, ontwerp: dict) -> tuple[str, str]:
    ap = doc.get("apparaat", {})
    tel = doc.get("telling", {})
    heeft_noten = bool(ap.get("voetnoten") or ap.get("eindnoten"))
    heeft_lijst = bool(ap.get("bronnenlijst"))
    heeft_bijlagen = bool(ap.get("bijlagen"))
    heeft_beeld = bool(tel.get("beelden"))
    citaten = ap.get("citaten", {})

    delen = []

    # -- de vorm -------------------------------------------------------
    delen.append('<div class="kaart"><h2>De vorm</h2>' + "".join([
        keuze("model", "Layoutmodel",
              [("breed", "breed"), ("kantlijn", "kantlijn"),
               ("dubbel", "dubbel"), ("flexibel", "flexibel")],
              ontwerp["model"],
              "breed is de veilige keuze; kantlijn alleen als er noten of bronnen "
              "naast de tekst kunnen; dubbel is het kortst."),
        keuze("register", "Kleurregister",
              [("helder", "helder"), ("diep", "diep"),
               ("zacht", "zacht"), ("contrast", "contrast")],
              ontwerp["register"],
              "helder houdt tachtig pagina's vol; diep en contrast kosten een "
              "pagina per hoofdstuk."),
        keuze("formaat", "Bladmaat",
              [("sfnl", "SFNL 210 × 275"), ("a4", "A4"),
               ("a4-liggend", "A4 liggend")],
              ontwerp["formaat"],
              "SFNL is de maat van de jaarrapporten; A4 voor de kantoorprinter."),
        keuze("opener", "Hoofdstuk begint met",
              [("nummer", "nummer"), ("band", "band"), ("blad", "blad")],
              ontwerp["opener"],
              "nummer kost niets, band een kwart pagina, blad een hele."),
        keuze("dichtheid", "Dichtheid",
              [("ruim", "ruim"), ("gemiddeld", "gemiddeld"), ("dicht", "dicht")],
              ontwerp["dichtheid"],
              "Verschuift het aantal regels per pagina met drie en de lucht "
              "tussen blokken. Geen drempel: qa_rapport.py meet achteraf wat "
              "het werkelijk werd."),
    ]) + "</div>")

    # -- de onderdelen -------------------------------------------------
    delen.append('<div class="kaart"><h2>Wat er in komt</h2>' + "".join([
        vinkje("omslag", "Omslag", "een eigen omslagpagina", ontwerp["omslag"]),
        vinkje("inhoudsopgave", "Inhoudsopgave", "met echte paginanummers",
               ontwerp["inhoudsopgave"]),
        keuze("inhoudDiepte", "Diepte", [("1", "alleen hoofdstukken"),
                                         ("2", "hoofdstukken en secties")],
              str(ontwerp["inhoudDiepte"])),
        vinkje("dubbelzijdig", "Dubbelzijdig",
               "hoofdstukken beginnen rechts; marges spiegelen",
               ontwerp["dubbelzijdig"]),
        vinkje("hoofdstuknummers", "Nummering", "Hoofdstuk 1, 2, 3 boven de titel",
               ontwerp["hoofdstuknummers"]),
        vinkje("exhibitnummers", "Figuurnummers", "Figuur 1, 2, 3 boven een beeld",
               ontwerp["exhibitnummers"]),
    ]) + "</div>")

    # -- de verwijzingen -----------------------------------------------
    verw = [f'<div class="kaart"><h2>Verwijzingen</h2>']
    if heeft_noten:
        verw.append(keuze("noten", "Noten",
                          [("voetnoot", "aan de voet"),
                           ("eindnoot-hoofdstuk", "achter het hoofdstuk"),
                           ("eindnoot-rapport", "achter het rapport")],
                          ontwerp["noten"],
                          f'Het brondocument heeft {ap.get("voetnoten", 0)} noten. '
                          f'Waar ze staan is opmaak; de tekst blijft gelijk.'))
    else:
        verw.append('<div class="rij"><label>Noten</label>'
                    '<p class="uitleg" style="grid-column:2;margin:5px 0 0">'
                    'Het brondocument heeft geen noten, dus er valt niets te '
                    'plaatsen.</p></div>')
    if heeft_lijst:
        lijst = ap["bronnenlijst"]
        verw.append(keuze("bronnenlijst", "Bronnenlijst",
                          [("geen", "als gewone tekst"),
                           ("apa", "alfabetisch, hangend"),
                           ("genummerd", "genummerd op citatievolgorde")],
                          ontwerp["bronnenlijst"],
                          f'Gevonden: {lijst["aantal"]} regels onder '
                          f'"{lijst["kop"]}". Voetnoten en een bronnenlijst gaan '
                          f'samen; dat is het gewone geval.'))
    else:
        verw.append('<div class="rij"><label>Bronnenlijst</label>'
                    '<p class="uitleg" style="grid-column:2;margin:5px 0 0">'
                    'Geen kop gevonden die een bronnenlijst aankondigt. Er wordt er '
                    'geen gemaakt — een lijst verzinnen doet deze skill niet.'
                    '</p></div>')
    if citaten.get("auteur_jaar"):
        verw.append(keuze("citaatstijl", "Verwijzingen in de tekst",
                          [("zoals-aangeleverd", "laten staan"),
                           ("uniform", "gelijktrekken"),
                           ("genummerd", "omzetten naar [1]")],
                          ontwerp.get("citaatstijl", "zoals-aangeleverd"),
                          f'{citaten["auteur_jaar"]} auteur-jaarverwijzingen '
                          f'gevonden. Gelijktrekken maakt van "e.a." overal '
                          f'"et al."; omzetten vraagt een bronnenlijst om naar '
                          f'te wijzen. Elke omzetting wordt gelogd.'))
    delen.append("".join(verw) + "</div>")

    # -- bijlagen ------------------------------------------------------
    if heeft_bijlagen:
        opties = [("geen", "geen aparte bijlagen")]
        for k in ap["bijlagen"]["koppen"]:
            opties.append((k["id"], f'vanaf "{k["tekst"][:58]}"'))
        gekozen = (ontwerp.get("bijlagen") or {}).get("vanaf") or ap["bijlagen"]["vanaf"]
        delen.append('<div class="kaart"><h2>Bijlagen</h2>' + keuzelijst(
            "bijlageVanaf", "Beginnen bij", opties, gekozen,
            "Vanaf dat punt komt er een scheidingsblad, tellen de openers in "
            "letters, en krijgen ze in de inhoudsopgave een eigen groep.") + "</div>")

    # -- beeld ---------------------------------------------------------
    delen.append('<div class="kaart"><h2>Beeld</h2>' + "".join([
        keuze("beeld", "Gebruikt dit rapport beeld",
              [("geen", "nee"), ("uit-bron", "wat in het document zit"),
               ("aangeleverd", "ja, apart aangeleverd")],
              ontwerp["beeld"],
              f'In het brondocument zitten {tel.get("beelden", 0)} beelden.'
              + ("" if heeft_beeld else
                 " Er zit geen beeld in; kies 'apart aangeleverd' als er nog "
                 "figuren bij moeten.")),
        tekstveld("beeldmap", "Waar staat het", ontwerp.get("beeldmap"),
                  "pad naar de map met de figuren"),
    ]) + '<p class="uitleg" style="grid-column:1/-1">Bij "apart aangeleverd" '
        'koppelt de skill elk bestand aan een blok in de tekst, en vraagt na '
        'welke alinea het hoort. Dat komt in een <code>beeld.json</code> naast '
        'het rapport te staan; een figuur zonder plek wordt niet geplaatst en '
        'gemeld, want gokken is hier hetzelfde als verzinnen.</p></div>')

    # -- de omslag -----------------------------------------------------
    delen.append('<div class="kaart"><h2>Op de omslag</h2>' + "".join([
        tekstveld("rapporttitel", "Titel", ontwerp.get("rapporttitel")
                  or doc.get("titel"), "de dektitel"),
        tekstveld("ondertitel", "Ondertitel", ontwerp.get("ondertitel"),
                  "één zin, of leeg"),
        tekstveld("opdrachtgever", "Opdrachtgever", ontwerp.get("opdrachtgever"),
                  "In opdracht van …"),
        tekstveld("datum", "Datum", ontwerp.get("datum"), "Maart 2026"),
    ]) + '<p class="uitleg" style="grid-column:1/-1">Dit is de enige plek waar '
        'tekst aan het rapport wordt toegevoegd, en die tekst komt woordelijk '
        'van jou. Leeg laten betekent dat het er niet op komt te staan.</p></div>')

    intro = (
        f'{tel.get("woorden", 0):,}'.replace(",", ".") +
        f' woorden, {tel.get("koppen", 0)} koppen, {tel.get("tabellen", 0)} tabellen, '
        f'{tel.get("beelden", 0)} beelden en {ap.get("voetnoten", 0)} noten. '
        'Vul in wat je wilt, kopieer onderaan de ontwerp.json en plak die terug '
        'in het gesprek. Alles heeft al een verdedigbare stand, dus alleen '
        'veranderen wat je anders wilt.')
    return "\n".join(delen), intro


def main() -> int:
    ap_ = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap_.add_argument("werkmap", type=Path)
    ap_.add_argument("--uit", type=Path, default=None)
    a = ap_.parse_args()

    docpad = a.werkmap / "document.json"
    if not docpad.exists():
        sys.exit(f"geen document.json in {a.werkmap}. Draai eerst lees_docx.py.")
    doc = json.loads(docpad.read_text(encoding="utf-8"))

    sys.path.insert(0, str(HIER))
    from bouw import STANDAARD_ONTWERP, laad_ontwerp
    ontwerp = (laad_ontwerp(a.werkmap) if (a.werkmap / "ontwerp.json").exists()
               else dict(STANDAARD_ONTWERP))

    # Wat de bron níét heeft, hoort ook niet als stand in de widget te
    # staan: anders komt er een besluit terug dat nergens over gaat.
    apparaat = doc.get("apparaat", {})
    if not (apparaat.get("voetnoten") or apparaat.get("eindnoten")):
        ontwerp["noten"] = "geen"
    if not apparaat.get("bronnenlijst"):
        ontwerp["bronnenlijst"] = "geen"
    if not doc.get("telling", {}).get("beelden") and ontwerp["beeld"] == "uit-bron":
        ontwerp["beeld"] = "geen"

    secties, intro = bouw_secties(doc, ontwerp)
    fonts = FONTS.read_text(encoding="utf-8") if FONTS.exists() else ""
    uit = a.uit or (a.werkmap / "ontwerpwidget.html")
    uit.write_text(SJABLOON.format(
        titel=_esc(doc.get("titel") or a.werkmap.name),
        intro=_esc(intro), secties=secties, fonts=fonts,
        maten=json.dumps(MATEN, ensure_ascii=False),
    ), encoding="utf-8")

    print(json.dumps({
        "widget": str(uit),
        "kb": round(uit.stat().st_size / 1024),
        "besluiten": ["model", "register", "formaat", "opener", "dichtheid",
                      "omslag", "inhoudsopgave", "dubbelzijdig", "nummering",
                      "noten", "bronnenlijst", "citaatstijl", "bijlagen",
                      "beeld", "omslagtekst"],
        "weggelaten": [n for n, aanwezig in (
            ("noten", bool(apparaat.get("voetnoten") or apparaat.get("eindnoten"))),
            ("bronnenlijst", bool(apparaat.get("bronnenlijst"))),
            ("bijlagen", bool(apparaat.get("bijlagen"))),
            ("citaatstijl", bool(apparaat.get("citaten", {}).get("auteur_jaar"))),
        ) if not aanwezig],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
