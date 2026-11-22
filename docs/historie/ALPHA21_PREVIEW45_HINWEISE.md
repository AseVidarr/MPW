# MPW v2.2.0 Alpha 21 Preview 45

Basis: Preview 44. Neu: read-only SQLite-Prüfwerkzeug `scripts/verify-sqlite-upgrade.py` und fünf Tests.

## Verwendung (nur Kopien von Testdaten)

```powershell
python scripts/verify-sqlite-upgrade.py "C:\MPW-Testdaten\mpw.sqlite" --media-root "C:\MPW-Testdaten\Medien" --output "C:\MPW-Testberichte\sqlite-vorher.json"
```

Nach einem Upgrade mit geschlossener MPW-Anwendung erneut prüfen und Berichte manuell vergleichen. Das Werkzeug führt `PRAGMA integrity_check`, `PRAGMA foreign_key_check` und Tabellen-Zeilenzählungen aus. Es prüft nur absolute Dateipfade in fünf üblichen Spaltennamen; relative Pfade, andere Schemas, verlinkte Medien, Backups und WAL-Zustände sind damit **nicht vollständig** geprüft. Keine Datenbank-Reparatur, kein Backup und keine Wiederherstellung. Bericht nur neu und außerhalb des Datenbankordners. Windows-Laufzeittest weiterhin offen.
