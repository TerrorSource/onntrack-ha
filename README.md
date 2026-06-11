# Onntrack voor Home Assistant

[![HACS Badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Integreer je Onntrack GPS tracker in Home Assistant. Toont locatie, adres, snelheid, spanning en meer — met automatisch token beheer.

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
   - IMEI nummer (te vinden op platform.onntrack.nl)

## Entiteiten

| Entiteit | Beschrijving |
|---|---|
| `device_tracker.onntrack_XXXXX_locatie` | GPS positie op de kaart |
| `sensor.onntrack_XXXXX_locatie_adres` | Volledig adres |
| `sensor.onntrack_XXXXX_status` | STATIC / MOVE |
| `sensor.onntrack_XXXXX_snelheid` | Snelheid in km/h |
| `sensor.onntrack_XXXXX_breedtegraad` | Latitude |
| `sensor.onntrack_XXXXX_lengtegraad` | Longitude |
| `sensor.onntrack_XXXXX_satellieten` | Aantal satellieten |
| `sensor.onntrack_XXXXX_spanning` | Externe spanning (V) |
| `sensor.onntrack_XXXXX_kilometer_vandaag` | Km gereden vandaag |
| `sensor.onntrack_XXXXX_laatste_online` | Tijdstip laatste contact |

## Token beheer

De integratie logt automatisch in en vernieuwt het token zodra het verloopt. Je wachtwoord wordt veilig opgeslagen in de Home Assistant `config_entries`.