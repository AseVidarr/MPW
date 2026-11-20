# MPW v2.2.0 RC1 – KI-Verbindungen Hotfix

Basis: MPW_v2.2.0_RC1_Preset_Zielband_Hotfix. Keine Datenbankmigration erforderlich.

## Reiter Konfiguration – Unterfenster „KI-Verbindungen“
Neuer Kasten **KI-Verbindungen** mit dem Knopf **„KI-Verbindungen einrichten …“**. Er öffnet ein eigenes Fenster, das den Stand prüft (im Hintergrund, MPW bleibt bedienbar) und fehlende Schritte per Knopf startet:

| Bereich | Anzeige | Knöpfe |
|---|---|---|
| Claude Code | installiert? angemeldet? | Installationsanleitung öffnen · Anmelden … (öffnet `claude auth login` in eigenem Fenster) |
| Gemini CLI / Codex CLI | installiert? Node.js vorhanden? | Anleitungen · Node.js herunterladen |
| API-Schlüssel | ANTHROPIC/OPENAI/GEMINI_API_KEY gesetzt? (Wert wird nie angezeigt) | Schlüsselseiten der Anbieter |
| MPW-Daten für Claude (MCP) | eingetragen/verbunden? | Verbinden (nur lesend) … · Trennen … · Für Claude Desktop kopieren |
| Suno (über Claude Code) | eingetragen / Anmeldung fehlt / verbunden | Suno eintragen … · Bei Suno anmelden … · Beta-Zugang beantragen |
| Netzwerk | erkennt Virenscanner, die verschlüsselte Verbindungen untersuchen (z. B. Norton), mit Hinweis | – |

- Jede Änderung an der Claude-Code-Einrichtung wird vorher bestätigt. MPW-Server und Suno werden für das ganze Benutzerkonto eingetragen (`--scope user`), der MPW-Server immer **ohne** Schreibzugriff.
- Installiert: `MPW-MCP.exe` neben `MPW.exe`; aus dem Quellcode: `python mpw_mcp_server.py`.
- MPW speichert keine Schlüssel und keine Anmeldedaten; jeder Anwender nutzt seine eigenen Konten.
- Alle Texte, Rückfragen, Meldungen und der Hilfeeintrag in DE/EN/FR/ES/IT; das offene Fenster wechselt die Sprache mit.

## Weitere Änderungen
- **CLI-Weg abgeschirmt:** „Prompt erstellen (CLI)“ ruft Claude Code jetzt mit `--strict-mcp-config` auf. Eingetragene MCP-Server (z. B. Suno) werden dabei nicht gestartet und können keine Credits verbrauchen.
- **CLI-Suche:** Findet `claude`/`gemini`/`codex` auch in den üblichen Installationsordnern (`%USERPROFILE%\.local\bin`, `%APPDATA%\npm`), wenn MPW nach einer frischen Installation den neuen PATH noch nicht kennt.

## Tests
- Neu: `tests/test_ai_connections.py` (Statusauswertung mit echten CLI-Ausgaben, Virenscanner-Erkennung, Befehle, Bestätigungen, Texte in 5 Sprachen).
- Angepasst: `tests/test_ai_cli_access.py` (neuer Schalter, Suche in Installationsordnern).
- 167 Tests, GUI- und MCP-Selbsttest, Start- und Workflow-Prüfung bestanden.
- Echtes Hauptfenster unsichtbar durchgespielt: echte (nur lesende) Statusprüfung, alle ändernden Knöpfe abgefangen und deren Befehle geprüft, Sprachwechsel, Bild des Fensters mit Windows-Schriften kontrolliert. Die Claude-Konfiguration des Testrechners blieb unverändert.

## Grenzen
- Gemini CLI und Codex CLI: nur „installiert“ wird geprüft, nicht die Anmeldung.
- Die Anmeldung bei Suno (OAuth) kann MPW nicht automatisieren; der Knopf öffnet Claude Code mit Anleitung (`/mcp`).
- Nicht sichtbar in der Windows-Oberfläche bedient. Kein Windows-EXE-Build erstellt.
