# Adviesvorm

Wat een deck beslisklaar maakt. `vormentaal.md` is de nagemeten maatstaf voor de vorm;
dit document is de laag erboven: hoe een deck een besluit draagt in plaats van informatie.
De regels hier zijn niet nagemeten uit de vijf winnende decks — ze komen uit het vak van
het adviseren zelf, en uit de plekken waar de winnende decks nog onder de lat van een
professioneel adviesdeck bleven. Waar dat zo is, staat het erbij.

Lees dit samen met `vormentaal.md`, één keer, vóór de outline.

---

## 1. Het antwoord staat voorop

Een adviesdeck is geen betoog dat naar een conclusie toewerkt; het is een conclusie met
het bewijs erachter. De lezer die na slide 2 stopt, kent het advies en de besluitvraag.
De rest van de deck bestaat voor de lezer die wil weten waarom.

Concreet: direct na de cover staat de adviesslide. Daarop staat het advies als bewering,
de twee of drie dragende argumenten in één regel elk, en wat er vandaag besloten moet
worden. De slides daarna zijn elk één argument met zijn bewijs; de slotslide herhaalt de
besluitvraag met de vervolgstappen.

De toets is de titelrij uit `voice.md`: lees alle titels achter elkaar. In een
beslisdeck is de eerste inhoudelijke titel het advies zelf, niet de aanleiding. Begint de
titelrij met context — "DE OPGAVE", "WAAR WE STAAN" — dan is het een informatiedeck, en
dat is een keuze die je bewust maakt, geen default. Voor een kennismaking of een
tussenrapportage mag de opbouw verhalend; voor elk deck waar een besluit op tafel ligt,
staat het antwoord voorop.

**De besluitvraag is letterlijk.** "Ter besluit: gaat het bestuur akkoord met scenario B
en de voorfinanciering van € 400.000?" is een besluitvraag. "Graag uw reactie" is er
geen. Een deck dat om een besluit vraagt, zegt welk besluit, van wie, en wanneer.

## 2. Eén exhibit, één boodschap, en de boodschap staat erop

De exhibit — grafiek, tabel, schema of verdeling — is het bewijs van de titel. Daaruit
volgt alles:

**Eén exhibit per boodschap.** Een tabel en een grafiek die dezelfde reeks tonen zijn
geen grondigheid maar twijfel: de lezer vergelijkt ze en vraagt zich af wat hij mist.
Dit is een fout die in de referentiedecks nog voorkomt (`08-tabel-naast-grafiek` toont
de omzetreeks twee keer). Kies: gaat het om de trend, dan de grafiek; moet de lezer
exacte bedragen kunnen naslaan of meer dan twee grootheden vergelijken, dan de tabel.
Twee exhibits op één slide mogen alleen als ze verschillende dingen bewijzen.

**De boodschap staat op de exhibit, niet ernaast.** Een kale grafiek vraagt de lezer
zelf de conclusie te trekken; een adviesgrafiek wijst hem aan. De middelen, van licht
naar zwaar:

- **De focuskleur.** Eén staaf, één cel, één rij in de accentkleur terwijl de rest
  navy of container blijft. `add_chart.py --highlight <categorie>` doet dit voor een
  grafiek met één reeks; in een tabel of eigen compositie doe je het met de vulling.
  Dit is het goedkoopste en meestal het juiste middel.
- **De reekscodering.** Realisatie navy, prognose oranje — de vaste codering uit
  `add_chart.py --series-colors navy,oranje`. Kosten grapefruit, baten emerald, conform
  de rol-naar-hue-laag uit `vormentaal.md` §3.
- **De uitgeschreven delta.** Naast of boven de grafiek één regel in kopmaat: "× 3,4 in
  vier jaar", "− 20 dagen". Dat is een eigen tekstvak dat je naast de exhibit zet, in de
  hue van de boodschap. Een lezer onthoudt de delta, niet de as.
- **De grens in de vorm.** Vergelijkt de titel met een norm, doel of capaciteit, dan
  hoort die grens ín het exhibit en niet alleen in de subtitel. Een losse lijn over een
  native grafiek tekenen is fragiel (de as bepaalt de schaal, jij niet); maak de grens
  dan structureel — een gestapelde staaf met "binnen de grens" in navy en "daarboven"
  in de accentkleur zegt hetzelfde en kan niet verschuiven.

En omdat de boodschap erop staat, hoeft de rest weg: geen rasterlijnen, geen
grafiektitel, geen astitel — `add_chart.py` doet dat al. De eenheid en de peildatum
staan in de bronregel onder de exhibit (`vormentaal.md` §11), het aantal decimalen is
overal gelijk, en datalabels staan aan zolang er acht of minder punten zijn.

**Tabellen zijn zetting, geen vlakken.** Getallen rechts uitgelijnd op de cijfers,
tekst links, de kopregel als enige rij met een volle vulling, een totaalregel zwaarder
gezet (SemiBold of een streep erboven) in plaats van gekleurd. Om en om inkleuren van
rijen is Word; een tabel in dit systeem scheidt met witruimte en één haarlijn onder de
kop. Negatieve bedragen krijgen een minteken, geen rood — rood-groen zonder betekenislaag
is precies de decoratie die `vormentaal.md` §3 verbiedt.

