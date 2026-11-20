# Windows-Installationsabnahme – Preview 43

Status: **alle manuellen Prüffälle offen**. Nur auf einer Windows-Testmaschine mit gesicherten Testdaten ausführen.

| ID | Testfall | Erwartetes Ergebnis | Status |
|---|---|---|---|
| W01 | Erstinstallation ohne Administratorrechte | Installer beendet erfolgreich, MPW startet | Offen |
| W02 | Start über Startmenü | Programm startet | Offen |
| W03 | Optionales Desktop-Symbol | Symbol zeigt auf MPW.exe | Offen |
| W04 | EXE-Selbsttest | Exitcode 0 | Offen |
| W05 | Upgrade einer vorhandenen Installation | Bestehende Konfiguration und Musikdaten bleiben erhalten | Offen |
| W06 | Deinstallation | Nur installierte Programmdateien entfernt | Offen |
| W07 | Benutzerdaten nach Deinstallation | Datenbank, Medien, Backups bleiben erhalten | Offen |
| W08 | Neuinstallation nach Deinstallation | Vorhandene Daten werden wiedergefunden | Offen |
| W09 | Sprachwechsel in allen 14 Reitern | Fünf Sprachen korrekt | Offen |
| W10 | Installer-Signatur/SmartScreen | Publisher-/Warnhinweise geprüft | Offen |

## Hilfsskript

`powershell -ExecutionPolicy Bypass -File scripts/verify-windows-install.ps1 -InstallerPath dist/MPW_Setup_v2.2.0_Alpha21_Preview43.exe`

Standardmäßig erfolgt nur eine Dateiprüfung mit SHA256-Ausgabe. Mit `-RunInstall` wird eine **neue** Testinstallation in einem noch nicht vorhandenen Verzeichnis ausgeführt. `-RunUninstall` ist nur gemeinsam mit `-RunInstall` zulässig. Benutzerdaten werden nicht automatisch angelegt oder gelöscht. Vor Upgrade-/Deinstallationstests Sicherung erstellen und Daten manuell prüfen.
