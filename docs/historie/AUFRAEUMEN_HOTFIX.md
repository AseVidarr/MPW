# Aufräumen-Hotfix (MPW 2.2.0 RC2)

Basis: MPW 2.2.0 RC2 (Stand nach `MPW_v2.2.0_RC2_Release_Vorbereitung_Hotfix.zip`).

## Änderungen

- Alle Änderungsnotizen der bisherigen Versionen und Hotfixes (`ALPHA*`, `FIX*_ANLEITUNG.txt`,
  `*_HOTFIX.md`, `WEB_STUFE*` usw., 132 Dateien) aus dem Hauptordner nach `docs/historie/` verschoben.
  Inhalt unverändert; per `git mv`, die Historie bleibt also erhalten.
- `audit_translations.py` nach `scripts/` verschoben, Pfad zu `source/workstation.py` angepasst.
- `README.md`: Hinweis auf `docs/historie/` ergänzt.
- Im Hauptordner bleiben nur noch `README.md`, `RELEASE_NOTES.md`, `build.ps1`, `BUILD_STARTEN.cmd`
  und die Git-Dateien. Dadurch zeigt die GitHub-Startseite direkt das README.

## Grenzen

- Am Programm selbst hat sich nichts geändert. Kein Code, Test, Build-Skript oder Workflow hat
  diese Notizen gelesen; `RELEASE_NOTES.md` (für den GitHub-Release) bleibt im Hauptordner.
- Künftige Hotfix-Notizen gehören nach `docs/historie/`.
