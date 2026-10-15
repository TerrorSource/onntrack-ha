# Onntrack voor Home Assistant

[![HACS Badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Validate](https://github.com/TerrorSource/onntrack-ha/actions/workflows/validate.yml/badge.svg)](https://github.com/TerrorSource/onntrack-ha/actions/workflows/validate.yml)

Integreer je Onntrack GPS-tracker in Home Assistant. Live locatie op de kaart, adres, snelheid, ontsteking, kilometerstanden en meer — met automatisch tokenbeheer en instelbaar update-interval.

## Installatie via HACS

1. Open HACS in Home Assistant
2. Ga naar **Integraties** → **⋮** → **Aangepaste repositories**
3. Voeg toe: `https://github.com/TerrorSource/onntrack-ha`
   Categorie: **Integratie**
4. Zoek naar "Onntrack" en installeer
5. Herstart Home Assistant
6. Ga naar **Instellingen** → **Apparaten & Diensten** → **Integratie toevoegen**
7. Zoek op "Onntrack" en vul in:
   - E-mailadres (Onntrack account)
   - Wachtwoord
   - IMEI nummer (te vinden op [platform.onntrack.nl](https://platform.onntrack.nl))

Vereist Home Assistant 2026.3 of nieuwer.

## Opties

Na installatie kun je via **Instellingen → Apparaten & Diensten → Onntrack → Configureren** instellen:

| Optie | Standaard | Beschrijving |
|---|---|---|
| Update-interval | 60 s | Hoe vaak de Onntrack cloud wordt bevraagd (30-600 s) |
| Voertuigtype | Overig | Bepaalt het icoon op de kaart: auto, bestelbus, vrachtwagen, motor, scooter |

## Entiteiten

| Entiteit | Beschrijving |
|---|---|
| **Locatie** (device tracker) | GPS-positie op de kaart |
| **Locatie adres** | Volledig adres van de huidige positie |
| **Status** | Geparkeerd / Onderweg / Offline |
| **Snelheid** | Snelheid in km/h |
| **Ontsteking** (binary sensor) | Contact aan/uit (ACC) |
| **Kilometers vandaag** | Afstand gereden vandaag |
| **Totale kilometerstand** | Odometer |
| **Laatste online** | Tijdstip laatste contact met de tracker |
| **Laatste GPS-fix** | Tijdstip van de laatste positiebepaling |
| **Ververs nu** (button) | Direct een verse update opvragen |

Diagnostisch (standaard onder "Diagnostic" op de apparaatpagina): breedtegraad, lengtegraad, satellieten, signaalsterkte, spanning, positioneringstype.

## Automatiseringsvoorbeeld

```yaml
automation:
  - alias: "Melding bij starten voertuig"
    triggers:
      - trigger: state
        entity_id: binary_sensor.onntrack_XXXXX_ontsteking
        to: "on"
    actions:
      - action: notify.mobile_app_telefoon
        data:
          message: "Het voertuig is gestart"
```

## Problemen melden

Voeg bij een [issue](https://github.com/TerrorSource/onntrack-ha/issues) altijd het diagnostics-bestand toe: **apparaatpagina → Download diagnostics** (locatiegegevens en inloggegevens worden automatisch weggelaten). Voor diepere analyse kun je debug-logging aanzetten via **Instellingen → Apparaten & Diensten → Onntrack → Foutopsporingsregistratie inschakelen**.

## Tokenbeheer

De integratie logt automatisch in en vernieuwt het token zodra het verloopt. Wijzigt je wachtwoord, dan vraagt Home Assistant eenmalig om het nieuwe wachtwoord (herauthenticatie). Je wachtwoord wordt opgeslagen in de Home Assistant `config_entries`.

## Ontwikkeling

De API-parsing zit in `custom_components/onntrack/parser.py` (bewust zonder Home Assistant-afhankelijkheden) en is getest met pytest:

```bash
pytest tests/
```

Elke push wordt gevalideerd met hassfest, HACS-validatie en de parser-tests (GitHub Actions).
