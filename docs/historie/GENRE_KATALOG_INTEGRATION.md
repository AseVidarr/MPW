# MPW v2.2.0 RC1 – Genre-Katalog-Integration

Additive Erweiterung des bereitgestellten RC1-Hotfix-Quellpakets.

- Beim nächsten Start werden 45 Hauptgenres, 408 eindeutige Subgenres und 415 Zuordnungen importiert.
- Die bisherige flache `genre_catalog`-Tabelle wird nur um fehlende Namen ergänzt. Bestehende Genre-Namen, Bands, Songs, Alben und Zuordnungen bleiben unverändert.
- Zusätzliche relationale Tabellen `mpw_main_genres`, `mpw_subgenres`, `mpw_genre_relations`, `mpw_genre_translations`, `mpw_genre_aliases`, `mpw_song_genres` stehen für die spätere hierarchische Oberfläche bereit.
- Bestehende MPW-Auswahlmenüs zeigen weiterhin eine flache Liste aller Genre-Namen. Hierarchische Auswahl und Mehrfachzuordnung im Editor sind **noch nicht implementiert**.
- Sprachstruktur für de/en/fr/es/it ist vorbereitet. Nur englische Anzeigenamen sind vorhanden; keine vollständige Übersetzung.
- Der Import ist wiederholbar und verwendet INSERT OR IGNORE.
- Die PyInstaller-Buildkonfiguration bindet die JSON-Referenzdaten ein.

Vor Einsatz an produktiven Daten unbedingt MPW-Datenbankbackup erstellen. Es wurden Syntaxprüfung und isolierte SQLite-Migrationstests durchgeführt, aber kein Windows-GUI-Abnahmetest und kein Installer-Build.
