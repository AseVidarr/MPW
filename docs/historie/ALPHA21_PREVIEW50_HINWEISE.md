# MPW Preview 50 – Backup-Sicherheit

- ZIP-Backups werden zunächst in einer temporären Datei auf demselben Laufwerk erstellt und geprüft; erst danach erfolgt die atomare Ersetzung des Zielarchivs.
- Ein fehlerhafter Backup-Vorgang überschreibt ein vorhandenes Archiv nicht.
- Die Wiederherstellung verweigert den Austausch der Datenbank, solange WAL-/SHM-Sidecars vorhanden sind. MPW muss vorher beendet und der Datenbankzustand geprüft werden.
- Fünf isolierte Regressionstests für gültige Backups, Fehlerfälle, Wiederherstellung und Medienerhalt.
- Kein Windows-GUI-Test und kein Installer-Build in dieser Umgebung.
