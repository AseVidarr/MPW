# Web-Anwendung Stufe 5 – An Suno senden im Browser

## Neu im Reiter „Songs & Suno“ (Browser)

- Knopf **„An Suno senden (MCP) …“** im Song-Editor öffnet denselben Dialog wie in der Desktop-App:
  - Auswahl: **aktiver Song-Prompt (gespeichert)** oder eine **gespeicherte Prompt-Version**,
    Songtitel bei Suno, Vorschau von Style und Lyrics mit Zeichenzahl.
  - Hinweis, wenn im Editor ungespeicherte Änderungen sind – gesendet wird immer der
    **gespeicherte** Stand. Der Server liest den Prompt dafür selbst aus der Datenbank;
    Text aus dem Browser wird nie an Suno geschickt.
  - **Senden erst nach Rückfrage** (Suno erstellt 2 Songs und verbraucht Credits).
  - Versand über Claude Code nur mit Sunos MCP-Server und nur `audio-create` / `audio-wait`
    (wie Desktop), mit Auftragsschlüssel gegen doppelte Abrechnung.
  - Ergebnis mit Laufzeitanzeige, Song-Links (öffnen im neuen Tab) und denselben Hinweisen wie
    in der Desktop-App (nicht verbunden, Prompt verändert übertragen, mehrfach aufgerufen,
    Credits fehlen, Zeitüberschreitung, Claude nicht angemeldet …).
  - **„Links beim Song speichern“** legt die Links unter Medien & Player ab; vorhandene Links
    bleiben, doppelte werden nicht angelegt. Gespeichert werden nur Links, die Suno diesem
    Server zurückgegeben hat, und nur echte `https://…suno.com/…`-Adressen.
- Es läuft immer nur eine KI- bzw. Suno-Anfrage gleichzeitig.

## Technik

- Kern (`source/mpw_core.py`): `SUNO_SEND_TEXTS` (5 Sprachen), `suno_prompt_choices`,
  `suno_send_problem`, `suno_send_outcome`, `save_suno_links` – die Desktop-App nutzt jetzt
  dieselben Texte und Regeln (vorher nur im Desktop-Code).
- Web (`source/mpw_web.py`): `GET /api/songs/<id>/suno`, `POST /api/songs/<id>/suno/send`
  (nur mit `confirm: true`), `POST /api/songs/<id>/suno/links`; Ergebnis über `GET /api/ai/jobs/<id>`.

## Geprüft

- 230 Unit-Tests (mit `-W error::ResourceWarning`), u. a.: ohne Bestätigung wird nichts gesendet,
  gesendet wird der gespeicherte Prompt (nicht Browser-Text), fremde Links werden verworfen,
  Links nur aus dem eigenen Auftrag und nur einmal, Fehlerfälle. Kein echter Aufruf von Claude
  Code oder Suno (keine Credits).
- Einzelskripte, alle Audit-Skripte, Selbsttests von Desktop, MCP-Server und Web-Server, Kern ohne Qt,
  Rauchtest des Desktop-Dialogs „An Suno senden“ (alle Fälle unverändert).
- Browser-Durchlauf mit Beispieldaten und Suno-Attrappe: Dialog, Versionswahl, Hinweis auf
  ungespeicherte Änderungen, Abbrechen bei der Rückfrage, Senden, Links öffnen/speichern – ohne Fehler.
