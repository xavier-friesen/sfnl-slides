#!/usr/bin/env python3
"""Wat er in een gezet rapport stil misgaat, gemeten in de browser.

Dit is geen poort en het keurt geen vorm af. Het meet dertien dingen die
je op een contactblad van dertig spreads niet ziet en die op papier wél
opvallen. Vier ervan blokkeren, en dat zijn precies de vier waar geen
interpretatie aan te pas komt.

**Blokkeert:**

* `klip` — een kader snijdt zijn eigen inhoud af. Er is tekst verdwenen
  die niemand ziet. Dit is de ernstigste meting die er is.
* `overloop` — een element steekt over de snijrand.
* `te-klein` — lopende tekst onder 8 pt of een kapitaallabel onder 6 pt.
* `leeg-kader` — een kolom die blanco blijft terwijl de kolom ernaast
  wél gevuld is. Een leeg láátste kader is een hoofdstukeinde en hoort
  zo; een leeg kader met een gevuld kader erachter betekent dat de
  stroom in de verkeerde orde is gevuld.

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
* `beeld-dpi` — de effectieve resolutie van elk beeld op papier.
* `contrast` — tekst op een kleurveld onder de leesbaarheidsdrempel.
* `maten` — het aantal verschillende lettergroottes. Boven de acht is er
  een compositieprobleem en geen maatprobleem.
* `lege-kantlijn` — hoeveel pagina's in het kantlijnmodel een lege
  kantlijn hebben. Boven de driekwart verdient dat model zijn ruimte
  niet en is `breed` de betere keuze.
* `tekstwand` — hoeveel spreads achter elkaar niets anders dragen dan
  lopende tekst. Vanaf vier is dat een leesbaarheidsprobleem, en het is
  het enige getal hier dat over de inhoud van de vorm gaat.

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

METING = r"""() => {
  const uit = {paginas: [], klip: [], overloop: [], teKlein: [], leegKader: [],
               wees: [], losseKop: [], beeld: [], contrast: [], maten: {},
               inhoud: [], legeKantlijn: 0, kantlijnPaginas: 0, tekstwand: 0,
               accentmerken: []};

  const paginas = Array.from(document.querySelectorAll('.pagina'));
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
      if (k.scrollHeight > k.clientHeight + 1) {
        uit.klip.push({pagina: nr, kader: j + 1,
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

    uit.paginas.push({
      nr: nr,
      folio: p.getAttribute('data-folio') || '',
      zijde: p.getAttribute('data-zijde') || '',
      model: p.getAttribute('data-model') || '',
      opener: p.getAttribute('data-opener') || '',
      vulgraad: Math.round(vulgraad * 100) / 100,
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
      const apparaat = el.closest(
        '.voetnoot, .kantnoot, .rapport-kopregel, .exhibit__bron, ' +
        '.exhibit__noot, .beeldblok figcaption');
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
      const tekst = (el.textContent || '').trim();
      const merk = tekst.length <= 3 || kapitaal
                   || el.classList.contains('opener__watermerk');
      const rij = {verhouding: Math.round(v * 100) / 100, drempel: drempel,
                   px: px, kleur: s.color, tekst: tekst.slice(0, 40)};
      if (merk) uit.accentmerken.push(rij); else uit.contrast.push(rij);
    });

  // Beeldresolutie op papier.
  document.querySelectorAll('.pagina img').forEach(img => {
    const b = img.getBoundingClientRect().width;
    if (!b || !img.naturalWidth) return;
    uit.beeld.push({breedte_px: Math.round(b), bron_px: img.naturalWidth,
                    dpi: Math.round(img.naturalWidth / (b / 96))});
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


def meet(html: Path) -> dict:
    with browser() as b:
        page = b.new_page(viewport={"width": 1000, "height": 1200})
        page.goto(html.resolve().as_uri())
        wacht_op_letters(page)
        return page.evaluate(METING)


def beoordeel(m: dict) -> dict:
    kritiek, aanwijzing, klein = [], [], []

    if m["klip"]:
        kritiek.append({"soort": "klip", "aantal": len(m["klip"]),
                        "waar": m["klip"][:6],
                        "wat": "een kader snijdt zijn inhoud af; er is tekst weg"})
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
            if p["vulgraad"] < 0.7 and not p["opener"] and p["nr"] != len(m["paginas"])]
    if slap:
        aanwijzing.append({"soort": "vulgraad", "aantal": len(slap),
                           "waar": [{"pagina": p["nr"], "vulgraad": p["vulgraad"]}
                                    for p in slap[:8]],
                           "wat": "deze pagina's staan minder dan 70 procent vol"})

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
    verslag = {
        "bestand": str(a.html),
        "paginas": len(m["paginas"]),
        "gemiddelde vulgraad": round(
            sum(p["vulgraad"] for p in m["paginas"]) / max(1, len(m["paginas"])), 2),
        "lettergroottes": sorted(float(k) for k in m["maten"]),
        "beelden": len(m["beeld"]),
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
