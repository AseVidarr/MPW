# MPW v2.2.0 RC1 – Preset-Zielband Hotfix

Basis: MPW_v2.2.0_RC1_Hardware_Auswahl_Hotfix. Keine Datenbankmigration erforderlich.

## Reiter Bands – Hardware-Preset-Bibliothek
Ein gespeichertes Preset lässt sich jetzt gezielt für eine andere Band übernehmen:
- Neues Auswahlmenü **Zielband**: Es folgt der oben unter „Instrumente / Hardware“ gewählten Band und kann für eine andere Band geändert werden.
- Neuer Knopf **Preset zur Band hinzufügen**: Er ergänzt bei der Zielband nur die Einträge, die noch fehlen. Vorhandene Hardware bleibt erhalten; doppelte Einträge (gleiche Gruppe und Hardware, unabhängig von Groß-/Kleinschreibung) werden übersprungen. Vorher erscheint eine Rückfrage mit der Anzahl neuer und übersprungener Einträge.
- **Preset auf Band anwenden** ersetzt wie bisher nach Bestätigung die gesamte Hardware, jetzt aber bei der Zielband.
- Nach dem Übertragen zeigt die Hardware-Liste oben die Zielband.
- Texte, Rückfragen, Meldungen und die integrierte Hilfe sind in DE/EN/FR/ES/IT verfügbar.

## Tests
- `tests/test_hardware_menus.py` erweitert (fehlende Einträge, keine Doppelungen, Verdrahtung, Übersetzungen).
- 154 Tests, Selbsttest, Start- und Workflow-Prüfung bestanden.
- Echtes Hauptfenster unsichtbar mit Temp-Datenbank durchgespielt: Zielband folgt/abweichend, Hinzufügen, erneutes Hinzufügen ohne Doppelungen, Ersetzen bei anderer Band (Quellband unverändert), englische Oberfläche.
- Hinweis: `scripts/audit-guide-translations.py` meldet die Bands-Hilfeeinträge als fehlend, weil es nicht alle Übersetzungstabellen auswertet; das galt schon vorher. Die Anzeige in der Hilfe wurde direkt geprüft und ist vollständig.

## Grenzen
Nicht sichtbar in der Windows-Oberfläche angesehen. Kein Windows-EXE-Build erstellt.
