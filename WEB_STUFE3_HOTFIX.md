# Web-Anwendung Stufe 3 – Bands im Browser anlegen

## Neu im Reiter „Bands“ (Browser)

- Knopf **„+ Neue Band“** über der Bandliste öffnet das Formular
  Bandname, Hauptgenre, Zweitgenre (Auswahl aus dem Genre-Katalog) und Persona.
- **„Band anlegen“** arbeitet nach denselben Regeln wie die Desktop-App:
  - Der Name muss als Ordnername gültig sein (keine Zeichen wie `< > : " / \ | ? *`,
    kein Punkt/Leerzeichen am Ende, keine reservierten Namen wie `CON`).
  - Gibt es die Band schon (Groß-/Kleinschreibung egal), wird sie ausgewählt –
    es wird nichts doppelt angelegt.
  - Der Band-Ordner wird im Band-Verzeichnis angelegt, dazu der feste Prompt-Ordner.
    Projekt-Unterordner entstehen erst beim Anlegen eines Projekts.
  - Gibt es schon einen **Ordner** dieses Namens, aber keine Band, wird nach Rückfrage
    der vorhandene Ordner übernommen – Dateien und Ordner darin bleiben unverändert.
    Die Band bekommt dabei die Schreibweise des Ordners.
  - Schlägt der Datenbank-Eintrag fehl, wird nur der gerade erzeugte leere Ordner entfernt.
- Die neue Band erscheint sofort in der Bandliste und im Band-Filter von „Songs & Suno“.
- Alle Texte in DE / EN / FR / ES / IT.

## Technik

- `source/mpw_core.py`: `create_band(...)` und `validate_folder_name(...)`
  (die Desktop-App nutzt jetzt dieselbe Namensprüfung).
- `source/mpw_web.py`: `POST /api/bands` (`name`, `genre`, `second_genre`, `persona`,
  `import_existing`) und `GET /api/band-options` (Genre-Katalog, Personas).
  Antworten: 409 `band_exists` / `folder_exists`, 400 `invalid_name` / `empty_field` /
  `too_long` / `invalid_persona`, 500 `folder_error`.

## Geprüft

- 220 Unit-Tests (mit `-W error::ResourceWarning`), Einzelskripte, alle Audit-Skripte,
  Selbsttests von Desktop, MCP-Server und Web-Server, Kern ohne Qt.
- Browser-Durchlauf mit Beispieldaten: leerer und ungültiger Name, neue Band
  (Doppelklick legt nur eine an), vorhandene Band, vorhandenen Ordner übernehmen,
  Abbrechen – ohne Fehler.
