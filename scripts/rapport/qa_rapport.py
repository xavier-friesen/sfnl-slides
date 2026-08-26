#!/usr/bin/env python3
"""Wat er in een gezet rapport stil misgaat, gemeten in de browser.

Dit is geen poort en het keurt geen vorm af. Het meet veertien dingen
die je op een contactblad van dertig spreads niet ziet en die op papier
wél opvallen. Zes ervan blokkeren. Vijf daarvan zijn metingen waar geen
interpretatie aan te pas komt; de zesde, `figuur-te-klein`, rust op één
aanname over de tekst ín een beeld, en die aanname staat erbij.

**Blokkeert:**

* `klip` — een kader snijdt zijn eigen inhoud af. Er is tekst verdwenen
  die niemand ziet. Dit is de ernstigste meting die er is, en daarom
  meet hij de onderkant van de diepste tekstdragende node en niet
  `scrollHeight`: dat laatste telt de ondermarge van het laatste blok
  mee en meldt dan een klip op een opsomming die keurig boven de rand
  eindigt. Zie `KLIP_LUCHT` hieronder.
* `overloop` — een element steekt over de snijrand.
* `te-klein` — lopende tekst onder 8 pt of een kapitaallabel onder 6 pt.
* `figuur-te-klein` — de tekst ín een aangeleverd beeld komt onder de
  leesvloer uit doordat het beeld in de kolom is teruggeschaald. Dit is
  de enige meting met een schatting erin, en de schatting staat in de
  uitvoer. Een beeld zonder enig detail draagt geen tekst en wordt niet
  beoordeeld; dat staat er als `figuur-zonder-detail`.
* `leeg-kader` — een kolom die blanco blijft terwijl de kolom ernaast
  wél gevuld is. Een leeg láátste kader is een hoofdstukeinde en hoort
  zo; een leeg kader met een gevuld kader erachter betekent dat de
  stroom in de verkeerde orde is gevuld.
* `contrast` — lopende tekst op een kleurveld onder de
  leesbaarheidsdrempel. Merktekens van een paar tekens tellen niet mee;
  die staan apart als `accentmerken`.

**Aanwijzing, en de render beslist:**

* `wees` en `weduwe` — een alinea die met één regel begint of eindigt op
  een paginagrens. De zetmotor hoort dit te voorkomen; komt het er toch
  door, dan is de ruimte ergens te krap.
* `losse-kop` — een kop als laatste element in een kader.
* `vulgraad` — hoe vol een pagina staat. Een pagina onder 70 procent die
  geen hoofdstukeinde is, heeft ergens een blok dat niet paste.
* `inhoud` — verwijst de inhoudsopgave naar de pagina waar de kop
  werkelijk staat. Dit is de meting die het vaakst iets vindt na een
  handmatige wijziging in het HTML-bestand.
* `beeld-dpi` — de effectieve resolutie van elk beeld op papier. Een
  beeld waarvan de intrinsieke breedte niet te lezen was, staat er als
  `beeld-ongemeten`: daar is niets van bekend, en dat is geen niets.
* `figuur-krap` — een figuur waarvan de geschatte tekst tussen 6 en 8 pt
  uitkomt. Leesbaar op de pers, maar niet meer dan dat.
* `maten` — het aantal verschillende lettergroottes. Boven de acht is er
  een compositieprobleem en geen maatprobleem.
* `lege-kantlijn` — hoeveel pagina's in het kantlijnmodel een lege
  kantlijn hebben. Boven de driekwart verdient dat model zijn ruimte
  niet en is `breed` de betere keuze.
* `tekstwand` — hoeveel spreads achter elkaar niets anders dragen dan
  lopende tekst. Vanaf vier is dat een leesbaarheidsprobleem, en het is
  het enige getal hier dat over de inhoud van de vorm gaat.
* `dichtheid` — hoeveel woorden er werkelijk op een tekstpagina staan,
  met de laagste en de hoogste erbij. **Zonder drempel**, en dat is met
  opzet: hoeveel er op een pagina mág staan hangt af van wat er staat,
  en een grens zou een hoofdstuk met drie figuren afkeuren om iets wat
  geen probleem is. Wat dit getal doet is de dichtheidsknop
  controleerbaar maken.

Gebruik:

    python qa_rapport.py werkmap/rapport.html
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER.parent / "documenten"))
from _browser import browser, wacht_op_letters  # noqa: E402

#: De zetspiegel op het rapportformaat is 650 px breed. Een beeld dat die
#: breedte vult en 650 px bron heeft, komt op 96 dpi. Onder 150 is het op
#: papier zichtbaar zacht; onder 100 is het een fout.
DPI_ZACHT = 150
DPI_FOUT = 100

#: Hoeveel px één regel tekst meet ín een aangeleverd beeld, gerekend in
#: de pixels van dat beeld zelf. **Dit is een aanname en geen meting**:
#: wat er in een PNG staat is voor dit script onzichtbaar, dus wie de
#: figuur belangrijk vindt moet ernaar kijken.
#:
#: De waarde: een aangeleverd beeld komt bijna altijd uit Word,
#: PowerPoint, Excel of een schermafdruk, en die zetten hun kleinste
#: tekst rond 10 pt op 96 dpi — 13,3 px, met een regelafstand van 1,4 is
#: dat 19 px per regel. Zulke bestanden worden op 2× geëxporteerd (een
#: retinascherm, "opslaan als afbeelding" op 192 dpi), en dat is de
#: reden dat ze met drieduizend pixels breed binnenkomen. 19 × 2 = 38.
#:
#: Wat dit getal waard is: een figuur van 3120 px in een kolom van 537 px
#: komt er op 2,7 pt uit, en dat is precies de figuur waar deze meting
#: voor gemaakt is. Staat er grotere tekst in het beeld, dan is het
#: oordeel te streng; staat er kleinere in, te mild. De verhouding zelf
#: — de schaal — staat in de uitvoer, dus de som is met een eigen
#: aanname over te doen.
BRONTEKSTREGEL_PX = 38

#: Van een regel is ongeveer 55 procent kapitaalhoogte; het oog leest de
#: kapitaalhoogte en niet de regelafstand. × 0,75 gaat van px naar pt.
KAPITAALDEEL = 0.55

#: Dezelfde leesvloer als voor een gespatieerd kapitaallabel: onder 6 pt
#: is het op papier geen tekst meer. Tussen 6 en 8 pt leest het, maar
#: alleen met de goede bril en het goede licht.
FIGUUR_VLOER_PT = 6.0
FIGUUR_KRAP_PT = 8.0

#: Hoeveel van de pixels van een beeld op een rand liggen. Het scheidt
#: één ding, en dat is het enige waar het voor bedoeld is: een vlak
#: zónder enig detail — een kleurveld, een lege plaatshouder — draagt
#: geen letter, en die op 3 pt afkeuren zou precies de valse melding
#: zijn die dit script hoort te vermijden. Gemeten op de proefbeelden
#: van deze skill: een egaal veld haalt 0,000 en een tabel met tekst
#: 0,05 tot 0,2. Een foto komt er ruim boven en wordt dus wél
#: beoordeeld — dat een foto geen tekst draagt, is aan het bestand niet
#: te zien, en dan is de melding met de aanname erbij eerlijker dan
#: stilte. Is het beeld niet te lezen (een canvas die niet vrijgegeven
#: wordt), dan wordt er beoordeeld: liever een melding te veel dan een
#: onleesbare figuur die niemand ziet.
FIGUUR_DETAIL = 0.005

#: Hoeveel px een tekstblok over de kaderrand mag steken voordat het
#: `klip` heet. Een regel neemt meer ruimte in dan zijn letters: de
#: halve interlinie onder de laatste regel is leeg papier, en die trekt
#: de meting er zelf al af. Wat hier overblijft is de speling voor
#: afrondingsverschillen in de layout.
KLIP_LUCHT = 1.0

METING = r"""(cfg) => {
  const uit = {paginas: [], klip: [], klipMarge: [], overloop: [], teKlein: [],
               leegKader: [], wees: [], losseKop: [], beeld: [],
               beeldOngemeten: [], contrast: [], maten: {}, inhoud: [],
               legeKantlijn: 0, kantlijnPaginas: 0, tekstwand: 0,
               accentmerken: []};

  const paginas = Array.from(document.querySelectorAll('.pagina'));

  // De drie getallen die van buiten komen; ze staan met hun reden
  // bovenaan dit bestand.
  const BRONTEKSTREGEL = cfg.brontekstregel;
  const KAPITAALDEEL = cfg.kapitaaldeel;
  const KLIPLUCHT = cfg.klipLucht;

  // Wat tekst draagt, en dus wat weg kan zijn als het onder de rand
  // staat. De tags eerst, dan de klassen uit §5 van het stramien die
  // een eigen tekstblok zijn en niet al een `p` of een `li` zijn. Een
  // `sup` en een `span` staan er met opzet niet bij: die zitten ín een
  // regel, hun doos wordt door `vertical-align` verschoven, en waar de
  // regel eindigt zegt het blok eromheen.
  const TEKSTNODES =
    'p, li, h1, h2, h3, h4, h5, h6, td, th, dt, dd, blockquote, pre, ' +
    'figure, figcaption, img, svg, table, ' +
    '.voetnoot, .kantnoot, .pullcitaat, .paneel--rapport, .citaatblok, ' +
    '.chapeau--rapport, .inhoud__regel, .exhibit, .beeldblok, ' +
    '.tabel--rapport, .lid, .colofon, .team, .extra__intro, .extra__lopend';
  // Wat ook zonder tekst inkt op het blad zet.
  const INKT = 'img, svg, hr, .scheiding__streep, .opener-band';

  // Een noot herken je aan zijn markering en niet aan zijn maat. Sinds
  // het nootcijfer in de `sup` zelf staat, is een nootverwijzing
  // `<sup data-noot="3">3</sup>` en een superscript uit de brontekst
  // `<sup>th</sup>` — even klein, even hoog, en alleen het attribuut
  // zegt welke van de twee het is. Wie op maat zoekt, vindt in
  // "September 12th" een noot die er niet is.
  const isNoot = (el) => !!(el.closest('.voetnoot, .kantnoot')
                            || el.closest('[data-noot], [data-noot-id]')
                            || el.closest('[data-toevoeging="nootnummer"]'));

  // Hoeveel detail draagt een beeld. Zie `FIGUUR_DETAIL` bovenaan: dit
  // scheidt een kleurveld van een figuur en verder niets. Het beeld
  // wordt op hoogstens 320 px breed getekend, want meer is er voor
  // deze vraag niet nodig.
  const detailVan = (img) => {
    try {
      const b = Math.min(320, img.naturalWidth);
      const h = Math.max(1, Math.round(img.naturalHeight * (b / img.naturalWidth)));
      const c = document.createElement('canvas');
      c.width = b; c.height = h;
      const ctx = c.getContext('2d', {willReadFrequently: true});
      ctx.drawImage(img, 0, 0, b, h);
      const d = ctx.getImageData(0, 0, b, h).data;
      let randen = 0, n = 0;
      const grijs = (i) => d[i] * .3 + d[i + 1] * .59 + d[i + 2] * .11;
      for (let y = 0; y < h; y++) {
        for (let x = 1; x < b; x++) {
          const i = (y * b + x) * 4;
          if (Math.abs(grijs(i) - grijs(i - 4)) > 8) randen++;
          n++;
        }
      }
      return n ? randen / n : null;
    } catch (e) {
      return null;   // een canvas die niet gelezen mag worden
    }
  };

  // De onderkant van de inkt, niet van de doos. Onder de laatste regel
  // van een tekstblok staat de halve interlinie leeg; die meetellen is
  // hoe een kader met een opsomming als laatste blok een klip ging
  // heten terwijl de laatste regel twee pixels boven de rand eindigde.
  const inktOnder = (el) => {
    const r = el.getBoundingClientRect();
    if (el.matches(INKT) || el.matches('table, figure')) return r.bottom;
    const s = getComputedStyle(el);
    const lh = parseFloat(s.lineHeight), fs = parseFloat(s.fontSize);
    if (!lh || !fs || lh <= fs * 1.2) return r.bottom;
    return r.bottom - (lh - fs * 1.2) / 2;
  };
  const lum = (c) => {
    const m = c.match(/[\d.]+/g); if (!m) return 1;
    const [r, g, b] = m.slice(0, 3).map(Number).map(v => {
      v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };
  const verhouding = (v, a) => {
    const l1 = lum(v), l2 = lum(a);
    return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
  };
  const achtergrondVan = (el) => {
    let n = el;
    while (n && n !== document.body) {
      const c = getComputedStyle(n).backgroundColor;
      if (c && c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent') return c;
      n = n.parentElement;
    }
    return 'rgb(255,255,255)';
  };

  let wandreeks = 0;
  paginas.forEach((p, i) => {
    const nr = i + 1;
    const pr = p.getBoundingClientRect();
    const kaders = Array.from(p.querySelectorAll('.kader'));
    const opener = p.querySelector('[data-plek="opener"]');
    let gevuld = 0, ruimte = 0;

    // Een leeg kader is alleen fout als er ná hem nog een gevuld kader
    // op dezelfde pagina staat: dan is de stroom in de verkeerde orde
    // gevuld. Een leeg láátste kader is het einde van een hoofdstuk of
    // van het rapport, en dat hoort zo. Dit onderscheid stond er eerst
    // niet in, en toen meldde de meting drie hoofdstukeindes als fout.
    let laatsteGevuld = -1;
    kaders.forEach((k, j) => { if (k.children.length) laatsteGevuld = j; });
    const leeg = kaders.filter((k, j) => !k.children.length && j < laatsteGevuld).length;

    kaders.forEach((k, j) => {
      // Klip: staat er tekst ónder de rand waar het kader afsnijdt.
      //
      // `scrollHeight` tegen `clientHeight` kan dat niet zien. Die
      // meting telt de ondermarge van het laatste blok mee — een
      // opsomming heeft er een van 17 tot 22 px — en meldt dan een klip
      // op een kader waar niets aan de hand is. Dat is duur: `klip`
      // blokkeert de oplevering en stuurt iemand op zoek naar tekst die
      // er nooit onder stond. Dus: zoek de diepste tekstdragende node
      // en leg zijn onderkant naast de rand van het kader.
      const kr = k.getBoundingClientRect();
      const ks = getComputedStyle(k);
      const rand = kr.bottom - (parseFloat(ks.borderBottomWidth) || 0);
      let diepte = -Infinity, diepste = null;
      k.querySelectorAll(TEKSTNODES).forEach(el => {
        const r = el.getBoundingClientRect();
        if (!r.width || !r.height) return;
        if (!(el.textContent || '').trim() && !el.matches(INKT)) return;
        const onder = inktOnder(el);
        if (onder > diepte) { diepte = onder; diepste = el; }
      });
      if (diepste && diepte - rand > KLIPLUCHT) {
        uit.klip.push({
          pagina: nr, kader: j + 1,
          over: Math.round((diepte - rand) * 10) / 10,
          // `getAttribute` en niet `className`: op een `svg` is dat
          // laatste een SVGAnimatedString en leest de melding dan
          // "[object SVGAnimatedString]".
          element: diepste.tagName.toLowerCase()
                   + ((diepste.getAttribute('class') || '').trim()
                      ? '.' + diepste.getAttribute('class').trim().split(/\s+/).join('.')
                      : ''),
          bron: diepste.getAttribute('data-bron')
                || (diepste.closest('[data-bron]') || {getAttribute: () => ''})
                     .getAttribute('data-bron') || '',
          tekst: (diepste.textContent || '').trim().slice(-60)});
      } else if (k.scrollHeight > k.clientHeight + 1) {
        // Alleen de ondermarge steekt over de rand. Er gaat geen letter
        // verloren, dus dit is geen melding — het staat hier zodat na
        // te lopen is waar de oude meting op afging.
        uit.klipMarge.push({pagina: nr, kader: j + 1,
                            over: Math.round(k.scrollHeight - k.clientHeight)});
      }
      // De vulgraad meet de onderkant van het laatste kind tegen de
      // onderkant van het kader. `scrollHeight` kan hier niet: dat is
      // minstens `clientHeight`, dus dan meet elke pagina 100 procent
      // vol — ook een pagina met vier regels tekst erop.
      const slot = k.lastElementChild;
      gevuld += slot
        ? Math.min(k.clientHeight,
                   slot.getBoundingClientRect().bottom - k.getBoundingClientRect().top)
        : 0;
      ruimte += k.clientHeight;

      // Wees en weduwe: een fragment van één regel aan een kadergrens.
      const eerste = k.firstElementChild, laatste = k.lastElementChild;
      const regels = (el) => {
        if (!el) return 99;
        const lh = parseFloat(getComputedStyle(el).lineHeight) || 17;
        return Math.round(el.getBoundingClientRect().height / lh);
      };
      if (laatste && laatste.classList.contains('is-gesplitst-kop')
          && regels(laatste) < 2) {
        uit.wees.push({pagina: nr, bron: laatste.getAttribute('data-bron') || ''});
      }
      if (eerste && eerste.classList.contains('is-gesplitst-staart')
          && regels(eerste) < 2) {
        uit.wees.push({pagina: nr, bron: eerste.getAttribute('data-bron') || '',
                       soort: 'weduwe'});
      }
      if (laatste && laatste.hasAttribute('data-kop')) {
        uit.losseKop.push({pagina: nr, kop: (laatste.textContent || '').slice(0, 60)});
      }
    });

    if (leeg) {
      uit.leegKader.push({pagina: nr, leeg: leeg, van: kaders.length});
    }
    const vulgraad = ruimte ? gevuld / ruimte : (opener ? 1 : 0);

    // Wat draagt deze pagina behalve lopende tekst.
    const dragers = p.querySelectorAll(
      '.exhibit, .beeldblok, .tabel--rapport, .pullcitaat, .paneel--rapport, ' +
      '.citaatblok, .opener, .kantnoot, .voetnoot, ul, ol');
    if (!dragers.length && kaders.length) { wandreeks++; }
    else { uit.tekstwand = Math.max(uit.tekstwand, wandreeks); wandreeks = 0; }

    if (p.getAttribute('data-model') === 'kantlijn') {
      uit.kantlijnPaginas++;
      const kl = p.querySelector('.kantlijn');
      if (kl && !kl.children.length) uit.legeKantlijn++;
    }

    // Hoeveel er werkelijk op deze pagina staat. Geen drempel: de
    // dichtheidsknop is een voorkeur en geen regel, en hoeveel er op
    // een pagina mág staan hangt af van wat er staat. Wat dit getal
    // wél doet is de knop controleerbaar maken — je ziet achteraf wat
    // 'dicht' in dit rapport betekende.
    let woorden = 0, tekens = 0;
    kaders.forEach(k => {
      const t = (k.textContent || '').trim();
      if (!t) return;
      tekens += t.length;
      woorden += t.split(/\s+/).filter(Boolean).length;
    });

    uit.paginas.push({
      nr: nr,
      folio: p.getAttribute('data-folio') || '',
      zijde: p.getAttribute('data-zijde') || '',
      model: p.getAttribute('data-model') || '',
      opener: p.getAttribute('data-opener') || '',
      deel: p.getAttribute('data-deel') || '',
      dichtheid: p.getAttribute('data-dichtheid') || '',
      blanco: p.hasAttribute('data-blanco'),
      vulgraad: Math.round(vulgraad * 100) / 100,
      woorden: woorden,
      tekens: tekens,
      dragers: dragers.length
    });

    // Overloop: alles binnen de pagina moet binnen de pagina blijven.
    p.querySelectorAll('.zetspiegel--rapport *').forEach(el => {
      const r = el.getBoundingClientRect();
      if (!r.width || !r.height) return;
      if (r.right > pr.right + 1 || r.left < pr.left - 1
          || r.bottom > pr.bottom + 1 || r.top < pr.top - 1) {
        uit.overloop.push({pagina: nr, klasse: el.className.toString().slice(0, 40),
                           over: Math.round(Math.max(r.right - pr.right,
                                                     pr.left - r.left,
                                                     r.bottom - pr.bottom,
                                                     pr.top - r.top))});
      }
    });
  });
  uit.tekstwand = Math.max(uit.tekstwand, wandreeks);

  // Lettergroottes en te kleine tekst.
  document.querySelectorAll('.pagina p, .pagina li, .pagina td, .pagina th, ' +
      '.pagina h1, .pagina h2, .pagina h3, .pagina span, .pagina figcaption')
    .forEach(el => {
      if (!(el.textContent || '').trim()) return;
      const s = getComputedStyle(el);
      const px = Math.round(parseFloat(s.fontSize) * 100) / 100;
      uit.maten[px] = (uit.maten[px] || 0) + 1;
      const pt = px * 0.75;
      // Drie vloeren, en welke geldt hangt af van wat het element ís.
      //
      // Lopende tekst: 8 pt. Apparaat — noten, bronregels, de kopregel,
      // een bijschrift: 7 pt, en dat is geen coulance maar de gemeten
      // norm. Het McKinsey Global Institute zet zijn voetnoten op 7 pt,
      // Bain zijn exhibitnoten op 6,2. Een gespatieerd kapitaallabel:
      // 6 pt, zoals de casespread Civitates doet.
      //
      // Wat apparaat ís, staat in de markering en niet in de maat. Een
      // noot is een noot omdat hij als noot gemarkeerd is; dat een
      // superscript uit de brontekst even klein staat, maakt daar geen
      // noot van. Zie `isNoot` bovenaan.
      const apparaat = isNoot(el) || el.closest(
        '.rapport-kopregel, .exhibit__bron, .exhibit__noot, ' +
        '.beeldblok figcaption');
      const kapitaal = s.textTransform === 'uppercase';
      const vloer = kapitaal ? 6 : (apparaat ? 7 : 8);
      if (pt < vloer - 0.05) {
        uit.teKlein.push({pt: Math.round(pt * 10) / 10, vloer: vloer,
                          rol: apparaat ? 'apparaat' : (kapitaal ? 'label' : 'lopend'),
                          tekst: (el.textContent || '').trim().slice(0, 40)});
      }
      const v = verhouding(s.color, achtergrondVan(el));
      const groot = px >= 24 || (px >= 18.66 && parseInt(s.fontWeight, 10) >= 700);
      const drempel = groot ? 3 : 4.5;
      if (v >= drempel) return;

      // Onder de drempel, en dan is de vraag wát het is.
      //
      // Oranje op wit haalt 2,58 en emerald 2,1. Dat is te weinig voor
      // een regel tekst en ruim genoeg voor een merkteken van één of
      // twee tekens dat je moet kunnen vínden, niet lezen: een
      // lijstnummer, een nootcijfer, een gespatieerd kapitaallabel. Die
      // worden apart geteld en niet als contrastfout gemeld — maar ze
      // worden wél geteld, met hun kleur, zodat het een keuze blijft en
      // geen ongeluk. Het watermerk hoort per definitie op de grens van
      // het zichtbare en valt er ook buiten.
      //
      // Het nootcijfer staat er op zijn markering en niet op zijn
      // lengte: een noot boven de negenennegentig heeft drie tekens en
      // een noot in een bijlage vier, en dan zou de lengteregel hem
      // ineens als lopende tekst zien.
      const tekst = (el.textContent || '').trim();
      const nootcijfer = el.matches('[data-toevoeging="nootnummer"], sup[data-noot]');
      const merk = nootcijfer || tekst.length <= 3 || kapitaal
                   || el.classList.contains('opener__watermerk');
      const rij = {verhouding: Math.round(v * 100) / 100, drempel: drempel,
                   px: px, kleur: s.color, tekst: tekst.slice(0, 40)};
      if (merk) uit.accentmerken.push(rij); else uit.contrast.push(rij);
    });

  // Beeldresolutie op papier, en hoeveel er van de tekst ín het beeld
  // overblijft.
  //
  // Het tweede is de meting die ontbrak. Een assessmenttabel van 3120 px
  // in een kolom van 537 px past keurig — aan de zetting is niets te
  // zien — en staat op papier op 2,7 pt. De som staat hieronder; de
  // aanname waar hij op rust staat bij `BRONTEKSTREGEL_PX`.
  //
  // De gerenderde breedte komt uit de DOM en niet uit het model. Wordt
  // een breed beeld naar een eigen bredere pagina gepromoveerd, dan
  // meet dit vanzelf die bredere kolom en komt de figuur er ruim boven
  // de vloer uit. Dat is de bedoeling: de meting hoort te zeggen wat er
  // op het blad staat.
  document.querySelectorAll('.pagina img').forEach(img => {
    const b = img.getBoundingClientRect().width;
    const p = img.closest('.pagina');
    const fig = img.closest('figure, .exhibit, .beeldblok');
    const naam = (fig
      ? (((fig.querySelector('.exhibit__nr, figcaption, .exhibit__titel') || {})
            .textContent || '').trim() || fig.getAttribute('data-bron') || '')
      : (img.getAttribute('alt') || '')).slice(0, 50);
    if (!b || !img.naturalWidth) {
      // Zonder intrinsieke breedte is er niets te rekenen. Dat stil
      // overslaan is hoe een figuur onder de vloer ongezien blijft, dus
      // het wordt geteld.
      uit.beeldOngemeten.push({
        pagina: p ? Number(p.getAttribute('data-volgnr') || 0) : 0,
        wat: naam, breedte_px: Math.round(b || 0), bron_px: img.naturalWidth || 0});
      return;
    }
    const schaal = b / img.naturalWidth;
    const pt = BRONTEKSTREGEL * schaal * KAPITAALDEEL * 0.75;
    const detail = detailVan(img);
    uit.beeld.push({
      pagina: p ? Number(p.getAttribute('data-volgnr') || 0) : 0,
      wat: naam,
      breedte_px: Math.round(b), bron_px: img.naturalWidth,
      dpi: Math.round(img.naturalWidth / (b / 96)),
      schaal: Math.round(schaal * 1000) / 1000,
      pt: Math.round(pt * 10) / 10,
      detail: detail === null ? null : Math.round(detail * 1000) / 1000});
  });

  // Klopt de inhoudsopgave met waar de koppen werkelijk staan. De
  // vergelijking gaat op het blok-id: twee secties met dezelfde naam
  // zijn twee secties, en op tekst vergelijken wijst dan naar de
  // verkeerde pagina.
  document.querySelectorAll('.inhoud__regel').forEach(r => {
    const naam = ((r.querySelector('.inhoud__naam') || {}).textContent || '').trim();
    const folio = ((r.querySelector('.inhoud__folio') || {}).textContent || '').trim();
    const id = r.getAttribute('data-verwijst');
    if (!id) { uit.inhoud.push({kop: naam.slice(0, 50), inhoudsopgave: folio,
                                werkelijk: 'geen verwijzing in de regel'}); return; }
    const kop = document.querySelector('.pagina [data-bron="' + id + '"][data-kop]');
    if (!kop) { uit.inhoud.push({kop: naam.slice(0, 50), inhoudsopgave: folio,
                                 werkelijk: 'kop niet gevonden'}); return; }
    const p = kop.closest('.pagina');
    const echt = p ? (p.getAttribute('data-folio') || '') : '';
    if (echt !== folio) {
      uit.inhoud.push({kop: naam.slice(0, 50), inhoudsopgave: folio, werkelijk: echt});
    }
  });
  return uit;
}"""


#: Wacht tot elk beeld gedecodeerd is. `wacht_op_letters` wacht op het
#: netwerk en op de letters; de beelden zitten hier als data-URI in het
#: bestand en zijn dus geen netwerkverkeer. Een beeld dat nog niet
#: gedecodeerd is, meldt `naturalWidth: 0` en heeft nog geen hoogte —
#: dan valt het uit de figuurmeting en staat het kader lager dan het op
#: papier staat. Dat is precies het soort verschil dat twee runs op
#: hetzelfde bestand uit elkaar laat lopen.
BEELDEN_KLAAR = """() => Promise.all(
  Array.from(document.images).map(
    i => i.complete ? null : (i.decode ? i.decode().catch(() => null)
                                       : null))).then(() => true)"""


def draagt_tekst(beeld: dict) -> bool:
    """Kan er tekst in dit beeld staan.

    Een vlak zonder enig randje draagt geen letter en wordt niet op
    leesbaarheid beoordeeld; zie `FIGUUR_DETAIL`. Is het detail niet
    gemeten, dan telt het beeld mee — liever een melding te veel.
    """
    return beeld.get("detail") is None or beeld["detail"] >= FIGUUR_DETAIL


def meet(html: Path) -> dict:
    with browser() as b:
        page = b.new_page(viewport={"width": 1000, "height": 1200})
        page.goto(html.resolve().as_uri())
        # Eerst de letters, dan de beelden, en dan pas meten. Zonder dit
        # meet je een bladspiegel die nog aan het schuiven is, en dan
        # zegt dezelfde meting op hetzelfde bestand twee keer iets
        # anders. Een meting die dat doet, is geen meting.
        wacht_op_letters(page)
        page.evaluate(BEELDEN_KLAAR)
        return page.evaluate(METING, {"brontekstregel": BRONTEKSTREGEL_PX,
                                      "kapitaaldeel": KAPITAALDEEL,
                                      "klipLucht": KLIP_LUCHT})


def beoordeel(m: dict) -> dict:
    kritiek, aanwijzing, klein = [], [], []

    if m["klip"]:
        kritiek.append({"soort": "klip", "aantal": len(m["klip"]),
                        "waar": m["klip"][:6],
                        "wat": "een kader snijdt zijn inhoud af; er staat tekst "
                               "onder de rand. `over` is hoeveel px het diepste "
                               "tekstblok onder de rand uitkomt, `element` welk "
                               "blok dat is en `tekst` het staartje ervan"})
    if m["overloop"]:
        kritiek.append({"soort": "overloop", "aantal": len(m["overloop"]),
                        "waar": m["overloop"][:6],
                        "wat": "een element steekt over de snijrand"})
    if m["teKlein"]:
        kritiek.append({"soort": "te-klein", "aantal": len(m["teKlein"]),
                        "waar": m["teKlein"][:6],
                        "wat": "tekst onder de leesvloer"})
    if m["leegKader"]:
        kritiek.append({"soort": "leeg-kader", "aantal": len(m["leegKader"]),
                        "waar": m["leegKader"][:6],
                        "wat": "een kolom blijft blanco terwijl de pagina tekst heeft"})

    if m["inhoud"]:
        aanwijzing.append({"soort": "inhoud", "aantal": len(m["inhoud"]),
                           "waar": m["inhoud"][:8],
                           "wat": "de inhoudsopgave wijst naar een andere pagina "
                                  "dan waar de kop staat"})
    if m["wees"]:
        aanwijzing.append({"soort": "wees", "aantal": len(m["wees"]),
                           "waar": m["wees"][:6],
                           "wat": "een alinea begint of eindigt met één losse regel"})
    if m["losseKop"]:
        aanwijzing.append({"soort": "losse-kop", "aantal": len(m["losseKop"]),
                           "waar": m["losseKop"][:6],
                           "wat": "een kop staat als laatste in zijn kolom"})

    slap = [p for p in m["paginas"]
            if p["vulgraad"] < 0.7 and not p["opener"] and not p.get("blanco")
            and p["nr"] != len(m["paginas"])]
    if slap:
        aanwijzing.append({"soort": "vulgraad", "aantal": len(slap),
                           "waar": [{"pagina": p["nr"], "vulgraad": p["vulgraad"]}
                                    for p in slap[:8]],
                           "wat": "deze pagina's staan minder dan 70 procent vol"})

    # Wat er van de tekst ín een figuur overblijft. De som staat in de
    # meting; wat hier gebeurt is hem tegen de vloer leggen. De vloer is
    # dezelfde 6 pt die voor een gespatieerd kapitaallabel geldt.
    deel = f"{KAPITAALDEEL}".replace(".", ",")
    schatting = (f"schatting: één regel in het aangeleverde bestand is "
                 f"{BRONTEKSTREGEL_PX} px (10 pt op 96 dpi, op 2× geëxporteerd). "
                 f"pt = {BRONTEKSTREGEL_PX} × schaal × {deel} × 0,75. "
                 f"Wat er werkelijk in het beeld staat, ziet dit script niet — "
                 f"staat er geen tekst in, dan zegt dit getal niets")
    # Een beeld zonder enig detail draagt geen tekst en wordt niet
    # beoordeeld; zie `FIGUUR_DETAIL`. Wat er niet in staat, kan er ook
    # niet te klein in staan.
    beoordeelbaar = [b for b in m["beeld"] if draagt_tekst(b)]
    vlak = [b for b in m["beeld"] if not draagt_tekst(b)]
    onleesbaar = [b for b in beoordeelbaar if b.get("pt", 99) < FIGUUR_VLOER_PT]
    krap = [b for b in beoordeelbaar
            if FIGUUR_VLOER_PT <= b.get("pt", 99) < FIGUUR_KRAP_PT]
    if onleesbaar:
        kritiek.append({"soort": "figuur-te-klein", "aantal": len(onleesbaar),
                        "waar": onleesbaar[:6], "aanname": schatting,
                        "wat": f"de tekst in deze figuren komt onder {FIGUUR_VLOER_PT:.0f} "
                               "pt uit; het beeld past in de kolom maar is niet "
                               "meer te lezen. Zet hem breder, laat hem op een "
                               "eigen pagina promoveren, of vraag om een versie "
                               "met minder in één beeld"})
    if krap:
        aanwijzing.append({"soort": "figuur-krap", "aantal": len(krap),
                           "waar": krap[:6], "aanname": schatting,
                           "wat": f"tussen {FIGUUR_VLOER_PT:.0f} en "
                                  f"{FIGUUR_KRAP_PT:.0f} pt; leesbaar, en niet meer "
                                  "dan dat"})
    if vlak:
        klein.append({"soort": "figuur-zonder-detail", "aantal": len(vlak),
                      "waar": [{"pagina": b["pagina"], "wat": b["wat"],
                                "detail": b["detail"]} for b in vlak[:4]],
                      "wat": "deze beelden dragen geen enkel randje en dus geen "
                             "tekst; ze zijn op leesbaarheid niet beoordeeld. Een "
                             "lege plaatshouder hoort hier te staan, een figuur niet"})
    if m["beeldOngemeten"]:
        aanwijzing.append({"soort": "beeld-ongemeten",
                           "aantal": len(m["beeldOngemeten"]),
                           "waar": m["beeldOngemeten"][:6],
                           "wat": "deze beelden hadden geen intrinsieke breedte of "
                                  "geen breedte op het blad; dpi en leesbaarheid "
                                  "zijn er niet van bekend"})

    fout = [b for b in m["beeld"] if b["dpi"] < DPI_FOUT]
    zacht = [b for b in m["beeld"] if DPI_FOUT <= b["dpi"] < DPI_ZACHT]
    if fout:
        aanwijzing.append({"soort": "beeld-dpi", "aantal": len(fout), "waar": fout[:6],
                           "wat": f"onder {DPI_FOUT} dpi; op papier zichtbaar zacht"})
    if zacht:
        klein.append({"soort": "beeld-dpi-grens", "aantal": len(zacht),
                      "waar": zacht[:4], "wat": f"tussen {DPI_FOUT} en {DPI_ZACHT} dpi"})
    if m["contrast"]:
        kritiek.append({"soort": "contrast", "aantal": len(m["contrast"]),
                        "waar": m["contrast"][:6],
                        "wat": "lopende tekst onder de leesbaarheidsdrempel"})
    if m["accentmerken"]:
        klein.append({"soort": "accentmerken", "aantal": len(m["accentmerken"]),
                      "waar": m["accentmerken"][:4],
                      "wat": "merktekens in het accent onder de tekstdrempel. Dat is "
                             "een keuze en geen fout — oranje op wit haalt 2,58 — "
                             "maar het staat hier zodat het een keuze blijft"})

    maten = sorted(float(k) for k in m["maten"])
    if len(maten) > 8:
        aanwijzing.append({"soort": "maten", "aantal": len(maten), "waar": maten,
                           "wat": "meer dan acht lettergroottes; dat is een "
                                  "compositieprobleem en geen maatprobleem"})
    if m["tekstwand"] >= 4:
        aanwijzing.append({"soort": "tekstwand", "aantal": m["tekstwand"],
                           "wat": f"{m['tekstwand']} pagina's achter elkaar dragen "
                                  "niets anders dan lopende tekst"})
    if m["kantlijnPaginas"] and m["legeKantlijn"] / m["kantlijnPaginas"] > 0.75:
        aanwijzing.append({
            "soort": "lege-kantlijn",
            "aantal": m["legeKantlijn"], "van": m["kantlijnPaginas"],
            "wat": "de kantlijn staat op driekwart van de pagina's leeg; dit rapport "
                   "heeft te weinig noten voor dit model, dus `breed` is beter"})

    return {"kritiek": kritiek, "aanwijzing": aanwijzing, "klein": klein}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=Path)
    ap.add_argument("--alles", action="store_true", help="ook de ruwe metingen")
    a = ap.parse_args()
    if not a.html.exists():
        sys.exit(f"niet gevonden: {a.html}")

    m = meet(a.html)
    oordeel = beoordeel(m)
    # De dichtheid, gemeten. Alleen over de pagina's die tekst dragen:
    # een omslag en een hoofdstukblad hebben er per definitie weinig, en
    # die zouden het gemiddelde omlaag trekken zonder dat het iets zegt.
    tekstpaginas = [p for p in m["paginas"] if p["woorden"] > 40]
    woorden = [p["woorden"] for p in tekstpaginas]
    gemeten = [b for b in m["beeld"] if draagt_tekst(b)]
    verslag = {
        "bestand": str(a.html),
        "paginas": len(m["paginas"]),
        "dichtheid": {
            "knop": (m["paginas"][0].get("dichtheid") if m["paginas"] else ""),
            "woorden per tekstpagina": {
                "gemiddeld": round(sum(woorden) / max(1, len(woorden))),
                "laagste": min(woorden) if woorden else 0,
                "hoogste": max(woorden) if woorden else 0,
            },
            "tekstpaginas": len(tekstpaginas),
            "wat": "geen drempel; dit staat er zodat je ziet wat de knop deed",
        },
        # De blanco pagina's van het katern tellen niet mee: ze staan er
        # omdat een vel vier pagina's is, niet omdat er iets niet paste.
        # Zonder deze uitzondering zakt de gemiddelde vulgraad van een
        # drukklaar rapport met drie lege bladen zichtbaar, en dan meet
        # het getal de drukkerij in plaats van de zetting.
        "gemiddelde vulgraad": round(
            sum(p["vulgraad"] for p in m["paginas"] if not p.get("blanco"))
            / max(1, len([p for p in m["paginas"] if not p.get("blanco")])), 2),
        "lettergroottes": sorted(float(k) for k in m["maten"]),
        "beelden": len(m["beeld"]),
        # De krapste figuur van het stel, zodat het getal er ook staat
        # als niets de vloer raakt. Het is een schatting; zie
        # `BRONTEKSTREGEL_PX`. Beelden zonder detail tellen niet mee:
        # daar staat geen tekst in.
        "kleinste figuurtekst": ({
            "pt": min(b["pt"] for b in gemeten),
            "wat": "geschat, op één aangenomen brontekstregel van "
                   f"{BRONTEKSTREGEL_PX} px"} if gemeten else None),
        **oordeel,
    }
    if a.alles:
        verslag["ruw"] = m
    (a.html.parent / "qa_rapport.json").write_text(
        json.dumps({**verslag, "ruw": m}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(json.dumps(verslag, ensure_ascii=False, indent=2))
    return 1 if oordeel["kritiek"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
