# Alpha 21 Preview 29 – Änderungen

- Kritischen Klasseninitialisierungsfehler in `RELEASE_EDIT_DE` korrigiert: zwei irrtümliche `self.release_edit_text(...)`-Aufrufe durch statische deutsche Texte ersetzt.
- ISRC-Duplikatdialog verwendet nun `release_edit_text(4)` statt eines fest eingebauten deutschen Satzes.
- Plattformstatus in der Release-Liste für EN/FR/ES/IT lokalisiert; unbekannte Statuswerte bleiben unverändert.
- Gespeicherte Statuswerte und SQL-Schema unverändert.

Prüfung: Python-Kompilierung und AST-Parsing bestanden; ZIP-CRC-Prüfung bestanden. Kein Windows-GUI-Test durchgeführt.
