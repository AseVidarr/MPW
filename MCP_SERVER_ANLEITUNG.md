# MPW als MCP-Server

Mit dem MCP-Server greifen KI-Werkzeuge wie **Claude Code, Claude Desktop, Gemini CLI und Codex CLI** direkt auf deine MPW-Daten zu. Beispiel in Claude Code:

> „Schreib für den Song *Rain Song* von *Iron Delta* einen neuen Suno-Prompt im Stil der letzten zwei Versionen und speichere ihn als neue Version.“

Die KI holt sich Bandprofil, Genres, Persona, Hardware und frühere Versionen selbst aus MPW.

## Programme

| Variante | Server-Befehl |
|---|---|
| Installiert | `MPW-MCP.exe` im Installationsordner (neben `MPW.exe`) |
| Portable | `App\MPW-MCP.exe`, nutzt automatisch den Portable-Ordner `Data` |
| Quellcode | `py -3 source\mpw_mcp_server.py` |

`MPW-MCP.exe --config` gibt die fertigen Einrichtungsbefehle mit dem richtigen Pfad aus und zeigt, welche Datenbank verwendet wird.

## Einrichten (Beispiel Installationsordner)

Claude Code:
```powershell
claude mcp add --scope user mpw -- "C:\Users\<Name>\AppData\Local\Programs\Music Production Workstation\MPW-MCP.exe"
```
Gemini CLI:
```powershell
gemini mcp add --scope user mpw "C:\Users\<Name>\AppData\Local\Programs\Music Production Workstation\MPW-MCP.exe"
```
Codex CLI:
```powershell
codex mcp add mpw -- "C:\Users\<Name>\AppData\Local\Programs\Music Production Workstation\MPW-MCP.exe"
```
Claude Desktop (`claude_desktop_config.json`): Eintrag unter `mcpServers` mit `"command"` auf den Pfad von `MPW-MCP.exe`. Die Vorlage gibt `--config` aus.

## Werkzeuge

Nur lesend (immer verfügbar):

| Werkzeug | Inhalt |
|---|---|
| `list_bands` | Bands mit Genres, Persona, Anzahl Projekte/Songs |
| `get_band` | Bandprofil, Instrumente/Hardware, Projekte mit Song-IDs |
| `list_songs` | Songs, filterbar nach Band, Titel, Status |
| `get_song` | aktiver Suno-Prompt, Notizen, Genres, Medien, Links, Releases |
| `list_prompt_versions` / `get_prompt_version` | gespeicherte Versionen, Volltext |
| `list_hardware_presets` | Hardware-Presets |
| `search_genres` | MPW-Genre-Katalog |
| `get_suno_briefing` | dieselbe Anweisung, die der AI Prompt Launcher an die KI schickt |

Schreibend (nur mit `--allow-write` oder `MPW_MCP_ALLOW_WRITE=1`):

| Werkzeug | Wirkung |
|---|---|
| `save_prompt_version` | legt eine **neue** Prompt-Version an (Anbieter „MCP“) plus TXT-Datei im Band-Ordner `Song-Prompts`, genau wie „Als neue Version speichern“ |

Für Schreibzugriff beim Einrichten `--allow-write` hinter den Pfad setzen, z. B.
`claude mcp add --scope user mpw -- "…\MPW-MCP.exe" --allow-write`.

## Sicherheit

- Gleicher Datenpfad wie MPW: Portable-`Data`, `MPW_DATA_ROOT` oder der in MPW eingestellte Band-Stammordner.
- Lesen öffnet die Datenbank schreibgeschützt (SQLite `mode=ro`) und nur für die Dauer einer Abfrage. MPW darf dabei geöffnet sein.
- Der Server legt nie eine Datenbank an und migriert nichts.
- Auch mit Schreibzugriff wird nichts geändert oder gelöscht. Der aktive Song-Prompt bleibt, wie er ist. Die Übernahme machst du selbst in MPW („Version B in Song-Editor übernehmen“).
- **Datenschutz:** Was die KI über MCP liest (Bandprofile, Songtexte, Notizen), geht an den jeweiligen KI-Anbieter.

## Technik

- MCP über stdio (JSON-RPC 2.0, Protokollversionen 2024-11-05 bis 2025-11-25), nur mit der Python-Standardbibliothek umgesetzt, keine zusätzlichen Pakete.
- Build: `installer/MPW.spec` erzeugt `MPW.exe` und `MPW-MCP.exe` im selben Ordner. `build.ps1` führt für beide einen Selbsttest aus, `MPW-MCP.exe --self-test` arbeitet nur mit einer Temp-Datenbank.
- Die Suno-Anweisung (`suno_prompt_request`) teilen sich GUI und MCP-Server.
- Tests: `tests/test_mcp_server.py` (14 Tests, nur Temp-Daten).
