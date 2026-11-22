# Preview 51 – Hotfix 1: Portable-ZIP-Prüfung

Fehler: Nach erfolgreichem PyInstaller-Build meldete die ZIP-Prüfung fälschlich, dass `App/MPW.exe` fehle.

Korrektur: ZIP-Eintragsnamen werden vor dem Pfadvergleich von Windows-Backslashes auf Schrägstriche normalisiert. Die Prüfung auf `App/MPW.exe` und `Start-MPW-Portable.cmd` bleibt aktiv.

Wenn der vorherige Build bereits ein `dist/MPW_Portable_v2.2.0_Alpha21_Preview51` und die gleichnamige ZIP erzeugt hat, diese *generierten* Dateien vor einem erneuten Build umbenennen oder nach Sicherung löschen. **Den Ordner `Data` einer bestehenden produktiven Portable-Version niemals löschen.**

Dieser Hotfix enthält Quellcode, keine fertig kompilierte Windows-EXE.
