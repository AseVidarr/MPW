# MPW v2.2.0 – Alpha 21 Preview 41

Basis: Preview 40. Schwerpunkt: Release-Vorbereitung und automatisierte Windows-Build-Vorabprüfung.

- Build-Ausgabeverzeichnis und Portable-ZIP auf `MPW_Portable_v2.2.0_Alpha21_Preview41` aktualisiert.
- Inno-Setup-Version auf `2.2.0` und Setup-Ausgabename auf `MPW_Setup_v2.2.0_Alpha21_Preview41` aktualisiert.
- Portable-Datenmarker `.mpw-portable-v2` **unverändert** belassen, um den bestehenden Launcher nicht zu beschädigen.
- Neue statische Tests `tests/test_release_preflight_p41.py` prüfen Versionskonsistenz, Selbsttests, Installer-Bereich, Portable-Datenschutz und Build-Eingaben.
- Die eigentliche Windows-Kompilierung, EXE-Ausführung und GUI-Abnahme sind weiterhin **nicht** durchgeführt. Das ZIP enthält Quellcode und Build-Skripte, keinen fertigen Windows-Installer.

Windows-Build: `powershell -ExecutionPolicy Bypass -File scripts\build.ps1` (auf einem Windows-PC mit Python 3.10+, PyInstaller und optional Inno Setup 6/7). Vor dem Test produktive Daten sichern.
