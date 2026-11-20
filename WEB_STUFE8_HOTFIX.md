# Web-Anwendung Stufe 8 – Backup im Browser

## Neuer Reiter „Backup“ (Browser)

Gleiche Regeln, gleiche Dateien wie die Desktop-App („Backup – Einstellungen“ / „Backup – Archiv“):

- **Status**: Backup-Ordner (erreichbar?), Statistik aus dem Prüfprotokoll (erfolgreich /
  fehlgeschlagen, letzter Eintrag – bei Fehler mit Grund), letzte automatische und nächste Sicherung.
- **Vollbackup jetzt erstellen …** (nach Rückfrage): nur die MPW-Datenbank, geprüft (ZIP + SQLite),
  Eintrag im Prüfprotokoll; Speicherplatz wird vorher geprüft.
- **Datenbank-Integrität prüfen**, **Backup-Ziel testen** (Schreibtest, Testdatei wird entfernt,
  freier Speicher), **Alle Backups prüfen** bzw. einzelnes Backup prüfen (✓/✗ in der Liste),
  **Prüfprotokoll anzeigen** – alles nur lesend.
- **Automatische Sicherung**: Intervall und Aufbewahrung (dieselbe `backup_settings.json`).
  Die fällige Sicherung selbst erstellt weiterhin die Desktop-App beim Start.
- **Backup-Ordner** ändern (nach Rückfrage; vollständiger Pfad, wird bei Bedarf angelegt,
  Schreibtest). Vorhandene Backups werden nicht verschoben.
- **Wiederherstellen …**: zwei Bestätigungen (Warnung + Bestätigungswort `WIEDERHERSTELLEN`).
  Vorher wird automatisch ein Sicherheitsbackup `MPW_vor_Wiederherstellung_…` angelegt;
  Medien sowie Band-/Projektordner bleiben unverändert. Ist die Datenbank noch von der
  Desktop-App geöffnet, wird die Wiederherstellung abgelehnt und nichts verändert.
- Es läuft immer nur eine Sicherung, Prüfung oder Wiederherstellung gleichzeitig.

## Technik

- Kern (`source/mpw_core.py`): `backup_settings`, `save_backup_settings`, `backup_directory`,
  `backup_inventory`, `backup_log_entries`, `automatic_backup_due`, `backup_file_in`
  (nur Dateinamen im Backup-Ordner), `test_backup_destination`, `new_backup_path`.
  Die Desktop-App liest/schreibt die Backup-Einstellungen jetzt über dieselben Funktionen.
- Web (`source/mpw_web.py`): `GET /api/backup`, `POST /api/backup/create` (`confirm`),
  `POST /api/backup/validate`, `GET /api/backup/jobs/<id>`, `POST /api/backup/integrity`,
  `GET /api/backup/log`, `POST /api/backup/settings`, `POST /api/backup/folder` (`confirm`),
  `POST /api/backup/test`, `POST /api/backup/restore` (`confirm` + `confirm_text`).

## Geprüft

- 239 Unit-Tests (mit `-W error::ResourceWarning`), u. a. Ordner (Bestätigung, relative Pfade
  abgewiesen), Einstellungen (nur erlaubte Werte), Backup + Prüfung + Protokoll, beschädigtes ZIP
  erkannt, unzulässige Dateinamen abgewiesen, **echte Wiederherstellung mit Sicherheitsbackup**
  (vorheriger Stand bleibt im Sicherheitsbackup erhalten), ohne Bestätigung/mit falschem Wort
  wird nichts geändert.
- Einzelskripte, alle Audit-Skripte, Selbsttests von Desktop, MCP-Server und Web-Server, Kern ohne Qt.
- Browser-Durchlauf mit Beispieldaten: Ordner festlegen, Ziel testen, Integrität, Vollbackup,
  Einstellungen, alle prüfen, Protokoll, Wiederherstellung mit falschem und richtigem Wort –
  ohne Fehler. Nur Temp-Daten, nie die echten MPW-Daten.
