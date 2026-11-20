# Web-Anwendung Stufe 9 – Plattensammlung im Browser

## Neuer Reiter „Plattensammlung“ (Browser)

Plattensammlung und Album-Details der Desktop-App in einem Reiter:

- **Neue Platte anlegen**: Albumtitel + Interpret (aus den Bands). Liste aller Platten links.
- **Album**: Cover, Titel, Interpret und Zusammenfassung (Tracks · Laufzeit aus lesbaren
  Audiodateien · Veröffentlichungsstand) – gleiche Regeln wie in der Desktop-App.
- **Trackliste**: Songs des Interpreten hinzufügen; mit „Auch Songs anderer Interpreten
  anzeigen“ auch Sampler/Gastbeiträge. Ein Song nur einmal pro Platte. Reihenfolge mit ↑/↓,
  Entfernen (Nummerierung wird automatisch 1 … n).
- **Album-Metadaten**: Veröffentlichung, Genre (Vorschläge aus dem Genre-Katalog), Label,
  UPC/EAN (12 bzw. 13 Ziffern).
- **Cover auswählen / ändern**: PNG, JPG, WEBP oder BMP bis 12 MB; der Inhalt wird geprüft
  (nicht nur die Endung), gespeichert unter `media/album_covers` wie in der Desktop-App,
  vorhandene Dateien werden nie überschrieben.
- **Trackliste als CSV exportieren**: gleiche Spalten wie die Desktop-App (UTF-8 mit BOM für Excel);
  der Browser speichert die Datei, auf dem PC wird nichts geschrieben.
- **Album-Druckansicht öffnen**: dieselbe Druckansicht wie in der Desktop-App im neuen Tab
  (drucken oder als PDF speichern).
- **Platte löschen …** nach Rückfrage – die Songs selbst bleiben erhalten.

Außerdem: Die Reiterleiste scrollt bei schmalen Fenstern waagerecht, statt Wörter umzubrechen;
Bildlaufleisten, Datumsauswahl und Kontrollkästchen erscheinen passend zum dunklen Design.

## Technik

- Kern (`source/mpw_core.py`): `list_albums`, `create_album`, `delete_album`, `album_detail`,
  `album_song_choices`, `add_album_track`, `remove_album_track`, `move_album_track`,
  `save_album_metadata`, `album_summary`, `album_release_text`, `format_duration`,
  `album_cover_file`, `set_album_cover`, `album_tracklist_rows`, `album_print_html`.
  Die Desktop-App nutzt jetzt dieselbe Zusammenfassung, Druckansicht und CSV-Zeilen.
- Web (`source/mpw_web.py`): `GET/POST /api/albums`, `GET /api/albums/<id>`,
  `POST /api/albums/<id>/delete` (`confirm`), `GET /api/albums/<id>/songs[?all=1]`,
  `POST /api/albums/<id>/tracks`, `…/tracks/<sid>/delete`, `…/tracks/<sid>/move`,
  `POST /api/albums/<id>/metadata`, `POST /api/albums/<id>/cover` (Bilddaten, max. 12 MB),
  `GET /api/albums/<id>/tracklist`. Cover und Druckansicht unter eigenen Adressen mit
  geheimer Kennung (HMAC mit dem Startschlüssel) und strenger Content-Security-Policy.

## Geprüft

- 243 Unit-Tests (mit `-W error::ResourceWarning`), u. a. Anlegen (leer/unbekannte Band),
  Songauswahl Interpret vs. alle, doppelter Track, Verschieben/Entfernen mit Neunummerierung,
  Metadaten (UPC/Datum), CSV-Inhalt, Druckansicht (maskierte Inhalte, CSP, falsche Kennung → 404),
  Cover-Upload (SVG/leer abgewiesen, PNG gespeichert und ausgeliefert, > 12 MB → 413), Löschen nur
  mit Bestätigung (Songs bleiben).
- Rauchtest der Desktop-Plattensammlung (Zusammenfassung mit Laufzeit, Druckansicht, CSV-Export).
- Einzelskripte, alle Audit-Skripte, Selbsttests von Desktop, MCP-Server und Web-Server, Kern ohne Qt.
- Browser-Durchlauf mit Beispieldaten: anlegen, Tracks (auch Sampler), Reihenfolge, entfernen,
  Metadaten, Cover-Upload, CSV-Inhalt, Druckansicht, Löschen mit „Nein“ – ohne Fehler.
