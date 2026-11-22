# MPW v2.2.0 – Alpha 21 Preview 39

Basis: Preview 38. Neu: `tests/test_open_dialog_language_p39.py` mit vier isolierten Regressionstests für bereits geöffnete Dialoge.

- Erscheinungsbild: sieben Sprachwechsel, Textaktualisierung, unveränderte Skalierungskennungen `cover`/`contain`/`stretch` und erhaltene Auswahl.
- Konfiguration: Wechsel durch alle fünf Sprachen und zurück; unveränderte Startreiter-Auswahl und Datenkennungen.
- PNG-Hintergrundmeldungen: Vollständigkeit und identische Formatierungsplatzhalter.
- AST-Schutz: Übersetzungsaktualisierung überschreibt keine Benutzereingaben und schreibt keine Einstellungen/Datenbank.

Die Tests verwenden kleine Qt-Testdoubles und erfordern kein installiertes PySide6. Sie ersetzen keine Windows-GUI-Abnahme. Bestehende produktive MPW-Daten wurden nicht geöffnet.
