#!/usr/bin/env python3
"""De ontwerpwidget: alle vormbesluiten op één pagina, met een preview.

Het vragenvuur van deze skill is met ruim dertig velden veel te lang
geworden voor een gesprek. Vier per keer door een keuzewidget betekent
acht rondes, en na de tweede weet niemand meer wat er in de eerste is
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

Het tweede wat hij anders doet: hij legt uit. De gebruiker kent deze
skill niet. `kantlijn`, `register` en `dichtheid` zijn woorden van
binnen de skill, en een keuzeknop met alleen zo'n woord erop is geen
vraag maar een raadsel. Elk veld zegt daarom wat je ervoor terugkrijgt,
en elk blok begint met één regel die zegt waar het over gaat en of je
het gerust kunt overslaan.

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
  --zacht: rgba(32,27,92,.70);
  --display: 'Montserrat', system-ui, sans-serif;
  --brood: 'Lato', system-ui, sans-serif;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; padding: 28px 30px 60px; background: #EFEEF2; color: var(--navy);
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
         box-shadow: 0 1px 3px rgba(32,27,92,.10); }}
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
.stip {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%;
        margin-right: 7px; border: 1px solid rgba(32,27,92,.28); }}
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

/* --- de preview --------------------------------------------------- */
/* De kolom blijft staan terwijl links wordt gescrold. Op een laag scherm
   is hij hoger dan het venster; dan scrolt hij zelf, want anders valt de
   kopieerknop eronder weg en dat is de enige knop die telt. */
.zij {{ position: sticky; top: 24px; max-height: calc(100vh - 48px);
       overflow-y: auto; }}
.preview {{ background: #fff; padding: 18px; box-shadow: 0 1px 3px rgba(32,27,92,.10); }}
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
               background: rgba(32,27,92,.10); }}
.zetspiegel {{ position: absolute; inset: 7.3% 5.9% 9.3% 7.8%; display: flex; gap: 3.8%; }}
.kolom {{ background: repeating-linear-gradient(
            transparent 0 3px, rgba(32,27,92,.30) 3px 4px); flex: 1; }}
.kant {{ flex: 0 0 21.5%; background: repeating-linear-gradient(
           transparent 0 4px, rgba(32,27,92,.14) 4px 5px); }}
.folio {{ position: absolute; bottom: 3.6%; right: 5.9%; width: 8%; height: 1.4%;
         background: var(--oranje); }}
.meting {{ margin-top: 14px; font-size: 12.5px; line-height: 1.45; }}
.meting b {{ font-family: var(--display); font-weight: 700; }}
.let {{ margin-top: 10px; padding: 9px 11px; background: var(--tint);
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
  oranje:  {{vlak: '#F87F4F', inkt: '#201B5C'}},
  verloop: {{vlak: 'linear-gradient(150deg, #F87F4F 0%, #F95D63 100%)', inkt: '#201B5C'}},
  navy:    {{vlak: '#201B5C', inkt: '#FFFFFF'}},
  violet:  {{vlak: '#6B5DAE', inkt: '#FFFFFF'}},
  mint:    {{vlak: '#E0F4F1', inkt: '#201B5C'}},
  wit:     {{vlak: '#FFFFFF', inkt: '#201B5C'}},
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
  return o;
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
                 zacht: 'var(--mint)', contrast: 'var(--violet)'}};
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

#: De kleur onder elke omslagknop. Alleen om de knop te laten zien wat
#: hij kiest; het echte veld staat in `stijl.css`.
VELDKLEUREN = {
    "oranje": "#F87F4F",
    "verloop": "linear-gradient(150deg, #F87F4F 0%, #F95D63 100%)",
    "navy": "#201B5C",
    "violet": "#6B5DAE",
    "mint": "#E0F4F1",
    "wit": "#FFFFFF",
}


def keuze(veld: str, label: str, opties: list, gekozen: str, uitleg: str = "",
          kleuren: dict | None = None) -> str:
    knoppen = []
    for waarde, tekst in opties:
        aan = " checked" if waarde == gekozen else ""
        stip = ""
        if kleuren and waarde in kleuren:
            stip = f'<i class="stip" style="background:{kleuren[waarde]}"></i>'
        knoppen.append(
            f'<label class="opt"><input type="radio" name="{veld}" '
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


def kaart(titel: str, toelicht: str, *stukken: str) -> str:
    """Een blok met een kop en één regel die zegt waar het over gaat.

    Die regel is niet decoratief. Wie deze skill niet kent, moet aan de
    kop kunnen zien of dit blok hem aangaat of dat hij het kan laten
    staan; zonder die regel wordt elk blok een vraag.
    """
    return (f'<div class="kaart"><h2>{_esc(titel)}</h2>'
            f'<p class="toelicht">{toelicht}</p>{"".join(stukken)}</div>')


def bouw_secties(doc: dict, ontwerp: dict) -> tuple[str, str]:
    ap = doc.get("apparaat", {})
    tel = doc.get("telling", {})
    heeft_noten = bool(ap.get("voetnoten") or ap.get("eindnoten"))
    heeft_lijst = bool(ap.get("bronnenlijst"))
    heeft_bijlagen = bool(ap.get("bijlagen"))
    heeft_beeld = bool(tel.get("beelden"))
    citaten = ap.get("citaten", {})
    el = ontwerp.get("elementen") or {}

    delen = []

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
        keuze("dichtheid", "Hoeveel tekst op een pagina",
              [("ruim", "ruim"), ("gemiddeld", "gemiddeld"), ("dicht", "dicht")],
              ontwerp["dichtheid"],
              "Dit verschuift twee dingen: het aantal regels dat op een pagina "
              "past — ongeveer drie heen of terug — en de lucht tussen alinea's "
              "en kopjes. Wat het niet doet is de letter kleiner maken; die "
              "blijft in alle drie de standen gelijk. Ruim leest rustiger, "
              "dicht scheelt pagina's."),
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
    delen.append(kaart(
        "Nummers en zijden",
        "Drie details van de nummering. Ze staan zoals een gedrukt rapport ze "
        "gewoonlijk heeft; overslaan kan.",
        vinkje("dubbelzijdig", "Dubbelzijdig",
               "wordt voor- en achterop gedrukt",
               bool(ontwerp["dubbelzijdig"]),
               "Hoofdstukken beginnen dan altijd op een rechterpagina, en de "
               "marges spiegelen zodat er bij de rug ruimte overblijft. Zet "
               "het uit als het rapport enkelzijdig geprint wordt of alleen "
               "als PDF wordt gelezen."),
        vinkje("hoofdstuknummers", "Hoofdstuk nummeren",
               "Hoofdstuk 1, 2, 3 boven de titel",
               bool(ontwerp["hoofdstuknummers"])),
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
    telregel = (
        "In het brondocument: " +
        f'{tel.get("woorden", 0):,}'.replace(",", ".") +
        f' woorden, {tel.get("koppen", 0)} koppen, {tel.get("tabellen", 0)} '
        f'tabellen, {tel.get("beelden", 0)} beelden en '
        f'{ap.get("voetnoten", 0)} noten.')
    return "\n".join(delen), intro, telregel


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
    if (a.werkmap / "ontwerp.json").exists():
        ontwerp = laad_ontwerp(a.werkmap)
    else:
        ontwerp = dict(STANDAARD_ONTWERP)
        ontwerp["elementen"] = dict(STANDAARD_ONTWERP["elementen"])

    # Wat de bron níét heeft, hoort ook niet als stand in de widget te
    # staan: anders komt er een besluit terug dat nergens over gaat.
    apparaat = doc.get("apparaat", {})
    heeft = {
        "noten": bool(apparaat.get("voetnoten") or apparaat.get("eindnoten")),
        "bronnenlijst": bool(apparaat.get("bronnenlijst")),
        "bijlagen": bool(apparaat.get("bijlagen")),
        "citaatstijl": bool(apparaat.get("citaten", {}).get("auteur_jaar")),
    }
    if not heeft["noten"]:
        ontwerp["noten"] = "geen"
    if not heeft["bronnenlijst"]:
        ontwerp["bronnenlijst"] = "geen"
    if not doc.get("telling", {}).get("beelden") and ontwerp["beeld"] == "uit-bron":
        ontwerp["beeld"] = "geen"

    secties, intro, telregel = bouw_secties(doc, ontwerp)
    fonts = FONTS.read_text(encoding="utf-8") if FONTS.exists() else ""
    uit = a.uit or (a.werkmap / "ontwerpwidget.html")
    uit.write_text(SJABLOON.format(
        titel=_esc(doc.get("titel") or a.werkmap.name),
        intro=_esc(intro), tel=_esc(telregel), secties=secties, fonts=fonts,
        maten=json.dumps(MATEN, ensure_ascii=False),
    ), encoding="utf-8")

    # De teller telt wat er werkelijk in de widget staat. Een besluit dat
    # is weggelaten omdat de bron het niet heeft, staat daarom niet in
    # beide lijsten.
    alle = ["model", "register", "formaat", "opener", "dichtheid",
            "omslag", "inhoudsopgave", "elementen", "inhoudDiepte",
            "dubbelzijdig", "nummering",
            "noten", "bronnenlijst", "citaatstijl", "bijlagen",
            "beeld", "omslagveld", "omslagtekst", "drukklaar", "katern",
            "herindelen", "beeldtekst"]
    weggelaten = [n for n, aanwezig in heeft.items() if not aanwezig]

    print(json.dumps({
        "widget": str(uit),
        "kb": round(uit.stat().st_size / 1024),
        "besluiten": [b for b in alle if b not in weggelaten],
        "weggelaten": weggelaten,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
