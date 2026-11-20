# MPW v2.2.0 RC1 – Suno-Senden Hotfix

Basis: MPW_v2.2.0_RC1_KI_Verbindungen_Hotfix. Keine Datenbankmigration erforderlich.

## Reiter Songs & Suno – „An Suno senden (MCP) …“
Neuer Knopf in einer eigenen Zeile unter den vier Song-Aktionen. Er öffnet ein Fenster:
- **Gespeicherter Prompt:** der gespeicherte aktive Song-Prompt oder eine gespeicherte Prompt-Version (neueste zuerst), mit Vorschau von Style und Lyrics samt Zeichenzahl.
- **Songtitel bei Suno:** vorbelegt mit dem Songtitel, änderbar.
- Ungespeicherte Änderungen im Editor werden **nicht** gesendet; ein Hinweis erscheint.
- **An Suno senden …** fragt vorher nach (Suno erstellt 2 Songs und verbraucht Credits) und läuft im Hintergrund.
- Ergebnis mit anklickbaren Song-Links; **Links beim Song speichern** legt sie unter Medien & Player ab (Plattform „Suno“, keine Doppelten).

## Technik
- Übertragung über Claude Code und Sunos offiziellen MCP-Server (`https://api.suno.com/mcp`), Werkzeug `audio-create` im Custom-Modus (`title`, `style`, `lyrics`), danach `audio-wait`.
- Claude Code läuft in einem leeren Temp-Ordner mit `--strict-mcp-config`, nur mit dem Suno-Server und nur mit den Werkzeugen `audio-create` und `audio-wait` erlaubt; die Anmeldungen bei Claude und Suno sind die des Anwenders.
- Jeder Auftrag hat einen eindeutigen `idempotency_key`: wiederholte Aufrufe werden von Suno nicht doppelt berechnet.
- MPW liest die tatsächlich gesendeten Werte und Sunos Antworten aus dem Datenstrom von Claude Code (`stream-json`) und meldet, wenn Claude den Prompt verändert oder mehrfach gesendet hat.
- Verständliche Meldungen für: Suno nicht verbunden/angemeldet, Claude nicht angemeldet, fehlende Credits und andere Suno-Fehler, Zeitüberschreitung (10 Minuten), leere Lyrics, überschrittene Grenzen.
- Texte, Rückfragen, Meldungen und Hilfeeintrag in DE/EN/FR/ES/IT.

## Tests
- Neu: `tests/test_suno_send.py` (Argumente, Datenstrom-Auswertung, Abgleich, CLI-Aufruf mit nur Suno und zwei Werkzeugen, Zeitüberschreitung, Texte, Thread-sichere Rückgabe).
- 180 Tests, GUI- und MCP-Selbsttest, Start- und Workflow-Prüfung bestanden.
- Echtes Hauptfenster unsichtbar durchgespielt (Suno-Aufruf nachgestellt, keine Credits verbraucht): Prompt-Auswahl, Hinweis auf ungespeicherte Änderungen, Senden, Ergebnis, Links speichern, Fehlerfälle, Sprachwechsel.
- Vorab mit dem echten Suno-Server geprüft (nur `account-usage`, ohne Credits): Verbindung aus dem Temp-Ordner mit vorhandener Anmeldung funktioniert.

## Grenzen
- Ein echter Sendevorgang (der Credits verbraucht) wurde nicht ausgeführt; bitte einmal selbst testen.
- Claude ist als Vermittler beteiligt; Abweichungen werden erkannt und gemeldet, aber erst nach dem Senden.
- Kein Windows-EXE-Build erstellt.
