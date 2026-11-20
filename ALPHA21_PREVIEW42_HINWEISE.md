# MPW v2.2.0 – Alpha 21 Preview 42

Basis: Preview 41. Schwerpunkt: Windows-Build-Schutzprüfungen und Release-Validierung.

- PowerShell-Build auf Preview 42 aktualisiert, ebenso Inno-Setup-Ausgabename.
- Explizite Python-Mindestversion (3.10) und Abhängigkeitsprüfung (PyInstaller, PySide6, mutagen) vor dem Build.
- Einheitliche Exitcode-Prüfung für Python, PyInstaller, Quellcode- und EXE-Selbsttest.
- Prüft MPW.exe und Portable-Kopie auf Existenz und nichtleere Dateigröße.
- Prüft nach ZIP-Erzeugung, ob MPW.exe und Start-Launcher enthalten sind.
- Prüft bei vorhandenem Inno Setup die tatsächliche Installer-EXE und die SHA256SUMS-Datei.
- Vorhandene Portable-Ausgabe und ZIP werden weiterhin nicht automatisch gelöscht oder überschrieben.
- Fünf neue statische Regressionstests in `tests/test_release_build_guards_p42.py`.

**Grenzen:** Statische Tests und Python-Tests können die Windows-PowerShell-Ausführung nicht ersetzen. Ein Windows-Build, EXE-Start, Installer-Test und GUI-Abnahme wurden hier nicht durchgeführt.
