# MPW v2.1.0 Stable – Windows-Buildpaket

Basis: hochgeladener Release-Kandidat mit `workstation.py`, `requirements.txt`, `README_START.md`.

## Bauen unter Windows 10/11 x64

1. Python 3.10+ (empfohlen 3.12) und Inno Setup 6 installieren.
2. Im entpackten Buildpaket PowerShell öffnen.
3. `powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1` ausführen.
4. Ergebnisse unter `dist`: `MPW_Setup_v2.1.0.exe`, `MPW_Portable_v2.1.0.zip`, `MPW/MPW.exe`, `SHA256SUMS.txt`.

Wenn Inno Setup fehlt, wird nur das Portable-Paket gebaut.

## Bestandsschutz

- Buildskript verwendet ausschließlich Quellcode im Buildpaket; produktive MPW-Daten werden nicht geöffnet.
- Setup enthält nur die Anwendung; es löscht oder migriert keine Datenbank- oder Medienordner.
- Deinstallation entfernt nur installierte Programmdateien, nicht das bestehende Benutzerverzeichnis.
- Installer-Version verwendet unveränderte MPW-Datenpfad-Ermittlung (Registry `HKCU\Software\MPW` oder Legacy-Verzeichnis).
- Portable-Starter setzt `MPW_DATA_ROOT` auf den eigenen Ordner `Data`, damit vorhandene Installationsdaten nicht versehentlich geöffnet werden. Beim ersten Start wird dort eine neue Datenbank angelegt.
- Portable-Updates: `Data` niemals überschreiben oder löschen; neue Programmdateien getrennt aktualisieren.
- Direkter Start von `App\MPW.exe` umgeht die Portable-Isolation: immer `Start-MPW-Portable.cmd` verwenden.

## Wichtig: Datenbestand beim Programmstart

Der Quellcode führt beim normalen Programmstart Schema-Initialisierung und mögliche Migrationen aus. Deshalb ist ein unveränderter produktiver Datenbestand **beim Start der installierten Anwendung nicht garantiert**. Vor einem Upgrade eine externe Sicherung erstellen, zuerst mit einer Kopie der Datenbank testen und Schema-Diff prüfen. Das Build selbst und das Installationsprogramm verändern die Bestandsdaten nicht.

## Release-Abnahme

- Python-Selbsttest und EXE-Selbsttest erfolgreich
- Installer auf sauberem Windows-PC testen
- Portable auf sauberem Windows-PC ohne Python testen
- Installer-Upgrade und Deinstallation mit Testdaten prüfen
- Datenverzeichnisse vor/nach Installation/Deinstallation per Hash vergleichen
- Anwendung mit kopiertem Datenbestand starten und Integrität prüfen
- Windows Defender/SmartScreen und Signierung prüfen (unsigned EXE kann Warnung erzeugen)
