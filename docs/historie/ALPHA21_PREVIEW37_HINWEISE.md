# MPW Alpha 21 – Preview 37

Automatisierte, Qt-unabhängige Sprachwechsel-Vertragstests ergänzt (`tests/test_language_switch_contract_p37.py`).

- Prüft Sprachabdeckung und gleiche Eintragszahlen der Konfigurations-, Erscheinungsbild- und Hintergrundbild-Übersetzungstabellen.
- Simuliert sieben aufeinanderfolgende Sprachwechsel für Plattformstatus DE/EN/FR/ES/IT/FR/DE; kontrolliert sichtbare Texte, unveränderte kanonische Statuswerte, beibehaltenen Auswahlindex und wieder aktivierte Signale.
- Prüft die Einbindung der Aktualisierungsfunktionen in `refresh_language_controls`.
- Reine statische und isolierte Logiktests; kein tatsächlicher GUI-/Windows-Lauf und keine Benutzerdaten geöffnet.

Ausführen: `python -m unittest discover -s tests -p test_language_switch_contract_p37.py -v`.
