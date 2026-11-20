# MPW Alpha 21 Preview 51 – Release-Vorbereitung

- Version auf Preview 51 aktualisiert.
- Veraltete Preview-47-Ausgabenamen in `scripts/build.ps1` und `installer/MPW.iss` auf Preview 51 geändert.
- Lesendes Release-Preflight-Skript hinzugefügt (`python scripts/release-preflight.py`).
- Drei Regressionstests für Release-Preflight und konsistente Paketnamen ergänzt.
- Datenbank, Medien und bestehende Installationen werden durch diese Prüfung nicht geöffnet oder verändert.
- Ein Windows-Installer oder eine portable EXE wurde **nicht** gebaut. Windows-GUI-, Installer- und Upgrade-Tests stehen aus.
