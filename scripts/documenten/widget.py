#!/usr/bin/env python3
"""De opdrachtwidget: het hele vragenvuur op één pagina, met een schets.

Deze route stelde tien vragen — vijf over de opdracht en vijf over de
vorm — en de vorm ging door `AskUserQuestion`. Dat widget neemt er vier
per keer, dus dat waren twee rondes, en de vijf opdrachtvragen stonden
daarnaast als proza in hetzelfde bericht. Wat de gebruiker dan ziet is
een tekstblok met vijf vragen, daarna vier knoppen, daarna nog eens twee
knoppen, en op geen enkel moment het geheel. Wie in de tweede ronde
bedenkt dat de omvang toch anders moet, kan er niet meer bij.

Dus: één pagina, alle tien tegelijk, en een schets die meebeweegt.
Hetzelfde patroon als `scripts/rapport/widget.py`, en met opzet dezelfde
vorm — een gebruiker die beide skills gebruikt, hoort niet twee keer een
ander formulier te leren.

Twee dingen zijn hier anders dan in de rapportroute, en ze komen uit het
verschil tussen de twee. Daar ligt er een `.docx`, dus kan de widget
lezen wat er is en alleen aanbieden wat er ligt; hier is er nog niets en
is de eerste vraag juist **wat heb je al**. En daar zijn alle besluiten
vormbesluiten; hier gaan er vijf over de opdracht, en die horen er in
één beweging bij: het formaat volgt uit wie het in handen krijgt, en het
beeldregister volgt uit de vraag of er beeld ís.

De schets is een **schema en geen zetproef**. De echte zetting staat in
`assets/documenten/keuzekaarten/vragenvuur.png`; die stuur je ernaast
mee.

De uitvoer is een `opdracht.json` die de gebruiker kopieert en
terugplakt. De vijf vormbesluiten plus `gedrukt` gaan daarna woordelijk
in het besluitenblok bovenaan `outline.md` — dat blijft de enige plek
waar ze staan, want deze route heeft geen `ontwerp.json` waar een script
uit leest.

Gebruik:

    python widget.py werkmap/
    python widget.py werkmap/ --titel "Uitnodiging werksessie"
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


def _esc(t) -> str:
    return html.escape(str(t or ""), quote=True)


#: De bladmaten, uit `reference/documenten-stramien.md` §1. Ze staan hier
#: zodat de schets de goede verhouding heeft; een zevende formaat bestaat
#: niet.
FORMATEN = {
    "sfnl":        {"mm": "210 × 275 mm", "px": (794, 1039), "kolommen": 2},
    "sfnl-spread": {"mm": "420 × 275 mm", "px": (1587, 1039), "kolommen": 3},
    "a4":          {"mm": "210 × 297 mm", "px": (794, 1123), "kolommen": 2},
    "a4-liggend":  {"mm": "297 × 210 mm", "px": (1123, 794), "kolommen": 3},
    "a5":          {"mm": "148 × 210 mm", "px": (559, 794), "kolommen": 1},
    "dl":          {"mm": "99 × 210 mm", "px": (374, 794), "kolommen": 1},
}

#: Woorden per pagina per beeldregister, uit `documenten-vormentaal.md`.
#: Een indicatie en geen drempel: `qa_document.py` telt zonder oordeel.
REGISTERS = {
    "tekst": {"woorden": "300–400", "beeld": "weinig tot geen"},
    "balans": {"woorden": "150–250", "beeld": "één drager per pagina"},
    "beeld": {"woorden": "60–120", "beeld": "beeld draagt de pagina"},
}


SJABLOON = """<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Opdracht — {titel}</title>
<style>
{fonts}
:root {{
  --navy: #201B5C; --oranje: #F87F4F; --emerald: #6AC6BA; --violet: #6B5DAE;
  --periwinkel: #8E9BF0;
  --mint: #E0F4F1; --tint: #F4F3F7; --lijn: rgba(32,27,92,.16);
  --zacht: rgba(32,27,92,.70);
  --display: 'Montserrat', system-ui, sans-serif;
  --brood: 'Lato', system-ui, sans-serif;
}}
* {{ box-sizing: border-box; }}
/* `[hidden]` uit de browserstijl heeft de laagste soortelijkheid die er
   is en verliest van elke klasse met een `display` erin. Dat is hier
   twee keer misgegaan — een rij die niet meedeed bleef staan, en het
   voorblad in de schets bleef zichtbaar onder een titelbalk. Eén regel
   bovenaan is goedkoper dan hem per klasse herhalen. */
