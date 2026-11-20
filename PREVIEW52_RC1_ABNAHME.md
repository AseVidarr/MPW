# MPW Preview 52 – Release Candidate 1

## Windows-Build
Im entpackten Projektordner `BUILD_STARTEN.cmd` starten oder `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\build.ps1` ausfuehren.

## Automatische Release-Pruefung (nur lesend)
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify-release-candidate.ps1 -RunPortableSelfTest`

Prueft: EXE, ZIP-Inhalt, SHA-256, Installer, EXE-Selbsttest. Das Skript installiert nichts und loescht keine Daten.

## Manuelle Windows-Abnahme
1. Portable-App aus ZIP in einen **neuen** Testordner entpacken und starten.
2. Neue Test-Band, Test-Projekt und Test-Song anlegen; danach Programm neu starten und Daten pruefen.
3. Backup in einem **separaten Testordner** erstellen und Ruecksicherung ausschliesslich mit Testdaten pruefen.
4. Installer in einer isolierten Testumgebung pruefen, vorhandene produktive Daten nicht als Testbasis verwenden.
5. Update-Verhalten bei geoeffneter App und Deinstallation ohne Datenverlust pruefen.

## Grenzen
Automatische Python-Tests ersetzen keine Windows-GUI-/Installer-Abnahme. Auf diesem System wurden keine Windows-EXE-Dateien gebaut.
