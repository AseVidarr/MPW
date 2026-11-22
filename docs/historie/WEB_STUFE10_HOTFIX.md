# Web-Anwendung Stufe 10 – Konfiguration im Browser

## Neuer Reiter „Konfiguration“ (Browser)

Gemeinsam mit der installierten MPW (dieselbe `app_configuration.json`):

- **Sprache / Language**: Automatisch, Deutsch, English, Français, Español, Italiano.
  Die Seite lädt danach in der neuen Sprache neu und bleibt auf dem Reiter „Konfiguration“.
  Gilt auch für die Desktop-App (ab ihrem nächsten Start). Alle anderen Einstellungen
  der Desktop-App (Startreiter, Farben, Hintergrund …) bleiben unverändert.
- **Speicherorte** (nur Anzeige): MPW-Datenordner, Datenbank, Mediendateien,
  Konfigurationsdatei, Band-Speicherort, Backup-Ordner. **Ordner öffnen** für Datenordner,
  Band-Speicherort und Backup-Ordner – im Explorer, Finder bzw. Linux-Dateimanager
  (nur diese drei MPW-Ordner, kein frei wählbarer Pfad).
- **Song/Projekt-Unterordner**: Vorlage für neue gemeinsame Projektordner – die vier
  Medienordner (Cover, Audio, Dokumente, Video) sind fest, bis zu sechs weitere möglich.
  Gleiche Prüfung wie in der Desktop-App (gültige Ordnernamen, keine Doppelten).
  Vorhandene Ordner werden nicht umbenannt, verschoben oder gelöscht.
- **Programm**: Version und System.

Bewusst nur in der Desktop-App: Band-Speicherort ändern (überträgt alle MPW-Daten – nicht,
während MPW im Browser läuft), Erscheinungsbild/Hintergrund, alte Musikordner übernehmen,
Projektdateien sortieren, Ordnersymbole aus Covern.

Außerdem: Nach einem Neuladen der Seite öffnet sich wieder der zuletzt verwendete Reiter.

## Technik

- Kern (`source/mpw_core.py`): `UI_LANGUAGES`, `save_app_configuration`,
  `configured_project_folders`, `clean_project_folder_template`, `open_in_file_manager`.
  Die Desktop-App speichert Einstellungen und liest die Ordner-Vorlage jetzt über dieselben Funktionen.
- Web (`source/mpw_web.py`): `GET /api/config`, `POST /api/config/language`,
  `POST /api/config/folders`, `POST /api/config/open-folder`; `/api/info` liest die Sprache
  aus dem Datenordner des laufenden Servers.

## Geprüft

- 246 Unit-Tests (mit `-W error::ResourceWarning`), u. a. Sprache (ungültig abgewiesen, sofort
  in `/api/info`, andere Desktop-Einstellungen bleiben erhalten), Ordner-Vorlage (ungültiger Name,
  Doppelte auch gegen die festen Ordner, mehr als sechs, Speichern), Ordner öffnen nur für
  MPW-Ordner (Öffnen im Test ersetzt).
- Einzelskripte, alle Audit-Skripte, Selbsttests von Desktop, MCP-Server und Web-Server, Kern ohne Qt.
- Browser-Durchlauf mit Beispieldaten: Speicherorte, Ordner-Vorlage (ungültig/gültig),
  Sprachwechsel Deutsch → Französisch → Automatisch mit Rückkehr auf den Reiter – ohne Fehler.
