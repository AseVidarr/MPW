# Web-Anwendung Stufe 2 – Bands bearbeiten im Browser

## Neu im Reiter „Bands“ (Browser)

- **Bandprofil**: Hauptgenre, Zweitgenre (Auswahlliste aus dem Genre-Katalog,
  neue Genres werden aufgenommen) und Persona bearbeiten und speichern.
  Der Bandname bleibt in der Desktop-App änderbar, weil der Band-Ordner daran hängt.
- **Instrumente / Hardware**: Einträge hinzufügen, bearbeiten und löschen
  (Löschen mit Rückfrage). „Gruppe“ und „Instrument / Hardware“ schlagen –
  wie in der Desktop-App – die bereits gespeicherten Werte vor.
- **Hardware-Presets**:
  - Preset zur Band *hinzufügen* (vorhandene Einträge bleiben, Doppelte werden übersprungen),
  - Preset auf Band *anwenden (ersetzen)* – nur nach Bestätigung,
  - Band-Hardware *als Preset speichern* (bei gleichem Namen Rückfrage zum Überschreiben).
- Alle Texte in DE / EN / FR / ES / IT.

## Technik

- Gemeinsame Logik in `source/mpw_core.py` (`update_band_profile`, `band_instruments`,
  `add_instrument`, `update_instrument`, `delete_instrument`, `load_preset_items`,
  `save_band_hardware_as_preset`, `transfer_preset_to_band`, `BandDataError`).
- Neue API-Routen in `source/mpw_web.py`:
  `GET /api/bands/<id>/full`, `GET /api/hardware/choices`, `GET /api/presets`,
  `POST /api/bands/<id>`, `POST /api/bands/<id>/instruments`,
  `POST /api/instruments/<id>`, `POST /api/instruments/<id>/delete`,
  `POST /api/bands/<id>/presets`, `POST /api/presets/<id>/transfer`
  (Ersetzen verlangt `confirm: true`).
- Robustheit:
  - Der Server liest den Anfrage-Körper immer vollständig, bevor er antwortet
    (behebt sporadische Verbindungsabbrüche unter Windows); > 64 KB → 413.
  - Gesperrte Datenbank beim Lesen → 503 `database_busy` statt Absturz.
  - Die Oberfläche sperrt Band-Aktionen, solange eine läuft (kein doppelter Eintrag
    bei Doppelklick).
  - Beim Start wird die Datenbank angelegt, falls sie noch fehlt.

## Geprüft

- 217 Unit-Tests (mit `-W error::ResourceWarning`), Einzelskripte,
  `audit-startup.py`, `audit-workflows.py`, `release-preflight.py`,
  `audit-guide-translations.py`, Selbsttests von Desktop, MCP-Server und Web-Server,
  Kern ohne Qt.
- Browser-Durchlauf mit Beispieldaten: Profil speichern, Doppelklick, Preset speichern,
  hinzufügen und ersetzen, Bandwechsel – ohne Fehler.
