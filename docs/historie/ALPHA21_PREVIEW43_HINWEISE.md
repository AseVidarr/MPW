# MPW v2.2.0 Alpha 21 Preview 43

Basis: Preview 42. Schwerpunkt: Windows-Installationsabnahme.

- Neues optionales Windows-Prüfskript `scripts/verify-windows-install.ps1` mit Installer-Dateiprüfung, SHA256, optionaler Erstinstallation, EXE-Selbsttest und optionaler Deinstallation.
- Schutz vor Installation in bereits bestehendes Testverzeichnis; keine automatische Löschung von Benutzerdaten.
- Neue manuelle Abnahmematrix `tests/WINDOWS_INSTALLATION_ABNAHME_P43.md` mit zehn offenen Testfällen (Installation, Upgrade, Deinstallation, Datenbestand, Sprachen).
- Build-Skript und Inno-Setup-Ausgabename auf Preview 43 aktualisiert.
- Fünf zusätzliche statische Tests in `tests/test_installer_acceptance_p43.py`.

**Grenzen:** Tests prüfen die Quelltexte und Python-Logik. Installer-Ausführung, Windows-GUI, Upgrade und Datenbestand sind nicht getestet. Ein Windows-Installer ist nicht Bestandteil dieses Quellcode-ZIPs.
