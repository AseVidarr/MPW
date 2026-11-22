# MPW v2.2.0 Alpha 21 Preview 48

Schwerpunkt: reproduzierbare statische Startprüfung der Initialisierungsreihenfolge.

- Neues `scripts/audit-startup.py`: untersucht die Konstruktor-Reihenfolge und bekannte kritische UI-Dictionaries, ohne PySide6 zu importieren oder Benutzerdaten zu öffnen.
- Drei neue Regressionstests, einschließlich eines simulierten Zugriffs vor Initialisierung.
- Versionskennung auf Preview 48 gesetzt.

**Grenze:** Eine statische Prüfung ersetzt keinen echten Windows-GUI-Start und kann dynamische Zugriffe nicht vollständig abdecken.
