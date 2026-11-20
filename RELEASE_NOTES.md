# MPW 2.2.0 RC2 – Music Production Workstation

Release-Kandidat 2 von MPW 2.2.0. **Neu: MPW im Browser** – dieselben Daten wie die installierte
MPW, lokal auf diesem PC, auch auf macOS und Linux.

> Release-Entwurf: vor dem Veröffentlichen prüfen. Vor dem ersten Start einer neuen Version
> empfiehlt sich ein Backup (Reiter „Backup“ → „Vollbackup jetzt erstellen“).

## Pakete

| Paket | Inhalt |
|---|---|
| `MPW_Setup_v2.2.0_RC2.exe` | Windows-Installation: Desktop-App + „MPW im Browser“ (Startmenü) + MCP-Server |
| `MPW_Portable_v2.2.0_RC2.zip` | Windows portabel: Desktop-App + Browser-Version, Daten im Portable-Ordner |
| `MPW_Portable_v2.2.0_RC2_macOS-arm64.tar.gz` | macOS (Apple Silicon) portabel, nur Browser-Oberfläche |
| `MPW_Portable_v2.2.0_RC2_Linux-x64.tar.gz` | Linux (x64) portabel, nur Browser-Oberfläche |

macOS/Linux: siehe `LIESMICH_MAC_LINUX.txt` im Paket (Start, Quarantäne unter macOS).
Prüfsummen: `SHA256SUMS.txt` (Windows) und `*.tar.gz.sha256` (macOS/Linux).

## MPW im Browser (neu)

Lokaler Webserver nur auf 127.0.0.1, Zufallsschlüssel pro Start, keine Freigaben ins Netz.
Desktop-App und Browser dürfen gleichzeitig offen sein. Alle Reiter in fünf Sprachen.

- **Songs & Suno** – Style/Lyrics bearbeiten (Sicherungsversion, Konfliktschutz), Prompt-Versionen,
  **An Suno senden (MCP)** über Claude Code mit Rückfrage und Link-Speicherung.
- **Bands** – Profil, Instrumente/Hardware, Hardware-Presets (hinzufügen/ersetzen), **Bands anlegen**
  mit derselben Ordnerlogik wie die Desktop-App.
- **Medien & Releases** – Plattform-Links, Mediendateien mit Vorschau und Audio/Video-Player,
  Releases mit Checkliste, ISRC-Abgleich und Plattformstatus.
- **Plattensammlung** – Alben, Trackliste, Metadaten, Cover, CSV-Export, Druckansicht.
- **AI Prompt Launcher** – Prompt über API oder CLI (Claude Code, Gemini CLI, Codex CLI),
  Anfrage kopieren & Plattform öffnen, Antwort importieren, als Version speichern.
- **KI-Verbindungen** – Status und Einrichtung (MPW-Daten nur lesend per MCP, Suno), Netzwerk-/Virenscanner-Hinweis.
- **Backup** – Vollbackup, Prüfungen, Prüfprotokoll, Einstellungen, Wiederherstellung mit doppelter
  Bestätigung und Sicherheitsbackup; **automatische Backups auch durch MPW im Browser** (nie doppelt).
- **Konfiguration** – Sprache, Speicherorte, Projekt-Unterordner-Vorlage.

## Desktop-App

- KI-Verbindungen-Assistent (Konfiguration) für Claude Code, Gemini CLI und Codex CLI:
  MPW-Daten per MCP (nur lesend), Suno-MCP, Anmeldung, Erkennung von HTTPS-Prüfung durch Virenscanner.
- Songs & Suno: „An Suno senden (MCP)“.
- Bands: Gruppe und Instrument/Hardware als Auswahlmenüs mit gespeicherten Werten;
  Hardware-Presets auf andere Bands übertragen (hinzufügen/ersetzen).
- AI Prompt Launcher: CLI-Zugang, verständliche Fehlermeldungen je Anbieter, aktuelles Claude-Modell
  und angepasste Token-Grenzen.
- Gemeinsamer Qt-freier Kern für Desktop-App, Browser-Version und MCP-Server – dieselben Regeln überall.

## Qualität

- Automatische Tests und Pakete für Windows, macOS und Linux bei jeder Änderung (GitHub Actions).
- Datenbank-Verbindungen und Netzwerkantworten werden zuverlässig geschlossen.
