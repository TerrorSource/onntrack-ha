# Release notes

## v1.0.8

### Nieuw
- **Eigen integratie-icoon**: het Onntrack-logo wordt nu meegeleverd in de `brand/`-map en verschijnt automatisch in HACS en op de apparaatpagina (geen grijze placeholder meer). Vereist Home Assistant 2026.3+.
- **Toestand-afhankelijke iconen** via `icons.json`: de ontsteking wisselt tussen motor-aan/motor-uit, en de status toont een parkeer-, rijdend- of offline-icoon.

### Verbeterd
- Config flow gemoderniseerd naar de actuele Home Assistant API's (`ConfigFlowResult`, ingebouwde reauth-helpers, nieuwe options flow-stijl).
- Tijdelijke debug-code voor het kaart-onderzoek verwijderd (geen extra API-call meer bij debug-logging; de ruwe monitordata wordt nog wel gelogd).
- API-client heeft nu eigen unittests (login, tokenverversing, foutafhandeling) die meedraaien in CI.

### Let op
- **Minimale Home Assistant-versie is nu 2026.3** (nodig voor het meegeleverde icoon).
- Nieuwe bestanden: `brand/icon.png`, `brand/icon@2x.png` en `icons.json` — upload de volledige map en herstart Home Assistant.

---

## v1.0.7

### Verbeteringen
- **"Ververs nu"-knop**: nieuwe button-entiteit op de apparaatpagina om direct een verse update op te vragen, zonder op het interval te wachten.
- **Apparaatinfo verrijkt**: het IMEI staat nu als serienummer op de apparaatpagina en er is een "Bezoek"-link naar platform.onntrack.nl.
- **README volledig herschreven**: opties, alle entiteiten, automatiseringsvoorbeeld en instructies voor het melden van problemen.

### Fixes
- **Geen valse posities meer bij verlies van GPS-fix**: de `0,0`-coördinaat (de "geen fix"-marker van veel trackers) wordt genegeerd; de laatst bekende echte positie blijft staan.
- **Robuustere foutafhandeling van de Onntrack API**: HTML-storingspagina's en HTTP-fouten leiden nu tot een nette "kan niet bijwerken"-melding in plaats van een foutmelding met traceback in het log.

### Installatie-opmerking
`button.py` is een nieuw bestand — installeer/upload de volledige map `custom_components/onntrack/` en herstart Home Assistant volledig.

---

## v1.0.6

### Nieuw
- **Ontsteking-sensor** (binary sensor) op basis van het ACC-signaal — bruikbaar voor "voertuig gestart"-automatiseringen.
- **Optiescherm** (Configureren): update-interval (30-600 s) en voertuigtype (bepaalt het kaarticoon).
- **"Laatste GPS-fix"-sensor**: tijdstip van de laatste positiebepaling, naast "Laatste online".
- **Diagnostics**: download een geredigeerd rapport via de apparaatpagina om bij issues te voegen.
- **Vertalingen**: alle entiteitsnamen in het Engels én Nederlands; status toont "Geparkeerd"/"Onderweg".

### Fixes
- Herauthenticatie werkt nu echt: bij een gewijzigd wachtwoord vraagt HA alleen het nieuwe wachtwoord (voorheen liep dit dood op "al geconfigureerd").
- Correcte ontlaadvolgorde van de integratie (voorheen konden entiteiten stilletjes bevriezen).
- Ontbrekende API-velden laten sensoren niet meer op "Onbekend" springen; de laatst bekende waarde blijft staan.
- Eenheden worden uit API-waarden gestript ("113.65km" → 113,65) zodat kilometerstanden echte getallen zijn met grafieken en statistieken.
- Zinloze langetermijnstatistieken van breedtegraad/lengtegraad verwijderd (HA vraagt eenmalig of je de oude statistieken wilt wissen — dat is bedoeld).
- Statuswaarden zijn lowercase geworden (`static`/`move`/`offline`) — let op in automatiseringen die op `STATIC`/`MOVE` filterden.

### Intern
- Volledige refactor: aparte API-client, pure geteste parser (pytest), modern `runtime_data`-patroon, gedeelde HTTP-sessie.
- GitHub Actions CI: hassfest, HACS-validatie en parser-tests bij elke push.

---

## v1.0.4 / v1.0.5 (niet als release gepubliceerd)

- Fix: "Laatste online"-sensor crashte met `Invalid datetime` (timestamp werd als tekst geleverd).
- Fix: inloggen faalde met code 20001 — wachtwoord wordt nu als MD5-hash verstuurd zoals de API verwacht.
- Debug-logging toegevoegd voor het onderzoek naar de kaart-update (issue #1).

---

## v1.0.3 en eerder

- v1.0.3: stabiliteitsverbeteringen.
- v1.0.2: fix ontbrekende `async_shutdown` methode.
- v1.0.1: fix authenticatie en sessiebeheer.
- v1.0.0: eerste versie.
