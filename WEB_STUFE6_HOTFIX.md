# Web-Anwendung Stufe 6 – KI-Verbindungen im Browser

## Neuer Reiter „KI-Verbindungen“ (Browser)

Dieselben Abschnitte, Texte (5 Sprachen) und Statusregeln wie im Desktop-Fenster
Konfiguration › KI-Verbindungen:

- **Claude Code**: installiert? angemeldet? – Installationsanleitung, „Anmelden …“.
- **Gemini CLI / Codex CLI / Node.js**: installiert? – Anleitungen bzw. Download.
- **API-Schlüssel**: nur *ob* `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY` gesetzt sind
  (Schlüssel werden nie angezeigt) – Links zu den Schlüssel-Seiten.
- **MPW-Daten für KI freigeben (MCP, nur lesend)** und **Suno**: Status je KI-CLI,
  „Einrichten für:“ Claude Code / Gemini CLI / Codex CLI, Verbinden/Trennen, Suno eintragen/
  entfernen – **jeweils erst nach Rückfrage** (der Server verlangt die Bestätigung zusätzlich).
  „Für Claude Desktop kopieren“ legt die Einrichtung in die Zwischenablage.
- **Bei Suno anmelden … / Anmelden …**: unter Windows öffnet sich wie in der Desktop-App ein
  eigenes Fenster; unter macOS/Linux zeigt die Seite den Befehl für das Terminal an.
- **Netzwerk**: erkennt, ob ein Virenscanner (z. B. Norton) die verschlüsselten Verbindungen zu
  api.anthropic.com / api.suno.com untersucht, mit Hinweis zur Ausnahme.
- Die Prüfung läuft im Hintergrund („… wird geprüft“) und blockiert keine Prompt-Erstellung;
  „Erneut prüfen“ startet sie neu.

## Technik

- Kern (`source/mpw_core.py`): `AI_CONNECTION_TEXTS` sowie `ai_connection_status` /
  `render_ai_connection_line` – die Desktop-App nutzt jetzt dieselben Texte und Statusregeln.
- Web (`source/mpw_web.py`): `GET /api/connections`, `POST /api/connections/check`,
  `GET /api/connections/jobs/<id>`, `POST /api/connections/setup` (nur mit `confirm: true`,
  nur feste Befehle für die drei bekannten CLIs), `POST /api/connections/login`,
  `GET /api/connections/desktop-config`.

## Geprüft

- 233 Unit-Tests (mit `-W error::ResourceWarning`), u. a.: ohne Bestätigung wird nichts geändert,
  nur feste Befehle, unbekannte CLI abgewiesen, fehlender MPW-MCP-Server gemeldet, Anmeldung
  Windows (eigenes Fenster) und macOS/Linux (Befehl anzeigen). Alle Systembefehle in den Tests ersetzt.
- Einzelskripte, alle Audit-Skripte, Selbsttests von Desktop, MCP-Server und Web-Server, Kern ohne Qt,
  Rauchtest des Desktop-Fensters KI-Verbindungen (alle drei KI-CLIs, unverändert).
- Browser-Durchlauf: echte (nur lesende) Statusprüfung, Links, Rückfrage mit „Nein“ (nichts geändert),
  Claude-Desktop-Einrichtung kopieren – ohne Fehler. Es wurde nichts an der KI-Einrichtung verändert
  und keine Anmeldung gestartet.
