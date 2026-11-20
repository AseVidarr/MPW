# MPW v2.2.0 Alpha 21 Preview 44

Basis: Preview 43. Schwerpunkt: **read-only Upgrade-Datenkontrolle**.

- Neues Skript `scripts/verify-upgrade-data.ps1` für einen SHA256-/Dateigrößen-Baseline-Vergleich der **explizit angegebenen** Datenverzeichnisse vor und nach einem Upgrade.
- Das Skript führt weder Installation noch Löschung, Kopieren oder Wiederherstellung aus. Es bricht bei fehlenden Dateien, Änderungen, Reparse-Point-Dateien, doppelten Dateien und vorhandener Manifest-Zieldatei ab.
- Neues Testmodul `tests/test_upgrade_data_safety_p44.py` mit fünf statischen Sicherheitsprüfungen.
- Build- und Installer-Bezeichnung auf Preview 44 gesetzt; APP_VERSION aktualisiert.

## Windows-Ablauf (nur mit TESTDATEN)

1. MPW vollständig schließen und ein externes Backup der Testdaten anfertigen.
2. Baseline außerhalb der Datenverzeichnisse erzeugen:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify-upgrade-data.ps1 -DataPaths 'C:\MPW-Testdaten' -ManifestPath 'C:\MPW-Testberichte\vorher.json'
```

3. Upgrade **manuell** durchführen und MPW starten/schließen.
4. Vergleich ausführen:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify-upgrade-data.ps1 -DataPaths 'C:\MPW-Testdaten' -ManifestPath 'C:\MPW-Testberichte\vorher.json' -Verify
```

**Wichtig:** MPW kann beim Start Datenbank-/Konfigurationsdateien regulär verändern. Ein Hash-Unterschied bedeutet daher zunächst *Unterschied*, nicht automatisch Datenverlust. SQLite-WAL-Dateien und laufende Prozesse können Ergebnisse verfälschen. Nur im vollständig geschlossenen Zustand prüfen. Externe, verlinkte Medienverzeichnisse separat angeben. Das Skript ist keine Backup-Lösung und kein Beweis für die semantische Integrität von SQLite.

**Grenzen:** PowerShell-Ausführung und Windows-Upgrade nicht in dieser Umgebung geprüft. Alle Windows-Abnahmen bleiben offen.
