# MPW v2.2.0 – Alpha 21 Preview 40

Basis: Preview 39. Neu: `tests/test_language_persistence_p40.py` mit fünf isolierten Tests der tatsächlichen Konfigurationsmethoden aus `source/workstation.py`.

- Rundlauf für Deutsch, Englisch, Französisch, Spanisch, Italienisch und Automatik mit erneutem Lesen der JSON-Konfiguration.
- Fehlende, beschädigte und nicht-objektförmige JSON-Konfigurationen sowie ungültige Sprachcodes.
- Sprachwechsel über `change_ui_language`: gültige Werte werden gespeichert und aktualisiert, ungültige ignoriert.
- Erhalt anderer Einstellungen, einschließlich Startreiter, Hintergrundskalierung und Unicode-Zeichen.
- Statische Kontrolle, dass die Konfigurationsmethoden keine Musikdatenbank ansprechen.

Alle Tests arbeiten ausschließlich in temporären Verzeichnissen. Die Windows-GUI-Abnahme bleibt offen. Die bisherigen Tests sind unverändert enthalten.
