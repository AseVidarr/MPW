# MPW v2.2.0 Alpha 21 – Preview 47

Basis: Preview 46 Hotfix 1 (Startfehlerkorrektur enthalten).

## Änderungen

- Fünf neue automatisierte Integrationstests führen die tatsächlichen MPW-Funktionen für SQLite-Backup, ZIP-Validierung und Wiederherstellung in temporären Verzeichnissen aus.
- Geprüft werden: Rücksicherung nach Änderung, Erhalt externer Medien und Einstellungen, Ablehnung ungültiger Datenbankschemata, ZIP-Pfadtraversal-Schutz und Ausschluss von Medien aus dem Datenbankbackup.
- Build- und Inno-Setup-Ausgabebezeichnungen auf Preview 47 aktualisiert (waren in Preview 46 Hotfix 1 teilweise noch auf Preview 45 eingestellt).
- **Wichtig:** MPW-Datenbankbackups enthalten absichtlich keine Audio-, Cover- oder sonstigen Mediendateien. Diese müssen separat gesichert werden.
- **Offen:** Praktischer Windows-Starttest, Installations-/Upgradetest und Wiederherstellung mit produktiven MPW-Daten. Bei laufender Anwendung/WAL-Verwendung nicht ohne vorherige Sicherung wiederherstellen.
