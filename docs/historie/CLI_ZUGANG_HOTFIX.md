# AI Prompt Launcher – CLI-Zugang

Neuer Weg neben API und Browser: **„Prompt erstellen (CLI)“** nutzt die lokal installierte KI-CLI mit deren eigener Anmeldung (Abo), ohne API-Schlüssel.

| KI-Plattform | Standard-CLI | Aufruf (Prompt über stdin) |
|---|---|---|
| Claude | `claude` (Claude Code) | `claude -p --output-format text [--model …]` |
| Gemini | `gemini` (Gemini CLI) | `gemini [-m …]` |
| ChatGPT | `codex` (Codex CLI) | `codex exec --skip-git-repo-check --sandbox read-only --output-last-message <tmp> -` |

- Feld **CLI-Befehl**: Programmname oder vollständiger Pfad; wird beim Plattformwechsel nur ersetzt, wenn kein eigener Pfad eingetragen ist. **CLI prüfen** zeigt den gefundenen Pfad an, ohne etwas zu senden.
- Feld **CLI-Modell**: optional; leer = Standardmodell der CLI.
- Die CLI läuft in einem leeren Temp-Ordner (danach gelöscht), ohne Shell, ohne Konsolenfenster, Zeitlimit 5 Minuten. Projektdateien und Datenbank sind für die CLI nicht sichtbar.
- Die Antwort landet wie beim API-Modus nur in den Editoren STYLE/LYRICS; gespeichert wird erst über „Als neue Version speichern“.
- Voraussetzung: CLI einmal im Terminal starten und anmelden.
- Fehlertexte (nicht gefunden, nicht angemeldet/Fehlercode, Zeitüberschreitung) und alle neuen Bedienelemente in DE/EN/FR/ES/IT.
- Integrierte Hilfe (ausführliche Anleitung DE/EN): Felder CLI-Befehl, CLI-Modell, CLI prüfen, Button „Prompt erstellen (CLI)“, Arbeitsablauf und zwei FAQ-Einträge (CLI nicht gefunden, Fehlercode). FR/ES/IT zeigen weiterhin die allgemeine Übersicht.
- Tests: `tests/test_ai_cli_access.py` (8 Tests, ohne echten CLI-Start). Keine Datenbankänderung.
