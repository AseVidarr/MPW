# MPW v2.2.0 RC1 – GitHub und Builds für drei Systeme (Schritt 3)

Basis: MPW_v2.2.0_RC1_Plattform_Neutral_Hotfix. Keine Änderung an MPW selbst.

## Neu
- **`.github/workflows/build.yml`**: Tests auf Windows, macOS und Linux (Unit-Tests, Testskripte, drei Selbsttests mit Temp-Daten); danach Pakete: Windows Setup + Portable (`build.ps1` mit Inno Setup), macOS- und Linux-Portable (nur Browser). Ein Tag `v…` legt einen **Release-Entwurf** an (Veröffentlichen bleibt manuell). Aktuelle Actions: checkout v7, setup-python v7, upload-artifact v7, download-artifact v8, action-gh-release v3; Rechte standardmäßig nur lesend.
- **`scripts/build-unix.sh`** + **`installer/MPW-Web.spec`**: baut auf macOS/Linux `App/MPW-Web` und `App/MPW-MCP` ohne Qt, Selbsttests vor und nach dem Bauen, Portable-Ordner mit Startskript, Anleitung und Markierung, Paket als `.tar.gz` (behält Ausführungsrechte) mit SHA-256. Überschreibt nie vorhandene Ausgaben.
- **`.gitignore`** (Build-Ausgaben, Pakete, Nutzerdaten `Data/`, `*.db`, `app_configuration.json`), **`.gitattributes`** (Unix-Zeilenenden für `.sh`/`.command`/`.py`, Windows-Zeilenenden für `.ps1`/`.cmd`/`.iss`).
- **`README.md`** (Startseite), **`GITHUB_EINRICHTEN.md`** (Veröffentlichen mit GitHub Desktop, erster Build, Release).
- Lokales Git-Repository (Branch `main`) mit erstem Commit.

## Tests
- Neu: `tests/test_ci_build.py` (Workflow-Aufbau, Action-Versionen, sichere Voreinstellungen, Build-Skript, Spec ohne Qt, Git-Dateien).
- Angepasst: `tests/test_ai_cli_access.py` (Programmsuche auch auf macOS/Linux).
- Shell-Skripte mit `sh -n` und `dash -n` geprüft; Linux-Startskript im Ablauf getestet (ohne/mit Markierung, Optionen).
- 214 Tests, alle Testskripte, drei Selbsttests, Start-/Workflow-/Release-Prüfung bestanden.

## Grenzen
Die Builds auf macOS/Linux und der Workflow selbst laufen erst nach dem Hochladen auf GitHub. macOS-Paket nur für Apple-Silicon (arm64). Programme sind nicht signiert (Hinweise in LIESMICH_MAC_LINUX.txt).
