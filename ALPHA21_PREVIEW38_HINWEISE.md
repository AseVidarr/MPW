# MPW Alpha 21 – Preview 38

## Neue automatisierte Prüfungen
- `tests/test_language_tab_coverage_p38.py`: fünf zusätzliche statische Vertragstests für alle 14 Reiter, vollständige Reitertitel in EN/FR/ES/IT, identische Schlüssel und Platzhalter in den zentralen Übersetzungswörterbüchern, stabile ursprüngliche Reiter-IDs und keine direkten Datenbankschreiboperationen in `refresh_language_controls`.
- Deutsch ist in diesen zentralen Wörterbüchern bewusst die unveränderte Originalsprache und benötigt keinen eigenen Übersetzungseintrag.
- `tests/WINDOWS_SPRACHWECHSEL_MATRIX_P38.csv`: 70 offene manuelle Testfälle (14 Reiter × 5 Sprachen), mit Spalten für Ergebnis und Notizen.

## Tests
- `python -m unittest discover -s tests -p 'test_language*py' -v`: 8/8 bestanden (Preview 37 + Preview 38).
- `python -m py_compile source/workstation.py`: bestanden.
- ZIP-Integrität: bestanden.
- Keine Windows-/Qt-GUI-Abnahme durchgeführt. Die Testmatrix ist **nicht** als bestanden markiert.
- Produktive Daten wurden nicht geöffnet.

## Nächster Schritt
Testmatrix auf Windows mit Testdaten abarbeiten, insbesondere offene Dialoge, Combo-Auswahlwerte und Rückwechsel zu Deutsch. Anschließend verbleibende Abweichungen korrigieren.
