#!/usr/bin/env python3
"""Meten wat mechanisch te meten valt, en verder niets.

Dit is geen poort en het keurt geen compositie af. Het meet dertien dingen die
je zonder oordeel kunt vaststellen en die stil misgaan — dat laatste is het
criterium. Een pagina die lelijk is, ziet iedereen op de render; een regel die
onder de snijrand is weggevallen omdat `.pagina` `overflow: hidden` draagt, ziet
niemand, ook de bouwer niet.

Drie ervan blokkeren, en dat zijn precies de drie waar geen interpretatie aan
te pas komt:

* **klip** — er staat tekst in een doos die hem afsnijdt. Er is dus tekst
  verdwenen.
* **overloop** — een element steekt over de snijrand zonder dat het als
  aflopend werk is aangemerkt. Op papier is dat weg.
* **te klein** — lopende tekst onder 8 pt, of een gespatieerd kapitaallabel
  onder 6 pt. Dat is niet krap maar onleesbaar.
* **emoji** — een tweede lettertype op de pagina dat als chatbericht leest.
* **titelbalk** — een balk van nul px hoog, doordat `--balk` niet op de
  .pagina staat. De titel staat er dan wel en de band niet.

De rest is een aanwijzing: kijk ernaar en beslis. Voor `vulgraad`, `maat` en
`palet` geldt uitdrukkelijk dat de render zwaarder weegt dan het getal.

Gebruik:

    python qa_document.py werkmap/document.html
    python qa_document.py werkmap/document.html --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _browser import browser, wacht_op_letters  # noqa: E402

#: Het palet. Alles wat een element als kleur of vulling draagt hoort hier te
#: staan, op de tinten van diezelfde kleuren na — die worden apart herkend.
#:
#: Uit `scripts/gedeeld/merk.py` en niet uit een eigen lijst. Die eigen lijst
#: heeft er gestaan, met de vijf waarden van vóór 27 augustus 2026 erin, en toen
#: was deze meting het tegendeel van wat ze moet zijn: het merkoranje van het
#: Word-sjabloon week 15 op het blauwkanaal af van het oranje dat hier stond, en
#: dat is meer dan de marge van `_dichtbij`. De poort meldde dus "kleur buiten
#: het palet" over de merkkleur zelf, op elk document. Een toets die zijn eigen
#: kopie van de waarheid bijhoudt, toetst op een gegeven moment die kopie.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gedeeld"))
from merk import KLEUREN, rgb  # noqa: E402

PALET = {naam: rgb(naam) for naam in KLEUREN}

#: Ondergrens voor lopende tekst. 8 pt bij 96 dpi is 10,67 px. Het SFNL-rapport
#: zet zijn brood op 10 pt (13,33 px); 8 pt is de bijschriftmaat en daaronder
#: staat niets.
MIN_PX = 10.4

EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF←-⇿⬀-⯿]")

METING = r"""() => {
  const uit = {paginas: [], maten: {}, families: {}, kleuren: {}, meldingen: []};
  const bleed = el => el.closest('.aflopend, .aflopend-boven, .aflopend-onder, ' +
                                '.aflopend-links, .aflopend-rechts, .bol, .watermerk, .rondfoto');
  // Alles buiten .zetspiegel is per definitie meubilair of aflopend werk: de
  // folio, de kopregel, een logo dat je zelf onderaan hebt gezet. Dat telt niet
  // mee in hoe vol de pagina staat. Deze regel verving een groeiende lijst met
  // klassenamen, en hij verving hem omdat die lijst nooit compleet werd — een
  // logo dat de bouwer zelf op `position: absolute; bottom: 46px` had gezet,
  // duwde de vulgraad naar 1,15 op een pagina die voor een derde leeg was.
  const meubel = el => !el.closest('.zetspiegel');
  const tekstVan = el => Array.from(el.childNodes)
      .filter(n => n.nodeType === 3).map(n => n.textContent).join('').trim();

  document.querySelectorAll('.pagina').forEach((pag, idx) => {
    const pr = pag.getBoundingClientRect();
    const zs = pag.querySelector('.zetspiegel');
    const st = getComputedStyle(zs || pag);
    const marge = {
      boven: parseFloat(st.paddingTop), onder: parseFloat(st.paddingBottom),
      links: parseFloat(st.paddingLeft), rechts: parseFloat(st.paddingRight)};
    if (!zs) uit.meldingen.push({soort: 'geen-zetspiegel', pagina: idx + 1});
    const p = {nr: idx + 1, w: Math.round(pr.width), h: Math.round(pr.height),
               formaat: pag.dataset.formaat || 'sfnl', overloop: [], klip: [],
               regels: [], onderrand: 0, woorden: 0, schaduw: 0, velden: []};

    // Aflopende kleurvelden tellen. Een veld is een vlak dat over de volle
    // breedte van het blad loopt, aan minstens één rand raakt, en een andere
    // kleur heeft dan het papier. De pagina zelf telt mee zodra hij niet wit
    // is. Zie `kleurveld-stapeling` in de beoordeling voor waarom dit een
    // blokkade is en geen aanwijzing.
    {
      const pagKleur = getComputedStyle(pag).backgroundColor;
      const wit = ['rgb(255, 255, 255)', 'rgba(0, 0, 0, 0)', 'transparent'];
      const pagIsWit = wit.indexOf(pagKleur) !== -1;
      if (!pagIsWit) p.velden.push({el: 'pagina', kleur: pagKleur, hoogte: p.h});
      pag.querySelectorAll('*').forEach(el => {
        const cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden') return;
        const bg = cs.backgroundColor;
        const heeftVerloop = cs.backgroundImage && cs.backgroundImage !== 'none';
        if (wit.indexOf(bg) !== -1 && !heeftVerloop) return;
        if (bg === pagKleur && !heeftVerloop) return;
        const r = el.getBoundingClientRect();
        if (r.width < pr.width - 1.5) return;              // niet over de volle breedte
        const raakt = (r.top <= pr.top + 1.5) || (r.bottom >= pr.bottom - 1.5);
        if (!raakt) return;                                 // zweeft, dus geen veld
        p.velden.push({el: el.className || el.tagName.toLowerCase(),
                       kleur: heeftVerloop ? 'verloop' : bg,
                       hoogte: Math.round(r.height),
                       deel: Math.round(r.height / pr.height * 100)});
      });
    }

    pag.querySelectorAll('*').forEach(el => {
      const r = el.getBoundingClientRect();
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return;
      if (r.width === 0 && r.height === 0) return;
      const naam = el.tagName.toLowerCase() +
        (el.className && typeof el.className === 'string' && el.className.trim()
          ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '');

      // 1. Klipping: er wordt tekst afgesneden.
      //
      // Meet de gezette tekstregels zelf, met een Range, en niet de dozen
      // eromheen. Twee redenen, allebei nagemeten:
      //
      // * `scrollHeight` van een container telt álles mee wat eruit steekt,
      //   ook een tonale bol die er juist hoort uit te steken. Een titelbalk
      //   met een `.bol` op `right: -120px` meldde 120 px klipping terwijl er
      //   geen letter verdween.
      // * Andersom valt tekst die uit zijn éígen vak loopt buiten elke
      //   doosmeting: een `<p>` met `white-space: nowrap` in een smalle
      //   container houdt de breedte van die container, dus geen enkel
      //   element steekt ergens uit — en toch is de helft van de kop weg.
      //
      // De regels van de tekst zijn het enige dat allebei ziet.
      if (cs.overflow !== 'visible' && el.clientHeight > 0 && el.clientWidth > 0) {
        const doos = el.getBoundingClientRect();
        const rand = {links: doos.left + parseFloat(cs.borderLeftWidth || 0),
                      rechts: doos.right - parseFloat(cs.borderRightWidth || 0),
                      boven: doos.top + parseFloat(cs.borderTopWidth || 0),
                      onder: doos.bottom - parseFloat(cs.borderBottomWidth || 0)};
        const loop = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
        let ergste = 0, welke = '', richting = 'hoogte';
        let knoop;
        while ((knoop = loop.nextNode())) {
          if (!knoop.textContent.trim()) continue;
          const ouder = knoop.parentElement;
          // Binnen een <svg> geldt een eigen coördinatenstelsel en snijdt de
          // viewBox met opzet; een <text> op de onderste regel meet daar de
          // descent van het font als overhang. Het logo meldde dat.
          if (!ouder || ouder.closest('svg') || bleed(ouder)) continue;
          const bereik = document.createRange();
          bereik.selectNodeContents(knoop);
          for (const r of bereik.getClientRects()) {
            const verticaal = Math.max(r.bottom - rand.onder, rand.boven - r.top);
            const horizontaal = Math.max(r.right - rand.rechts, rand.links - r.left);
            const over = Math.max(verticaal, horizontaal);
            if (over > ergste) {
              ergste = over;
              richting = verticaal >= horizontaal ? 'hoogte' : 'breedte';
              welke = knoop.textContent.trim().slice(0, 60);
            }
          }
        }
        if (ergste > 1.5) {
          p.klip.push({el: naam, tekort: Math.round(ergste),
                       richting, tekst: welke});
        }
      }

      // 2. Overloop: buiten de snijrand, en niet als aflopend werk bedoeld.
      if (!bleed(el)) {
        const uitsteek = Math.max(pr.left - r.left, r.right - pr.right,
                                  pr.top - r.top, r.bottom - pr.bottom);
        if (uitsteek > 1.5) {
          p.overloop.push({el: naam, px: Math.round(uitsteek),
                           tekst: (el.innerText || '').trim().slice(0, 60)});
        }
      }

      // 3. Hoe ver komt de inhoud naar beneden — dood wit onderin.
      // Alleen dragende elementen tellen: iets met eigen tekst, of een blad
      // (beeld, lijn, svg). Een omhullende doos telt niet mee, want .zetspiegel
      // staat op height:100% en zou de meting altijd op vol zetten. Dat was de
      // eerste versie van deze meting en hij gaf 1.04 op een pagina met een
      // derde van het blad leeg.
      const blad = el.children.length === 0;
      const draagt = blad || tekstVan(el).length > 1;
      if (draagt && !bleed(el) && !meubel(el)
          && r.bottom > p.onderrand && r.bottom <= pr.bottom + 1) {
        p.onderrand = r.bottom - pr.top;
      }

      // 4. Maten, families, kleuren.
      const eigen = tekstVan(el);
      if (eigen.length > 1) {
        const px = Math.round(parseFloat(cs.fontSize) * 100) / 100;
        uit.maten[px] = (uit.maten[px] || 0) + eigen.length;
        const fam = (cs.fontFamily.split(',')[0] || '').replace(/['"]/g, '').trim();
        uit.families[fam] = (uit.families[fam] || 0) + eigen.length;
        uit.kleuren[cs.color] = (uit.kleuren[cs.color] || 0) + eigen.length;
        p.woorden += eigen.split(/\s+/).filter(Boolean).length;
        // Twee vloeren, want een gespatieerd kapitaallabel leest anders dan
        // een regel brood. Het SFNL-drukwerk zet zijn kleinste labels op
        // 6,8 pt (gemeten in de casespread) en dat is leesbaar omdat het
        // kapitalen zijn met ruime spatiëring en hooguit drie woorden.
        // Lopende tekst onder 8 pt is dat niet.
        const kapitaal = cs.textTransform === 'uppercase'
                      && parseFloat(cs.letterSpacing) / px >= 0.055;
        const vloer = kapitaal ? 8.0 : 10.4;
        if (px < vloer) {
          uit.meldingen.push({soort: 'te-klein', pagina: idx + 1, el: naam,
                              px, vloer, kapitaal, tekst: eigen.slice(0, 50)});
        }
        // Regellengte: alleen voor echt lopende tekst.
        if (el.closest('.tekst, .chapeau') && eigen.length > 90) {
          const per = px * 0.485;                     // gemeten voor Lato Light
          p.regels.push({el: naam, tekens: Math.round(r.width / per),
                         breedte: Math.round(r.width)});
        }
      }
      const bg = cs.backgroundColor;
      if (bg && bg !== 'rgba(0, 0, 0, 0)' && r.width * r.height > 900) {
        uit.kleuren[bg] = (uit.kleuren[bg] || 0) + 1;
      }
      if (cs.boxShadow && cs.boxShadow !== 'none'
          && cs.boxShadow.split(/,(?![^(]*\))/).some(d => !d.includes('inset'))) {
        p.schaduw += 1;
      }
    });

    // 6. Twee dingen die je op de render wél ziet maar makkelijk vergeet.
    p.leegBeeld = Array.from(pag.querySelectorAll('.beeldkader--leeg'))
      .map(el => el.dataset.wat || '(zonder data-wat)');
    p.balk = pag.querySelector('.titelbalk')
      ? {gezet: getComputedStyle(pag).getPropertyValue('--balk').trim(),
         hoogte: Math.round(pag.querySelector('.titelbalk').getBoundingClientRect().height)}
      : null;

    p.vulgraad = Math.round(
      ((p.onderrand - marge.boven) / (pr.height - marge.boven - marge.onder)) * 100) / 100;

    // 5. Het grootste gat ín de pagina.
    //
    // De vulgraad ziet alleen of de inhoud tot onderaan komt, en dat is niet
    // genoeg: een pagina met een blok bovenaan, een blok onderaan en niets
    // ertussen meet 0,99 en heeft een gat van een derde blad. Gemeten op de
    // eerste proefdocument — pagina 3 haalde vulgraad 0,93 met een wit vlak van
    // 250 px in het midden, en dat was het duidelijkst zichtbare defect van de
    // hele document. Dus: leg de zetspiegel als een bezetting van 4 px per stap
    // en zoek de langste lege reeks.
    const top = pr.top + marge.boven, bod = pr.bottom - marge.onder;
    const stap = 4, n = Math.max(1, Math.ceil((bod - top) / stap));
    const bezet = new Array(n).fill(false);
    pag.querySelectorAll('*').forEach(el => {
      if (bleed(el) || meubel(el)) return;
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return;
      const draagt = el.children.length === 0 || tekstVan(el).length > 1;
      if (!draagt) return;
      const r = el.getBoundingClientRect();
      if (r.height === 0 || r.width === 0) return;
      const a = Math.max(0, Math.floor((r.top - top) / stap));
      const b = Math.min(n - 1, Math.ceil((r.bottom - top) / stap));
      for (let i = a; i <= b; i++) bezet[i] = true;
    });
    let langste = 0, loop = 0, eindeVan = 0;
    for (let i = 0; i < n; i++) {
      if (bezet[i]) { loop = 0; continue; }
      loop++;
      if (loop > langste) { langste = loop; eindeVan = i; }
    }
    // Een gat dat tot de onderrand doorloopt is dood wit onderin en dat meldt
    // de vulgraad al; hier gaat het om het gat tússen twee blokken.
    p.gat = (eindeVan >= n - 1) ? 0 : Math.round(langste * stap);
    p.gat_op = Math.round((eindeVan - langste + 1) * stap + marge.boven);
    uit.paginas.push(p);
  });

  uit.tekst = document.body.innerText;
  return uit;
}"""


def _rgb(s: str) -> tuple[int, int, int] | None:
    m = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", s)
    return (int(m[1]), int(m[2]), int(m[3])) if m else None


def _dichtbij(c: tuple[int, int, int], marge: int = 10) -> str | None:
    for naam, p in PALET.items():
        if all(abs(a - b) <= marge for a, b in zip(c, p)):
            return naam
    return None


def _lum(c: tuple[int, int, int]) -> float:
    def kanaal(v: float) -> float:
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (kanaal(x) for x in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


def toets(html: Path) -> dict:
    with browser() as b:
        page = b.new_page(viewport={"width": 1700, "height": 1200})
        page.goto(html.resolve().as_uri())
        wacht_op_letters(page)
        m = page.evaluate(METING)

    bev: list[dict] = []

    for p in m["paginas"]:
        for k in p["klip"]:
            bev.append({"ernst": "critical", "soort": "klip", "pagina": p["nr"],
                        "wat": f"{k['el']} snijdt tekst af: {k['tekort']} px te veel in de "
                               f"{k.get('richting', 'hoogte')}",
                        "tekst": k.get("tekst", "")})
        for o in p["overloop"]:
            bev.append({"ernst": "critical", "soort": "overloop", "pagina": p["nr"],
                        "wat": f"{o['el']} steekt {o['px']} px over de snijrand "
                               f"zonder .aflopend",
                        "tekst": o.get("tekst", "")})
        # 170 px is ongeveer tien regels: een gat dat je op de render meteen
        # ziet. Lager afstellen levert een melding op elke omslag op. En een
        # pagina met minder dan zeventig woorden is een display-pagina — daar
        # ís de leegte de compositie, en dan zegt deze meting niets.
        if p["gat"] >= 170 and p["woorden"] >= 70:
            bev.append({"ernst": "warn", "soort": "gat", "pagina": p["nr"],
                        "wat": f"een leeg vlak van {p['gat']} px over de volle breedte, "
                               f"vanaf {p['gat_op']} px onder de bovenmarge. Dat is geen "
                               f"witruimte maar een gat: verdeel de ruimte tussen de "
                               f"blokken in plaats van hem op één plek te laten vallen, "
                               f"of geef de pagina meer inhoud"})
        if p["vulgraad"] < 0.72:
            bev.append({"ernst": "warn", "soort": "dood-wit", "pagina": p["nr"],
                        "wat": f"de inhoud houdt op {int(p['vulgraad'] * 100)} procent van "
                               f"de zetspiegel op — maak de elementen groter of "
                               f"de pagina korter, niet het gat"})
        for r in p["regels"]:
            if r["tekens"] < 30:
                bev.append({"ernst": "warn", "soort": "maat", "pagina": p["nr"],
                            "wat": f"{r['el']} zet ongeveer {r['tekens']} tekens per regel "
                                   f"({r['breedte']} px) — onder 30 valt een uitgevulde "
                                   f"regel uit elkaar"})
            elif r["tekens"] > 88:
                bev.append({"ernst": "warn", "soort": "maat", "pagina": p["nr"],
                            "wat": f"{r['el']} zet ongeveer {r['tekens']} tekens per regel "
                                   f"— boven 88 raakt het oog de volgende regel kwijt"})
        for wat in p["leegBeeld"]:
            bev.append({"ernst": "warn", "soort": "leeg-beeldkader", "pagina": p["nr"],
                        "wat": f"er staat nog een leeg beeldkader: {wat!r}. Zet het beeld "
                               f"erin, of haal het kader weg en herverdeel de ruimte — "
                               f"een gemarkeerd vlak dat blijft staan, gaat mee de PDF in"})
        if p["balk"] and p["balk"]["gezet"] in ("", "0px", "0"):
            bev.append({"ernst": "critical", "soort": "titelbalk", "pagina": p["nr"],
                        "wat": f"er staat een .titelbalk maar --balk is niet gezet, dus de "
                               f"band zakt terug op zijn padding ({p['balk']['hoogte']} px) "
                               f"en de titel erin wordt afgesneden. Zet --balk op de "
                               f".pagina en niet op de balk zelf — de zetspiegel leest "
                               f"dezelfde waarde"})

        if len(p.get("velden", [])) > 1:
            bev.append({"ernst": "critical", "soort": "kleurveld-stapeling",
                        "pagina": p["nr"], "velden": p["velden"],
                        "wat": "twee of meer aflopende kleurvelden op één pagina. "
                               "Een heel blad in een kleur is al de zwaarste "
                               "vorm die dit drukwerk kent; er een tweede band "
                               "overheen leggen maakt er drie oppervlakken van — "
                               "veld, band en de tekst die op geen van beide "
                               "meer thuishoort. Kleur één ding: het blad, of "
                               "een kader. Zie documenten-vormentaal.md §12"})
        if p["schaduw"]:
            bev.append({"ernst": "warn", "soort": "schaduw", "pagina": p["nr"],
                        "wat": f"{p['schaduw']} element(en) met een slagschaduw. Op papier "
                               f"bestaat die niet; gebruik een haarlijn in de eigen kleur"})

    for mel in m["meldingen"]:
        if mel["soort"] == "te-klein":
            grens = f"{mel['vloer'] / 96 * 72:.0f} pt"
            soort = "een kapitaallabel" if mel.get("kapitaal") else "lopende tekst"
            bev.append({"ernst": "critical", "soort": "te-klein", "pagina": mel["pagina"],
                        "wat": f"{mel['el']} staat op {mel['px']} px "
                               f"({mel['px'] / 96 * 72:.1f} pt) — de vloer voor {soort} "
                               f"is {grens}",
                        "tekst": mel["tekst"]})
        elif mel["soort"] == "geen-zetspiegel":
            bev.append({"ernst": "warn", "soort": "zetspiegel", "pagina": mel["pagina"],
                        "wat": "deze pagina heeft geen .zetspiegel, dus geen marge en geen "
                               "gemeten vulgraad. Alleen goed als de pagina echt niets "
                               "anders draagt dan aflopend werk"})

    families = {k: v for k, v in m["families"].items() if v > 40}
    if len(families) > 2:
        bev.append({"ernst": "critical", "soort": "letterfamilies",
                    "wat": f"{len(families)} letterfamilies dragen tekst: "
                           f"{', '.join(sorted(families))}. Er zijn er twee: "
                           f"Montserrat voor de kop, Lato voor het brood"})

    maten = sorted(float(k) for k, v in m["maten"].items() if v > 30)
    if len(maten) > 6:
        bev.append({"ernst": "warn", "soort": "maten",
                    "wat": f"{len(maten)} maten dragen tekst ({', '.join(f'{x:g}' for x in maten)}). "
                           f"De ladder heeft er vier plus twee; een vijfde maat is "
                           f"meestal een compositieprobleem"})

    vreemd = []
    for k, v in m["kleuren"].items():
        c = _rgb(k)
        if not c or v < 25:
            continue
        if _dichtbij(c) is None and c != (0, 0, 0):
            vreemd.append(k)
    if vreemd:
        bev.append({"ernst": "warn", "soort": "palet",
                    "wat": f"kleur buiten het palet: {', '.join(sorted(set(vreemd))[:6])}. "
                           f"Een tint is alpha op een merkkleur, geen nieuwe kleur"})

    if EMOJI.search(m["tekst"]):
        gevonden = sorted(set(EMOJI.findall(m["tekst"])))[:8]
        bev.append({"ernst": "critical", "soort": "emoji",
                    "wat": f"emoji in de tekst: {' '.join(gevonden)}. Teken het icoon "
                           f"zelf in SVG of laat het weg"})

    return {
        "bestand": str(html),
        "paginas": [{"nr": p["nr"], "formaat": p["formaat"],
                     "maat": [p["w"], p["h"]], "woorden": p["woorden"],
                     "vulgraad": p["vulgraad"], "gat": p["gat"]}
                    for p in m["paginas"]],
        "bevindingen": bev,
        "critical": sum(1 for b in bev if b["ernst"] == "critical"),
        "warn": sum(1 for b in bev if b["ernst"] == "warn"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=Path)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not a.html.exists():
        sys.exit(f"niet gevonden: {a.html}")

    r = toets(a.html)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 1 if r["critical"] else 0

    print(f"{r['bestand']} — {len(r['paginas'])} pagina's")
    for p in r["paginas"]:
        print(f"  {p['nr']:>2}. {p['formaat']:<12} {p['woorden']:>4} woorden   "
              f"vulgraad {p['vulgraad']:.2f}   grootste gat {p['gat']:>3} px")
    if not r["bevindingen"]:
        print("\ngeen bevindingen. De render blijft de vormbeoordeling.")
        return 0
    print()
    for ernst in ("critical", "warn"):
        for b in r["bevindingen"]:
            if b["ernst"] != ernst:
                continue
            pag = f"p{b['pagina']} " if b.get("pagina") else ""
            print(f"  [{ernst:<8}] {pag}{b['soort']}: {b['wat']}")
            if b.get("tekst"):
                print(f"             … {b['tekst']!r}")
    print(f"\n{r['critical']} critical, {r['warn']} warn")
    return 1 if r["critical"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