[hidden] {{ display: none !important; }}
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
.rij {{ display: grid; grid-template-columns: 178px minmax(0,1fr); gap: 12px 16px;
       align-items: start; margin-bottom: 14px; }}
.rij:last-child {{ margin-bottom: 0; }}
.rij > label {{ font-weight: 700; font-size: 13.5px; padding-top: 5px; }}
.opties {{ display: flex; flex-wrap: wrap; gap: 7px; }}
.opt {{ position: relative; }}
.opt input {{ position: absolute; opacity: 0; pointer-events: none; }}
.opt span {{ display: block; cursor: pointer; padding: 6px 11px; font-size: 13px;
            border: 1px solid var(--lijn); background: #fff; }}
.opt input:checked + span {{ background: var(--navy); color: #fff;
                            border-color: var(--navy); font-weight: 700; }}
.opt input:focus-visible + span {{ outline: 2px solid var(--oranje); outline-offset: 2px; }}
.opt.nadruk span {{ box-shadow: 0 0 0 2px var(--oranje); }}
.uitleg {{ grid-column: 2; margin: 6px 0 0; font-size: 12px; line-height: 1.45;
          color: var(--zacht); }}
.uitleg b {{ font-weight: 700; color: var(--navy); }}
textarea, input[type=text] {{
  width: 100%; font-family: var(--brood); font-size: 13.5px; padding: 7px 9px;
  border: 1px solid var(--lijn); background: #fff; color: var(--navy);
}}
textarea {{ min-height: 62px; resize: vertical; line-height: 1.45; }}
.slot {{ margin: 16px 0 0; font-size: 12px; color: var(--zacht); line-height: 1.5; }}
.zij {{ position: sticky; top: 28px; }}
.schets {{ background: #fff; padding: 18px; box-shadow: 0 1px 3px rgba(32,27,92,.10); }}
.blaadje {{ position: relative; margin: 0 auto 12px; background: #fff;
           box-shadow: inset 0 0 0 1px var(--lijn); overflow: hidden;
           width: 190px; height: 249px; transition: width .15s, height .15s; }}
.blaadje.spread {{ width: 280px; height: 183px; }}
.blaadje.a4 {{ width: 186px; height: 263px; }}
.blaadje.liggend {{ width: 280px; height: 198px; }}
.blaadje.a5 {{ width: 160px; height: 227px; }}
.blaadje.dl {{ width: 112px; height: 237px; }}
.b-balk {{ position: absolute; top: 0; left: 0; right: 0; height: 22%;
          background: var(--oranje); }}
.b-zet {{ position: absolute; inset: 0; padding: 13px 12px; display: flex;
         flex-direction: column; gap: 6px; }}
.b-vlak {{ flex: 1 1 auto; min-height: 0; display: grid; gap: 7px; }}
.b-kolom {{ background: repeating-linear-gradient(
   to bottom, rgba(32,27,92,.30) 0 1px, transparent 1px 4px); height: 100%; }}
.b-titel {{ font-family: var(--display); font-weight: 800; font-size: 10px;
           line-height: 1.15; margin: 0 0 4px; }}
.b-streep {{ width: 34px; height: 3px; background: var(--oranje); margin: 0 0 5px; }}
.voorblad {{ position: absolute; inset: 0; padding: 15px 14px;
            display: flex; flex-direction: column; justify-content: flex-end; }}
.meting {{ font-size: 11.5px; line-height: 1.5; color: var(--zacht); margin: 0; }}
.meting b {{ color: var(--navy); font-weight: 700; }}
.uitvoer {{ margin-top: 16px; background: #fff; padding: 16px 18px 18px;
           box-shadow: 0 1px 3px rgba(32,27,92,.10); }}
.uitvoer h3 {{ font-family: var(--display); font-weight: 800; font-size: 13px;
              letter-spacing: .1em; text-transform: uppercase; margin: 0 0 8px; }}
pre {{ background: var(--tint); padding: 12px; margin: 0; overflow: auto;
      max-height: 300px; font-size: 11.5px; line-height: 1.45; }}
button {{ margin-top: 12px; font-family: var(--display); font-weight: 700;
         font-size: 13px; padding: 9px 16px; border: 0; background: var(--navy);
         color: #fff; cursor: pointer; }}
button:hover {{ background: var(--oranje); color: var(--navy); }}
.klaar {{ display: inline-block; margin-left: 10px; font-size: 12.5px;
         font-weight: 700; color: var(--emerald); }}
.let {{ margin: 10px 0 0; font-size: 12px; line-height: 1.45; color: var(--zacht); }}
.let b {{ color: var(--navy); font-weight: 700; }}
@media (max-width: 980px) {{ .blad {{ grid-template-columns: 1fr; }}
  .zij {{ position: static; }} }}
</style>
</head>
<body>
<h1>Wat wordt dit voor document?</h1>
<p class="intro">Tien vragen: vijf over de opdracht en vijf over de vorm. Ze staan hier
allemaal tegelijk omdat ze aan elkaar hangen — het formaat volgt uit wie het in handen
krijgt, en het beeldregister uit de vraag of er beeld is. De vormvragen staan al op de
stand die voor de meeste documenten klopt, dus als je alleen het bovenste blok invult,
kun je hieronder op kopiëren drukken.</p>
<p class="tel">Er wordt niets geschreven voordat dit terug is. Vul in, druk op
<b>kopieer</b>, en plak het resultaat in het gesprek.</p>

<div class="blad">
<div class="kolommen">
{secties}
</div>

<div class="zij">
  <div class="schets">
    <div class="blaadje" id="blaadje">
      <div class="b-balk" id="b-balk" hidden></div>
      <div class="voorblad" id="b-voorblad" hidden>
        <div class="b-streep"></div>
        <p class="b-titel" id="b-voortitel">Titel</p>
      </div>
      <div class="b-zet" id="b-zet"></div>
    </div>
    <p class="meting" id="meting"></p>
    <p class="let" id="let"></p>
  </div>
  <div class="uitvoer">
    <h3>Dit plak je terug</h3>
    <pre id="uit"></pre>
    <button id="kopieer" type="button">Kopieer</button>
    <span class="klaar" id="klaar" hidden>gekopieerd</span>
  </div>
</div>
</div>

<script>
const FORMATEN = {formaten};
const REGISTERS = {registers};

function lees() {{
  const o = {{}};
  for (const el of document.querySelectorAll('[data-veld]')) {{
    const v = el.getAttribute('data-veld');
    if (el.type === 'radio') {{ if (el.checked) o[v] = el.value; }}
    else if (el.type === 'checkbox') {{ o[v] = el.checked; }}
    else o[v] = el.value.trim();
  }}
  // De omvang is een getal of het woord "volgt". Als getal hoort het als
  // getal in de JSON: een script dat de katernsom uitrekent kan met "4"
  // niets en met 4 wel.
  if (o.omvang && o.omvang !== 'volgt') o.omvang = parseInt(o.omvang, 10);
  // Het tweede accent hoort alleen bij het register met kleurvlakken, en
  // de balkkleur alleen bij de titelbalk. Anders staat er een keuze in de
  // JSON die nergens op de pagina te zien is.
  if (o.register !== 'vlakken') delete o.accent;
  if (o.opening !== 'titelbalk') delete o.balkkleur;
  if (o.opening !== 'voorblad') {{
    delete o.dektitel; delete o.ondertitel; delete o.afzender; delete o.datum;
  }}
  for (const k of ['materiaal','lezer','voorbeeld','beeldbron',
                   'dektitel','ondertitel','afzender','datum']) {{
    if (k in o && !o[k]) o[k] = null;
  }}
  return o;
}}

function ververs() {{
  const o = lees();
  const f = FORMATEN[o.formaat] || FORMATEN.sfnl;
  const b = document.getElementById('blaadje');
  b.className = 'blaadje' + (o.formaat === 'sfnl' ? '' : ' ' + o.formaat.replace('sfnl-',''));

  // De opening. Een voorblad is een hele pagina en dus geen tekst; een
  // titelbalk is een band met tekst eronder; een gewone titel loopt mee.
  const voorblad = o.opening === 'voorblad';
  document.getElementById('b-voorblad').hidden = !voorblad;
  document.getElementById('b-balk').hidden = o.opening !== 'titelbalk';
  document.getElementById('b-voortitel').textContent = o.dektitel || 'de titel';
  const veld = {{oranje: 'var(--oranje)', navy: 'var(--navy)', violet: 'var(--violet)'}};
  document.getElementById('b-balk').style.background =
    veld[o.balkkleur] || 'var(--oranje)';
  b.style.background = voorblad
    ? (o.register === 'navy' ? 'var(--navy)' : 'var(--oranje)') : '#fff';
  document.getElementById('b-voortitel').style.color =
    (voorblad && o.register === 'navy') ? '#fff' : 'var(--navy)';

  const zet = document.getElementById('b-zet');
  zet.innerHTML = '';
  zet.hidden = voorblad;
  zet.style.paddingTop = o.opening === 'titelbalk' ? '28%' : '13px';
  if (o.opening === 'titel') {{
    const s = document.createElement('div'); s.className = 'b-streep'; zet.appendChild(s);
    const t = document.createElement('p'); t.className = 'b-titel';
    t.textContent = o.dektitel || 'de titel'; zet.appendChild(t);
  }}
  // De kolommen. In px en niet in procenten: een percentagehoogte in
  // een gridcel met een auto-rij valt terug op de inhoudshoogte, en die
  // is nul — dan staat er een lege schets en lijkt de keuze niets te
  // doen. De hoogte van het blaadje is bekend, dus is de som ook bekend.
  const hoog = b.clientHeight || 249;
  const wrap = document.createElement('div');
  wrap.className = 'b-vlak';
  wrap.style.gridTemplateColumns = 'repeat(' + f.kolommen + ', 1fr)';
  const deel = {{tekst: 0.94, balans: 0.74, beeld: 0.46}}[o.beeldregister] || 0.74;
  const ruimte = hoog * (o.opening === 'titelbalk' ? 0.52
    : (o.opening === 'titel' ? 0.62 : 0.78));
  for (let i = 0; i < f.kolommen; i++) {{
    const k = document.createElement('div');
    k.className = 'b-kolom';
    k.style.height = Math.round(ruimte * deel) + 'px';
    // Beeldgedreven is niet minder tekst maar ander materiaal, dus staat
    // de laatste kolom als vlak en niet als regels.
    if (i === f.kolommen - 1 && o.beeldregister === 'beeld') {{
      k.className = '';
      k.style.background = 'var(--mint)';
      k.style.height = Math.round(ruimte) + 'px';
    }}
    wrap.appendChild(k);
  }}
  zet.appendChild(wrap);
  if (o.register === 'vlakken') {{
    const vlak = document.createElement('div');
    vlak.style.flex = '0 0 auto';
    vlak.style.height = Math.round(hoog * 0.16) + 'px';
    vlak.style.background = {{mint: 'var(--mint)', violet: 'var(--violet)',
      periwinkel: 'var(--periwinkel)'}}[o.accent] || 'var(--mint)';
    zet.appendChild(vlak);
  }}

  const r = REGISTERS[o.beeldregister] || REGISTERS.balans;
  const omvang = o.omvang === 'volgt' ? null : o.omvang;
  let tekst = '<b>' + f.mm + '</b> &middot; ongeveer <b>' + r.woorden +
    '</b> woorden per pagina &middot; ' + r.beeld;
  if (omvang) {{
    const paginas = voorblad ? omvang - 1 : omvang;
    tekst += '. Van de <b>' + omvang + '</b> pagina\\'s ' +
      (voorblad ? 'gaat er één naar het voorblad, dus blijven er <b>' + paginas +
        '</b> over voor de inhoud' : 'is er geen aan de titel kwijt');
  }} else {{
    tekst += ". De omvang volgt uit de inhoud en staat straks in de outline";
  }}
  document.getElementById('meting').innerHTML = tekst + '.';

  // De katernsom. Alleen als het gedrukt wordt, want op een scherm is het
  // aantal vrij en dan is deze regel ruis.
  const let_ = document.getElementById('let');
  if (o.gedrukt === 'ja' && omvang) {{
    if (omvang <= 2) {{
      let_.innerHTML = 'Eén plat vel, ' + (omvang === 1 ? 'enkelzijdig' : 'dubbelzijdig') +
        '. Daar hoort geen katernsom bij.';
    }} else if (omvang % 4 === 0) {{
      let_.innerHTML = '<b>' + omvang + '</b> pagina\\'s komt uit op de pers: ' +
        (omvang / 4) + ' gevouwen ' + (omvang === 4 ? 'vel' : 'vellen') + '.';
    }} else {{
      const naar = Math.ceil(omvang / 4) * 4;
      let_.innerHTML = '<b>' + omvang + '</b> pagina\\'s bestaat niet op de pers. ' +
        'Op papier wordt dat een katern van <b>' + naar + '</b> met ' + (naar - omvang) +
        ' lege ' + (naar - omvang === 1 ? 'pagina' : "pagina's") + ' erin. ' +
        'Inkorten naar ' + (Math.floor(omvang / 4) * 4 || 2) + ', uitbreiden naar ' +
        naar + ', of het bij een PDF houden — dat is jouw keuze en de skill legt hem voor.';
    }}
  }} else if (o.gedrukt === 'ja') {{
    let_.innerHTML = 'Het wordt gedrukt, dus het aantal pagina\\'s moet vanaf vier ' +
      'deelbaar door vier zijn. Dat rekent de skill uit zodra de omvang vaststaat.';
  }} else if (o.gedrukt === 'weet-niet') {{
    let_.innerHTML = 'Zolang dit niet vaststaat gaat de skill uit van een PDF, en dan ' +
      'is het aantal pagina\\'s vrij. Wordt het toch gedrukt, dan kan het aantal nog ' +
      'schuiven.';
  }} else {{
    let_.innerHTML = 'Een PDF op een scherm: pagina 1 staat alleen en niemand slaat om. ' +
      'Het aantal pagina\\'s is vrij.';
  }}

  document.getElementById('uit').textContent = JSON.stringify(o, null, 1);
}}

// Het tweede accent en de balkkleur horen alleen bij hun eigen stand.
// Zichtbaar houden wat niet meedoet, is een keuze aanbieden die nergens
// naartoe gaat.
function toonAfhankelijk() {{
  const o = lees();
  const zet = (naam, aan) => {{
    const rij = document.querySelector('[data-rij="' + naam + '"]');
    if (rij) rij.hidden = !aan;
  }};
  zet('accent', document.querySelector('[data-veld="register"]:checked')?.value === 'vlakken');
  zet('balkkleur', document.querySelector('[data-veld="opening"]:checked')?.value === 'titelbalk');
  zet('omslagtekst', document.querySelector('[data-veld="opening"]:checked')?.value === 'voorblad');
}}

document.addEventListener('input', () => {{ toonAfhankelijk(); ververs(); }});
document.addEventListener('change', () => {{ toonAfhankelijk(); ververs(); }});
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
toonAfhankelijk();
ververs();
</script>
</body>
</html>
"""


def keuze(veld: str, label: str, opties: list, gekozen: str,
          uitleg: str = "", rij: str = "") -> str:
    knoppen = []
    for waarde, naam in opties:
        aan = " checked" if str(waarde) == str(gekozen) else ""
        knoppen.append(
            f'<label class="opt"><input type="radio" name="{veld}" '
            f'data-veld="{veld}" value="{_esc(waarde)}"{aan}>'
            f'<span>{_esc(naam)}</span></label>')
    rijattr = f' data-rij="{rij}"' if rij else ""
    return (f'<div class="rij"{rijattr}><label>{_esc(label)}</label>'
            f'<div class="opties">{"".join(knoppen)}</div>'
            + (f'<p class="uitleg">{uitleg}</p>' if uitleg else "")
            + '</div>')


def tekstvak(veld: str, label: str, plaatshouder: str = "",
             uitleg: str = "", rij: str = "") -> str:
    rijattr = f' data-rij="{rij}"' if rij else ""
    return (f'<div class="rij"{rijattr}><label>{_esc(label)}</label>'
            f'<textarea data-veld="{veld}" placeholder="{_esc(plaatshouder)}"></textarea>'
            + (f'<p class="uitleg">{uitleg}</p>' if uitleg else "")
            + '</div>')


def regel(veld: str, label: str, waarde: str = "", plaatshouder: str = "",
          uitleg: str = "", rij: str = "") -> str:
    rijattr = f' data-rij="{rij}"' if rij else ""
    return (f'<div class="rij"{rijattr}><label>{_esc(label)}</label>'
            f'<input type="text" data-veld="{veld}" value="{_esc(waarde)}" '
            f'placeholder="{_esc(plaatshouder)}">'
            + (f'<p class="uitleg">{uitleg}</p>' if uitleg else "")
            + '</div>')


def kaart(titel: str, toelicht: str, *stukken: str) -> str:
    return (f'<div class="kaart"><h2>{_esc(titel)}</h2>'
            f'<p class="toelicht">{toelicht}</p>{"".join(stukken)}</div>')


def bouw_secties(titel: str = "") -> str:
    delen = []

    # -- de opdracht ---------------------------------------------------
    delen.append(kaart(
        "De opdracht",
        "Vijf vragen over wat dit moet worden. Ze bepalen de vorm eronder, en de "
        "eerste bepaalt of er iets te vormen valt: zonder materiaal is schrijven "
        "de opdracht en niet opmaken.",
        tekstvak("materiaal", "Wat heb je al?",
                 "een notitie, een transcript, een reeks losse punten, een "
                 "afgeronde tekst — of een pad naar het bestand",
                 "Dit is het materiaal waaruit het document bestaat. Er komt geen "
                 "rubriek, geen alinea en geen pagina bij die hier niet in staat. "
                 "Is er nog niets, zeg dat dan: dan is <b>sfnl-writer</b> de "
                 "skill die de tekst maakt en komt deze daarna."),
        tekstvak("lezer", "Wie krijgt dit in handen, en wat moet die erna doen?",
                 "bijvoorbeeld: wethouders van vier gemeenten, die moeten "
                 "besluiten of ze meedoen",
                 "Een uitnodiging moet iemand naar een zaal krijgen, een "
                 "executive summary moet iemand een besluit laten nemen, een "
                 "proposal moet een aanbesteding winnen. Dat zijn drie "
                 "verschillende documenten en niet drie titels."),
        keuze("gedrukt", "Wordt dit gedrukt?",
              [("nee", "nee, het blijft een PDF"), ("ja", "ja, het gaat naar de pers"),
               ("weet-niet", "weet ik nog niet")],
              "nee",
              "Gedrukt betekent dat het aantal pagina's vanaf vier deelbaar door "
              "vier moet zijn, dat de spreads moeten kloppen en dat de snijrand "
              "ertoe doet. Op een scherm staat pagina 1 alleen en slaat niemand "
              "om. Dit is het enige antwoord uit dit blok dat verderop een script "
              "aanstuurt — het wordt de vlag <code>--gedrukt</code>."),
        regel("voorbeeld", "Is er een bestaand stuk dat als voorbeeld dient?",
              plaatshouder="een pad, een link, of leeg",
              uitleg="Krijg je er een, dan is dát de maatstaf: de skill rendert "
                     "het, kijkt ernaar, en volgt de vormentaal ervan in plaats "
                     "van de eigen maatstaf."),
        tekstvak("beeldbron", "Is er beeld?",
                 "foto's, logo's van partners, een grafiek — of niets",
                 "Dit is de vraag die het vaakst te laat komt. Zonder beeld is "
                 "<b>beeldgedreven</b> hieronder geen optie: dat wordt dan grote "
                 "lege vlakken met een kop erin, en dat is precies hoe een pagina "
                 "eruitziet die niemand heeft ontworpen."),
    ))

    # -- de vorm -------------------------------------------------------
    delen.append(kaart(
        "De vorm",
        "Vijf besluiten, van grof naar fijn: het formaat bepaalt hoeveel er per "
        "pagina in gaat, de omvang hoeveel pagina's dat zijn, het kleurregister "
        "hoeveel vlak er staat, het beeldregister wat daarbinnen tekst blijft, en "
        "de opening raakt alleen de eerste pagina. Alles staat op de stand die "
        "voor de meeste documenten klopt. De schets rechts beweegt mee.",
        keuze("formaat", "Papierformaat",
              [("sfnl", "SFNL 210 × 275 mm"), ("a4", "A4"), ("a5", "A5"),
               ("sfnl-spread", "spread 420 × 275"), ("a4-liggend", "A4 liggend"),
               ("dl", "DL-paneel")],
              "sfnl",
              "<b>SFNL 210 × 275</b> is de maat van de jaarrapporten en de reden "
              "dat ze als magazine lezen. <b>A4</b> kies je als het door een "
              "kantoorprinter moet of als bijlage bij een aanbesteding gaat. "
              "<b>A5</b> voor een uitnodiging of een programmaboekje: dan is het "
              "één kolom en gaat de letter omhoog. De <b>spread</b> is de "
              "dubbelpagina voor één case. Een zevende formaat bestaat niet."),
        keuze("omvang", "Hoeveel pagina's",
              [("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("8", "8"),
               ("12", "12"), ("16", "16"), ("volgt", "volgt uit de inhoud")],
              "4",
              "Vier is het gewone document: pagina 2 en 3 liggen tegenover "
              "elkaar. <b>Eén tot drie</b> is één blad, en dat is een ander stuk "
              "en niet een korter stuk — er is geen buitenste pagina om iets op "
              "te zetten dat apart moet staan, en geen ruimte voor een aanloop. "
              "<b>Acht tot zestien</b> valt in delen uiteen en krijgt kopregels "
              "en folio's. <b>Volgt uit de inhoud</b> stelt dit besluit uit naar "
              "de outline, niet verder: daar staat het met de reden erbij en keur "
              "je het goed vóór er iets gebouwd wordt."),
        keuze("register", "Kleurgebruik",
              [("wit", "wit met oranje accent"), ("vlakken", "kleurvlakken als ritme"),
               ("oranje", "oranje dominant"), ("navy", "navy dominant")],
              "wit",
              "<b>Wit met oranje accent</b> is navy letter op wit, met oranje "
              "voor de labels en de streep: het register van vrijwel elke "
              "inhoudspagina in het rapport. <b>Kleurvlakken als ritme</b> zet er "
              "vlakken tussen, en dan spreek je hier het tweede accent af — één "
              "keuze voor het hele document en niet per pagina. Een <b>executive "
              "summary is navy</b>; dat is geen keuze maar wat er aan een "
              "bestuurstafel hoort."),
        keuze("accent", "Tweede accent",
              [("mint", "mint"), ("violet", "violet"), ("periwinkel", "periwinkel")],
              "mint",
              "Alleen bij kleurvlakken als ritme, en één kleur voor het hele "
              "document. Twee tweede accenten naast elkaar is geen ritme meer.",
              rij="accent"),
        keuze("beeldregister", "Tekst tegenover beeld",
              [("tekst", "tekstgedreven"), ("balans", "gebalanceerd"),
               ("beeld", "beeldgedreven")],
              "balans",
              "<b>Tekstgedreven</b> is 300 tot 400 woorden per pagina, "
              "<b>gebalanceerd</b> 150 tot 250, <b>beeldgedreven</b> 60 tot 120. "
              "De getallen zijn een indicatie en ze werken twee kanten op: past "
              "het verhaal in minder, dan is het minder. Een bewering schrappen "
              "om onder een richtwaarde te blijven is de verkeerde reductie, en "
              "er staat daarom geen drempel op."),
        keuze("opening", "Hoe de titel op het document komt",
              [("voorblad", "een voorblad"), ("titelbalk", "een titelbalk"),
               ("titel", "gewoon een titel")],
              "voorblad",
              "Een <b>voorblad</b> is een hele pagina met alleen de titel op een "
              "kleurveld: een kwart van een document van vier, de helft van een "
              "tweeluik. Dat is wat elk SFNL-drukwerk doet en de pagina waaraan "
              "iemand het stuk herkent — maar onder de vier pagina's wordt het "
              "duur, en dan is de <b>titelbalk</b> meestal het antwoord: een "
              "aflopende band bovenaan pagina 1, ongeveer een kwart pagina, met "
              "de inhoud eronder. <b>Gewoon een titel</b> kost vrijwel niets. "
              "Hoofdstukopeningen zijn iets anders en horen in de outline."),
        keuze("balkkleur", "Kleur van de titelbalk",
              [("oranje", "oranje"), ("navy", "navy"), ("violet", "violet")],
              "oranje",
              "Op oranje is de inkt navy; op navy en violet is hij wit.",
              rij="balkkleur"),
    ))

    # -- de omslagtekst ------------------------------------------------
    delen.append(f'<div data-rij="omslagtekst">' + kaart(
        "Wat er op het voorblad staat",
        "Vier velden, woordelijk van jou. Dit is de enige tekst op het document "
        "die niet uit het materiaal komt, dus er wordt niets bij verzonnen — ook "
        "geen datum. Leeg laten betekent dat het er niet op staat.",
        regel("dektitel", "Titel", titel, "de titel zoals hij op het blad komt"),
        regel("ondertitel", "Ondertitel", "", "of leeg"),
        regel("afzender", "Afzender of opdrachtgever", "",
              "Social Finance NL, de opdrachtgever, of beide"),
        regel("datum", "Datum", "", "zoals het er moet staan, bijvoorbeeld april 2026"),
    ) + '</div>')

    return "".join(delen)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("werkmap", type=Path, nargs="?", default=Path("."),
                    help="waar de widget wordt neergezet")
    ap.add_argument("--titel", default="",
                    help="een titel die al bekend is; komt in het veld te staan")
    ap.add_argument("--uit", type=Path, default=None,
                    help="een ander pad voor het HTML-bestand")
    a = ap.parse_args()

    a.werkmap.mkdir(parents=True, exist_ok=True)
    doel = a.uit or (a.werkmap / "opdrachtwidget.html")

    fonts = FONTS.read_text(encoding="utf-8") if FONTS.exists() else ""
    if not FONTS.exists():
        print("let op: de ingesloten letters staan niet in "
              f"{FONTS} — de widget valt terug op de systeemletter. "
              "Draai `python haal_fonts.py` als dat stoort.", file=sys.stderr)

    secties = bouw_secties(a.titel)
    doel.write_text(SJABLOON.format(
        titel=_esc(a.titel or "nieuw document"),
        fonts=fonts,
        secties=secties,
        formaten=json.dumps(FORMATEN, ensure_ascii=False),
        registers=json.dumps(REGISTERS, ensure_ascii=False),
    ), encoding="utf-8")

    velden = sorted({m.group(1) for m in
                     re.finditer(r'data-veld="([^"]+)"', secties)})
    print(json.dumps({
        "widget": str(doel),
        "kb": round(doel.stat().st_size / 1024),
        "vragen": len(velden),
        "velden": velden,
        "stuur mee": "assets/documenten/keuzekaarten/vragenvuur.png",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
