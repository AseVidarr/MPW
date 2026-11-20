MPW v2.2.0 Alpha 8 – Dropdown-Übersetzungen
26 statische Dropdown-Optionen in sechs auditierten Comboboxen.
Sprachwechsel sofort, keine Änderungen an SQLite, Statuswerten oder Songdaten.
Die interne Logik nutzt in diesen Comboboxen Indizes bzw. itemData.
Andere Dropdowns (insbesondere Status und Genres) bleiben bewusst unverändert,
solange sie intern über currentText() ausgewertet werden.
Prüfung: Python-Syntax und ZIP-Integrität; Windows-GUI-Test noch ausstehend.
Build: powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
