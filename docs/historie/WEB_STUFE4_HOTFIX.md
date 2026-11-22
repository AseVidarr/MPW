# Web-Anwendung Stufe 4 – AI Prompt Launcher im Browser

## Neuer Reiter „AI Prompt Launcher“ (Browser)

- **Ziel**: Band → Ziel-Song / Projekt. Projekte ohne Song-Eintrag sind markiert;
  „Song-Eintrag anlegen“ legt ihn nach Rückfrage an (keine Dateien werden verändert).
- **KI-Plattform** ChatGPT / Gemini / Claude, **Hardware** aus dem Bandprofil oder einem Preset,
  **Songidee / Anweisung**.
- **Prompt erstellen (API)**: Modell wie in der Desktop-App vorbelegt. Der API-Schlüssel kann
  eingegeben werden oder kommt aus der Umgebungsvariable (`OPENAI_API_KEY`, `GEMINI_API_KEY`,
  `ANTHROPIC_API_KEY`); die Oberfläche zeigt nur, *ob* dort einer gefunden wurde.
  Der eingegebene Schlüssel gilt nur für diese eine Anfrage, wird nicht gespeichert, nicht
  protokolliert und nie zurückgegeben; das Eingabefeld wird sofort geleert.
- **Prompt erstellen (CLI)**: über Claude Code, Gemini CLI oder Codex CLI mit deren eigener
  Anmeldung (kein API-Schlüssel), „CLI prüfen“ zeigt den gefundenen Pfad.
  Die Anfrage läuft im Hintergrund (API bis 3 Min., CLI bis 5 Min.); die Seite zeigt die Laufzeit.
  Es läuft immer nur eine KI-Anfrage gleichzeitig.
- **Anfrage kopieren & Plattform öffnen**: kopiert die Anfrage (mit STYLE-/LYRICS-Copy-Boxen)
  in die Zwischenablage und öffnet ChatGPT, Gemini bzw. Claude in einem neuen Tab.
- **Antwort übernehmen**: aus einer Datei (TXT/MD/JSON, max. 2 MB) oder per Einfügen;
  JSON und `[STYLE]`/`[LYRICS]` werden erkannt.
- **Als neue Version speichern**: legt eine Prompt-Version an und archiviert sie als Textdatei
  im Ordner „Song-Prompts“ der Band. Der aktive Song-Prompt bleibt unverändert
  (übernommen wird er wie gewohnt im Reiter „Songs & Suno“).
- Rechts: gespeicherte Versionen des Ziel-Songs ansehen und in Style/Lyrics laden.
- Fehlermeldungen der Anbieter und CLIs sind dieselben wie in der Desktop-App (5 Sprachen).
- Vor dem Schließen der Seite warnt der Browser, wenn ein KI-Ergebnis noch nicht gespeichert ist.

Noch nicht im Browser (weiter in der Desktop-App): Versionen vergleichen, Version ins Projekt
exportieren, Prompt über Weblink importieren.

## Technik

- Kern (`source/mpw_core.py`): `AI_PROVIDERS`, `AI_DEFAULT_MODELS`, `AI_PLATFORM_URLS`,
  `ai_cli_prompt`, `ai_browser_prompt`, `project_song_id`, `ensure_project_song`,
  `save_prompt_version` und die Fehlertexte `AI_ERROR_TEXTS` – die Desktop-App nutzt
  dieselben Konstanten, Texte und Prompt-Bausteine (vorher doppelt im Desktop-Code).
- Web (`source/mpw_web.py`): `GET /api/ai/options`, `GET /api/ai/targets`,
  `POST /api/projects/<id>/song` (nur mit `confirm: true`), `POST /api/ai/generate`,
  `GET /api/ai/jobs/<id>`, `POST /api/ai/check-cli`, `POST /api/ai/request-text`,
  `POST /api/ai/parse`, `POST /api/songs/<id>/prompt-versions`.

## Geprüft

- 226 Unit-Tests (mit `-W error::ResourceWarning`), u. a. API-Anfrage mit Attrappe statt echter KI
  (kein Netz, keine Kosten), Schlüssel taucht nie in Antworten auf, nur eine Anfrage gleichzeitig,
  CLI fehlt / unsicherer CLI-Befehl, Speichern mit und ohne Band-Ordner.
- Einzelskripte, alle Audit-Skripte, Selbsttests von Desktop, MCP-Server und Web-Server, Kern ohne Qt.
- Browser-Durchlauf mit Beispieldaten und KI-Attrappe: fehlender Schlüssel, Anfrage mit Laufzeitanzeige,
  Antwort, Speichern samt Textdatei, abgelehnter Schlüssel, Anfrage kopieren, Antwort einfügen,
  Version laden, Song-Eintrag anlegen, CLI prüfen – ohne Fehler. Eine echte KI wurde nicht aufgerufen.
