# MPW v2.2.0 RC1 – MPW im Browser, Stufe 1

Basis: MPW_v2.2.0_RC1_MCP_Drei_KI_Hotfix. Keine Datenbankmigration erforderlich.

## Neu: MPW im Browser (lokal)
`MPW-Web.exe` (Quellcode: `py -3 source\mpw_web.py`) startet einen kleinen Server **nur auf diesem PC** und öffnet die Oberfläche im Standardbrowser. Es werden **dieselben Daten** verwendet wie von der installierten bzw. portablen MPW (gleiche Datenpfad-Ermittlung wie MPW.exe und MPW-MCP.exe). Desktop-App und Browser dürfen gleichzeitig offen sein.

Stufe 1 enthält:
- **Songs & Suno:** Bandfilter, Suche, Songliste; Editor für Status, Distributor, Plattformen, Style und Lyrics mit Zeichenzählern; „Song speichern“ mit automatischer Sicherungsversion (wie in der Desktop-App); „Änderungen verwerfen“; gespeicherte Prompt-Versionen ansehen und in den Editor übernehmen.
- **Bands:** Profil, Genres, Persona, Instrumente/Hardware und Song/Projekte ansehen (nur lesend); Klick auf einen Song öffnet ihn im Editor.
- Sprache aus MPW › Konfiguration (DE/EN/FR/ES/IT), bei „Automatisch“ die Browsersprache.
- **Konfliktschutz:** Wurde der Song inzwischen anderswo (z. B. in der Desktop-App) geändert, speichert der Browser nicht, sondern meldet den Konflikt; die Eingabe bleibt im Editor.

## Sicherheit
- Server nur auf 127.0.0.1, pro Start ein Zufallsschlüssel (im URL-Fragment, nicht in Logs/Referer), ohne den die Daten-Schnittstelle nichts liefert.
- Fremde Host-Namen werden abgewiesen (Schutz gegen DNS-Rebinding), keine CORS-Freigaben, strenge Content-Security-Policy, nur feste Dateien auslieferbar.
- Alle Inhalte werden im Browser als Text gesetzt (kein HTML aus Songtexten).
- Nur Python-Standardbibliothek, keine zusätzlichen Pakete.

## Gemeinsame Logik
„Song speichern“ nutzt in Desktop-App und Browser dieselbe Funktion `save_song_record` (Sicherungsversion und Speichern in einer Transaktion).

## Build und Installation
- `installer/MPW.spec` baut zusätzlich `MPW-Web.exe` (inkl. Ordner `web`); `scripts/build.ps1` führt den Web-Selbsttest für Quellcode und EXE aus.
- Installer: Startmenü-Eintrag „MPW im Browser“.
- Portable: `Start-MPW-Web-Portable.cmd` (nutzt den Ordner `Data` der Portable-Version).
- Die Datenbank muss existieren: MPW einmal normal starten, bevor MPW-Web genutzt wird.

## Tests
- Neu: `tests/test_web_server.py` (Zugriffsschutz, Host-Prüfung, Sicherheits-Header, kein Pfadausbruch, Lesen, Speichern mit Sicherungsversion, Konflikt, Prüfungen, Sprache, Übersetzungen vollständig, keine HTML-Einschleusung).
- Angepasst: `tests/test_workflow_acceptance_p49.py` (gemeinsame Speicherfunktion).
- 195 Tests, GUI-, MCP- und Web-Selbsttest, Start-, Workflow- und Release-Prüfung bestanden.
- Echter Browser-Durchlauf mit Beispieldaten: Laden, Bearbeiten, Speichern mit Sicherungsversion, Konflikt, Verwerfen, Version übernehmen, Code im Songtext als reiner Text, Bands-Ansicht, Englisch.

## Grenzen
- Weitere Reiter folgen in späteren Stufen.
- `MPW-Web.exe` wurde nicht gebaut (Build-Probe abgebrochen); Installer und Portable-Paket nicht neu erstellt.
- Die Webanwendung benötigt in dieser Stufe noch PySide6 (wie MPW selbst); für macOS/Linux folgt eine Qt-freie Kernlogik.
