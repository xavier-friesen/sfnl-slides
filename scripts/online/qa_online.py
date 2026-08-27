#!/usr/bin/env python3
"""Meten wat op één render niet te zien is, in vier standen.

Dit is geen poort en het keurt geen compositie af. Het meet wat je zonder
oordeel kunt vaststellen en wat **stil** misgaat — dat laatste is het criterium,
en op een scherm betekent het iets anders dan op papier. Een lelijke pagina ziet
iedereen op de render. Een token dat alleen binnen het donkerblok is
gedefinieerd, ziet niemand, want in de stand waarin je kijkt klopt hij.

**Drie dingen blokkeren**, en het zijn precies de drie waar geen interpretatie
aan te pas komt én die je op geen enkele render ziet:

* **token** — een custom property die in een van de vier standen niet
  resolveert. Twee oorzaken, en beide zijn onzichtbaar: hij staat alleen in het
  `@media (prefers-color-scheme: dark)`-blok, dus in de ongestempelde lichte
  stand bestaat hij niet; of hij komt uit `merk.css` onder een andere naam dan
  deze stijl verwacht, en dan valt de kleur weg zonder foutmelding.
* **contrast** — een tekst-op-grond-verhouding onder 4,5 (of 3,0 voor grote
  tekst) in één van de twee thema's. Op papier kun je 2,51 als merkteken
  verdedigen; op een scherm met een schermlezer en een toetsenbord niet. Dit is
  een harde grens en geen aanwijzing.
* **wit-op-oranje** — dezelfde meting, met een eigen naam en een eigen reden.
  `merk.md` §4 staat wit op oranje in drukwerk uitdrukkelijk toe, en dat is de
  ene plek waar 2,51 een merkbesluit is in plaats van een fout. Op een scherm
  erft `sfnl-online-design` die uitzondering niet, en dan is het handig dat de
  melding dát zegt in plaats van alleen een getal.
* **klip** — tekst die door `overflow: hidden` of `clip` wegvalt en die niemand
  kan terugscrollen. Er is dus tekst verdwenen.

De rest is een aanwijzing: kijk ernaar en beslis. Twee daarvan staan er omdat de
opdracht ze noemt en ze niet blokkeren, met de reden erbij:

* **grond** — de body draagt geen eigen achtergrond. De pagina rendert dan
  gewoon, maar hij leent zijn grond van wat erachter staat, en in een
  artifactviewer is dat het thema van de host. Dat is een risico dat pas in een
  andere omgeving uitkomt, en daarom een aanwijzing en geen blokkade.
* **horizontaal** — het document is breder dan het venster. De meting is
  `scrollWidth − clientWidth` en die telt ook een px afrondingsverschil van een
  transform of een scrollbalkgoot mee, dus het getal staat erbij en de render op
  de smalle breedte is de beoordelaar.

**De vier standen**, want dat is de kern van deze meting:

| stand | `prefers-color-scheme` | `data-theme` | wat hij toetst |
|---|---|---|---|
| licht | light | — | het volledige lichte palet staat op `:root` |
| donker | dark | — | de mediaquery doet zijn werk |
| donker-gestempeld | light | dark | de stempel wint van een licht systeem |
| licht-gestempeld | dark | light | de `:not()`-wachter wint van een donker systeem |

Alle kleurrekenkunde gebeurt in de browser, op een canvas van één pixel. Dat is
niet netjes maar noodzakelijk: `color-mix()` computeert in Chromium naar
`color(srgb …)` en niet naar `rgb()`, en een parser die dat niet kent, meet stil
de verkeerde kleur.

Gebruik:

    python qa_online.py werkmap/dashboard.html
    python qa_online.py werkmap/dashboard.html --json
    python qa_online.py werkmap/dashboard.html --breedtes 1440,420
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

WORTEL = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORTEL / "scripts" / "documenten"))
from _browser import browser, wacht_op_letters  # noqa: E402

# Het palet komt uit merk.py en niet uit een eigen lijst. Een toets die zijn
# eigen kopie van de waarheid bijhoudt, toetst op een gegeven moment die kopie
# — dat is precies wat `qa_document.py` is overkomen met de vijf oude waarden.
sys.path.insert(0, str(WORTEL / "scripts" / "gedeeld"))
from merk import KLEUREN, rgb as merk_rgb  # noqa: E402

PALET = {naam: merk_rgb(naam) for naam in KLEUREN}

#: (naam, prefers-color-scheme, data-theme of None)
STANDEN = (("licht", "light", None),
           ("donker", "dark", None),
           ("donker-gestempeld", "light", "dark"),
           ("licht-gestempeld", "dark", "light"))

#: De vloeren voor tekst op een scherm. Hoger dan op papier: een blad ligt op
#: 35 cm en een scherm op 50 tot 70.
VLOER_TEKST = 13.0
VLOER_CAPS = 11.5

#: Wat de meting in de browser van buiten meekrijgt: de twee vloeren, en de
#: drie merkkleuren die hij bij naam nodig heeft voor de wit-op-oranje-toets.
#: Uit merk.py, want een toets met zijn eigen kopie van het palet toetst op een
#: gegeven moment die kopie.
INVARIANTEN = {"tekst": VLOER_TEKST, "caps": VLOER_CAPS,
               "wit": list(merk_rgb("wit")),
               "oranje": list(merk_rgb("oranje")),
               "grapefruit": list(merk_rgb("grapefruit"))}

EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]")

# ---------------------------------------------------------------------------
# De meting in de browser
# ---------------------------------------------------------------------------

METING = r"""(inv) => {
  const vloerTekst = inv.tekst, vloerCaps = inv.caps;
  // De drie merkwaarden die deze meting bij naam nodig heeft, aangeleverd uit
  // merk.py. Ze staan hier niet als hexwaarde: dan zou deze toets zijn eigen
  // kopie van het palet bijhouden en op een gegeven moment die kopie toetsen.
  const WIT = inv.wit, ORANJE = inv.oranje, GRAPEFRUIT = inv.grapefruit;
  const dichtbij = (a, b, marge) => a && b
    && Math.abs(a[0] - b[0]) <= marge && Math.abs(a[1] - b[1]) <= marge
    && Math.abs(a[2] - b[2]) <= marge;
  // --- kleur, en al het rekenwerk erop -------------------------------------
  // Eén pixel op een canvas normaliseert elke kleursyntaxis die de browser
  // kent, inclusief de `color(srgb …)` waar color-mix() naar computeert.
  const cv = document.createElement('canvas');
  cv.width = cv.height = 1;
  const ctx = cv.getContext('2d', {willReadFrequently: true});
  const cache = new Map();
  const pixel = (s) => {
    if (!s) return null;
    if (cache.has(s)) return cache.get(s);
    let uit = null;
    try {
      ctx.clearRect(0, 0, 1, 1);
      ctx.fillStyle = '#000';
      ctx.fillStyle = s;
      ctx.fillRect(0, 0, 1, 1);
      const d = ctx.getImageData(0, 0, 1, 1).data;
      uit = [d[0], d[1], d[2], d[3] / 255];
    } catch (e) { uit = null; }
    cache.set(s, uit);
    return uit;
  };
  const lum = (c) => {
    const k = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92
                                     : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * k(c[0]) + 0.7152 * k(c[1]) + 0.0722 * k(c[2]);
  };
  const contrast = (a, b) => {
    const la = lum(a), lb = lum(b);
    return Math.round(((Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05)) * 100) / 100;
  };
  const overheen = (voor, achter) => {  // voor met alpha over achter
    const a = voor[3];
    return [voor[0] * a + achter[0] * (1 - a),
            voor[1] * a + achter[1] * (1 - a),
            voor[2] * a + achter[2] * (1 - a), 1];
  };
  const KLEURSTUK = /rgba?\([^)]*\)|color\([^)]*\)|#[0-9a-fA-F]{3,8}|\b(?:hsla?|oklch|oklab|lab|lch)\([^)]*\)/g;

  /* De effectieve grond onder een element. Loopt op door de voorouders tot er
     iets dekkend is, en composeert alles wat halfdoorzichtig is erover. Een
     verloop levert meer dan één kandidaat en dan geldt de slechtste — dat is de
     enige eerlijke meting op het huisverloop, waar navy 6,29 haalt op de oranje
     kant en 5,13 op de grapefruit-kant. */
  const grondVan = (el) => {
    const lagen = [];
    let n = el;
    while (n && n.nodeType === 1) {
      const cs = getComputedStyle(n);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') {
        const stukken = (cs.backgroundImage.match(KLEURSTUK) || [])
          .map(pixel).filter(c => c && c[3] > 0.5);
        if (stukken.length) { lagen.push(stukken); break; }
      }
      const bg = pixel(cs.backgroundColor);
      if (bg && bg[3] > 0.004) {
        lagen.push([bg]);
        if (bg[3] > 0.995) break;
      }
      n = n.parentElement;
    }
    // Niets gevonden: geen enkel element in de keten draagt een achtergrond.
    // Dan is de grond die van de host, en die kennen we niet. Meet tegen wit
    // en zeg dat het onzeker is — nooit overslaan. Overslaan was de eerste
    // versie hiervan, en dan bleef juist de ergste bevinding uit: op een
    // pagina met een doorzichtige body werd oranje-op-wit helemaal niet
    // gemeten, want er was geen wit om tegen te meten.
    if (!lagen.length) return {kleuren: [[255, 255, 255, 1]], onbekend: true};
    // Van achter naar voren composeren. Startpunt: het diepste dekkende laagje,
    // of anders wit — en dan is de meting onzeker en dat melden we.
    let onbekend = false;
    let basis = lagen[lagen.length - 1];
    if (!(basis[0][3] > 0.995)) { onbekend = true; }
    let uit = basis.map(c => c[3] > 0.995 ? c : overheen(c, [255, 255, 255, 1]));
    for (let i = lagen.length - 2; i >= 0; i--) {
      const nieuw = [];
      for (const onder of uit) for (const boven of lagen[i]) nieuw.push(overheen(boven, onder));
      uit = nieuw.slice(0, 4);
    }
    return {kleuren: uit, onbekend};
  };

  const eigenTekst = (el) => Array.from(el.childNodes)
      .filter(n => n.nodeType === 3).map(n => n.textContent).join('').trim();
  const naamVan = (el) => el.tagName.toLowerCase() +
    (el.className && typeof el.className === 'string' && el.className.trim()
      ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '');

  const uit = {tokens: {}, bevindingen: [], maten: {}, families: {},
               kleuren: [], grond: null, inkt: null, schuift: 0, breedste: [],
               teksten: 0, cssfout: null};

  // --- 1. De tokens ---------------------------------------------------------
  // Elke custom property die ergens in een stylesheet wordt gedeclareerd,
  // moet in deze stand resolveren. Een leeg antwoord betekent: hij bestaat
  // niet, en dan valt de eigenschap die hem gebruikt stil terug.
  const wortel = getComputedStyle(document.documentElement);
  const namen = new Set();
  const opWortelVan = new Set();
  const scopes = {};   // eigenschap -> {scope: waarde}
  uit.cssfout = null;
  /* Let op de volgorde van de takken hieronder, en niet op de leesbaarheid:
     sinds CSS Nesting draagt élke CSSStyleRule een `cssRules`-lijst, ook een
     lege. Een tak `else if (r.cssRules) recurse()` vóór `else if (r.style)`
     stuurt daardoor iedere gewone regel de lege recursie in, en dan vindt deze
     meting nul tokens — zonder foutmelding, want er is niets fout. Dat is
     precies wat er gebeurde: `tokens 0` op een pagina met 105 stijlregels en
     31 tokens in het merkblok. Dus: eerst de declaraties oogsten, dán
     afdalen. */
  const regelsIn = (lijst, scope) => {
    for (const r of lijst) {
      if (r.type === 4 /* media */) {
        const dark = /prefers-color-scheme\s*:\s*dark/.test(r.conditionText || '');
        const print = /\bprint\b/.test(r.conditionText || '');
        regelsIn(r.cssRules || [], dark ? 'media-donker' : (print ? 'print' : scope));
        continue;
      }
      if (r.style) {
        const sel = r.selectorText || '';
        // Staat de declaratie op de wortel? Alleen dán kun je hem op de wortel
        // nameten. Een token dat op `.grafiek` staat (zoals `--plot-hoogte`)
        // hoort niet op `:root` te resolveren en is geen bevinding — dat was
        // de eerste valse melding van deze toets.
        const opWortel = /(^|[\s,>+~])(:root|html)\b/.test(sel);
        let s = scope;
        if (scope === 'basis') {
          if (/\[data-theme\s*=\s*["']?dark/.test(sel)) s = 'stempel-donker';
          else if (/\[data-theme\s*=\s*["']?light/.test(sel)) s = 'stempel-licht';
          else if (/^\s*:root\s*$/.test(sel) || /^\s*html\s*$/.test(sel)) s = 'root';
          else s = 'overig';
        } else if (scope === 'media-donker') {
          s = 'media-donker';
        }
        // Met een index en niet met for...of: een CSSStyleDeclaration is niet
        // in elke engine itereerbaar, en een throw hier zou in de catch
        // hieronder verdwijnen. Dáárvoor is `cssfout`.
        for (let i = 0; i < r.style.length; i++) {
          const p = r.style.item(i);
          if (!p || !p.startsWith('--')) continue;
          namen.add(p);
          (scopes[p] = scopes[p] || {})[s] = r.style.getPropertyValue(p).trim();
          if (opWortel) opWortelVan.add(p);
        }
      }
      if (r.cssRules && r.cssRules.length) regelsIn(r.cssRules, scope);
    }
  };
  for (const sheet of document.styleSheets) {
    try {
      regelsIn(sheet.cssRules, 'basis');
    } catch (e) {
      // Alleen een cross-origin stylesheet mag hier landen. Al het andere is
      // een fout in deze meting en dan moet je het weten.
      if (!uit.cssfout) uit.cssfout = String(e);
    }
  }
  for (const n of namen) {
    uit.tokens[n] = {waarde: wortel.getPropertyValue(n).trim(),
                     scopes: scopes[n] || {},
                     opWortel: opWortelVan.has(n)};
  }

  // --- 2. De grond van de body ---------------------------------------------
  const bcs = getComputedStyle(document.body);
  const bg = pixel(bcs.backgroundColor);
  uit.grond = {css: bcs.backgroundColor, alpha: bg ? bg[3] : null};
  uit.inkt = bcs.color;
  const bodyDoorzichtig = !bg || bg[3] < 0.995;

  // --- 3. Breedte ----------------------------------------------------------
  const de = document.documentElement;
  uit.schuift = de.scrollWidth - de.clientWidth;
  if (uit.schuift > 1) {
    const grens = de.clientWidth;
    document.querySelectorAll('*').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width === 0) return;
      const over = Math.round(r.right - grens);
      if (over > 1) uit.breedste.push({el: naamVan(el), over});
    });
    uit.breedste.sort((a, b) => b.over - a.over);
    uit.breedste = uit.breedste.slice(0, 4);
  }

  // --- 4. Per element ------------------------------------------------------
  document.querySelectorAll('*').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return;
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) return;
    const naam = naamVan(el);
    const tekst = eigenTekst(el);

    // 4a. Klipping. Alleen waar de richting werkelijk `hidden` of `clip` is:
    // een houder met `overflow-x: auto` is de reparatie en niet het defect,
    // want daar kan de lezer bij.
    const hx = /^(hidden|clip)$/.test(cs.overflowX);
    const hy = /^(hidden|clip)$/.test(cs.overflowY);
    if ((hx || hy) && el.clientWidth > 0 && el.clientHeight > 0
        && !el.closest('svg')) {
      const doos = r;
      const rand = {links: doos.left + parseFloat(cs.borderLeftWidth || 0),
                    rechts: doos.right - parseFloat(cs.borderRightWidth || 0),
                    boven: doos.top + parseFloat(cs.borderTopWidth || 0),
                    onder: doos.bottom - parseFloat(cs.borderBottomWidth || 0)};
      const loop = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      let ergste = 0, welke = '', richting = '';
      let knoop;
      while ((knoop = loop.nextNode())) {
        if (!knoop.textContent.trim()) continue;
        if (knoop.parentElement && knoop.parentElement.closest('svg')) continue;
        const bereik = document.createRange();
        bereik.selectNodeContents(knoop);
        for (const rr of bereik.getClientRects()) {
          const v = hy ? Math.max(rr.bottom - rand.onder, rand.boven - rr.top) : 0;
          const h = hx ? Math.max(rr.right - rand.rechts, rand.links - rr.left) : 0;
          const over = Math.max(v, h);
          if (over > ergste) {
            ergste = over;
            richting = v >= h ? 'hoogte' : 'breedte';
            welke = knoop.textContent.trim().slice(0, 60);
          }
        }
      }
      if (ergste > 1.5) {
        uit.bevindingen.push({soort: 'klip', ernst: 'critical', el: naam,
          wat: `${naam} snijdt tekst af: ${Math.round(ergste)} px te veel in de ${richting}`,
          tekst: welke});
      }
    }

    if (tekst.length < 2) return;
    uit.teksten += 1;

    // 4b. Maten en families.
    const px = Math.round(parseFloat(cs.fontSize) * 100) / 100;
    uit.maten[px] = (uit.maten[px] || 0) + tekst.length;
    const fam = (cs.fontFamily.split(',')[0] || '').replace(/['"]/g, '').trim();
    uit.families[fam] = (uit.families[fam] || 0) + tekst.length;

    const caps = cs.textTransform === 'uppercase'
              && parseFloat(cs.letterSpacing) / px >= 0.055;
    const vloer = caps ? vloerCaps : vloerTekst;
    // Het woordmerk is geen tekst maar een merk: het draagt de gemeten
    // spatiëring van het logo (0,04em) en valt daarmee net buiten de
    // caps-vloer, terwijl niemand het leest — hij herkent het. Dit is de enige
    // uitzondering op de vloer en hij staat hier met naam en al, zodat er geen
    // tweede bij kan komen zonder dat iemand het ziet.
    if (px < vloer && !el.closest('.logo')) {
      uit.bevindingen.push({soort: 'te-klein', ernst: 'warn', el: naam,
        wat: `${naam} staat op ${px} px — de vloer voor ` +
             `${caps ? 'een kapitaallabel' : 'lopende tekst'} op een scherm is ${vloer} px`,
        tekst: tekst.slice(0, 50)});
    }

    // 4c. Contrast. Dit is de harde grens van deze skill.
    const vg0 = pixel(cs.color);
    const g = grondVan(el);
    if (vg0 && g.kleuren.length) {
      const groot = px >= 24 || (px >= 18.66 && parseFloat(cs.fontWeight) >= 700);
      const drempel = groot ? 3.0 : 4.5;
      let slechtste = 99, tegen = '';
      for (const achter of g.kleuren) {
        const vg = vg0[3] > 0.995 ? vg0 : overheen(vg0, achter);
        const c = contrast(vg, achter);
        if (c < slechtste) {
          slechtste = c;
          tegen = `rgb(${achter.map(x => Math.round(x)).slice(0, 3).join(', ')})`;
        }
      }
      uit.kleuren.push({el: naam, px, kleur: cs.color, verhouding: slechtste});

      // Wit op oranje krijgt zijn eigen melding, en niet omdat de generieke
      // contrasttoets hem zou missen — 2,51 zakt onder 4,5 én onder 3,0, dus
      // hij komt er sowieso uit. Het is omdat `merk.md` §4 hier een
      // uitzondering toestaat die op een scherm níet geldt, en dat is precies
      // het soort regel dat iemand per ongeluk uit het drukwerk overneemt.
      // Met de reden erbij is de melding een antwoord; zonder is hij een getal.
      const opOranje = g.kleuren.some(c => dichtbij(c, ORANJE, 14)
                                        || dichtbij(c, GRAPEFRUIT, 14));
      const isWit = dichtbij(vg0, WIT, 12);
      if (isWit && opOranje) {
        uit.bevindingen.push({soort: 'wit-op-oranje', ernst: 'critical', el: naam,
          wat: `${naam} zet witte tekst op een oranje vlak: ${slechtste.toFixed(2)}. ` +
               `merk.md §4 staat dat in drukwerk toe (de lessenband van de ` +
               `casespread doet het), maar op een scherm erft sfnl-online-design die ` +
               `uitzondering niet — hier is 4,5 voor lopende tekst en 3,0 voor ` +
               `grote tekst een blokkade. Navy op oranje haalt 6,29`,
          tekst: tekst.slice(0, 50)});
      } else if (slechtste < drempel) {
        uit.bevindingen.push({soort: 'contrast', ernst: 'critical', el: naam,
          wat: `${naam} haalt ${slechtste.toFixed(2)} op zijn grond (${tegen}) — ` +
               `de drempel voor ${groot ? 'grote tekst' : 'lopende tekst'} op ` +
               `${px} px is ${drempel.toFixed(1)}`,
          tekst: tekst.slice(0, 50)});
      } else if (g.onbekend && !bodyDoorzichtig) {
        // Draagt de body zélf geen grond, dan geldt dit voor élk element op de
        // pagina en is één melding genoeg — die staat in `grond`. Zonder deze
        // uitzondering stond er honderd keer dezelfde regel.
        uit.bevindingen.push({soort: 'grond-onzeker', ernst: 'warn', el: naam,
          wat: `${naam} staat op geen enkele dekkende achtergrond; de ${slechtste.toFixed(2)} ` +
               `hierboven is tegen wit gemeten en niet tegen wat er werkelijk staat`});
      }
    }

    // 4d. Aanraakdoel. WCAG 2.2 vraagt 24 x 24 CSS-px voor iets wat je aanwijst.
    if (/^(a|button|summary|input|select)$/.test(el.tagName.toLowerCase())
        && cs.display !== 'inline'
        && (r.width < 24 || r.height < 24)) {
      uit.bevindingen.push({soort: 'aanraakdoel', ernst: 'warn', el: naam,
        wat: `${naam} meet ${Math.round(r.width)} x ${Math.round(r.height)} px — ` +
             `onder 24 x 24 is het op een aanraakscherm niet te raken`});
    }

    // 4e. Schaduw. merk.md §4: geen schaduw, in geen enkel medium.
    if (cs.boxShadow && cs.boxShadow !== 'none'
        && cs.boxShadow.split(/,(?![^(]*\))/).some(d => !d.includes('inset'))) {
      uit.bevindingen.push({soort: 'schaduw', ernst: 'warn', el: naam,
        wat: `${naam} draagt een slagschaduw. Een kaart krijgt een haarlijn in ` +
             `zijn eigen kleur`});
    }

    // 4f. De leesmaat. Alleen echt lopende tekst.
    if (el.closest('.tekst, .chapeau') && tekst.length > 90) {
      const per = px * 0.485;           // gemeten voor Lato Light
      const tekens = Math.round(r.width / per);
      if (tekens > 90) {
        uit.bevindingen.push({soort: 'leesmaat', ernst: 'warn', el: naam,
          wat: `${naam} zet ongeveer ${tekens} tekens per regel (${Math.round(r.width)} px) ` +
               `— boven 90 raakt het oog de volgende regel kwijt. Zet .leesmaat erop`});
      } else if (tekens < 30) {
        uit.bevindingen.push({soort: 'leesmaat', ernst: 'warn', el: naam,
          wat: `${naam} zet ongeveer ${tekens} tekens per regel — onder 30 valt ` +
               `een alinea uit elkaar`});
      }
    }
  });

  // --- 5. Statische dingen: één keer per stand, maar ze veranderen niet ----
  // 5a. Een vaste kleur in een SVG. Dit is de klassieke donkeremodusfout: de
  // grafiek blijft navy terwijl de grond navy wordt.
  document.querySelectorAll('svg [fill], svg [stroke], svg[fill], svg[stroke]')
    .forEach(el => {
      for (const attr of ['fill', 'stroke']) {
        const v = (el.getAttribute(attr) || '').trim();
        if (!v || /^(none|currentcolor|transparent|inherit|url\()/i.test(v)) continue;
        if (v.startsWith('var(')) continue;
        uit.bevindingen.push({soort: 'vaste-kleur', ernst: 'warn',
          el: el.tagName.toLowerCase(),
          wat: `<${el.tagName.toLowerCase()} ${attr}="${v}"> in een SVG. Een vaste ` +
               `kleur wisselt niet mee met het thema — zet currentColor of een ` +
               `var(--reeks-n)`});
      }
    });

  // 5b. Een bron buiten dit bestand. In een artifact blokkeert het CSP-beleid
  // elke andere host; los werkt het alleen mét internet.
  const extern = [];
  document.querySelectorAll('link[href], script[src], img[src], source[src], iframe[src]')
    .forEach(el => {
      const u = el.getAttribute('href') || el.getAttribute('src') || '';
      if (/^(https?:)?\/\//i.test(u)) extern.push(u.slice(0, 90));
    });
  if (extern.length) {
    uit.bevindingen.push({soort: 'extern', ernst: 'warn',
      wat: `${extern.length} bron(nen) buiten dit bestand: ${extern.slice(0, 3).join(', ')}. ` +
           `Sluit ze in als data-URI; het CSP-beleid van een artifact blokkeert ze`});
  }

  // 5c. Toegankelijkheid: taal, koppenrij, alternatieve tekst, tabelkoppen.
  const lang = (document.documentElement.getAttribute('lang') || '').toLowerCase();
  if (!lang) {
    uit.bevindingen.push({soort: 'taal', ernst: 'warn',
      wat: 'geen lang op <html>. Een schermlezer kiest dan de verkeerde stem, ' +
           'en de afbreking valt op Engelse regels'});
  } else if (!lang.startsWith('nl')) {
    uit.bevindingen.push({soort: 'taal', ernst: 'warn',
      wat: `lang="${lang}" op <html> terwijl de pagina Nederlands is`});
  }
  const koppen = Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6'))
    .map(h => parseInt(h.tagName[1], 10));
  if (!koppen.length) {
    uit.bevindingen.push({soort: 'koppen', ernst: 'warn',
      wat: 'geen enkele <h1>–<h6>. Een schermlezer navigeert op koppen; een ' +
           'pagina zonder koppen is één blok'});
  } else {
    if (koppen[0] !== 1) {
      uit.bevindingen.push({soort: 'koppen', ernst: 'warn',
        wat: `de eerste kop is een <h${koppen[0]}>. De pagina begint met één <h1>`});
    }
    for (let i = 1; i < koppen.length; i++) {
      if (koppen[i] - koppen[i - 1] > 1) {
        uit.bevindingen.push({soort: 'koppen', ernst: 'warn',
          wat: `de koppenrij springt van h${koppen[i - 1]} naar h${koppen[i]}`});
        break;
      }
    }
  }
  document.querySelectorAll('img').forEach(el => {
    if (el.getAttribute('alt') === null) {
      uit.bevindingen.push({soort: 'alt', ernst: 'warn',
        wat: `<img src="${(el.getAttribute('src') || '').slice(0, 40)}"> zonder alt. ` +
             `Leeg (alt="") is een geldig antwoord voor een beeld dat niets zegt`});
    }
  });
  document.querySelectorAll('svg').forEach(el => {
    const verborgen = el.getAttribute('aria-hidden') === 'true';
    const benoemd = el.getAttribute('aria-label') || el.querySelector('title');
    if (!verborgen && !benoemd) {
      uit.bevindingen.push({soort: 'alt', ernst: 'warn',
        wat: 'een <svg> zonder <title>, aria-label of aria-hidden="true". Een ' +
             'grafiek heeft een naam nodig; een icoon naast tekst is aria-hidden'});
    }
  });
  document.querySelectorAll('table').forEach(el => {
    if (!el.querySelector('th')) {
      uit.bevindingen.push({soort: 'tabelkop', ernst: 'warn',
        wat: 'een <table> zonder <th>. Zonder kopcellen leest een schermlezer ' +
             'een raster losse getallen'});
    } else {
      const zonder = Array.from(el.querySelectorAll('th'))
        .filter(th => !th.getAttribute('scope')).length;
      if (zonder) {
        uit.bevindingen.push({soort: 'tabelkop', ernst: 'warn',
          wat: `${zonder} <th> zonder scope="col" of scope="row"`});
      }
    }
  });

  // 5d. `outline: none` zonder vervanging. Statisch uit de stylesheets, want
  // :focus-visible matcht niet op een programmatische focus.
  const focusweg = [];
  const zoekFocus = (lijst) => {
    for (const r of lijst) {
      if (r.cssRules) { zoekFocus(r.cssRules); continue; }
      if (!r.style || !r.selectorText) continue;
      if (!/:focus/.test(r.selectorText)) {
        // Ook buiten :focus is `outline: none` op een interactief element fout.
        if (!/\b(a|button|input|select|textarea|summary)\b|\[tabindex/.test(r.selectorText)) continue;
      }
      const o = (r.style.getPropertyValue('outline') || '').trim();
      const ow = (r.style.getPropertyValue('outline-width') || '').trim();
      const weg = /^(none|0|0px)$/.test(o) || /^(0|0px)$/.test(ow)
               || /\b(none)\b/.test(r.style.getPropertyValue('outline-style') || '');
      if (!weg) continue;
      const vervanging = (r.style.getPropertyValue('box-shadow') || '')
                      || (r.style.getPropertyValue('border') || '')
                      || (r.style.getPropertyValue('background-color') || '');
      if (!vervanging) focusweg.push(r.selectorText.slice(0, 70));
    }
  };
  for (const sheet of document.styleSheets) {
    try { zoekFocus(sheet.cssRules); } catch (e) { /* cross-origin */ }
  }
  if (focusweg.length) {
    uit.bevindingen.push({soort: 'focus', ernst: 'warn',
      wat: `outline weggehaald zonder vervanging op: ${focusweg.slice(0, 3).join(' · ')}. ` +
           `Dat maakt de pagina onbruikbaar met een toetsenbord, en je ziet het ` +
           `op geen enkele render`});
  }

  // 5e. Emoji.
  const emo = (document.body.innerText || '')
    .match(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/gu);
  if (emo) {
    uit.bevindingen.push({soort: 'emoji', ernst: 'warn',
      wat: `emoji in de tekst: ${[...new Set(emo)].slice(0, 8).join(' ')}. Teken ` +
           `het icoon zelf in SVG op het raster van 24, of laat het weg`});
  }

  return uit;
}"""


# ---------------------------------------------------------------------------
# Het palet
# ---------------------------------------------------------------------------

def _op_de_lijn(c: tuple[float, float, float], pal: dict, marge: float = 14.0) -> bool:
    """Ligt deze kleur op of dicht bij het pad tussen twee merkkleuren?

    Dat is de mechanische vorm van de regel uit `merk.md` §4: een tint is een
    percentage van een merkkleur, geen nieuwe kleur. `color-mix(in srgb, wit 8%,
    navy)` ligt exact op het lijnstuk wit–navy; een willekeurig ander blauw ligt
    nergens.
    """
    waarden = list(pal.values())
    for i, a in enumerate(waarden):
        for b in waarden[i:]:
            ab = [b[k] - a[k] for k in range(3)]
            n2 = sum(x * x for x in ab)
            if n2 == 0:
                t = 0.0
            else:
                t = sum((c[k] - a[k]) * ab[k] for k in range(3)) / n2
                t = max(0.0, min(1.0, t))
            d = sum((a[k] + t * ab[k] - c[k]) ** 2 for k in range(3)) ** 0.5
            if d <= marge:
                return True
    return False


# ---------------------------------------------------------------------------
# Toetsen
# ---------------------------------------------------------------------------

def toets(html: Path, breedtes: list[int]) -> dict:
    pal, merkbron = PALET, "scripts/gedeeld/merk.py"
    uri = html.resolve().as_uri()
    ruw: list[tuple[str, int, dict]] = []

    with browser() as b:
        for naam, schema, stempel in STANDEN:
            ctx = b.new_context(color_scheme=schema,
                                viewport={"width": breedtes[0], "height": 1000})
            page = ctx.new_page()
            page.goto(uri)
            if stempel:
                page.evaluate("(t) => document.documentElement.setAttribute('data-theme', t)",
                              stempel)
            wacht_op_letters(page)
            for breed in breedtes:
                page.set_viewport_size({"width": breed, "height": 1000})
                page.wait_for_timeout(140)
                ruw.append((naam, breed, page.evaluate(METING, INVARIANTEN)))
            ctx.close()

    bev: list[dict] = []
    standnamen = [s[0] for s in STANDEN]

    # --- de tokens, over alle standen heen ---------------------------------
    alle_tokens = {}
    for naam, _breed, m in ruw:
        for tok, info in m["tokens"].items():
            rij = alle_tokens.setdefault(tok, {"scopes": info["scopes"],
                                              "opWortel": info.get("opWortel", False),
                                              "leeg": []})
            rij["opWortel"] = rij["opWortel"] or info.get("opWortel", False)
            if not info["waarde"] and naam not in rij["leeg"]:
                rij["leeg"].append(naam)
    for tok, rij in sorted(alle_tokens.items()):
        # Een token dat nergens op de wortel wordt gedeclareerd, is lokaal —
        # `--plot-hoogte` op `.grafiek`, `--kolom-min` op een raster. Dat hoort
        # op `:root` niet te resolveren en is dus geen bevinding.
        if not rij["leeg"] or not rij["opWortel"]:
            continue
        sc = rij["scopes"]
        if "root" not in sc and ("media-donker" in sc or "stempel-donker" in sc):
            reden = ("staat alleen in een donkerblok "
                     f"({', '.join(sorted(k for k in sc if 'donker' in k))}) en niet op "
                     "de kale :root, dus in de ongestempelde lichte stand bestaat hij niet")
        elif not sc:
            reden = ("wordt gebruikt maar nergens gedeclareerd — waarschijnlijk komt hij "
                     "uit merk.css onder een andere naam")
        else:
            reden = f"is gedeclareerd in {', '.join(sorted(sc))} maar resolveert hier niet"
        bev.append({"ernst": "critical", "soort": "token",
                    "standen": rij["leeg"],
                    "wat": f"{tok} {reden}"})

    # --- de twee donkerblokken tegen elkaar --------------------------------
    scopes = ruw[0][2]["tokens"]
    uit_de_pas = []
    for tok, info in sorted(scopes.items()):
        sc = info["scopes"]
        a, c = sc.get("media-donker"), sc.get("stempel-donker")
        if (a is None) != (c is None) or (a is not None and a != c):
            uit_de_pas.append(f"{tok}: media {a!r} / stempel {c!r}")
    if uit_de_pas:
        bev.append({"ernst": "warn", "soort": "donkerblokken",
                    "wat": f"{len(uit_de_pas)} token(s) verschillen tussen het "
                           f"@media-donkerblok en het [data-theme=\"dark\"]-blok: "
                           f"{'; '.join(uit_de_pas[:4])}. Dan ziet iemand met een "
                           f"donker systeem iets anders dan iemand die de schakelaar "
                           f"heeft gebruikt"})

    # --- de rest, per stand, en daarna samengevoegd ------------------------
    per_bevinding: dict[tuple, dict] = {}

    def leg_neer(soort: str, ernst: str, wat: str, stand: str, breed: int,
                 tekst: str = "") -> None:
        sleutel = (soort, wat)
        r = per_bevinding.setdefault(sleutel, {"ernst": ernst, "soort": soort,
                                              "wat": wat, "tekst": tekst,
                                              "standen": [], "breedtes": []})
        merk = f"{stand}" if breed == breedtes[0] else f"{stand}@{breed}"
        if merk not in r["standen"]:
            r["standen"].append(merk)
        if breed not in r["breedtes"]:
            r["breedtes"].append(breed)

    gronden: dict[str, str] = {}
    for naam, breed, m in ruw:
        gronden[naam] = m["grond"]["css"]
        if m.get("cssfout"):
            leg_neer("cssfout", "warn",
                     f"een stylesheet was niet uit te lezen ({m['cssfout']}), dus "
                     f"de tokentoets is over dat blad heen gestapt. Bij een "
                     f"ingesloten <style> hoort dat niet te kunnen",
                     naam, breed)
        for f in m["bevindingen"]:
            leg_neer(f["soort"], f["ernst"], f["wat"], naam, breed, f.get("tekst", ""))

        if m["grond"]["alpha"] is not None and m["grond"]["alpha"] < 0.995:
            leg_neer("grond", "warn",
                     f"de body draagt geen dekkende achtergrond "
                     f"({m['grond']['css']}). De pagina leent zijn grond dan van "
                     f"wat erachter staat, en in een artifactviewer is dat het "
                     f"thema van de host: dan klapt de tekst om en de grond niet",
                     naam, breed)

        if m["schuift"] > 1:
            wie = ", ".join(f"{x['el']} (+{x['over']} px)" for x in m["breedste"][:3])
            leg_neer("horizontaal", "warn",
                     f"het document is {m['schuift']} px breder dan het venster. "
                     f"Verdacht: {wie or 'niets aanwijsbaars'}. Een brede tabel of "
                     f"grafiek hoort in een .tabelhouder met overflow-x: auto te "
                     f"staan, niet de pagina breder te duwen",
                     naam, breed)

        families = {k: v for k, v in m["families"].items() if v > 40}
        if len(families) > 2:
            leg_neer("letterfamilies", "warn",
                     f"{len(families)} letterfamilies dragen tekst: "
                     f"{', '.join(sorted(families))}. Er zijn er twee: Montserrat "
                     f"voor de kop, Lato voor het brood", naam, breed)

        maten = sorted(float(k) for k, v in m["maten"].items() if v > 30)
        if len(maten) > 6:
            leg_neer("maten", "warn",
                     f"{len(maten)} maten dragen tekst "
                     f"({', '.join(f'{x:g}' for x in maten)}). De schermladder heeft "
                     f"er zes; een zevende is meestal een compositieprobleem",
                     naam, breed)

        if pal:
            vreemd = set()
            for k in m["kleuren"]:
                c = _kleur(k["kleur"])
                if c and not _op_de_lijn(c, pal):
                    vreemd.add(k["kleur"])
            if vreemd:
                leg_neer("palet", "warn",
                         f"tekstkleur buiten het palet: {', '.join(sorted(vreemd)[:5])}. "
                         f"Een tint is een percentage van een merkkleur "
                         f"(color-mix), geen nieuwe kleur", naam, breed)

    bev += sorted(per_bevinding.values(),
                  key=lambda r: (0 if r["ernst"] == "critical" else 1, r["soort"]))

    return {
        "bestand": str(html),
        "merkbron": merkbron,
        "standen": standnamen,
        "breedtes": breedtes,
        "gronden": gronden,
        "tokens": len(scopes),
        "bevindingen": bev,
        "critical": sum(1 for b in bev if b["ernst"] == "critical"),
        "warn": sum(1 for b in bev if b["ernst"] == "warn"),
    }


def _kleur(css: str) -> tuple[float, float, float] | None:
    m = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", css)
    if m:
        return (float(m[1]), float(m[2]), float(m[3]))
    m = re.match(r"color\(srgb ([\d.]+) ([\d.]+) ([\d.]+)", css)
    if m:
        return tuple(float(m[i]) * 255 for i in (1, 2, 3))  # type: ignore[return-value]
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=Path)
    ap.add_argument("--breedtes", default="1440,420")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not a.html.exists():
        sys.exit(f"niet gevonden: {a.html}")
    breedtes = [int(x) for x in a.breedtes.split(",") if x.strip()]

    r = toets(a.html, breedtes)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 1 if r["critical"] else 0

    print(f"{r['bestand']}")
    print(f"  merkbron   {r['merkbron']}")
    print(f"  tokens     {r['tokens']}")
    print(f"  breedtes   {', '.join(str(b) for b in r['breedtes'])}")
    for stand, grond in r["gronden"].items():
        print(f"  grond      {stand:<18} {grond}")
    if len(set(r["gronden"].values())) < 2:
        print("             ^ dezelfde grond in elke stand — dat is bijna altijd "
              "een body zonder eigen achtergrond")

    if not r["bevindingen"]:
        print("\ngeen bevindingen. De render in beide thema's blijft de vormbeoordeling.")
        return 0
    print()
    for ernst in ("critical", "warn"):
        for b in r["bevindingen"]:
            if b["ernst"] != ernst:
                continue
            waar = ", ".join(b.get("standen", [])) or "alle standen"
            print(f"  [{ernst:<8}] {b['soort']}: {b['wat']}")
            print(f"             standen: {waar}")
            if b.get("tekst"):
                print(f"             … {b['tekst']!r}")
    print(f"\n{r['critical']} critical, {r['warn']} warn")
    return 1 if r["critical"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
