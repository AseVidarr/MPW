# MPW v2.2.0 Alpha 21 Preview 46

Basis: Preview 45. Das SQLite-Prüfwerkzeug berücksichtigt jetzt das echte MPW-Schema: `media_assets.relative_path` und `albums.cover_path`. Relative Pfade werden nur mit explizit angegebenem `--mpw-root` geprüft. Fehlende Dateien, Pfade außerhalb des MPW-Verzeichnisses und nicht auflösbare Referenzen führen zu einem negativen Prüfergebnis. Fünf neue Tests prüfen diese Fälle.

Beispiel (MPW geschlossen, ausschließlich Testkopien):

```powershell
python scripts/verify-sqlite-upgrade.py "C:\MPW-Testdaten\mpw.sqlite" --mpw-root "C:\MPW-Testdaten" --output "C:\MPW-Testberichte\pruefung.json"
```

**Grenzen:** Noch kein tatsächlicher Backup-Restore-Test und keine Windows-Abnahme. Das Skript prüft keine Medien-URLs, keine Inhalte der Dateien und nicht alle möglichen weiteren Speicherorte. Der Datenbankzugriff ist read-only.
