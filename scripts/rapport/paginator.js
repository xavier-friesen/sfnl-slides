/* =====================================================================
   paginator.js — de zetmotor

   Dit is het stuk waar een rapport zich van een document onderscheidt.
   Een document van vier pagina's componeer je met de hand: je weet wat
   er op pagina drie staat omdat je het erop hebt gezet. Een rapport van
   tachtig pagina's kan dat niet — daar loopt de tekst, en de vraag is
   waar hij mag afbreken.

   De motor vult **kaders**. Een kader is een doos met een gemeten
   hoogte; op een pagina in het dubbele model staan er twee, in het
   brede model één. De blokken uit de stroom gaan er één voor één in.
   Past een blok niet meer, dan wordt hij gesplitst op een regelgrens,
   of hij verhuist in zijn geheel naar het volgende kader.

   Vier dingen die deze motor doet en die een simpele "knip om de
   zoveel pixels" niet doet:

   1. **Splitsen op de regel, niet op het blok.** Een alinea van twaalf
      regels waarvan er nog vier passen, laat er vier staan en neemt er
      acht mee. Dat gaat met een `Range` en een binaire zoektocht over
      de tekenposities: de grootste positie waarvan de onderkant nog
      boven de kadergrens ligt. Daarna schuift de knip terug naar de
      dichtstbijzijnde woordgrens, want een woord doormidden knippen zou
      de tekst veranderen.

   2. **Weduwen en wezen.** Eén regel van een alinea onderaan een pagina
      is een wees; één regel bovenaan de volgende is een weduwe. Allebei
      verboden: is er maar plek voor één regel, dan gaat de hele alinea
      mee; blijft er maar één regel over, dan gaat er een tweede mee.

   3. **Een kop blijft bij zijn tekst.** Een sectiekop onderaan een
      pagina met zijn eerste alinea op de volgende is het defect dat een
      lezer als eerste ziet. De kop neemt minimaal twee regels van de
      alinea eronder mee, en lukt dat niet, dan verhuizen ze samen.

   4. **Voetnoten korten de tekst in.** Een noot staat op de pagina waar
      zijn verwijzing staat. Dat betekent dat de tekstruimte kleiner
      wordt op het moment dat de verwijzing geplaatst wordt — en dat de
      motor daarna opnieuw moet meten of het blok er nog wel in past.
      Deze lus is de reden dat de zetting soms een blok terugneemt dat
      hij net had geplaatst.

   Wat de motor uitdrukkelijk **niet** doet, is tekst veranderen. Hij
   splitst en verplaatst en verder niets: geen woord wordt afgekort,
   geen zin ingekort, geen kop herschreven. `tekstcheck.py` controleert
   dat achteraf door alle stukken van hetzelfde `data-bron` weer aan
   elkaar te plakken en met de bron te vergelijken.

   Aangeroepen als `window.zet(config)` vanuit `bouw.py`. Levert een
   verslag terug met het aantal pagina's, de kop-naar-folio-kaart voor
   de inhoudsopgave, en wat er is misgegaan.
   ===================================================================== */

