# Preview 47 Hotfix 1 – Startfehler im Backup-Reiter

**Fehler:** `AttributeError: 'Workstation' object has no attribute 'appearance_text_p35'` beim Aufbau von `build_backup()`.

**Ursache:** Der Backup-Reiter wurde vor der Konfigurations-/Erscheinungsbild-Oberfläche erstellt. Eine fälschlich eingefügte Registrierung des Backup-Hinweises unter `appearance_text_p35['background_note']` griff auf ein noch nicht vorhandenes Dictionary zu und vermischte außerdem zwei inhaltlich unterschiedliche Hinweise.

**Änderung:** Entfernen dieser Registrierung. Der Backup-Hinweis bleibt als `QLabel` im Backup-Reiter erhalten; die PNG-Hintergrundbeschreibung wird wie bisher separat im Erscheinungsbild-Reiter verwaltet.

**Tests:** Drei zusätzliche statische Regressionstests für Reihenfolge, Initialisierung und Vermeidung des verfrühten Zugriffs. Tests unter Linux ersetzen keinen realen Windows-GUI-Start.

**Installation:** In neuen Ordner entpacken und `source/workstation.py` wie bisher starten. Bestehende produktive Daten vor Tests sichern.
