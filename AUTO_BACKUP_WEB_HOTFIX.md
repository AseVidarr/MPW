# Automatische Backups auch durch MPW im Browser

## Warum

Fällige automatische Sicherungen hat bisher nur die Desktop-App beim Start angelegt.
Auf macOS und Linux gibt es nur MPW im Browser – dort entstand deshalb nie ein automatisches Backup.

## Was sich ändert

- **MPW im Browser (MPW-Web)** prüft beim Start und danach **stündlich**, ob laut
  Einstellung (Intervall, Aufbewahrung, Backup-Ordner – dieselbe `backup_settings.json`)
  ein automatisches Backup fällig ist, und legt es dann an (`MPW_auto_….zip`, geprüft,
  im Prüfprotokoll vermerkt). Ergebnis auch im Konsolenfenster.
- **Nie doppelt**: Desktop-App und MPW-Web nutzen dieselbe Funktion und eine Sperrdatei
  `MPW_auto_backup.lock` im Backup-Ordner. Wer zuerst kommt, sichert; der andere tut nichts.
  Innerhalb der Sperre wird erneut geprüft, ob die Sicherung noch fällig ist. Eine Sperre,
  die älter als eine Stunde ist (z. B. nach einem Absturz), wird ersetzt.
- **Aufbewahrung** wie bisher: nur automatische `MPW_auto_`-Backups über der gewählten Anzahl
  werden gelöscht – manuelle Backups und Sicherheitsbackups nie.
- **Reiter „Backup“** im Browser zeigt zusätzlich das Ergebnis der letzten Prüfung durch
  MPW-Web (gesichert / fehlgeschlagen mit Grund); die Texte nennen jetzt beide Programme.
- **Desktop-App**: `run_scheduled_backup` nutzt die gemeinsame Funktion
  `mpw_core.run_due_automatic_backup` (gleiches Verhalten, zusätzlich mit Sperre;
  Fehler beim Start werden wie bisher als Hinweis gezeigt und verhindern den Start nicht).

## Geprüft

- 241 Unit-Tests (mit `-W error::ResourceWarning`), u. a.: deaktiviert → nichts; Laufwerk fehlt →
  Fehler gemeldet; fällig → Backup; nicht fällig → nichts; Aufbewahrung löscht nur `MPW_auto_`;
  Sperre eines anderen Programms → nichts; verwaiste Sperre → wird ersetzt; MPW-Web meldet
  „fehlgeschlagen“ bzw. „gesichert“ und der Prüf-Thread endet sauber; `main()` startet die Prüfung.
- Rauchtest der Desktop-App (Qt offscreen, Temp-Daten): Backup beim Start, nicht doppelt,
  keine Sicherung während MPW-Web die Sperre hält.
- Einzelskripte, alle Audit-Skripte, Selbsttests von Desktop, MCP-Server und Web-Server, Kern ohne Qt.
- Browser: Reiter „Backup“ zeigt die von MPW-Web erstellte automatische Sicherung und den nächsten Termin.
