# MPW v2.2.0 RC1 – Plattformneutral (Schritt 2 für macOS/Linux)

Basis: MPW_v2.2.0_RC1_Kern_ohne_Qt_Hotfix. Keine Datenbankmigration. Unter Windows keine Verhaltensänderung.

## Portable-Erkennung (mpw_core.portable_root_for)
Entscheidend ist immer die Markierungsdatei `.mpw-portable-v2`. Erkannte Aufbauten:
- `<Portable>/App/<Programm>` – Windows, Linux, macOS (einfache Programmdatei)
- `<Portable>/<Name>.app/Contents/MacOS/<Programm>` und `<Portable>/App/<Name>.app/...` – macOS-App-Paket
- **macOS App Translocation** (Start aus „Downloads“ ohne Freigabe): MPW bricht mit klarem Hinweis ab, statt die Daten still in einem falschen Ordner abzulegen.

## KI-Programme auf allen Systemen
- Suche zusätzlich in den üblichen Ordnern: Windows `%USERPROFILE%\.local\bin`, `%APPDATA%\npm`; macOS/Linux `~/.local/bin`, `~/.claude/local`, `~/.npm-global/bin`, `~/.volta/bin`, `~/bin`, `/opt/homebrew/bin`, `/usr/local/bin`, `/usr/bin`, `NPM_CONFIG_PREFIX`, nvm (neueste Node-Version zuerst).
- Beim Start eines KI-Programms steht dessen Ordner vorn im Suchpfad: Gemini/Codex (Node-Skripte) finden so `node`.
- MCP-Server-Pfad ohne `.exe` außerhalb von Windows (`MPW-MCP`).

## Webanwendung legt die Datenbank an
`MPW-Web` bereitet die Datenbank beim Start wie die Desktop-App vor (anlegen falls fehlend, neue Tabellen/Spalten ergänzen, nichts löschen). Nötig, weil auf macOS/Linux die Webanwendung das einzige MPW-Programm ist.

## Startdateien für macOS/Linux
- `scripts/Start-MPW-Web.command` (macOS, Doppelklick im Terminal), `scripts/start-mpw-web.sh` (Linux); prüfen die Portable-Markierung, legen `Data` an, starten `App/MPW-Web`; Unix-Zeilenenden.
- `scripts/LIESMICH_MAC_LINUX.txt`: Start, Gatekeeper-Freigabe (`xattr -dr com.apple.quarantine`), `chmod +x`, MCP, Updates ohne Datenverlust.
- Werden ab Schritt 3 (GitHub Actions) in die Mac-/Linux-Pakete übernommen.

## Tests
- Neu: `tests/test_platform_neutral.py` (Portable-Aufbauten aller Systeme, App Translocation, Programmsuche Windows/macOS/Linux inkl. nvm, Suchpfad, Startskripte mit Unix-Zeilenenden, Webanwendung legt Datenbank an).
- Angepasst: `tests/test_ai_cli_access.py`, `tests/test_suno_send.py`, `tests/test_portable_isolation.py`, `tests/verify_source.py` (prüfte seit Schritt 1 die falsche Datei – behoben).
- 206 Tests, alle Testskripte, GUI-/MCP-/Web-Selbsttest, Start-/Workflow-/Release-Prüfung bestanden; Web und MCP ohne PySide6 geprüft; Desktop-Fensterdurchläufe (Hardware-Menüs/Presets, An Suno senden) bestanden.

## Grenzen
macOS und Linux wurden nur nachgestellt (Ordnerstrukturen, Pfade), nicht auf echten Systemen ausgeführt – das folgt mit den GitHub-Builds in Schritt 3.
