# MPW – Music Production Workstation

Bands, Songs, Suno-Prompts, KI-Verbindungen (Claude, Gemini, ChatGPT), Medien, Releases und Plattensammlung verwalten – lokal auf deinem Computer.

## Varianten

| System | Paket | Desktop-App | Browser-Oberfläche |
|---|---|---|---|
| Windows | Setup (`MPW_Setup_*.exe`) | ✔ | ✔ (Startmenü „MPW im Browser“) |
| Windows | Portable (`MPW_Portable_*.zip`) | ✔ `Start-MPW-Portable.cmd` | ✔ `Start-MPW-Web-Portable.cmd` |
| macOS | Portable (`*_macOS-*.tar.gz`) | – | ✔ `Start-MPW-Web.command` |
| Linux | Portable (`*_Linux-*.tar.gz`) | – | ✔ `start-mpw-web.sh` |

Die Browser-Oberfläche läuft **nur auf deinem Computer** (127.0.0.1) und nutzt **dieselben Daten** wie die Desktop-App. Portable-Versionen speichern alles im Ordner `Data` daneben. macOS/Linux: siehe `scripts/LIESMICH_MAC_LINUX.txt`.

## Aufbau

- `source/mpw_core.py` – Kernlogik ohne Oberfläche (Daten, Backup, KI, Suno), läuft ohne Qt
- `source/workstation.py` – Desktop-App (PySide6)
- `source/mpw_web.py`, `source/web/` – Browser-Oberfläche
- `source/mpw_mcp_server.py` – MCP-Server für KI-Programme
- `tests/` – automatische Tests · `scripts/` – Build- und Startskripte · `installer/` – PyInstaller/Inno Setup
- `docs/historie/` – Änderungsnotizen der bisherigen Versionen und Hotfixes · `RELEASE_NOTES.md` – aktuelle Versionshinweise

## Bauen und Testen

- Windows: `build.ps1` (Setup + Portable) · macOS/Linux: `sh scripts/build-unix.sh`
- Tests: `python -m unittest discover -s tests -p "test_*.py"`
- GitHub Actions (`.github/workflows/build.yml`) testet auf Windows, macOS und Linux und baut alle Pakete; ein Tag `v…` erstellt einen Release-Entwurf.
