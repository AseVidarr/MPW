# MPW v2.2.0 RC1 – Hardware-Auswahl Hotfix

Basis: MPW_v2.2.0_RC1_Claude_Modell_Hotfix. Keine Datenbankmigration erforderlich.

## Reiter Bands – Abschnitt „Instrumente / Hardware“
Die Felder **Gruppe** und **Instrumente / Hardware** sind jetzt editierbare Auswahlmenüs (wie Hauptgenre/Zweitgenre):
- Gespeicherten Eintrag auswählen oder wie bisher einen neuen Text eintippen.
- **Gruppe** listet alle gespeicherten Gruppen aller Bands und aller Hardware-Presets, alphabetisch, ohne Doppelungen (Groß-/Kleinschreibung und Leerzeichen am Rand werden ignoriert).
- **Instrumente / Hardware** listet die gespeicherten Einträge der gewählten Gruppe. Bei neuer oder leerer Gruppe erscheinen alle gespeicherten Einträge.
- Die Menüs aktualisieren sich nach Hinzufügen, Speichern, Löschen und Preset-Anwenden. Neue Einträge erscheinen erst nach „Instrument hinzufügen“ im Menü.
- „Ausgewählte Hardware löschen“ leert nur die Eingabe; die Menüeinträge bleiben, solange der Wert noch irgendwo gespeichert ist.
- Ein beschädigtes Hardware-Preset wird beim Füllen der Menüs übersprungen.

Gespeicherte Daten werden nur gelesen, nicht verändert.

## Tests
- Neu: `tests/test_hardware_menus.py` (Datenquelle, Doppelungen, Gruppenfilter, nur lesend, Qt-Menüverhalten).
- 151 Tests und Selbsttest bestanden.
- Zusätzlich das echte Hauptfenster unsichtbar mit Temp-Datenbank durchgespielt: auswählen, neu eintippen, hinzufügen, laden, ändern, löschen.

## Grenzen
Nicht sichtbar in der Windows-Oberfläche angesehen. Kein Windows-EXE-Build erstellt.
