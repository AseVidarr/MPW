# MPW v2.2.0 Alpha 21 Preview 49

Schwerpunkt: isolierte Funktionsabnahme der Datenbank-Arbeitsabläufe.

- Neues `scripts/audit-workflows.py`: verwendet die tatsächliche `init_database`-Funktion aus `source/workstation.py`, ohne die PySide6-Oberfläche zu importieren oder produktive Daten zu öffnen.
- Acht Prüfpunkte: Schema und Fremdschlüssel, Band/Projekt/Song, Prompt-Versionshistorie, verwaiste Referenzen, Transaktions-Rollback, Löschkaskade, SQLite-Integrität und temporäre Testdaten.
- Vier neue Regressionstests in `tests/test_workflow_acceptance_p49.py`.
- Versionskennung auf Preview 49 aktualisiert.

**Grenzen:** Der Workflow-Test führt SQL-Operationen auf einer isolierten Datenbank aus; er klickt nicht die echten PySide6-Dialoge. Windows-GUI-Start, Installer und Backup-Wiederherstellung müssen gesondert unter Windows abgenommen werden. Produktive Daten werden nicht geöffnet.
