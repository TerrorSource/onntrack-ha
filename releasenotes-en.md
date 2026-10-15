# Release notes

## v1.0.8

### New
- **Bundled integration icon**: the Onntrack logo now ships in the `brand/` folder and automatically appears in HACS and on the device page (no more grey placeholder). Requires Home Assistant 2026.3+.
- **State-based icons** via `icons.json`: the ignition switches between engine-on/engine-off, and the status shows a parked, driving or offline icon.

### Improved
- Config flow modernized to current Home Assistant APIs (`ConfigFlowResult`, built-in reauth helpers, new options flow style).
- Removed temporary debug code from the map investigation (no extra API call during debug logging; raw monitor data is still logged).
- The API client now has its own unit tests (login, token refresh, error handling) running in CI.

### Note
- **Minimum Home Assistant version is now 2026.3** (required for the bundled icon).
- New files: `brand/icon.png`, `brand/icon@2x.png` and `icons.json` — upload the complete folder and fully restart Home Assistant.

---

## v1.0.7

### Improvements
- **"Refresh now" button**: new button entity on the device page to request a fresh update immediately, without waiting for the polling interval.
- **Richer device info**: the IMEI is now shown as the serial number on the device page, and a "Visit" link points to platform.onntrack.nl.
- **README fully rewritten**: options, all entities, an automation example and instructions for reporting issues.

### Fixes
- **No more false positions when the GPS fix is lost**: the `0,0` coordinate (the "no fix" marker used by many trackers) is ignored; the last known real position is kept.
- **More robust Onntrack API error handling**: HTML maintenance pages and HTTP errors now result in a clean "update failed" message instead of a traceback in the log.

### Installation note
`button.py` is a new file — install/upload the complete `custom_components/onntrack/` folder and fully restart Home Assistant.

---

## v1.0.6

### New
- **Ignition sensor** (binary sensor) based on the ACC signal — useful for "vehicle started" automations.
- **Options screen** (Configure): update interval (30-600 s) and vehicle type (sets the map icon).
- **"Last GPS fix" sensor**: timestamp of the most recent position fix, next to "Last online".
- **Diagnostics**: download a redacted report from the device page to attach to issues.
- **Translations**: all entity names in English and Dutch; status shows "Parked"/"Moving".

### Fixes
- Re-authentication now actually works: after a password change HA only asks for the new password (previously this dead-ended on "already configured").
- Correct unload order of the integration (previously entities could silently freeze).
- Missing API fields no longer flip sensors to "Unknown"; the last known value is kept.
- Units are stripped from API values ("113.65km" → 113.65) so mileage values are real numbers with graphs and statistics.
- Removed meaningless long-term statistics for latitude/longitude (HA asks once whether to delete the old statistics — that is intended).
- Status values are now lowercase (`static`/`move`/`offline`) — note this in automations that filtered on `STATIC`/`MOVE`.

### Internal
- Full refactor: separate API client, pure unit-tested parser (pytest), modern `runtime_data` pattern, shared HTTP session.
- GitHub Actions CI: hassfest, HACS validation and parser tests on every push.

---

## v1.0.4 / v1.0.5 (not published as a release)

- Fix: "Last online" sensor crashed with `Invalid datetime` (timestamp was delivered as text).
- Fix: login failed with code 20001 — the password is now sent as an MD5 hash as the API expects.
- Added debug logging for the map update investigation (issue #1).

---

## v1.0.3 and earlier

- v1.0.3: stability improvements.
- v1.0.2: fix missing `async_shutdown` method.
- v1.0.1: fix authentication and session management.
- v1.0.0: initial release.
