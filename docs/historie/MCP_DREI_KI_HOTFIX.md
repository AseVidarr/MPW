# MPW v2.2.0 RC1 – MCP für drei KI Hotfix

Basis: MPW_v2.2.0_RC1_Suno_Senden_Hotfix. Keine Datenbankmigration erforderlich.

## Konfiguration › KI-Verbindungen
Die MCP-Verbindungen (MPW-Daten und Suno) lassen sich jetzt für **Claude Code, Gemini CLI und Codex CLI** einrichten:
- **MPW-Daten für KI freigeben (MCP):** je eine Statuszeile pro KI; Menü **Einrichten für:** wählt die KI für „Verbinden (nur lesend) …“ und „Trennen …“. „Für Claude Desktop kopieren“ bleibt.
- **Suno:** je eine Statuszeile pro KI; Knöpfe „Suno eintragen …“, „Bei Suno anmelden …“, neu **„Suno entfernen …“**, „Beta-Zugang beantragen“ für die gewählte KI.
- Status: verbunden · eingetragen · Anmeldung bei Suno fehlt · Verbindung fehlgeschlagen · nicht eingerichtet · nicht installiert.
- Rückfragen und Hinweise nennen die gewählte KI; Texte in DE/EN/FR/ES/IT.

| KI | MPW-Daten eintragen | Suno eintragen | Entfernen | Suno-Anmeldung |
|---|---|---|---|---|
| Claude Code | `claude mcp add --scope user mpw -- <Server>` | `claude mcp add --scope user --transport http suno <URL>` | `claude mcp remove <name> --scope user` | Fenster mit `claude`, dort `/mcp` |
| Gemini CLI | `gemini mcp add --scope user mpw <Server>` | `gemini mcp add --scope user --transport http suno <URL>` | `gemini mcp remove --scope user <name>` | Fenster mit `gemini`, dort `/mcp auth suno` |
| Codex CLI | `codex mcp add mpw -- <Server>` | `codex mcp add suno --url <URL>` | `codex mcp remove <name>` | `codex mcp login suno` (Browser) |

Status: Claude `claude mcp get`, Gemini `gemini mcp list`, Codex `codex mcp list --json`. MPW trägt Server nie mit Schreibzugriff und nie als „vertrauenswürdig“ (ohne Bestätigungen) ein.

## Abschirmung der MPW-Prompt-Anfragen
- Claude Code: weiterhin `--strict-mcp-config`.
- **Codex CLI (neu):** MPW liest die in `%USERPROFILE%\.codex\config.toml` (bzw. `CODEX_HOME`) eingetragenen MCP-Server und schaltet sie für jede Prompt-Anfrage mit `-c mcp_servers.<name>.enabled=false` ab.
- Gemini CLI: Kein dokumentierter Schalter. Gemini führt Werkzeuge ohne Bestätigung im nicht-interaktiven Modus nicht aus, und MPW trägt Server nicht als vertrauenswürdig ein.

„An Suno senden (MCP)“ im Reiter Songs & Suno nutzt weiterhin Claude Code.

## Tests
- `tests/test_ai_connections.py`: Befehle für alle drei KI, Suno-Anmeldung je KI, Auswertung von `gemini mcp list` und `codex mcp list --json`, Rückfrage und Zielauswahl in allen Aktionen, keine doppelt genutzten Textschlüssel.
- `tests/test_ai_cli_access.py`: Codex-Abschirmung, Lesen der Codex-Konfiguration.
- 185 Tests, GUI- und MCP-Selbsttest, Start- und Workflow-Prüfung bestanden; echtes Fenster unsichtbar durchgespielt (alle Befehle für die drei KI abgefangen und geprüft, Bild kontrolliert, Suno-Senden weiterhin in Ordnung).

## Grenzen
- Gemini CLI und Codex CLI waren auf dem Testrechner nicht installiert. Die Befehle folgen deren offizieller Dokumentation, wurden aber nicht gegen die echten Programme ausgeführt. Das Ausgabeformat von `codex mcp list --json` ist nicht dokumentiert und wird tolerant gelesen.
- Ob Codex `-c mcp_servers.<name>.enabled=false` in `codex exec` wie dokumentiert anwendet, ist ungeprüft.
- Der Status zeigt Einträge auf Benutzerebene. Nur für einen Projektordner eingetragene Server erscheinen als „nicht eingerichtet“.
- Kein Windows-EXE-Build erstellt.
