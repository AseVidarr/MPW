# MPW v2.2.0 RC1 – Kernlogik ohne Qt (Schritt 1 für Mac/Linux)

Basis: MPW_v2.2.0_RC1_Web_Stufe1_Hotfix. Keine Datenbankmigration, keine Funktionsänderung für Anwender.

- Neues Modul `source/mpw_core.py`: alle Qt-freien Teile aus `workstation.py` (Datenpfad, Schema, Speichern, Backup, KI-/CLI-/Suno-Aufrufe, MCP-Einrichtung, Prompt-TXT-Archiv). `workstation.py` importiert den Kern; Desktop-Verhalten unverändert.
- `mpw_web.py` und `mpw_mcp_server.py` nutzen nur noch den Kern und laufen **ohne PySide6** (geprüft mit gesperrtem PySide6: beide Selbsttests bestanden, kein Qt-Modul geladen).
- Ordnersymbol aus Cover (Windows/Qt) über einen Haken (`COVER_ICON_HOOK`), den die Desktop-App setzt.
- Kleine Korrektur: HTTP-Fehlerantworten der KI-Anbieter werden nach dem Lesen geschlossen.
- Tests und Prüfskripte (`audit-workflows.py`, `release-preflight.py`) auf den Kern umgestellt.

Offen (nächste Schritte): Plattformneutralität (Portable-Erkennung Mac/Linux, Registry, CLI-Pfade), GitHub Actions, Webanwendung ausbauen.