(function () {
  'use strict';

  var TOLERANTIE = 0.75;   // px. Onder deze marge heet een blok passend.
  var MAX_RONDEN = 20000;  // noodrem tegen een lus die niet vordert.

  /* ------------------------------------------------------------------
     Meten
     ------------------------------------------------------------------ */

  function regelhoogte(el) {
    var s = getComputedStyle(el);
    var lh = parseFloat(s.lineHeight);
    if (!lh || isNaN(lh)) lh = parseFloat(s.fontSize) * 1.3;
    return lh;
  }

  function past(kader) {
    return kader.scrollHeight <= kader.clientHeight + TOLERANTIE;
  }

  /**
   * Hoeveel er onderaan het kader nog vrij is, in px.
   *
   * Niet `clientHeight - scrollHeight`: `scrollHeight` is per definitie
   * minstens `clientHeight`, dus dat is voor een niet-vol kader altijd
   * nul of negatief. Dat was fout en het was duur — de kopregel die er
   * twee regels vrij eist, gooide daardoor élke kop naar het volgende
   * kader, en het brede model liep van 40 naar 55 pagina's.
   *
   * Wat wél meet: de onderkant van het laatste kind tegen de onderkant
   * van het kader.
   */
  function ruimteOver(kader) {
    var laatste = kader.lastElementChild;
    if (!laatste) return kader.clientHeight;
    return grensVan(kader) - laatste.getBoundingClientRect().bottom;
  }

  /** De onderkant van het kader in schermcoördinaten. */
  function grensVan(kader) {
    return kader.getBoundingClientRect().top + kader.clientHeight;
  }

  /* ------------------------------------------------------------------
     Tekstknopen en posities

     Een alinea is in de DOM geen platte reeks tekens maar een boom met
     `<b>`, `<i>` en `<sup>` erin. Om op een tekenpositie te kunnen
     knippen, wordt die boom eerst afgevlakt tot een lijst tekstknopen
     met hun beginpositie. Daarna is een globale positie een paar
     (knoop, offset), en `Range` kan daarop knippen zonder de inline
     opmaak stuk te maken.
     ------------------------------------------------------------------ */

  function tekstknopen(el) {
    var uit = [], totaal = 0;
    var tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null);
    var n;
    while ((n = tw.nextNode())) {
      var len = n.nodeValue.length;
      if (!len) continue;
      uit.push({ knoop: n, start: totaal, lengte: len });
      totaal += len;
    }
    return { knopen: uit, totaal: totaal };
  }

  function positie(vlak, i) {
    var lijst = vlak.knopen;
    for (var k = 0; k < lijst.length; k++) {
      if (i <= lijst[k].start + lijst[k].lengte) {
        return [lijst[k].knoop, i - lijst[k].start];
      }
    }
    var l = lijst[lijst.length - 1];
    return [l.knoop, l.lengte];
  }

  function volleTekst(vlak) {
    var s = '';
    for (var k = 0; k < vlak.knopen.length; k++) s += vlak.knopen[k].knoop.nodeValue;
    return s;
  }

  /** Het aantal regelboxen tussen het begin van el en positie i. */
  function regelsTot(vlak, range, i) {
    if (i <= 0) return 0;
    var p = positie(vlak, i);
    range.setStart(vlak.knopen[0].knoop, 0);
    range.setEnd(p[0], p[1]);
    var rects = range.getClientRects();
    var tops = {}, aantal = 0;
    for (var k = 0; k < rects.length; k++) {
      if (rects[k].height <= 0) continue;
      var sleutel = Math.round(rects[k].top * 2);
      if (!tops[sleutel]) { tops[sleutel] = 1; aantal++; }
    }
    return aantal;
  }

  /* ------------------------------------------------------------------
     Splitsen van een tekstblok op een regelgrens
     ------------------------------------------------------------------ */

  /**
   * Zoekt de grootste tekenpositie waarvan de onderkant nog binnen het
   * kader valt, schuift die terug naar een woordgrens, en past de
   * weduwe- en wezenregel toe.
   *
   * Levert `null` wanneer er niet zinnig te splitsen valt — dan hoort
   * het hele blok te verhuizen.
   */
  function knippunt(el, grens, minKop, minStaart) {
    var vlak = tekstknopen(el);
    if (!vlak.totaal) return null;
    var range = document.createRange();

    function ondergrensVan(i) {
      var p = positie(vlak, i);
      range.setStart(vlak.knopen[0].knoop, 0);
      range.setEnd(p[0], p[1]);
      var rects = range.getClientRects();
      var onder = -Infinity;
      for (var k = 0; k < rects.length; k++) {
        if (rects[k].height > 0 && rects[k].bottom > onder) onder = rects[k].bottom;
      }
      return onder === -Infinity ? -Infinity : onder;
    }

    if (ondergrensVan(vlak.totaal) <= grens + TOLERANTIE) return null;  // past heel

    var lo = 0, hi = vlak.totaal;
    while (lo < hi) {
      var mid = Math.ceil((lo + hi) / 2);
      if (ondergrensVan(mid) <= grens + TOLERANTIE) lo = mid; else hi = mid - 1;
    }
    if (lo <= 0) return null;

    // Terug naar een woordgrens. De spatie zelf blijft in het kopstuk,
    // want anders verdwijnt hij en verandert de tekst.
    var tekst = volleTekst(vlak);
    var knip = lo;
    while (knip > 0 && !/\s/.test(tekst.charAt(knip - 1))) knip--;
    if (knip <= 0) return null;

    var regelsKop = regelsTot(vlak, range, knip);
    if (regelsKop < minKop) return null;          // wees: alles verhuist

    // Weduwe: blijft er maar één regel over, dan gaat er een regel meer
    // mee. Dat kan een paar keer terug moeten, want een regel terug
    // maakt de staart twee regels.
    var totaalRegels = regelsTot(vlak, range, vlak.totaal);
    var pogingen = 0;
    while (totaalRegels - regelsKop < minStaart && pogingen < 6) {
      var doel = regelsKop - 1;
      if (doel < minKop) return null;
      var nieuw = knip;
      while (nieuw > 0 && regelsTot(vlak, range, nieuw) > doel) {
        nieuw--;
        while (nieuw > 0 && !/\s/.test(tekst.charAt(nieuw - 1))) nieuw--;
      }
      if (nieuw <= 0) return null;
      knip = nieuw;
      regelsKop = regelsTot(vlak, range, knip);
      pogingen++;
    }
    return { positie: knip, vlak: vlak };
  }

  /**
   * Knipt het blok in tweeën. Het kopstuk komt op de plek van het
   * origineel te staan; het origineel houdt de staart en wordt
   * teruggegeven zodat de aanroeper hem weer in de wachtrij kan zetten.
   */
  function knip(el, punt) {
    var p = positie(punt.vlak, punt.positie);
    var range = document.createRange();
    range.setStart(el, 0);
    range.setEnd(p[0], p[1]);
    var fragment = range.extractContents();

    var kop = el.cloneNode(false);
    kop.appendChild(fragment);
    kop.classList.add('is-gesplitst-kop');
    kop.setAttribute('data-deel', String((+el.getAttribute('data-deel') || 1)));
    el.classList.add('is-gesplitst-staart');
    el.setAttribute('data-deel', String((+el.getAttribute('data-deel') || 1) + 1));
    el.parentNode.insertBefore(kop, el);
    el.parentNode.removeChild(el);
    return { kop: kop, staart: el };
  }

  /* ------------------------------------------------------------------
     Splitsen van een lijst en van een tabel

     Allebei op hun eigen natuurlijke grens: een lijst tussen twee
     items, een tabel tussen twee rijen. De laatste passende `li` mag
     daarna nog op de regel gesplitst worden; een tabelrij niet, want
     een rij die halverwege afbreekt is geen rij meer.
     ------------------------------------------------------------------ */

  function splitsContainer(el, kader, itemKiezer, naSplitsing) {
    var items = itemKiezer(el);
    if (items.length < 2) return null;
    var grens = grensVan(kader);
    var laatstePassend = -1;
    for (var i = 0; i < items.length; i++) {
      if (items[i].getBoundingClientRect().bottom <= grens + TOLERANTIE) laatstePassend = i;
      else break;
    }
    if (laatstePassend < 0) return null;
    if (laatstePassend >= items.length - 1) return null;

    var staart = el.cloneNode(false);
    staart.classList.add('is-gesplitst-staart');
    el.classList.add('is-gesplitst-kop');
    for (var j = items.length - 1; j > laatstePassend; j--) {
      staart.insertBefore(items[j], staart.firstChild);
    }

    // Hermeten, want de onderkant van het laatste item is niet de
    // onderkant van de lijst: daar komt de ondermarge van de lijst zelf
    // nog bij. Gemeten op de proef: een gesplitste opsomming stak zo
    // 7 px over de kadergrens, en dat was zichtbaar als klip.
    var rondjes = 0;
    while (!past(kader) && el.children.length > 1 && rondjes++ < 40) {
      staart.insertBefore(el.lastElementChild, staart.firstChild);
    }
    if (!el.children.length) {
      // Er past niets meer; de splitsing draaien we terug.
      while (staart.firstChild) el.appendChild(staart.firstChild);
      el.classList.remove('is-gesplitst-kop');
      return null;
    }
    if (naSplitsing) naSplitsing(el, staart, el.children.length - 1);
    return staart;
  }

  function splitsLijst(el, kader) {
    return splitsContainer(el, kader,
      function (l) { return Array.prototype.slice.call(l.children); },
      function (kop, staart) {
        // De nummering van een genummerde lijst loopt door. Zonder dit
        // begint het vervolg op de volgende pagina weer bij 1.
        if (staart.tagName === 'OL') {
          var start = (+kop.getAttribute('start') || 1) + kop.children.length;
          staart.setAttribute('start', String(start));
          staart.style.counterReset = 'opsomming ' + (start - 1);
        }
      });
  }

  function splitsTabel(el, kader) {
    var body = el.querySelector('tbody');
    if (!body) return null;
    var kop = el.querySelector('thead');
    var grens = grensVan(kader);
    var rijen = Array.prototype.slice.call(body.rows);
    var laatstePassend = -1;
    for (var i = 0; i < rijen.length; i++) {
      if (rijen[i].getBoundingClientRect().bottom <= grens + TOLERANTIE) laatstePassend = i;
      else break;
    }
    // Een tabel met minder dan twee rijen op deze pagina is geen tabel.
    if (laatstePassend < 1 || laatstePassend >= rijen.length - 1) return null;

    var staart = el.cloneNode(false);
    staart.classList.add('is-gesplitst-staart');
    if (kop) {
      var herhaald = kop.cloneNode(true);
      herhaald.classList.add('is-herhaald');
      // De kop staat nu twee keer in het document. Dat is toegevoegde
      // tekst — nodig, want een vervolgtabel zonder kolomnamen is
      // onleesbaar — en tekstcheck.py moet hem daarom kunnen overslaan.
      herhaald.setAttribute('data-toevoeging', 'tabelkop');
      staart.appendChild(herhaald);
    }
    var nieuwBody = document.createElement('tbody');
    for (var j = laatstePassend + 1; j < rijen.length; j++) nieuwBody.appendChild(rijen[j]);
    staart.appendChild(nieuwBody);
    el.classList.add('is-gesplitst-kop');

    // Hermeten, om dezelfde reden als bij de lijst: de onderkant van de
    // laatste rij is niet de onderkant van de tabel.
    var rondjes = 0;
    while (!past(kader) && body.rows.length > 1 && rondjes++ < 60) {
      nieuwBody.insertBefore(body.rows[body.rows.length - 1], nieuwBody.firstChild);
    }
    if (!body.rows.length) {
      while (nieuwBody.rows.length) body.appendChild(nieuwBody.rows[0]);
      el.classList.remove('is-gesplitst-kop');
      return null;
    }
    return staart;
  }

  /* ------------------------------------------------------------------
     De pagina's
     ------------------------------------------------------------------ */

  function Zetter(cfg) {
    this.cfg = cfg;
    this.rapport = document.getElementById('rapport');
    this.paginas = [];
    this.pagina = null;
    this.kaders = [];
    this.kaderNr = 0;
    this.folio = cfg.eersteFolio || 1;
    this.kopregel = { hoofdstuk: '', nummer: '' };
    this.kaart = [];        // kop -> folio, voor de inhoudsopgave
    this.extra = [];        // blokken die vóór het huidige terug moeten
    this.deel = '';         // '' of 'bijlagen', vanaf het scheidingsblad
    this.klachten = [];
  }

  Zetter.prototype.sjabloon = function (naam) {
    var t = document.getElementById('sjabloon-' + naam);
    if (!t) throw new Error('sjabloon ontbreekt: ' + naam);
    return t.content.firstElementChild.cloneNode(true);
  };

  Zetter.prototype.nieuwePagina = function (opties) {
    opties = opties || {};
    var p = this.sjabloon(opties.sjabloon || 'tekst');
    var zijde = (this.paginas.length + (this.cfg.eersteZijde === 'verso' ? 1 : 0)) % 2
      ? 'verso' : 'recto';
    p.setAttribute('data-zijde', zijde);
    p.setAttribute('data-register', this.cfg.register || 'helder');
    p.setAttribute('data-formaat', this.cfg.formaat || 'sfnl');
    p.setAttribute('data-dichtheid', this.cfg.dichtheid || 'gemiddeld');
    // Vanaf het scheidingsblad draagt elke pagina dat hij bij de
    // bijlagen hoort. Dat stuurt de kicker en de kopregel.
    if (this.deel) p.setAttribute('data-deel', this.deel);
    if (opties.scheiding) p.setAttribute('data-scheiding', opties.scheiding);
    var basis = this.cfg.paginamodel || this.cfg.model;
    var model = opties.model || basis;
    p.setAttribute('data-model', model);
    // Een pagina die van het basismodel afwijkt, houdt wél de broodmaat
    // van het basismodel. Dat geldt in een flexibel rapport, en het
    // geldt net zo goed voor de ene brede pagina die een te wijde tabel
    // in een dubbel rapport krijgt: zonder dit staat die pagina op 11 pt
    // naast tweeëntwintig pagina's op 10, en meet qa_rapport.py een
    // achtste lettergrootte.
    //
    // Op de pagina en niet op het lichaam, want het eindbestand heeft
    // een ander lichaam dan de werkpagina waarin gezet is.
    if (this.cfg.model === 'flexibel' || model !== basis) {
      p.setAttribute('data-flex', 'ja');
    }
    p.setAttribute('data-volgnr', String(this.paginas.length + 1));
    if (opties.opener) p.setAttribute('data-opener', opties.opener);
    if (opties.veld) p.setAttribute('data-veld', opties.veld);
    if (opties.inkt) p.setAttribute('data-inkt', opties.inkt);

    // Het paginanummer staat altíjd op de pagina als gegeven, ook als
    // het er niet op gedrukt wordt. De inhoudsopgave leest het daar af,
    // en die moet ook naar een pagina kunnen verwijzen waarop de folio
    // zelf onderdrukt is — een hoofdstukblad, bijvoorbeeld.
    p.setAttribute('data-folio', String(this.folio));
    var folio = p.querySelector('.rapport-folio');
    if (folio && (opties.folio === false || (this.cfg.folioVanaf || 1) > this.folio)) {
      folio.remove();
    } else if (folio) {
      folio.textContent = String(this.folio);
    }
    var kop = p.querySelector('.rapport-kopregel');
    if (kop) {
      if (opties.kopregel === false || !this.kopregel.hoofdstuk) {
        kop.remove();
      } else {
        var links = kop.querySelector('[data-plek="links"]');
        var rechts = kop.querySelector('[data-plek="rechts"]');
        if (links) links.textContent = this.cfg.rapporttitel || '';
        if (rechts) rechts.textContent = this.kopregel.hoofdstuk;
        p.setAttribute('data-kopregel', this.kopregel.hoofdstuk);
      }
    }
    this.rapport.appendChild(p);
    this.paginas.push(p);
    this.folio++;
    this.pagina = p;
    this.kaders = Array.prototype.slice.call(p.querySelectorAll('.kader'));
    this.kaderNr = 0;
    return p;
  };

  Zetter.prototype.kader = function () {
    if (!this.pagina || this.kaderNr >= this.kaders.length) this.nieuwePagina();
    return this.kaders[this.kaderNr];
  };

  Zetter.prototype.volgendKader = function () {
    this.kaderNr++;
    if (this.kaderNr >= this.kaders.length) this.nieuwePagina();
    return this.kaders[this.kaderNr];
  };

  /* --- voetnoten --------------------------------------------------- */

  Zetter.prototype.notenVan = function (blok) {
    var merken = blok.querySelectorAll('sup[data-noot]');
    var uit = [];
    for (var i = 0; i < merken.length; i++) uit.push(merken[i].getAttribute('data-noot'));
    return uit;
  };

  /**
   * De noten van dit blok op deze pagina zetten.
   *
   * In het kantlijnmodel gaan ze de kantlijn in en niet de voet: daar
   * staan ze naast de regel waar ze bij horen, en dan kost een noot de
   * tekst geen hoogte. In de andere twee modellen staan ze aan de voet,
   * en dan krimpt het raster mee — de flexbox regelt dat. Vandaar dat
   * de aanroeper na het zetten van een noot opnieuw moet meten of het
   * blok er nog wel in past, en dat `herstel` bestaat voor het geval
   * dat wat er al stond er niet meer in past.
   */
  Zetter.prototype.zetNoten = function (blok) {
    if (this.cfg.notenOpPagina === false) return [];
    var ids = this.notenVan(blok);
    if (!ids.length) return [];
    var kantlijn = this.pagina.querySelector('.kantlijn');
    var bak = kantlijn || this.pagina.querySelector('.voetnoten');
    if (!bak) return [];
    var gezet = [];
    for (var i = 0; i < ids.length; i++) {
      var bron = document.getElementById('noot-' + ids[i]);
      if (!bron) continue;
      if (this.rapport.querySelector('[data-noot-id="' + ids[i] + '"]')) continue;
      var noot = bron.cloneNode(true);
      noot.removeAttribute('id');
      noot.setAttribute('data-noot-id', ids[i]);
      bak.appendChild(noot);
      gezet.push(noot);
    }
    return gezet;
  };

  /** De noten die op deze pagina bij dit blok horen. */
  Zetter.prototype.notenOpPaginaVan = function (blok) {
    var ids = this.notenVan(blok), uit = [];
    for (var i = 0; i < ids.length; i++) {
      var el = this.pagina.querySelector('[data-noot-id="' + ids[i] + '"]');
      if (el) uit.push(el);
    }
    return uit;
  };

  Zetter.prototype.haalNotenWeg = function (noten) {
    for (var i = 0; i < noten.length; i++) {
      if (noten[i].parentNode) noten[i].parentNode.removeChild(noten[i]);
    }
  };

  /* --- het plaatsen ------------------------------------------------ */

  Zetter.prototype.isSplitsbaar = function (el) {
    if (el.hasAttribute('data-heel')) return false;
    var t = el.tagName;
    return t === 'P' || t === 'UL' || t === 'OL' || t === 'TABLE' || t === 'DIV';
  };

  Zetter.prototype.splits = function (el, kader) {
    var t = el.tagName;
    if (t === 'UL' || t === 'OL') return splitsLijst(el, kader);
    if (t === 'TABLE') return splitsTabel(el, kader);
    var minKop = +(el.getAttribute('data-min-kop') || this.cfg.minRegelsOnder || 2);
    var minStaart = +(el.getAttribute('data-min-staart') || this.cfg.minRegelsBoven || 2);
    var punt = knippunt(el, grensVan(kader), minKop, minStaart);
    if (!punt) return null;
    return knip(el, punt).staart;
  };

  /**
   * Zet één blok. Levert een blok terug dat nog geplaatst moet worden
   * (de staart van een splitsing), of `null` wanneer het blok helemaal
   * geplaatst is.
   */
  /** Staat er al iets op de huidige pagina. */
  Zetter.prototype.isBegonnen = function () {
    if (!this.pagina) return false;
    if (this.kaderNr > 0) return true;
    for (var i = 0; i < this.kaders.length; i++) {
      if (this.kaders[i].children.length) return true;
    }
    return this.pagina.querySelector('[data-plek="opener"], .opener-band') !== null;
  };

  Zetter.prototype.plaats = function (blok) {
    if (blok.hasAttribute('data-hoofdstuk')) {
      this.kopregel.hoofdstuk = blok.getAttribute('data-hoofdstuk');
    }

    // Een blok dat een heel blad voor zichzelf opeist: de omslag, en de
    // hoofdstukopener in de bladvariant. Die gaan niet door een kader.
    if (blok.getAttribute('data-opener') === 'blad') {
      var sjabloon = blok.getAttribute('data-sjabloon') || 'opener';
      if (blok.getAttribute('data-scheiding') === 'bijlagen') this.deel = 'bijlagen';
      this.sluitPagina();
      if (this.cfg.dubbelzijdig && sjabloon !== 'omslag') this.naarRecto();
      var bladzij = this.nieuwePagina({
        // De omslag is geen hoofdstukblad: op een hoofdstukblad hangt de
        // titel onderaan, op een omslag staat hij in het midden.
        sjabloon: sjabloon, opener: sjabloon === 'omslag' ? 'omslag' : 'blad',
        kopregel: false,
        folio: blok.getAttribute('data-folio') !== 'nee',
        veld: blok.getAttribute('data-veld') || undefined,
        inkt: blok.getAttribute('data-inkt') || undefined,
        scheiding: blok.getAttribute('data-scheiding') || undefined
      });
      bladzij.querySelector('[data-plek="opener"]').appendChild(blok);
      this.sluitPagina();
      return null;
    }

    // Een blok dat op een nieuwe pagina hoort te beginnen.
    if (blok.hasAttribute('data-nieuwe-pagina') && this.isBegonnen()) {
      this.sluitPagina();
    }

    if (!this.pagina) {
      if (this.cfg.dubbelzijdig && blok.hasAttribute('data-hoofdstuk')) this.naarRecto();
      var opties = {};
      if (blok.getAttribute('data-opener') === 'band') {
        opties.opener = 'band';
        opties.kopregel = false;
      }
      if (blok.getAttribute('data-model')) opties.model = blok.getAttribute('data-model');
      this.nieuwePagina(opties);
    }
    var kader = this.kader();

    // De band staat buiten de zetspiegel en duwt hem omlaag. `--balk`
    // gaat op de pagina en niet op de band, zodat de zetspiegel en het
    // raster hem allebei meetellen zonder dat de hoogte twee keer
    // genoemd wordt.
    if (blok.getAttribute('data-opener') === 'band') {
      var plek = this.pagina.querySelector('[data-plek="band"]');
      if (plek) {
        plek.className = 'opener-band';
        plek.setAttribute('data-veld', blok.getAttribute('data-veld') || '');
        plek.appendChild(blok);
        this.pagina.style.setProperty('--balk',
          (blok.getAttribute('data-balk') || this.cfg.bandhoogte || 220) + 'px');
        this.pagina.setAttribute('data-opener', 'band');
        return null;
      }
    }

    // De hoofdstukopener staat over de volle zetspiegel, boven het
    // raster. In het dubbele model is dat het verschil tussen een
    // hoofdstuktitel over de pagina en een hoofdstuktitel in de
    // linkerkolom; in de andere modellen verandert er niets aan de
    // breedte en houdt het de plaatsing op één plek.
    if (blok.classList.contains('opener')) {
      var kopplek = this.pagina.querySelector('[data-plek="kop"]');
      if (kopplek && !kopplek.children.length) {
        kopplek.appendChild(blok);
        return null;
      }
    }

    var eerste = kader.children.length === 0;
    kader.appendChild(blok);
    if (eerste) blok.classList.add('is-eerste-in-kader');

    // Breder dan het kader. Dit is het enige geval waarin de hoogte
    // niets zegt: een tabel van acht kolommen past qua hoogte prima in
    // een kolom van 310 px en steekt er 74 px naast uit. `scrollHeight`
    // ziet dat niet, dus het ging stil mis.
    if (blok.scrollWidth > kader.clientWidth + 1) {
      var over = Math.round(blok.scrollWidth - kader.clientWidth);
      if (this.kaders.length > 1 && !blok.classList.contains('is-vol-geprobeerd')) {
        // In het dubbele model: eigen pagina over de volle zetspiegel.
        kader.removeChild(blok);
        blok.classList.add('is-vol-geprobeerd');
        this.gooiLegePaginaWeg();
        this.sluitPagina();
        this.nieuwePagina({ model: 'breed' });
        this.kaders[0].appendChild(blok);
        kader = this.kaders[0];
        eerste = true;
      }
      if (blok.scrollWidth > kader.clientWidth + 1) {
        // Nog steeds te breed, ook over de volle breedte. Dan wordt de
        // tabel in zijn breedte gedwongen — de cellen breken af, er
        // gaat geen tekst verloren — en het gaat als klacht mee, want
        // dit is een inhoudelijk probleem en geen zetprobleem.
        blok.classList.add('is-te-breed');
        this.klachten.push({
          soort: 'te-breed',
          bron: blok.getAttribute('data-bron') || '',
          over: over,
          folio: this.pagina.getAttribute('data-folio') || '',
          wat: 'Dit blok is ' + over + ' px breder dan de volle zetspiegel. Het is '
             + 'in de breedte gedwongen, dus de cellen breken af. Een tabel met zo '
             + 'veel kolommen hoort gekanteld, gesplitst of naar een liggende bijlage.'
        });
      }
    }

    // Een kop die niet genoeg ruimte overlaat voor twee regels tekst,
    // hoort hier niet te staan.
    //
    // Dit is de vooruitkijkende helft van de kop-blijft-bij-zijn-tekst-
    // regel, en het is de helft die het werk doet. `bindKop` en
    // `neemKopMee` repareren achteraf en zien niet elk geval: een kop
    // die past, gevolgd door een alinea die past, gevolgd door een blok
    // dat het kader alsnog laat krimpen. Vooraf meten kan niet misgaan:
    // is er na de kop geen plek voor twee regels, dan gaat de kop mee
    // naar het volgende kader en is er niets te repareren. Gemeten op de
    // proef in het brede model: "Wie financiert wat" stond alleen
    // onderaan pagina 34.
    if (blok.hasAttribute('data-kop') && !eerste && past(kader)) {
      var lh = regelhoogte(kader);
      var onder = parseFloat(getComputedStyle(blok).marginBottom) || 0;
      if (ruimteOver(kader) - onder < 2 * lh) {
        kader.removeChild(blok);
        blok.classList.remove('is-eerste-in-kader');
        this.volgendKader();
        return blok;
      }
    }

    var noten = this.zetNoten(blok);

    // Een voetnoot kort de héle pagina in, niet alleen de kolom waar
    // zijn verwijzing staat. In het dubbele model betekent dat: een noot
    // van een blok in kolom 2 maakt kolom 1 korter, en dan past wat daar
    // al stond er niet meer in. Achteraf repareren geeft een lus — het
    // blok dat je terugneemt neemt zijn noot mee, de kolom groeit weer,
    // en het blok past weer. Dus wordt het vooraf beslist: past de
    // pagina niet meer mét dit blok en zijn noot, dan hoort dit blok op
    // de volgende pagina. Gemeten op de proef in het dubbele model: één
    // pagina met 7 px klip in kolom 1, veroorzaakt door een noot uit
    // kolom 2.
    if (past(kader) && !this.paginaPast() && (!eerste || this.kaderNr > 0)) {
      this.haalNotenWeg(noten);
      kader.removeChild(blok);
      blok.classList.remove('is-eerste-in-kader');
      this.neemKopMee(kader);
      this.sluitPagina();
      return blok;
    }

    if (past(kader)) {
      this.bindKop(blok, kader);
      this.herstel(kader);
      return null;
    }

    // Past niet. Eerst proberen te splitsen.
    if (this.isSplitsbaar(blok)) {
      var staart = this.splits(blok, kader);
      if (staart) {
        // De noten van de staart horen niet meer op deze pagina.
        this.haalNotenWeg(noten);
        this.zetNoten(kader.lastElementChild || blok);
        if (!past(kader)) {
          // Zelfs het kopstuk past niet meer nu de noten erbij staan.
          var kopstuk = kader.lastElementChild;
          if (kopstuk && !eerste) {
            kader.removeChild(kopstuk);
            this.samenvoegen(kopstuk, staart);
            this.haalNotenWeg(this.notenOpPaginaVan(kopstuk));
            this.volgendKader();
            return kopstuk;
          }
        }
        this.volgendKader();
        return staart;
      }
    }

    // Niet splitsbaar of niet zinnig te splitsen: het blok verhuist.
    this.haalNotenWeg(noten);
    kader.removeChild(blok);
    blok.classList.remove('is-eerste-in-kader');

    this.neemKopMee(kader);

    if (eerste) {
      // Het blok past niet eens in een leeg kader. Terugzetten en
      // melden — hier is de vorm te klein voor de inhoud, en dat is een
      // ontwerpbesluit en geen zetprobleem.
      kader.appendChild(blok);
      this.zetNoten(blok);
      this.klachten.push({
        soort: 'te-groot-voor-kader',
        bron: blok.getAttribute('data-bron') || '',
        tekst: (blok.textContent || '').slice(0, 90),
        folio: this.pagina.getAttribute('data-folio') || '',
        wat: 'Dit blok past niet in een heel kader en steekt eruit.'
      });
      this.volgendKader();
      return null;
    }
    this.volgendKader();
    return blok;
  };

  /**
   * Het kader terugsnoeien tot het weer past.
   *
   * Nodig omdat een kader kán krimpen ná het plaatsen: een voetnoot van
   * een later blok kort de tekstkolom in, en dan past wat er al stond
   * niet meer. Het laatste blok gaat er dan af en terug in de wachtrij.
   * Zonder dit sneed het kader zijn eigen inhoud af — gemeten op de
   * proef in het dubbele model: één pagina met 7 px klip.
   */
  Zetter.prototype.herstel = function (kader) {
    var terug = [];
    var rondjes = 0;
    while (!past(kader) && kader.children.length > 1 && rondjes++ < 40) {
      var laatste = kader.lastElementChild;
      this.haalNotenWeg(this.notenOpPaginaVan(laatste));
      kader.removeChild(laatste);
      laatste.classList.remove('is-eerste-in-kader');
      terug.unshift(laatste);        // in leesvolgorde houden
    }
    if (!terug.length) return false;
    // En als er nu een kop als laatste overblijft, gaat die ook mee.
    var kop = kader.lastElementChild;
    if (kop && kop.hasAttribute('data-kop')
        && !kop.classList.contains('is-eerste-in-kader')) {
      kader.removeChild(kop);
      terug.unshift(kop);
    }
    this.extra = terug.concat(this.extra);
    this.volgendKader();
    return true;
  };

  /** Passen álle kaders op deze pagina nog. */
  Zetter.prototype.paginaPast = function () {
    for (var i = 0; i < this.kaders.length; i++) {
      if (!past(this.kaders[i])) return false;
    }
    return true;
  };

  /**
   * De kop die als laatste in het kader staat mee terug in de wachtrij.
   *
   * Dit is het tweede geval van de kop-blijft-bij-zijn-tekst-regel, en
   * het is het geval dat `bindKop` niet ziet: die kijkt of het blok
   * onder de kop te weinig regels kríjgt, en hier krijgt het er nul
   * omdat het helemaal verhuist. Gemeten op de eerste proef in het
   * dubbele model: "De uitvoerder telt" stond onderaan een kolom met
   * zijn tekst op de volgende pagina.
   */
  Zetter.prototype.neemKopMee = function (kader) {
    var kop = kader.lastElementChild;
    if (!kop || !kop.hasAttribute('data-kop')) return false;
    if (kop.classList.contains('is-eerste-in-kader')) return false;
    kader.removeChild(kop);
    this.extra = [kop].concat(this.extra);
    return true;
  };

  /** Twee stukken van hetzelfde blok weer aan elkaar. */
  Zetter.prototype.samenvoegen = function (kop, staart) {
    while (staart.firstChild) kop.appendChild(staart.firstChild);
    kop.classList.remove('is-gesplitst-kop');
    kop.removeAttribute('data-deel');
    if (staart.parentNode) staart.parentNode.removeChild(staart);
  };

  /**
   * Een kop blijft bij zijn tekst. Staat er een kop vlak boven dit
   * blok en krijgt dit blok minder dan twee regels, dan verhuizen ze
   * samen naar het volgende kader.
   */
  Zetter.prototype.bindKop = function (blok, kader) {
    var vorige = blok.previousElementSibling;
    if (!vorige || !vorige.hasAttribute('data-kop')) return;
    if (vorige.classList.contains('is-eerste-in-kader')) return;
    var lh = regelhoogte(blok);
    var regels = Math.round(blok.getBoundingClientRect().height / lh);
    if (regels >= (this.cfg.minRegelsNaKop || 2)) return;

    kader.removeChild(blok);
    kader.removeChild(vorige);
    this.klachten.push({
      soort: 'kop-verhuisd',
      bron: vorige.getAttribute('data-bron') || '',
      tekst: (vorige.textContent || '').slice(0, 60),
      folio: this.pagina.getAttribute('data-folio') || '',
      wat: 'Kop met te weinig tekst eronder; samen naar de volgende pagina.'
    });
    this.volgendKader();
    var nieuw = this.kader();
    nieuw.appendChild(vorige);
    vorige.classList.add('is-eerste-in-kader');
    nieuw.appendChild(blok);
  };

  /**
   * De kop-naar-folio-kaart, gelezen uit de afgemaakte pagina's.
   *
   * Dit gebeurde eerst tijdens het plaatsen, en dat was fout: een kop
   * die geplaatst is kan daarna nog verhuizen — door de kop-bij-zijn-
   * tekst-regel, door een voetnoot die de kolom inkort, door een blok
   * dat achteraf teruggenomen wordt. Dan stond er in de kaart de folio
   * van de pagina waar hij éérst op stond. Gemeten op de proef in het
   * dubbele model: twee van de zeventien verwijzingen zaten er één
   * pagina naast.
   *
   * Achteraf uit de DOM lezen kan niet misgaan: waar een kop staat, is
   * waar hij staat.
   */
  Zetter.prototype.bouwKaart = function () {
    this.kaart = [];
    var koppen = this.rapport.querySelectorAll('[data-kop]');
    for (var i = 0; i < koppen.length; i++) {
      var el = koppen[i];
      if (el.classList.contains('is-gesplitst-staart')) continue;
      var p = el.closest('.pagina');
      this.kaart.push({
        bron: el.getAttribute('data-bron') || '',
        niveau: +el.getAttribute('data-kop') || 1,
        tekst: (el.getAttribute('data-kop-tekst') || el.textContent || '').trim(),
        nummer: el.getAttribute('data-nummer') || '',
        groep: el.getAttribute('data-groep') || (p ? (p.getAttribute('data-deel') || '') : ''),
        folio: p ? (p.getAttribute('data-folio') || '') : ''
      });
    }
  };

  /**
   * De huidige pagina weggooien als er niets op staat.
   *
   * Nodig bij het promoveren van een te breed blok: de pagina was al
   * aangemaakt voordat bleek dat het blok er niet in paste, en zonder
   * dit bleef hij als blanco blad midden in het rapport staan. Gemeten
   * op de proef in het dubbele model: pagina 12 was leeg.
   */
  Zetter.prototype.gooiLegePaginaWeg = function () {
    if (!this.pagina) return false;
    if (this.isBegonnen()) return false;
    if (this.paginas[this.paginas.length - 1] !== this.pagina) return false;
    this.pagina.parentNode.removeChild(this.pagina);
    this.paginas.pop();
    this.folio--;
    this.sluitPagina();
    return true;
  };

  Zetter.prototype.sluitPagina = function () {
    this.pagina = null;
    this.kaders = [];
    this.kaderNr = 0;
  };

  /** Een lege pagina invoegen tot de volgende een rechterpagina is. */
  Zetter.prototype.naarRecto = function () {
    this.sluitPagina();
    var volgende = (this.paginas.length + (this.cfg.eersteZijde === 'verso' ? 1 : 0)) % 2
      ? 'verso' : 'recto';
    if (volgende === 'verso') {
      this.nieuwePagina({ sjabloon: 'leeg', kopregel: false, folio: false });
      this.sluitPagina();
    }
  };

  /* --- kantnoten --------------------------------------------------- */

  /**
   * Een kantnoot staat in de kantlijn op de hoogte van het blok waar
   * hij bij hoort. Dat kan pas als de pagina af is, want daarvoor
   * verschuift alles nog.
   */
  Zetter.prototype.plaatsKantnoten = function () {
    for (var i = 0; i < this.paginas.length; i++) {
      var p = this.paginas[i];
      var kantlijn = p.querySelector('.kantlijn');
      if (!kantlijn) continue;
      var basis = kantlijn.getBoundingClientRect().top;
      var onderkant = kantlijn.getBoundingClientRect().bottom;

      // De losse kantnoten uit de tekstkolom halen, en de voetnoten die
      // hier al staan op hun plek zetten. Allebei krijgen ze de hoogte
      // van hun anker: het blok ervoor, of het nootcijfer zelf.
      var los = p.querySelectorAll('.kader .kantnoot');
      for (var k = 0; k < los.length; k++) kantlijn.appendChild(los[k]);

      var items = Array.prototype.slice.call(
        kantlijn.querySelectorAll('.kantnoot, .voetnoot'));
      var metTop = [];
      for (var j = 0; j < items.length; j++) {
        var noot = items[j];
        var anker = null;
        var nid = noot.getAttribute('data-noot-id');
        if (nid) anker = p.querySelector('.kader sup[data-noot="' + nid + '"]');
        if (!anker) anker = noot.previousElementSibling;
        var top = anker ? anker.getBoundingClientRect().top - basis : 0;
        metTop.push({ el: noot, top: Math.max(0, top) });
      }
      metTop.sort(function (a, b) { return a.top - b.top; });

      var vorigeOnder = -Infinity;
      for (var m = 0; m < metTop.length; m++) {
        var top = Math.max(metTop[m].top, vorigeOnder + 9);
        metTop[m].el.style.top = top + 'px';
        kantlijn.appendChild(metTop[m].el);
        vorigeOnder = top + metTop[m].el.offsetHeight;
      }
      // Wat onder de kantlijn uit zou lopen, schuift terug omhoog.
      var overschot = vorigeOnder - (onderkant - basis);
      if (overschot > 0) {
        for (var q = 0; q < metTop.length; q++) {
          var nieuw = Math.max(0, parseFloat(metTop[q].el.style.top) - overschot);
          metTop[q].el.style.top = nieuw + 'px';
        }
      }
    }
  };

  /* ------------------------------------------------------------------
     De inhoudsopgave
     ------------------------------------------------------------------ */

  function bouwInhoud(regels, cfg) {
    var houder = document.createElement('div');
    houder.className = 'inhoud';
    houder.setAttribute('data-toevoeging', 'inhoudsopgave');
    var groep = '';
    for (var i = 0; i < regels.length; i++) {
      var r = regels[i];
      if (r.niveau > (cfg.inhoudDiepte || 2)) continue;
      // De overgang naar de bijlagen krijgt een tussenkop, want een
      // inhoudsopgave waarin bijlage A tussen hoofdstuk 5 en 6 staat,
      // leest als een fout in de nummering.
      if ((r.groep || '') !== groep) {
        groep = r.groep || '';
        if (groep === 'bijlagen') {
          var tussen = document.createElement('p');
          tussen.className = 'inhoud__groep';
          tussen.textContent = cfg.bijlagewoord || 'Bijlagen';
          houder.appendChild(tussen);
        }
      }
      var regel = document.createElement('div');
      regel.className = 'inhoud__regel';
      regel.setAttribute('data-niveau', String(r.niveau));
      // De verwijzing gaat op het blok-id en niet op de koptekst. Twee
      // secties in één rapport kunnen dezelfde naam hebben — "Bronnen",
      // "De opgave" — en dan wijst een controle op tekst naar de eerste
      // die hij tegenkomt in plaats van naar déze.
      if (r.bron) regel.setAttribute('data-verwijst', r.bron);
      var stukken = [];
      if (r.nummer) stukken.push('<span class="inhoud__nr">' + r.nummer + '</span>');
      stukken.push('<span class="inhoud__naam"></span>');
      stukken.push('<span class="inhoud__leader"></span>');
      stukken.push('<span class="inhoud__folio">' + (r.folio || '') + '</span>');
      regel.innerHTML = stukken.join('');
      regel.querySelector('.inhoud__naam').textContent = r.tekst;
      houder.appendChild(regel);
    }
    return houder;
  }

  /* ------------------------------------------------------------------
     De aanroep
     ------------------------------------------------------------------ */

  window.zet = function (cfg) {
    cfg = cfg || {};
    var rapport = document.getElementById('rapport');
    var stroom = document.getElementById('stroom');
    rapport.innerHTML = '';

    // Een verse kopie van de stroom, want de vorige ronde heeft de
    // originele knopen verplaatst en gesplitst.
    var werk = stroom.cloneNode(true);
    var wachtrij = Array.prototype.slice.call(werk.children);

    // De inhoudsopgave op zijn plek zetten, als die er is.
    if (cfg.inhoud && cfg.inhoud.length) {
      for (var i = 0; i < wachtrij.length; i++) {
        if (wachtrij[i].getAttribute('data-plek') === 'inhoudsopgave') {
          var blok = bouwInhoud(cfg.inhoud, cfg);
          blok.setAttribute('data-nieuwe-pagina', 'ja');
          wachtrij[i].parentNode.replaceChild(blok, wachtrij[i]);
          wachtrij[i] = blok;
          break;
        }
      }
    } else {
      wachtrij = wachtrij.filter(function (el) {
        return el.getAttribute('data-plek') !== 'inhoudsopgave';
      });
    }

    var z = new Zetter(cfg);
    var ronden = 0;
    while (wachtrij.length && ronden++ < MAX_RONDEN) {
      var blok = wachtrij.shift();
      if (!blok || !blok.tagName) continue;
      var rest = z.plaats(blok);
      if (rest) wachtrij.unshift(rest);
      // De koppen die achterbleven moeten vóór hun eigen tekst terug.
      while (z.extra.length) wachtrij.unshift(z.extra.pop());
    }
    if (ronden >= MAX_RONDEN) {
      z.klachten.push({ soort: 'lus', wat: 'De zetting kwam niet tot een eind.' });
    }

    z.bouwKaart();
    z.plaatsKantnoten();

    // De laatste pagina mag niet halfleeg blijven zonder dat iemand het
    // ziet; dat is geen fout maar het hoort in het verslag.
    var laatste = z.paginas[z.paginas.length - 1];
    var vulling = 1;
    if (laatste) {
      var k = laatste.querySelector('.kader');
      if (k && k.clientHeight) vulling = k.scrollHeight / k.clientHeight;
    }

    return {
      paginas: z.paginas.length,
      folios: z.folio - 1,
      inhoud: z.kaart,
      klachten: z.klachten,
      vullingLaatste: Math.round(vulling * 100) / 100
    };
  };
})();