**Een schema bewijst een volgorde, een verdeling bewijst een verhouding.** Kies de
exhibitvorm bij wat de titel beweert, niet bij wat er aan data ligt. Beweert de titel
dat de route korter wordt, dan is de exhibit twee routes onder elkaar met de dagen erbij.
Beweert hij dat één post de begroting draagt, dan is het een 100%-staaf of een
verdeling, geen tabel met acht rijen.

## 3. Schets twee composities voordat je er één bouwt

De eerste compositie die je invalt is vrijwel altijd de meest gangbare: drie kaarten,
vier rijen, tweeluik. Soms is die ook goed. Maar je weet het pas als er iets naast
heeft gestaan.

Daarom, per contentslide, vóór het bouwen en ná de outline: noem twee wezenlijk
verschillende composities voor dezelfde boodschap, in één regel elk, en kies met een
reden die over de boodschap gaat. Wezenlijk verschillend betekent een andere leesroute
of een ander zwaartepunt — niet dezelfde drie kaarten met een andere vulling.

    Slide 4 — "de route wordt 20 dagen korter"
    a. twee stroomschema's onder elkaar, nu en straks, dagen als heldgetal links
    b. één tijdlijn op schaal met de knip gemarkeerd, delta als focusregel rechts
    keuze: a — de boodschap is de vergelijking, en b verbergt de twee loketten

Twee regels denkwerk per slide, geen apart document en geen goedkeuringsronde. Het
resultaat mag in de bouwnotities blijven. Wat het voorkomt is de deck waarin elke slide
de eerste inval is — en de eerste inval is deckbreed dezelfde, dus dat is ook waar de
eenvormigheid uit `vormentaal.md` §10 vandaan komt.

## 4. De weigerlijst

Defaults, geen verboden: de vraag van de klant of de inhoud kan elk ervan terugverdienen.
Maar grijp je ernaar terwijl de inhoud er niet om vraagt, dan was het geen keuze en
herken je het als vulwerk. Dan is het antwoord de compositie herzien, niet het element
mooier maken.

- **Drie gelijke kaarten omdat het er drie zijn.** Het aantal en de vorm volgen uit de
  inhoud (`vormentaal.md` §12). Drie kaarten zijn goed wanneer drie dingen gelijkwaardig
  zijn; een advies met een voorkeursscenario is niet gelijkwaardig, dus daar krijgt het
  voorkeursscenario het gewicht.
- **Pijlen en chevrons als decoratie.** Een pijl betekent dat iets ergens heen gaat. Vier
  blokken met pijlen ertussen die geen volgorde dragen zijn een lijst in vermomming.
- **Een 2×2-matrix zonder twee echte assen.** Het kwadrant is het meest versleten
  adviesgereedschap dat er is. Twee assen die allebei iets meten en waarvan de kruising
  iets betekent: prima. Vier categorieën in vier hoeken zetten omdat het er vier zijn: nee.
- **Icoontegels.** Een rij tegels met een pictogram, een kop en twee regels is de
  categoriedefault van elk gegenereerd deck. Het sjabloon heeft geen icoonbibliotheek en
  dat is geen gemis: de kop in zijn hue draagt de categorie sneller dan een pictogram.
- **De genummerde band 01/02/03.** Nummers wanneer de volgorde informatie is — stappen,
  fasen, prioriteit. Niet als ornament op een opsomming die net zo goed andersom kon.
- **De samenvattingsband op elke slide.** Eén band per vier slides (`vormentaal.md` §10);
  de sluitregel op wit of de volle cel in de tabel doen hetzelfde werk stiller.
- **Stockfoto-sfeer in de contentzone.** Foto's horen op de cover, de dividers en de
  outro, waar het sjabloon ze zet. Een foto tussen de exhibits vult ruimte die een
  argument had moeten vullen.

## 5. De beslistoets op de render

De visuele loop uit de skill beoordeelt de vorm. Doe daarna, één keer, deze twee dingen
op het contactblad:

1. **De titelrij hardop.** Alle titels achter elkaar: is dat het advies zoals je het in
   een minuut aan de klant vertelt? Mist er een stap, staat er een titel die aankondigt
   in plaats van beweert, dan is dat een contentfout die geen render laat zien.
2. **De kneep per slide.** Klein bekeken moet op elke slide de drager overblijven — en
   over de deck heen moeten die dragers verschillen. Tien keer hetzelfde silhouet met
   dezelfde plek voor het grote getal is dezelfde eenvormigheid als tien keer layout 19,
   alleen een niveau hoger.

En de laatste vraag, die niets met vorm te maken heeft: kan de ontvanger met alleen deze
deck het besluit nemen, verdedigen bij zijn eigen bestuur, en over een halfjaar terugvinden
waarom het zo besloten is? Dat is waar "consultancy-klaar" op toetst. Nee op één van de
drie: er mist een slide, en dat repareer je in de outline, niet in de opmaak.
