#!/usr/bin/env python3
"""De ontwerpwidget: alle vormbesluiten op één pagina, met een preview.

Het vragenvuur van deze skill is met achtentwintig besluiten, verspreid
over ruim dertig velden, veel te lang geworden voor een gesprek. Vier per
keer door een keuzewidget betekent zeven rondes, en na de tweede weet
niemand meer wat er in de eerste is gekozen. Dus: één pagina, alles zichtbaar, en een schematische preview
die meebeweegt.

Wat deze widget anders maakt dan een formulier: hij wordt **per rapport
gegenereerd**. Hij leest `document.json` en biedt alleen aan wat er
werkelijk ligt. Geen bronnenlijst in het brondocument betekent geen keuze
tussen apa en genummerd; geen bijlagekoppen betekent geen bijlagevraag;
zijn er geen noten, dan vervalt de vraag waar ze moeten staan. Dat is
belangrijker dan het lijkt — de meest gestelde vraag in een intake is er
een die de gebruiker niet kan beantwoorden omdat hij over iets gaat wat
er niet is.

Het tweede wat hij anders doet: hij legt uit. De gebruiker kent deze
skill niet. `kantlijn`, `register` en `dichtheid` zijn woorden van
binnen de skill, en een keuzeknop met alleen zo'n woord erop is geen
vraag maar een raadsel. Elk veld zegt daarom wat je ervoor terugkrijgt,
en elk blok begint met één regel die zegt waar het over gaat en of je
het gerust kunt overslaan.

Het derde: hij laat bovenaan zien wat er niet gevraagd maar gezien is.
`lees_docx.py` legt naast de wijzigingsvoorstellen zes waarnemingen over
het document als geheel vast — een Engelse bron, koppen die zichzelf
nummeren, een figuur die een browser niet kan tonen — en die sturen de
vormbesluiten eronder. Ze staan daarom bóven de vraagblokken, elk met
wat er is gezien en wat ermee gebeurt; bij de twee die een besluit
hieronder raken staat erbij welk. Is er niets gezien, dan staat er
niets: een kopje met "geen bevindingen" eronder kost de lezer aandacht
en geeft er niets voor terug.

De preview is een **schema en geen zetproef**: het laat de omslag, de
marges, de kolommen, de band en de folio zien, en het reageert op elke
knop. De echte zetting staat in de drie keuzekaarten in
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
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
WORTEL = HIER.parent.parent
FONTS = WORTEL / "assets" / "documenten" / "fonts" / "fonts.css"

# De merkwaarden komen uit de merklaag en staan hier niet. De widget is een
# HTML-pagina en geen rapport, dus hij kan `stijl.css` niet gebruiken — maar
# het veld in de preview hoort wél dezelfde kleur te hebben als het veld op de
# omslag, anders kiest de gebruiker een kleur die hij niet krijgt.
sys.path.insert(0, str(WORTEL / "scripts" / "gedeeld"))
from merk import css_variabelen  # noqa: E402


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
{merk}
/* Wat alleen de widget nodig heeft. De kleuren, het verloop en de letters
   staan in het merkblok hierboven; dit zijn de drie waarden die van dit
   formulier zijn en van niets anders: navy op alpha voor een haarlijn en
   voor een stille regel, en de tafel waarop de kaarten liggen. */
:root {{
  --lijn:  rgba(var(--navy-rgb), .16);
  --zacht: rgba(var(--navy-rgb), .70);
  --tafel: #EFEEF2;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; padding: 28px 30px 60px; background: var(--tafel); color: var(--navy);
  font-family: var(--brood); font-weight: 300; font-size: 15px; line-height: 1.5;
}}
h1 {{ font-family: var(--display); font-weight: 800; font-size: 27px;
     letter-spacing: -.015em; margin: 0 0 8px; }}
p.intro {{ margin: 0 0 6px; max-width: 68ch; }}
p.tel {{ margin: 0 0 22px; font-size: 12.5px; color: var(--zacht); max-width: 68ch; }}
h2 {{ font-family: var(--display); font-weight: 800; font-size: 13px;
     letter-spacing: .13em; text-transform: uppercase; color: var(--oranje);
     margin: 0 0 10px; padding-top: 12px; border-top: 3px solid var(--oranje);
     display: inline-block; }}
.blad {{ display: grid; grid-template-columns: minmax(0,1fr) 330px; gap: 34px;
        align-items: start; max-width: 1180px; }}
.kaart {{ background: #fff; padding: 20px 22px 22px; margin-bottom: 16px;
         box-shadow: 0 1px 3px rgba(var(--navy-rgb),.10); }}
.toelicht {{ margin: 0 0 16px; font-size: 12.5px; line-height: 1.5;
            color: var(--zacht); max-width: 74ch; }}
.rij {{ display: grid; grid-template-columns: 172px minmax(0,1fr); gap: 12px 16px;
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
/* Een stand die bij dít document de goede is, krijgt een streep. Alleen
   aanwijzen, niet aanvinken: welke stand het wordt blijft een besluit
   van de gebruiker. */
.opt.wijs span {{ border-color: var(--oranje);
                 box-shadow: inset 0 -3px 0 var(--oranje); }}
.stip {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%;
        margin-right: 7px; border: 1px solid rgba(var(--navy-rgb),.28); }}
.uitleg {{ grid-column: 2; font-size: 12.5px; color: var(--zacht);
          line-height: 1.5; margin: -8px 0 0; }}
.slot {{ font-size: 12.5px; color: var(--zacht); line-height: 1.5;
        margin: 14px 0 0; max-width: 74ch; }}
input[type=text] {{
  width: 100%; padding: 7px 10px; border: 1px solid var(--lijn);
  font-family: var(--brood); font-size: 14px; color: var(--navy); background: #fff;
}}
input[type=number] {{
  width: 82px; padding: 7px 10px; border: 1px solid var(--lijn);
  font-family: var(--brood); font-size: 14px; color: var(--navy); background: #fff;
}}
.getal {{ display: flex; align-items: center; gap: 10px; }}
.getal span {{ font-size: 13px; color: var(--zacht); }}
.aan {{ display: flex; align-items: center; gap: 9px; font-size: 13.5px; }}
.aan input {{ width: 17px; height: 17px; accent-color: var(--navy); }}
select {{ padding: 7px 10px; border: 1px solid var(--lijn); font-family: var(--brood);
         font-size: 14px; color: var(--navy); background: #fff; max-width: 100%; }}

/* De zes aanvinkbare onderdelen. Naast elkaar, want het is één vraag:
   wat komt er in het rapport te staan. */
.vinkjes {{ display: grid; grid-template-columns: repeat(2, minmax(0,1fr));
           gap: 12px 20px; margin-bottom: 18px; }}
.vink {{ display: grid; grid-template-columns: 17px minmax(0,1fr); gap: 10px;
        align-items: start; cursor: pointer; }}
.vink input {{ width: 17px; height: 17px; margin: 3px 0 0; accent-color: var(--navy); }}
.vink span {{ font-size: 12.5px; line-height: 1.45; color: var(--zacht); }}
.vink b {{ display: block; font-size: 13.5px; font-weight: 700; color: var(--navy); }}

/* --- wat er eerst beslist moet worden ------------------------------ */
/* Deze kaart staat boven de vormblokken, want het zijn waarnemingen die
   de keuzes eronder sturen en niet andersom. De lijn links zet hem apart
   van de vraagblokken zonder alarm te slaan; er is niets kapot, er valt
   iets te beslissen. */
.eerst {{ border-left: 4px solid var(--oranje); }}
.bev + .bev {{ margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--lijn); }}
.bev h3 {{ font-family: var(--display); font-weight: 700; font-size: 14px;
          margin: 0 0 5px; }}
.bev p {{ margin: 0; font-size: 12.5px; line-height: 1.5; color: var(--zacht);
         max-width: 74ch; }}
.bev p.doen {{ margin-top: 5px; color: var(--navy); }}
.bev .vb {{ color: var(--navy); }}

/* --- de preview --------------------------------------------------- */
/* De kolom blijft staan terwijl links wordt gescrold. Op een laag scherm
   is hij hoger dan het venster; dan scrolt hij zelf, want anders valt de
   kopieerknop eronder weg en dat is de enige knop die telt. */
.zij {{ position: sticky; top: 24px; max-height: calc(100vh - 48px);
       overflow-y: auto; }}
.preview {{ background: #fff; padding: 18px; box-shadow: 0 1px 3px rgba(var(--navy-rgb),.10); }}
.schetsen {{ display: grid; grid-template-columns: 92px minmax(0,1fr);
            gap: 16px; align-items: start; }}
figure {{ margin: 0; }}
figcaption {{ margin-top: 7px; font-size: 11.5px; line-height: 1.35;
             color: var(--zacht); }}
.blad-schets {{ position: relative; width: 100%; aspect-ratio: 794 / 1039;
               background: #fff; border: 1px solid var(--lijn); overflow: hidden; }}
.blad-schets.a4 {{ aspect-ratio: 794 / 1123; }}
.blad-schets.liggend {{ aspect-ratio: 1123 / 794; }}
.omslag-schets {{ background: var(--oranje); color: var(--navy);
                 border-color: transparent; }}
.omslag-schets.uit {{ opacity: .22; }}
.omslag-titel, .omslag-regel, .omslag-merk {{ position: absolute;
  background: currentColor; }}
.omslag-titel {{ left: 12%; right: 22%; top: 44%; height: 5.5%; opacity: .92; }}
.omslag-regel {{ left: 12%; right: 46%; top: 53%; height: 3%; opacity: .55; }}
.omslag-merk  {{ left: 12%; right: 62%; bottom: 9%; height: 2.6%; opacity: .8; }}
.band {{ position: absolute; top: 0; left: 0; right: 0; height: 22%;
        background: var(--oranje); }}
.band::after {{ content: ""; position: absolute; width: 150%; height: 150%;
               left: -60%; top: -95%; border-radius: 50%;
               background: rgba(var(--navy-rgb),.10); }}
.zetspiegel {{ position: absolute; inset: 7.3% 5.9% 9.3% 7.8%; display: flex; gap: 3.8%; }}
.kolom {{ background: repeating-linear-gradient(
            transparent 0 3px, rgba(var(--navy-rgb),.30) 3px 4px); flex: 1; }}
.kant {{ flex: 0 0 21.5%; background: repeating-linear-gradient(
           transparent 0 4px, rgba(var(--navy-rgb),.14) 4px 5px); }}
.folio {{ position: absolute; bottom: 3.6%; right: 5.9%; width: 8%; height: 1.4%;
         background: var(--oranje); }}
.meting {{ margin-top: 14px; font-size: 12.5px; line-height: 1.45; }}
.meting b {{ font-family: var(--display); font-weight: 700; }}
.let {{ margin-top: 10px; padding: 9px 11px; background: var(--navy-tint);
       font-size: 12.5px; line-height: 1.45; }}

/* --- de uitvoer ---------------------------------------------------- */
.uit {{ margin-top: 16px; }}
pre {{ background: var(--navy); color: #EDECF4; padding: 15px 17px; margin: 0;
      font: 400 12.5px/1.55 ui-monospace, 'SF Mono', Menlo, monospace;
      overflow-x: auto; white-space: pre-wrap; word-break: break-word;
      max-height: 470px; overflow-y: auto; }}
button {{ font-family: var(--display); font-weight: 700; font-size: 13px;
         letter-spacing: .04em; padding: 10px 18px; border: 0; cursor: pointer;
         background: var(--oranje); color: var(--navy); margin-top: 10px; }}
button:active {{ transform: translateY(1px); }}
.klaar {{ margin-left: 10px; font-size: 13px; color: var(--emerald); font-weight: 700; }}
</style>
</head>
<body>

<h1>Ontwerp van het rapport</h1>
<p class="intro">{intro}</p>
<p class="tel">{tel}</p>

<div class="blad">
  <div>
{secties}
  </div>

  <div class="zij">
    <div class="preview">
      <h2 style="border-color: var(--navy); color: var(--navy)">Schets</h2>
      <div class="schetsen">
        <figure>
          <div class="blad-schets omslag-schets" id="p-omslag">
            <div class="omslag-titel"></div>
            <div class="omslag-regel"></div>
            <div class="omslag-merk"></div>
          </div>
          <figcaption id="p-omslag-bij">de omslag</figcaption>
        </figure>
        <figure>
          <div class="blad-schets" id="schets">
            <div class="band" id="p-band" hidden></div>
            <div class="zetspiegel" id="p-zet">
              <div class="kolom"></div>
            </div>
            <div class="folio"></div>
          </div>
          <figcaption>een pagina met tekst</figcaption>
        </figure>
      </div>
      <p class="meting" id="p-meting"></p>
      <p class="let">Dit is een schema en geen zetproef: het laat het kleurveld
        van de omslag, de marges, de kolommen en de band zien. Hoe het er écht
        uitziet staat in de drie keuzekaarten die hierbij horen.</p>
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

//: Wat de schets van de omslag laat zien. Dezelfde zes velden als in
//: `bouw.py`; het verloop is het huisverloop uit stijl.css.
const VELD = {{
  oranje:  {{vlak: 'var(--oranje)',    inkt: 'var(--navy)'}},
  verloop: {{vlak: 'var(--verloop)',   inkt: 'var(--navy)'}},
  navy:    {{vlak: 'var(--navy)',      inkt: 'var(--wit)'}},
  violet:  {{vlak: 'var(--violet)',    inkt: 'var(--wit)'}},
  mint:    {{vlak: 'var(--mint-tint)', inkt: 'var(--navy)'}},
  wit:     {{vlak: 'var(--wit)',       inkt: 'var(--navy)'}},
}};

const EXTRA = ['overOns', 'team', 'colofon', 'achterblad'];

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
  // De vier extra pagina's staan als losse vinkjes in het formulier maar
  // horen in `ontwerp.json` als één blok: `elementen`.
  const el = {{}};
  for (const k of EXTRA) {{
    el[k] = o['elementen.' + k] === true;
    delete o['elementen.' + k];
  }}
  o.elementen = el;
  // Twee toestemmingen. Ze staan als ja/nee in het formulier omdat een
  // uitgevinkt hokje niet laat zien dat "nee" de stand is.
  for (const k of ['herindelen', 'beeldtekst']) o[k] = o[k] === 'ja';
  o.katern = Math.max(1, parseInt(o.katern, 10) || 4);
  for (const k of ['rapporttitel','ondertitel','opdrachtgever','datum','beeldmap']) {{
    if (!o[k]) o[k] = null;
  }}
  // Hoofdstuknummers heeft drie standen en de derde is een woord, geen
  // ja of nee. Als vinkje ingelezen zou "uit de bron" als "aan" terugkomen
  // en dan telt de skill alsnog zelf.
  o.hoofdstuknummers = o.hoofdstuknummers === 'uit-bron'
    ? 'uit-bron' : o.hoofdstuknummers === 'ja';
  // De taal staat in het formulier als twee knoppen plus een vrij veld,
  // en in `ontwerp.json` als één ISO-code. Leeg mag hij niet zijn: dan
  // zet Chromium af zonder woordenboek en vervalt de afbreking stil.
  const code = (o.taalkeus === 'anders'
    ? (o.taalAnders || '') : (o.taalkeus || 'nl')).trim();
  delete o.taalkeus; delete o.taalAnders;
  // De taal vooraan, want het is het besluit dat als eerste vaststaat.
  return {{ taal: code || 'nl', ...o }};
}}

function ververs() {{
  const o = lees();
  const m = MAAT[o.model] || MAAT.breed;
  const schets = document.getElementById('schets');
  const omslag = document.getElementById('p-omslag');
  for (const el of [schets, omslag]) {{
    el.classList.toggle('a4', o.formaat === 'a4');
    el.classList.toggle('liggend', o.formaat === 'a4-liggend');
  }}

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
                 zacht: 'var(--mint-tint)', contrast: 'var(--violet)'}};
  band.style.background = kleur[o.register] || 'var(--oranje)';
  zet.style.paddingTop = o.opener === 'band' ? '17%' : '0';

  // Het kleurveld van de omslag. Wit krijgt een lijn, anders is er geen
  // omslag te zien; dat is meteen het argument voor de standaard.
  const v = VELD[o.omslagveld] || VELD.oranje;
  omslag.style.background = v.vlak;
  omslag.style.color = v.inkt;
  omslag.style.borderColor = o.omslagveld === 'wit' ? 'var(--lijn)' : 'transparent';
  omslag.classList.toggle('uit', !o.omslag);
  document.getElementById('p-omslag-bij').textContent =
    o.omslag ? 'de omslag, veld ' + o.omslagveld : 'geen omslag';

  const per = {{ruim: 0.88, gemiddeld: 1, dicht: 1.12}}[o.dichtheid] || 1;
  let tekst = '<b>' + m.tekens + '</b> tekens per regel &middot; brood op <b>' +
    m.brood + '</b> &middot; ongeveer <b>' + Math.round(m.woorden * per) +
    '</b> woorden per pagina bij dichtheid <b>' + o.dichtheid + '</b>';
  if (o.drukklaar) {{
    tekst += ". Gaat naar de drukker: het aantal pagina's wordt achteraan met " +
      "blanco pagina's aangevuld tot een veelvoud van <b>" + o.katern + "</b>.";
  }}
  document.getElementById('p-meting').innerHTML = tekst;

  // Een taal buiten de tabel krijgt wel de goede afbreking maar
  // Nederlandse woorden. Dat hoort hier te staan en niet pas op stderr
  // van het bouwscript, want hier wordt de taal gekozen.
  const code = String(o.taal || 'nl').toLowerCase();
  const kort = code.split('-')[0];
  const let_ = document.getElementById('taal-let');
  if (kort !== 'nl' && kort !== 'en') {{
    let_.innerHTML = 'Voor <b>' + o.taal + '</b> heeft de skill geen eigen ' +
      'woorden. De tekst wordt wél in die taal afgebroken, maar Hoofdstuk, ' +
      'Figuur en Noten blijven Nederlands. Het bouwscript zegt dat er ook bij.';
  }} else if (code !== kort) {{
    // en-GB krijgt de Engelse woorden: een streekvariant heeft dezelfde.
    let_.innerHTML = 'Voor <b>' + o.taal + '</b> pakt de skill de ' +
      (kort === 'nl' ? 'Nederlandse' : 'Engelse') + ' woorden — een ' +
      'streekvariant heeft dezelfde — en de tekst wordt op ' + o.taal +
      ' afgebroken.';
  }} else {{
    let_.textContent = 'Nederlands en Engels zijn de twee talen waarvoor de ' +
      'skill eigen woorden heeft. Bij deze twee klopt allebei: de afbreking ' +
      'en de toegevoegde woorden.';
  }}

  document.getElementById('uit').textContent = JSON.stringify(o, null, 1);
}}

// Wie een code in het vrije veld typt, heeft de knop ernaast bedoeld.
// Zonder dit blijft `nl` aangevinkt en gaat de getypte code verloren.
const taalVrij = document.querySelector('[data-veld="taalAnders"]');
taalVrij.addEventListener('input', () => {{
  const anders = document.querySelector('[data-veld="taalkeus"][value="anders"]');
  if (taalVrij.value.trim()) anders.checked = true;
}});

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

#: De kleur onder elke omslagknop. Alleen om de knop te laten zien wat
#: hij kiest; het echte veld staat in `stijl.css`. Als variabele en niet als
#: waarde, want de stip hoort dezelfde kleur te hebben als het blad — en die
#: komt uit het merkblok dat bovenaan de widget staat.
VELDKLEUREN = {
    "oranje": "var(--oranje)",
    "verloop": "var(--verloop)",
    "navy": "var(--navy)",
    "violet": "var(--violet)",
    "mint": "var(--mint-tint)",
    "wit": "var(--wit)",
}


def keuze(veld: str, label: str, opties: list, gekozen: str, uitleg: str = "",
          kleuren: dict | None = None, nadruk: str | None = None) -> str:
    """Een rij knoppen waarvan er één aan staat.

    `nadruk` streept één stand aan omdat een bevinding bovenaan zegt dat
    hij hier de goede is. Het zet hem niet aan: wat er in het rapport
    komt te staan blijft een besluit van de gebruiker, en een widget die
    zelf alvast kiest laat niet zien dat er gekozen is.
    """
    knoppen = []
    for waarde, tekst in opties:
        aan = " checked" if waarde == gekozen else ""
        wijs = " wijs" if nadruk is not None and waarde == nadruk else ""
        stip = ""
        if kleuren and waarde in kleuren:
            stip = f'<i class="stip" style="background:{kleuren[waarde]}"></i>'
        knoppen.append(
            f'<label class="opt{wijs}"><input type="radio" name="{veld}" '
            f'data-veld="{veld}" value="{_esc(waarde)}"{aan}>'
            f'<span>{stip}{_esc(tekst)}</span></label>')
    hulp = f'<p class="uitleg">{uitleg}</p>' if uitleg else ""
    return (f'<div class="rij"><label>{_esc(label)}</label>'
            f'<div class="opties">{"".join(knoppen)}</div>{hulp}</div>')


def vinkje(veld: str, label: str, tekst: str, aan: bool, uitleg: str = "") -> str:
    c = " checked" if aan else ""
    hulp = f'<p class="uitleg">{uitleg}</p>' if uitleg else ""
    return (f'<div class="rij"><label>{_esc(label)}</label>'
            f'<label class="aan"><input type="checkbox" data-veld="{veld}"{c}>'
            f'<span>{_esc(tekst)}</span></label>{hulp}</div>')


def vink(veld: str, titel: str, tekst: str, aan: bool) -> str:
    """Eén onderdeel uit het blok "Wat er in komt"."""
    c = " checked" if aan else ""
    return (f'<label class="vink"><input type="checkbox" data-veld="{veld}"{c}>'
            f'<span><b>{_esc(titel)}</b>{_esc(tekst)}</span></label>')


def tekstveld(veld: str, label: str, waarde, plaatshouder: str = "") -> str:
    return (f'<div class="rij"><label>{_esc(label)}</label>'
            f'<input type="text" data-veld="{veld}" value="{_esc(waarde)}" '
            f'placeholder="{_esc(plaatshouder)}"></div>')


def getalveld(veld: str, label: str, waarde, achter: str = "", uitleg: str = "",
              laag: int = 1, hoog: int = 64) -> str:
    hulp = f'<p class="uitleg">{uitleg}</p>' if uitleg else ""
    na = f'<span>{_esc(achter)}</span>' if achter else ""
    return (f'<div class="rij"><label>{_esc(label)}</label>'
            f'<div class="getal"><input type="number" data-veld="{veld}" '
            f'value="{_esc(waarde)}" min="{laag}" max="{hoog}" step="1">'
            f'{na}</div>{hulp}</div>')


def keuzelijst(veld: str, label: str, opties: list, gekozen: str,
               uitleg: str = "") -> str:
    regels = []
    for waarde, tekst in opties:
        aan = " selected" if waarde == gekozen else ""
        regels.append(f'<option value="{_esc(waarde)}"{aan}>{_esc(tekst)}</option>')
    hulp = f'<p class="uitleg">{uitleg}</p>' if uitleg else ""
    return (f'<div class="rij"><label>{_esc(label)}</label>'
            f'<select data-veld="{veld}">{"".join(regels)}</select>{hulp}</div>')


def kaart(titel: str, toelicht: str, *stukken: str, klasse: str = "") -> str:
    """Een blok met een kop en één regel die zegt waar het over gaat.

    Die regel is niet decoratief. Wie deze skill niet kent, moet aan de
    kop kunnen zien of dit blok hem aangaat of dat hij het kan laten
    staan; zonder die regel wordt elk blok een vraag.
    """
    return (f'<div class="kaart{(" " + klasse) if klasse else ""}">'
            f'<h2>{_esc(titel)}</h2>'
            f'<p class="toelicht">{toelicht}</p>{"".join(stukken)}</div>')


#: De zeven waarnemingen die `lees_docx.py` als `vormbesluit` meegeeft, in
#: de volgorde waarin ze hier komen te staan. Een signaal dat hier niet
#: in staat, is een wijzigingsvoorstel over één blok en hoort niet in
#: deze widget: dat komt pas ná het ontwerp aan de beurt.
VORMBESLUITEN = ("bron-niet-nederlands", "koppen-een-niveau-te-diep",
                 "kop-nummert-zichzelf", "beeld-niet-renderbaar",
                 "beeld-buiten-de-stroom", "kop-zonder-inhoud",
                 "vetregel-als-kop")


def _stuks(n: int, enkel: str, meer: str) -> str:
    return f"{n} {enkel if n == 1 else meer}"


def _voorbeelden(waarden: list) -> str:
    """Eén of twee voorbeelden uit het document, tussen aanhalingstekens.

    Twee is het maximum. Een derde maakt van een waarneming een lijst,
    en een lijst wordt overgeslagen; hier hoeft de gebruiker alleen te
    herkennen waar het over gaat.
    """
    stuks = [f'<span class="vb">"{_esc(w)}"</span>'
             for w in waarden[:2] if str(w or "").strip()]
    return " en ".join(stuks)


def bevinding(sig: dict) -> tuple[str, str, str] | None:
    """Eén vormbesluit als drie stukken tekst: kop, gezien, wat nu.

    De tekst wordt hier opgebouwd uit de getallen in het signaal en niet
    overgenomen uit `wat` en `voor de vorm`. Die twee velden zijn voor
    het gesprek geschreven en staan in de taal van de skill; hier staat
    wat de gebruiker ermee moet, en waar hij dat regelt.
    """
    soort = sig.get("soort")

    if soort == "bron-niet-nederlands":
        sleutel = sig.get("taal") or ""
        naam = str(sleutel).capitalize() or "een andere taal"
        tr = sig.get("treffers") or {}
        return (
            "Het brondocument is niet in het Nederlands geschreven",
            f'Van de {sig.get("woorden", 0)} woorden lopende tekst horen er '
            f'{tr.get(sleutel, 0)} bij het {naam} en {tr.get("nederlands", 0)} '
            f'bij het Nederlands.',
            f'Zet de taal hieronder bij <b>De taal</b> op {naam}; staat er geen '
            f'knop voor, vul dan de ISO-code in het veld ernaast. Doe het nu en '
            f'niet na het bouwen: de taal bepaalt waar elke regel breekt en in '
            f'welke taal de woorden staan die de skill zelf toevoegt.')

    if soort == "koppen-een-niveau-te-diep":
        return (
            "Alle koppen staan een niveau te diep",
            f'{_stuks(sig.get("koppen", 0), "kop", "koppen")}, en de hoogste '
            f'staat op niveau {sig.get("hoogste_niveau", 2)}. Niveau 1 komt niet '
            f'voor — dat gebeurt bij een sjabloon waarin niveau 1 voor de omslag '
            f'was.',
            'De skill kan alle koppen één niveau omhoog schuiven voordat er '
            'gezet wordt. Dat verandert de opmaak en geen woord van de tekst, '
            'en ze vraagt het je eerst. Gebeurt het niet, dan wordt elk '
            'hoofdstuk een sectie: geen hoofdstukopening op de pagina en een '
            'inhoudsopgave zonder bovenste laag.')

    if soort == "kop-nummert-zichzelf":
        niveaus = sig.get("niveaus") or []
        zin = "; ".join(
            f'op niveau {n.get("niveau")} dragen {n.get("genummerd")} van de '
            f'{n.get("koppen")} koppen hun eigen nummer' for n in niveaus)
        vb = _voorbeelden(
            [v for n in niveaus for v in (n.get("voorbeelden") or [])])
        gezien = (zin[:1].upper() + zin[1:]) if zin else "De koppen dragen een nummer"
        return (
            "De koppen dragen hun eigen nummer",
            gezien + (f', bijvoorbeeld {vb}.' if vb else "."),
            'Kies hieronder bij <b>Nummers en zijden</b> de stand <b>uit de '
            'bron overnemen</b>. De skill telt dan niet zelf mee, het nummer '
            'blijft staan waar de auteur het schreef, en het grote cijfer op de '
            'hoofdstukopening wordt uit de kop gelezen. Laat je het op nummeren '
            'staan, dan komt er straks "3 3.2 Werkwijze" op de pagina en in de '
            'inhoudsopgave.')

    if soort == "beeld-niet-renderbaar":
        best = sig.get("bestanden") or []
        aantal = sig.get("aantal", len(best))
        formaten = ", ".join(sorted({b.get("formaat", "") for b in best}))
        vb = _voorbeelden([b.get("naam") for b in best])
        return (
            "Een beeldbestand dat een browser niet kan tonen",
            f'{aantal} van de {sig.get("van", aantal)} beeldbestanden '
            f'{"staat" if aantal == 1 else "staan"} in een formaat dat een '
            f'browser niet opent: {formaten}'
            + (f'. Het gaat om {vb}.' if vb else "."),
            "Het rapport wordt in een browser gezet. Zo'n bestand komt daar "
            "niet als foutmelding op de pagina maar als een leeg vlak, precies "
            "zo groot als de figuur had moeten zijn. Het moet dus vóór het "
            "bouwen vervangen worden door een png of een svg in dezelfde maat; "
            "de skill vraagt wie dat doet en zet er tot die tijd niets neer.")

    if soort == "beeld-buiten-de-stroom":
        best = sig.get("bestanden") or []
        aantal = sig.get("aantal", len(best))
        vb = _voorbeelden([b.get("naam") if isinstance(b, dict) else b
                           for b in best])
        return (
            "Beeld dat buiten de tekst staat",
            _stuks(aantal, "beeldbestand", "beeldbestanden") + " in het "
            "Word-document " + ("wordt" if aantal == 1 else "worden")
            + " door geen enkele alinea genoemd"
            + (f': {vb}.' if vb else "."),
            'Een figuur in een tekstvak, een SmartArt of een beeld in de '
            'koptekst zit niet in de tekststroom. Het is niet ingelezen en het '
            'komt dus ook niet in het rapport. Moet het toch mee, dan vraagt de '
            'skill achter welk blok het hoort: waar het staan moet, staat '
            'nergens in het bestand.')

    if soort == "kop-zonder-inhoud":
        koppen = sig.get("koppen") or []
        aantal = sig.get("aantal", len(koppen))
        vb = _voorbeelden([k.get("tekst") for k in koppen])
        return (
            "Een kop zonder iets eronder",
            _stuks(aantal, "kop heeft", "koppen hebben") + " niets onder zich: "
            "geen alinea, geen lijst, geen tabel, geen beeld en geen diepere kop"
            + (f'. Het gaat om {vb}.' if vb else "."),
            "Zo'n kop is er een die de auteur vergeten is in te vullen, of een "
            'sectie die leeg gebleven is. Gezet komt hij onderaan een pagina te '
            'staan met wit eronder, en in de inhoudsopgave verwijst hij naar '
            'niets. De skill laat hem staan en vraagt of hij weg mag of bij de '
            'volgende hoort — dat is een wijziging in de tekst en die gaat apart '
            'langs jou.')

    if soort == "vetregel-als-kop":
        aantal = sig.get("aantal", 0)
        vb = _voorbeelden(sig.get("voorbeelden") or [])
        return (
            "Vetgezette regels die als tussenkop werken",
            _stuks(aantal, "alinea is", "alinea's zijn") + " volledig "
            "vetgezet, kort, en zonder punt aan het eind, met gewone tekst "
            "eronder" + (f'. Het gaat om {vb}.' if vb else "."),
            'In Word zijn dat alinea\'s en geen koppen, en dat verschil zag de '
            'zetting: zo\'n regel kon als laatste regel van een pagina komen te '
            'staan met zijn tekst op de volgende. Dat gebeurt niet meer — ze '
            'blijven bij hun tekst, en dat is geen keuze. Wat je hieronder bij '
            '<b>De vorm</b> wél kiest, is of ze ook de lucht van een tussenkop '
            'krijgen of vetgezette alinea\'s blijven zoals in Word.')

    return None


def bevindingenkaart(gevonden: dict) -> str:
    """De kaart met de vormbesluiten, of niets.

    Niets als er niets is gezien. Een kopje met "geen bevindingen"
    eronder is ruis: het vraagt de aandacht van de lezer en geeft er
    niets voor terug.
    """
    stukken = []
    for soort in VORMBESLUITEN:
        sig = gevonden.get(soort)
        if not sig:
            continue
        gemaakt = bevinding(sig)
        if not gemaakt:
            continue
        titel, gezien, doen = gemaakt
        stukken.append(f'<div class="bev"><h3>{_esc(titel)}</h3>'
                       f'<p>{gezien}</p><p class="doen">{doen}</p></div>')
    if not stukken:
        return ""
    return kaart(
        "Dit moet je eerst beslissen",
        "Wat er bij het inlezen aan het document zelf opviel — niet aan de "
        "tekst, aan de vorm ervan. Het staat bovenaan omdat het de keuzes "
        "hieronder stuurt. Per bevinding staat er eerst wat er gezien is en "
        "daaronder wat ermee gebeurt; raakt het een keuze hieronder, dan staat "
        "erbij welke. Achteraf hierop terugkomen kost een nieuwe zetting.",
        *stukken, klasse="eerst")


def bouw_secties(doc: dict, ontwerp: dict,
                 vormbesluiten: dict | None = None) -> tuple[str, str, str]:
    ap = doc.get("apparaat", {})
    tel = doc.get("telling", {})
    heeft_noten = bool(ap.get("voetnoten") or ap.get("eindnoten"))
    heeft_lijst = bool(ap.get("bronnenlijst"))
    heeft_bijlagen = bool(ap.get("bijlagen"))
    heeft_beeld = bool(tel.get("beelden"))
    citaten = ap.get("citaten", {})
    el = ontwerp.get("elementen") or {}
    gevonden = vormbesluiten or {}
    eigen_nummers = bool(gevonden.get("kop-nummert-zichzelf"))
    vetregels = gevonden.get("vetregel-als-kop") or {}

    delen = []

    # -- wat er eerst beslist moet worden ------------------------------
    # Boven de vormblokken: het zijn waarnemingen die de keuzes eronder
    # sturen. Andersom staat een gebruiker een taal te kiezen zonder te
    # weten dat zijn bron Engels is.
    eerst = bevindingenkaart(gevonden)
    if eerst:
        delen.append(eerst)

    # -- de taal -------------------------------------------------------
    taal = str(ontwerp.get("taal") or "nl").strip() or "nl"
    taalkeus = taal.lower() if taal.lower() in ("nl", "en") else "anders"
    # Wijst een bevinding een taal aan, dan wordt die stand aangestreept.
    # Aanvinken doet de widget niet: de taal van het rapport is niet
    # hetzelfde als de taal van de bron, en dat verschil is een besluit.
    bron = gevonden.get("bron-niet-nederlands") or {}
    gemeten = {"nederlands": "nl", "engels": "en",
               "duits": "de", "frans": "fr"}.get(bron.get("taal") or "")
    delen.append(kaart(
        "De taal",
        "In welke taal dit rapport gezet wordt. Eén vraag, en hij staat "
        "vooraan omdat hij vóór het bouwen vast moet staan.",
        keuze("taalkeus", "Taal van het rapport",
              [("nl", "Nederlands"), ("en", "Engels"),
               ("anders", "een andere taal")],
              taalkeus,
              "De taal doet twee dingen. Ze bepaalt met welk woordenboek de "
              "tekst wordt afgebroken, en dus waar elke regel breekt en waar "
              "een pagina vol is. En ze bepaalt in welke taal de woorden staan "
              "die deze skill zelf toevoegt: <b>Hoofdstuk 3</b>, <b>Figuur "
              "7</b>, <b>Noten</b>. Alle andere tekst komt woordelijk uit het "
              "Word-document en blijft staan zoals hij er staat.",
              nadruk=(None if gemeten is None
                      else (gemeten if gemeten in ("nl", "en") else "anders"))),
        tekstveld("taalAnders", "Andere taal",
                  "" if taalkeus != "anders" else taal,
                  "ISO-code, bijvoorbeeld de, fr of en-GB"),
        '<p class="slot" id="taal-let"></p>',
        '<p class="slot">Kies de taal vóór het bouwen. Achteraf omzetten '
        'verschuift de regelval over het hele rapport, en een alinea die daar '
        'een regel langer van wordt valt onder de rand van zijn kader weg — '
        'zonder foutmelding en zonder dat iemand het ziet.</p>'))

    # -- de vorm -------------------------------------------------------
    delen.append(kaart(
        "De vorm",
        "Hoe een pagina eruitziet: de kolommen, de kleur, het papier. Alles "
        "staat op de stand die voor de meeste rapporten klopt, dus je kunt dit "
        "blok overslaan. De schets rechts beweegt mee.",
        keuze("model", "Kolommen op de pagina",
              [("breed", "één brede kolom"), ("kantlijn", "kolom met kantlijn"),
               ("dubbel", "twee kolommen"), ("flexibel", "wisselend")],
              ontwerp["model"],
              "<b>Eén brede kolom</b> is de veilige keuze: de tekst loopt over "
              "de volle breedte. <b>Kolom met kantlijn</b> zet er een smalle "
              "kolom naast waar noten, bijschriften en tussenkopjes in staan; "
              "kies dat alleen als er zulke tekst is. <b>Twee kolommen</b> "
              "levert het kortste rapport, maar kortere regels. "
              "<b>Wisselend</b> laat de opmaak per hoofdstuk kiezen tussen die "
              "drie."),
        keuze("register", "Kleurgebruik",
              [("helder", "helder"), ("diep", "diep"),
               ("zacht", "zacht"), ("contrast", "contrast")],
              ontwerp["register"],
              "<b>Helder</b> is wit papier met navy tekst en oranje accenten, "
              "en dat houdt tachtig pagina's vol. <b>Diep</b> zet dezelfde "
              "tekstpagina's, maar laat elk hoofdstuk op een navy vlak "
              "beginnen. <b>Zacht</b> ruilt het oranje accent voor emerald en "
              "een lichte munttint: rustiger, voor een evaluatie. "
              "<b>Contrast</b> zet violet naast oranje, voor een rapport dat "
              "uit losse cases bestaat. Geen van de vier raakt de tekst; ze "
              "verschillen pas echt op de hoofdstukopening hieronder."),
        keuze("formaat", "Papierformaat",
              [("sfnl", "SFNL 210 × 275 mm"), ("a4", "A4"),
               ("a4-liggend", "A4 liggend")],
              ontwerp["formaat"],
              "SFNL 210 × 275 is de maat van de jaarrapporten: iets breder en "
              "korter dan A4, en het moet naar een drukker. A4 past in de "
              "kantoorprinter en in een ordner."),
        keuze("opener", "Begin van een hoofdstuk",
              [("nummer", "een nummer boven de titel"),
               ("band", "een gekleurde band"),
               ("blad", "een hele pagina")],
              ontwerp["opener"],
              "Wat een hoofdstuk aankondigt, en wat dat aan ruimte kost. Het "
              "<b>nummer</b> kost niets: de tekst begint gewoon bovenaan. De "
              "<b>band</b> is een kleurvlak over de bovenkant van die pagina "
              "en kost ongeveer een kwart pagina. Een <b>hele pagina</b> kost "
              "er precies één per hoofdstuk, dus dat loont pas vanaf een stuk "
              "of veertig pagina's."),
        keuze("kopregel", "Kopregel bovenaan",
              [("beide", "rapport links, hoofdstuk rechts"),
               ("hoofdstuk", "alleen het hoofdstuk"),
               ("rapport", "alleen de rapporttitel"),
               ("geen", "geen kopregel")],
              ontwerp.get("kopregel", "beide"),
              "De regel in kleine cursieve letters bovenaan elke pagina, met "
              "een haarlijn ernaast. Hij zegt waar je bent in een rapport dat "
              "iemand halverwege opslaat. <b>Rapport links, hoofdstuk "
              "rechts</b> zet één naam per zijde aan de buitenkant: de "
              "linkerpagina draagt de rapporttitel, de rechter de "
              "hoofdstuknaam. Wordt het rapport in één zitting gelezen, of "
              "heeft het geen hoofdstukken, dan zegt die regel op elke pagina "
              "hetzelfde en is <b>geen kopregel</b> de rustigere pagina. Op de "
              "pagina waar een hoofdstuk begint staat hij nooit — daar staat "
              "de titel zelf al."),
        keuze("dichtheid", "Hoeveel tekst op een pagina",
              [("ruim", "ruim"), ("gemiddeld", "gemiddeld"), ("dicht", "dicht")],
              ontwerp["dichtheid"],
              "Dit verschuift twee dingen: het aantal regels dat op een pagina "
              "past — ongeveer drie heen of terug — en de lucht tussen alinea's "
              "en kopjes. Wat het niet doet is de letter kleiner maken; die "
              "blijft in alle drie de standen gelijk. Ruim leest rustiger, "
              "dicht scheelt pagina's."),
        # Alleen aanbieden als het document ze heeft. Een keuze over iets
        # wat er niet is, is een vraag die de gebruiker niet kan
        # beantwoorden — dezelfde regel als bij de noten en de
        # bronnenlijst.
        keuze("vetkop", "Vetgezette tussenkopjes",
              [("binden", "laten zoals ze staan"),
               ("als-kop", "als tussenkop zetten")],
              ontwerp.get("vetkop", "binden"),
              f'Dit document heeft {vetregels.get("aantal", 0)} regels die '
              f'volledig vetgezet zijn en zich als tussenkop gedragen — zie de '
              f'bevinding bovenaan. Ze blijven in beide standen bij hun tekst; '
              f'dat is geen keuze. <b>Laten zoals ze staan</b> houdt ze precies '
              f'zoals in Word: vetgezette alinea\'s in de tekst. <b>Als '
              f'tussenkop zetten</b> geeft ze de lucht van een kopje erboven, '
              f'zodat ze op de pagina als kop lezen. De letter blijft in beide '
              f'gelijk, en de tekst verandert in geen van de twee.')
        if vetregels else "",
    ))

    # -- wat er in komt ------------------------------------------------
    delen.append(kaart(
        "Wat er in komt",
        "Welke pagina's het rapport krijgt naast de tekst uit het "
        "Word-document. De eerste twee vult de skill zelf; bij de vier "
        "daaronder moet de tekst van jou komen, en die staan daarom "
        "standaard uit. Sla je dit blok over, dan krijg je een omslag en een "
        "inhoudsopgave en verder niets erbij.",
        '<div class="vinkjes">' + "".join([
            vink("omslag", "Omslag",
                 "een voorblad met de titel op een kleurveld",
                 bool(ontwerp["omslag"])),
            vink("inhoudsopgave", "Inhoudsopgave",
                 "met paginanummers, geteld na het zetten",
                 bool(ontwerp["inhoudsopgave"])),
            vink("elementen.overOns", "Over ons",
                 "een pagina over Social Finance NL",
                 bool(el.get("overOns"))),
            vink("elementen.team", "Team",
                 "wie eraan gewerkt heeft, met naam en rol",
                 bool(el.get("team"))),
            vink("elementen.colofon", "Colofon",
                 "de verantwoording achterin",
                 bool(el.get("colofon"))),
            vink("elementen.achterblad", "Achterblad",
                 "de achterkant, in dezelfde kleur als de omslag",
                 bool(el.get("achterblad"))),
        ]) + "</div>",
        keuze("inhoudDiepte", "Inhoudsopgave toont",
              [("1", "alleen hoofdstukken"),
               ("2", "hoofdstukken en secties")],
              str(ontwerp["inhoudDiepte"]),
              "Bij een rapport met veel tussenkopjes wordt de tweede stand "
              "snel twee pagina's lang."),
        '<p class="slot">De titel van de omslag vul je verderop in, en de '
        'paginanummers van de inhoudsopgave komen uit de zetting. De vier '
        'andere pagina\'s zijn de enige plek in het hele rapport waar tekst '
        'staat die niet in het Word-document stond. Die tekst schrijf je zelf '
        'of hij gaat langs jou ter goedkeuring, en hij komt in een '
        '<code>paginas.json</code> naast het rapport te staan. Staat er een '
        'aan zonder tekst, dan wordt die pagina niet gemaakt en krijg je dat '
        'te horen: een lege teampagina is erger dan geen teampagina. Het '
        'achterblad is de uitzondering — dat bestaat ook met alleen het merk '
        'erop.</p>',
    ))

    # -- nummering -----------------------------------------------------
    hn = ontwerp.get("hoofdstuknummers")
    hn_keus = "uit-bron" if hn == "uit-bron" else ("ja" if hn else "nee")
    hn_uitleg = (
        "<b>De skill telt ze</b> zet <b>Hoofdstuk 1</b>, <b>2</b>, <b>3</b> "
        "boven de titel en herhaalt het cijfer groot op de achtergrond van de "
        "hoofdstukopening. <b>Niet nummeren</b> laat allebei weg. <b>Uit de "
        "bron overnemen</b> is voor een document waarin de auteur zijn "
        "hoofdstukken al genummerd heeft: er komt geen regel <b>Hoofdstuk 3</b> "
        "boven een kop die zelf al \"3. De opgave\" heet, want dat is "
        "dubbelop, maar het grote cijfer blijft wel staan. Dat cijfer komt dan "
        "uit de kop zelf en niet uit een eigen telling — die twee lopen uiteen "
        "zodra de bron een hoofdstuk overslaat of bij een ander cijfer begint. "
        "De koptekst verandert in geen van de drie standen.")
    if eigen_nummers:
        hn_uitleg = ("Dit document nummert zijn koppen zelf, zie de bevinding "
                     "bovenaan. <b>Uit de bron overnemen</b> is dan de stand "
                     "die klopt. ") + hn_uitleg
    delen.append(kaart(
        "Nummers en zijden",
        ("Drie details van de nummering. Twee staan zoals een gedrukt rapport "
         "ze gewoonlijk heeft, maar de hoofdstukken moet je hier wel "
         "aanwijzen: dit document nummert zijn koppen zelf."
         if eigen_nummers else
         "Drie details van de nummering. Ze staan zoals een gedrukt rapport ze "
         "gewoonlijk heeft; overslaan kan."),
        vinkje("dubbelzijdig", "Dubbelzijdig",
               "wordt voor- en achterop gedrukt",
               bool(ontwerp["dubbelzijdig"]),
               "Hoofdstukken beginnen dan altijd op een rechterpagina, en de "
               "marges spiegelen zodat er bij de rug ruimte overblijft. Zet "
               "het uit als het rapport enkelzijdig geprint wordt of alleen "
               "als PDF wordt gelezen."),
        keuze("hoofdstuknummers", "Hoofdstukken nummeren",
              [("ja", "de skill telt ze"), ("nee", "niet nummeren"),
               ("uit-bron", "uit de bron overnemen")],
              hn_keus, hn_uitleg,
              nadruk="uit-bron" if eigen_nummers else None),
        vinkje("exhibitnummers", "Figuren nummeren",
               "Figuur 1, 2, 3 bij een beeld of tabel",
               bool(ontwerp["exhibitnummers"]),
               "Nodig zodra de tekst naar een figuur verwijst."),
    ))

    # -- de verwijzingen -----------------------------------------------
    verw = []
    if heeft_noten:
        verw.append(keuze("noten", "Noten komen",
                          [("voetnoot", "onderaan de pagina"),
                           ("eindnoot-hoofdstuk", "achter het hoofdstuk"),
                           ("eindnoot-rapport", "achter het rapport")],
                          ontwerp["noten"],
                          f'Het brondocument heeft {ap.get("voetnoten", 0)} '
                          f'noten. Dit gaat alleen over waar ze op het blad '
                          f'komen te staan; de tekst van de noot blijft '
                          f'woordelijk gelijk. Onderaan de pagina leest het '
                          f'makkelijkst, achterin is rustiger.'))
    else:
        # Geen vraag, maar wel een antwoord: `noten: geen` hoort in de
        # uitvoer te staan, anders leest `ontwerp.json` alsof er noten
        # onderaan de pagina komen die er niet zijn.
        verw.append('<div class="rij"><label>Noten</label>'
                    '<input type="hidden" data-veld="noten" value="geen">'
                    '<p class="uitleg" style="grid-column:2;margin:5px 0 0">'
                    'Het brondocument heeft geen noten, dus er valt niets te '
                    'plaatsen.</p></div>')
    if heeft_lijst:
        lijst = ap["bronnenlijst"]
        verw.append(keuze("bronnenlijst", "Bronnenlijst",
                          [("geen", "als gewone tekst laten staan"),
                           ("apa", "alfabetisch, met inspringing"),
                           ("genummerd", "genummerd op volgorde van gebruik")],
                          ontwerp["bronnenlijst"],
                          f'Gevonden: {lijst["aantal"]} regels onder de kop '
                          f'"{lijst["kop"]}". Bij de eerste stand wordt er niets '
                          f'aan gedaan en blijven het alinea\'s. De twee andere '
                          f'zetten er een echte lijst van, met een vaste vorm '
                          f'per regel. Noten onderaan de pagina én een '
                          f'bronnenlijst achterin gaan prima samen; dat is het '
                          f'gewone geval.'))
    else:
        verw.append('<div class="rij"><label>Bronnenlijst</label>'
                    '<input type="hidden" data-veld="bronnenlijst" value="geen">'
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
                          f'{citaten["auteur_jaar"]} verwijzingen van het type '
                          f'(Jansen, 2024) gevonden. Dit is de enige vraag in '
                          f'dit blok die de tekst zelf raakt. '
                          f'<b>Gelijktrekken</b> maakt van "e.a." overal "et '
                          f'al." en zet de leestekens hetzelfde; '
                          f'<b>omzetten</b> vervangt de verwijzing door een '
                          f'nummer en vraagt dus een bronnenlijst om naar te '
                          f'wijzen. Elke vervanging wordt vastgelegd en '
                          f'achteraf gecontroleerd.'))
    delen.append(kaart(
        "Verwijzingen",
        "Noten en bronnen: waar ze terechtkomen en hoe ze eruitzien. Heeft het "
        "brondocument ze niet, dan staat dat er hieronder en valt er niets te "
        "kiezen. Voor een gewoon rapport kloppen de standen zoals ze staan.",
        *verw))

    # -- bijlagen ------------------------------------------------------
    if heeft_bijlagen:
        opties = [("geen", "geen aparte bijlagen")]
        for k in ap["bijlagen"]["koppen"]:
            opties.append((k["id"], f'vanaf "{k["tekst"][:58]}"'))
        gekozen = (ontwerp.get("bijlagen") or {}).get("vanaf") or ap["bijlagen"]["vanaf"]
        delen.append(kaart(
            "Bijlagen",
            "Het brondocument lijkt bijlagen te hebben. Hier zeg je waar het "
            "hoofdverhaal ophoudt en de bijlagen beginnen. Staat er al de "
            "goede kop, dan hoef je niets te doen.",
            keuzelijst(
                "bijlageVanaf", "Bijlagen beginnen", opties, gekozen,
                "Vanaf dat punt komt er een scheidingsblad, worden de koppen "
                "geteld in letters (Bijlage A, B, C) en krijgen ze in de "
                "inhoudsopgave een eigen groep. Kies de eerste stand als alles "
                "gewoon doorloopt.")))

    # -- beeld ---------------------------------------------------------
    delen.append(kaart(
        "Beeld",
        "Of er figuren, foto's of grafieken in het rapport komen, en waar die "
        "vandaan komen. Zitten ze in het Word-document, dan klopt de stand al "
        "en kun je verder.",
        keuze("beeld", "Beeld in dit rapport",
              [("geen", "geen"), ("uit-bron", "wat in het document zit"),
               ("aangeleverd", "apart aangeleverd")],
              ontwerp["beeld"],
              f'In het brondocument zitten {tel.get("beelden", 0)} beelden.'
              + ("" if heeft_beeld else
                 " Er zit geen beeld in; kies \"apart aangeleverd\" als er nog "
                 "figuren bij moeten.")),
        tekstveld("beeldmap", "Waar staan ze", ontwerp.get("beeldmap"),
                  "pad naar de map met de figuren"),
        '<p class="slot">Bij "apart aangeleverd" koppelt de skill elk bestand '
        'aan een blok in de tekst, en vraagt na welke alinea het hoort. Dat '
        'komt in een <code>beeld.json</code> naast het rapport te staan; een '
        'figuur zonder plek wordt niet geplaatst en gemeld, want gokken is '
        'hier hetzelfde als verzinnen.</p>'))

    # -- de omslag -----------------------------------------------------
    delen.append(kaart(
        "De omslag",
        "De voorkant: welke kleur eronder ligt en wat erop staat. Dit is het "
        "ene blok dat je wel moet nalopen, want de tekst komt hier woordelijk "
        "van jou; leeg laten betekent dat het er niet op komt te staan.",
        keuze("omslagveld", "Kleurveld",
              [(w, w) for w in ("oranje", "verloop", "navy",
                                "violet", "mint", "wit")],
              ontwerp.get("omslagveld", "oranje"),
              "Waarom niet wit als standaard: een wit voorblad met een titel "
              "erop is de eerste pagina van een manuscript en niet de omslag "
              "van een rapport. Dat ene vlak is voor wie het oppakt het "
              "verschil tussen een document en een uitgave, en het is het "
              "goedkoopste verschil dat er is. <b>Wit</b> kan wel — een "
              "opdrachtgever kan erom vragen — maar dan is het gekozen. Het "
              "kleurveld staat los van het kleurgebruik hierboven: ook een "
              "rapport in <b>zacht</b> krijgt een oranje omslag tenzij je hier "
              "iets anders aanwijst.",
              kleuren=VELDKLEUREN),
        tekstveld("rapporttitel", "Titel", ontwerp.get("rapporttitel")
                  or doc.get("titel"), "de titel op de omslag"),
        tekstveld("ondertitel", "Ondertitel", ontwerp.get("ondertitel"),
                  "één zin, of leeg"),
        tekstveld("opdrachtgever", "Opdrachtgever", ontwerp.get("opdrachtgever"),
                  "In opdracht van …"),
        tekstveld("datum", "Datum", ontwerp.get("datum"), "Maart 2026")))

    # -- de drukker ----------------------------------------------------
    delen.append(kaart(
        "Naar de drukker",
        "Alleen invullen als er papier van komt. Blijft het een PDF, dan laat "
        "je dit blok staan en verandert er niets.",
        vinkje("drukklaar", "Wordt gedrukt",
               "dit rapport gaat gebonden naar een drukker",
               bool(ontwerp.get("drukklaar"))),
        getalveld("katern", "Katern", ontwerp.get("katern", 4),
                  "pagina's per vel",
                  "Een drukker drukt niet per pagina maar per vel, en een vel "
                  "dat je dubbelvouwt levert vier pagina's op. Een rapport van "
                  "45 pagina's wordt dus hoe dan ook 48 pagina's papier; de "
                  "vraag is alleen of jij bepaalt wat er op die laatste drie "
                  "staat of dat de drukker er iets van maakt. Zet je dit aan, "
                  "dan vult de skill achteraan blanco pagina's bij tot het "
                  "uitkomt. De twee andere uitwegen zijn inkorten of het bij "
                  "een PDF houden, en die kiest niemand voor je. Vier is het "
                  "gewone katern; sommige drukkers rekenen op acht of "
                  "zestien.")))

    # -- wat de opmaak met de tekst mag --------------------------------
    delen.append(kaart(
        "Wat de opmaak met de tekst mag",
        "Twee vragen over de tekst zelf. Allebei staan ze op nee, en dat is de "
        "veilige stand: de opmaak laat de tekst dan precies zoals hij in het "
        "Word-document staat. Dit is het blok dat er het meest toe doet, dus "
        "lees het wel even.",
        keuze("herindelen", "Tekst herindelen",
              [("nee", "nee, laten staan"), ("ja", "ja, voorstellen mag")],
              "ja" if ontwerp.get("herindelen") else "nee",
              "Soms staat er iets in het Word-document dat op de pagina anders "
              "beter uitkomt. Vier alinea's die allemaal met een streepje "
              "beginnen zijn eigenlijk een genummerde lijst; een lange alinea "
              "kan in tweeën zodat er een figuur naast past. Bij <b>ja</b> mag "
              "de opmaak zulke voorstellen doen, en elk voorstel komt "
              "afzonderlijk langs jou voordat er iets gebeurt. Bij <b>nee</b> "
              "doet de skill geen enkel voorstel en blijft de indeling zoals "
              "hij is. Dit gaat over de vorm van de blokken, niet over het "
              "herschrijven van zinnen."),
        keuze("beeldtekst", "Tekst in een figuur",
              [("nee", "nee, laten staan"), ("ja", "ja, aanpassen mag")],
              "ja" if ontwerp.get("beeldtekst") else "nee",
              "In een figuur of infographic staat eigen tekst: labels, een "
              "legenda, een bijschrift. Bij <b>nee</b> blijft die staan zoals "
              "hij staat, ook als hij niet in het kader past — dan hoor je dat "
              "hij niet past en beslis jij. Bij <b>ja</b> mag de opmaak hem "
              "korter maken of anders afbreken om hem passend te krijgen."))
    )

    intro = ("Alles staat al op een stand die te verdedigen is, dus je hoeft "
             "alleen te veranderen wat je anders wilt; wat je niet kent, kun "
             "je laten staan. Elk blok zegt bovenaan waar het over gaat. "
             "Rechts staat de uitkomst: die kopieer je onderaan en plak je "
             "terug in het gesprek.")
    if eerst:
        intro = ("Begin bovenaan: daar staat wat er aan dit document is gezien "
                 "en wat je daarover moet beslissen. De blokken eronder staan "
                 "al op een stand die te verdedigen is, dus daar verander je "
                 "alleen wat je anders wilt; wat je niet kent, kun je laten "
                 "staan. Rechts staat de uitkomst: die kopieer je onderaan en "
                 "plak je terug in het gesprek.")
    telregel = (
        "In het brondocument: " +
        f'{tel.get("woorden", 0):,}'.replace(",", ".") +
        f' woorden, {tel.get("koppen", 0)} koppen, {tel.get("tabellen", 0)} '
        f'tabellen, {tel.get("beelden", 0)} beelden en '
        f'{ap.get("voetnoten", 0)} noten.')
    return "\n".join(delen), intro, telregel


#: Een veld in het formulier heet niet altijd zoals het besluit in
#: `ontwerp.json` heet: de taal staat er als een keuzerij plus een vrij
#: veld, de vier extra pagina's als losse vinkjes, de bijlagen als de
#: kop waar ze beginnen.
VELD_NAAR_BESLUIT = {
    "taalkeus": "taal", "taalAnders": "taal",
    "bijlageVanaf": "bijlagen",
    "elementen.overOns": "elementen", "elementen.team": "elementen",
    "elementen.colofon": "elementen", "elementen.achterblad": "elementen",
}

#: Alles wat in `ontwerp.json` terecht kan komen, in de volgorde van het
#: formulier. Wat de bron niet heeft, wordt niet gevraagd en staat dan in
#: `weggelaten`.
BESLUITEN = ("taal", "model", "register", "formaat", "opener", "kopregel",
             "dichtheid", "vetkop",
             "omslag", "inhoudsopgave", "elementen", "inhoudDiepte",
             "dubbelzijdig", "hoofdstuknummers", "exhibitnummers",
             "noten", "bronnenlijst", "citaatstijl", "bijlagen",
             "beeld", "beeldmap", "omslagveld",
             "rapporttitel", "ondertitel", "opdrachtgever", "datum",
             "drukklaar", "katern", "herindelen", "beeldtekst")

_VELD = re.compile(r'<(?:input|select)\b([^>]*?)data-veld="([^"]+)"')


def gestelde_besluiten(secties: str) -> list:
    """Welke besluiten er werkelijk in het formulier staan.

    Geteld uit de HTML en niet uit een lijst ernaast. Zo'n lijst loopt
    achter zodra er een blok bij komt, en dan meldt de widget besluiten
    die hij niet vraagt — precies wat hij hoort te voorkomen.

    Een verborgen veld telt niet mee. Dat is een antwoord dat meegaat
    omdat het in `ontwerp.json` hoort te staan, maar er is niets
    gevraagd: het brondocument heeft geen noten, dus er valt niets te
    plaatsen.
    """
    gevraagd = set()
    for kop, naam in _VELD.findall(secties):
        if 'type="hidden"' in kop:
            continue
        gevraagd.add(VELD_NAAR_BESLUIT.get(naam, naam))
    return [b for b in BESLUITEN if b in gevraagd]


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

    # De vormbesluiten uit `signalen.json`: waarnemingen over het
    # document als geheel, die vóór het bouwen vast moeten staan. De
    # wijzigingsvoorstellen over losse blokken blijven hier buiten; die
    # komen pas ná het ontwerp aan de beurt.
    sigpad = a.werkmap / "signalen.json"
    signalen = json.loads(sigpad.read_text(encoding="utf-8")) if sigpad.exists() else []
    vormbesluiten = {s.get("soort"): s for s in signalen
                     if isinstance(s, dict) and s.get("groep") == "vormbesluit"}

    sys.path.insert(0, str(HIER))
    from bouw import STANDAARD_ONTWERP, laad_ontwerp
    if (a.werkmap / "ontwerp.json").exists():
        ontwerp = laad_ontwerp(a.werkmap)
    else:
        ontwerp = dict(STANDAARD_ONTWERP)
        ontwerp["elementen"] = dict(STANDAARD_ONTWERP["elementen"])

    # Wat de bron níét heeft, hoort ook niet als stand in de widget te
    # staan: anders komt er een besluit terug dat nergens over gaat.
    apparaat = doc.get("apparaat", {})
    if not (apparaat.get("voetnoten") or apparaat.get("eindnoten")):
        ontwerp["noten"] = "geen"
    if not apparaat.get("bronnenlijst"):
        ontwerp["bronnenlijst"] = "geen"
    if not doc.get("telling", {}).get("beelden") and ontwerp["beeld"] == "uit-bron":
        ontwerp["beeld"] = "geen"

    secties, intro, telregel = bouw_secties(doc, ontwerp, vormbesluiten)
    fonts = FONTS.read_text(encoding="utf-8") if FONTS.exists() else ""
    uit = a.uit or (a.werkmap / "ontwerpwidget.html")
    uit.write_text(SJABLOON.format(
        titel=_esc(doc.get("titel") or a.werkmap.name),
        merk=css_variabelen(),
        intro=_esc(intro), tel=_esc(telregel), secties=secties, fonts=fonts,
        maten=json.dumps(MATEN, ensure_ascii=False),
    ), encoding="utf-8")

    # De teller telt wat er werkelijk in de widget staat, uit de HTML
    # zelf. Een besluit dat is weggelaten omdat de bron het niet heeft,
    # staat daarom in de tweede lijst en niet in de eerste.
    gevraagd = gestelde_besluiten(secties)

    print(json.dumps({
        "widget": str(uit),
        "kb": round(uit.stat().st_size / 1024),
        "besluiten": gevraagd,
        "weggelaten": [b for b in BESLUITEN if b not in gevraagd],
        "vormbesluiten": [s for s in VORMBESLUITEN if s in vormbesluiten],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
