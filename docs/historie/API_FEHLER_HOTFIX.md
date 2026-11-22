# MPW v2.2.0 RC1 – API-Fehler Hotfix

Basis: MPW_v2.2.0_RC1_MCP_Hotfix (enthält auch Prompt-Laden- und CLI-Zugang-Hotfix). Keine Datenbankmigration erforderlich.

## AI Prompt Launcher – verständliche API-Fehlermeldungen
Fehler bei „Prompt erstellen (API)“ werden nach Ursache erkannt und in der eingestellten Sprache (DE/EN/FR/ES/IT) gemeldet, ergänzt um die Meldung des Anbieters:
- HTTP 401/403 Schlüssel abgelehnt · 404 Modell unbekannt · 402/429 Limit oder Guthaben · 400/422 ungültige Anfrage · 5xx Anbieter gestört
- keine Verbindung, Zeitüberschreitung (90 s), blockierte/verweigerte, abgeschnittene, leere oder unerwartete Antworten
- Abgeschnittene Antworten (Längenlimit) werden nicht in die Editoren übernommen.
- Ein im Fehlertext enthaltener API-Schlüssel wird durch *** ersetzt; jeder Fehler wird im Fehlerprotokoll vermerkt.
- Fehlerhaftes Hardware-Preset: normale Fehlermeldung statt Programmfehler, Schlüsselfeld wird geleert.

## Datenbankstart
`init_database` schließt die Verbindung, wenn die Schema-Initialisierung fehlschlägt. Unter Windows blieb `workstation.db` sonst gesperrt und der eigentliche Fehler wurde verdeckt.

## Prüfskripte und Tests
- `scripts/audit-workflows.py` lädt `mpw_genre_upgrade` selbst aus `source/` (lief vorher nur mit gesetztem PYTHONPATH).
- Tests unter Windows lauffähig: SQLite-Verbindungen werden geschlossen; Symlink-Test weicht ohne Symlink-Recht auf eine Directory Junction aus.
- 8 Testdateien ohne `unittest.main()` ergänzt (liefen einzeln gestartet bisher leer).
- Neue Tests: `test_ai_api_errors.py`, `test_init_database_no_leak.py`.

Alle Tests ausführen: `py -3 -I -m unittest discover -s tests -p "test_*.py"` (144 Tests).
Selbsttest ohne `-I` starten: `py -3 source\workstation.py --self-test`.

## Grenzen
Nicht mit echten API-Schlüsseln und nicht in der laufenden Windows-Oberfläche getestet; Anbieterantworten im Test sind nachgestellt. Kein Windows-EXE-Build erstellt.
