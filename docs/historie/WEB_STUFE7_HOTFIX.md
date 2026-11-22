# Web-Anwendung Stufe 7 – Medien & Releases im Browser

## Neuer Reiter „Medien & Releases“ (Browser)

Links Songliste (Band-Filter, Suche), rechts zwei Bereiche:

**Medien** (wie „Medien & Player“ der Desktop-App)
- **Verlinkte Plattform-Medien**: ansehen, im neuen Tab öffnen, hinzufügen (nur gültige
  http(s)-Links ohne Zugangsdaten; derselbe Link nur einmal), löschen nach Rückfrage
  (die Datei auf der Plattform bleibt unverändert). Gespeicherte Suno-Links erscheinen hier.
- **Mediendateien** aus den Projektordnern (Cover, Audio, Dokumente, Video) und noch vorhandene
  Altbestände. Vorschau im Browser: Bilder, **Audio- und Video-Player** (mit Spulen), Text;
  PDF öffnet im neuen Tab. Andere Formate werden gelistet, aber nicht ausgeliefert.
- Dateien importieren, Audioanalyse (FFmpeg) und Medien-Explorer bleiben in der Desktop-App.

**Releases** (wie „Releases Distri“)
- Distributor (mit Vorschlägen), Release-Datum, ISRC, UPC/EAN.
- **Release-Checkliste** (nur Hinweis, nichts wird gespeichert) – gleiche Regeln und Texte wie Desktop.
- **Release speichern / ISRC abgleichen**: neue Veröffentlichung; gibt es die ISRC schon, wählt man
  den Datensatz und bestätigt die Änderung (wie im Desktop-Dialog).
- **Streamingplattformen** je Release: Plattform, Status (in 5 Sprachen angezeigt, gespeichert wird
  der feste deutsche Wert wie in der Desktop-App), optionaler Direktlink.

## Sicherheit der Dateiauslieferung

- Dateien werden nur aus den Medienordnern des jeweiligen Songs (innerhalb des MPW-Datenordners
  bzw. Band-Ordners) und nur in bekannten Formaten ausgeliefert.
- Jede Datei-Adresse enthält eine Kennung, die mit dem Zufallsschlüssel dieses Starts gebildet
  wird – andere Webseiten können sie nicht erraten. Dateipfade gehen nie an den Browser.
- Schutz-Header: `nosniff`, `no-store`, `same-origin`, Sandbox (außer PDF für den PDF-Betrachter).

## Technik

- Kern (`source/mpw_core.py`): `song_media_links`, `add_media_link`, `delete_media_link`,
  `song_media_files`, `release_checklist`, `isrc_matches`, `save_release`, `song_releases`,
  `save_release_platform` sowie die Texte `RELEASE_PREFLIGHT_I18N`, `RELEASE_EDIT_TEXTS`,
  `RELEASE_EDIT_DE`, `PLATFORM_STATUS_LABELS`, `MEDIA_CONFIRM_I18N` (Desktop nutzt dieselben;
  die Release-Checkliste der Desktop-App verwendet jetzt `release_checklist`).
- Web (`source/mpw_web.py`): `GET /api/songs/<id>/media`, `POST /api/songs/<id>/media-links`,
  `POST /api/songs/<id>/media-links/<lid>/delete` (nur mit `confirm: true`), `GET /media/<id>/<kennung>`
  (mit Teilabruf/Range), `GET /api/songs/<id>/releases`, `POST /api/songs/<id>/releases/check`,
  `POST /api/songs/<id>/releases` (Änderung per ISRC nur mit `update_id` + `confirm: true`),
  `POST /api/releases/<rid>/platforms`.
- Oberfläche: `hidden` setzt sich jetzt immer gegen andere Anzeige-Regeln durch (behebt einen
  sichtbar gebliebenen Auswahlbereich).

## Geprüft

- 236 Unit-Tests (mit `-W error::ResourceWarning`), u. a. Links (ungültige/doppelte/Löschen nur mit
  Bestätigung), Dateiauslieferung (nur mit Kennung, nur erlaubte Formate, Teilabruf, fremder Host
  abgewiesen, keine Pfade an den Browser), Releases (Checkliste, ISRC-Abgleich mit Bestätigung,
  ungültige ISRC/Datum, Plattformstatus).
- Einzelskripte, alle Audit-Skripte, Selbsttests von Desktop, MCP-Server und Web-Server, Kern ohne Qt,
  Rauchtest der Desktop-Release-Checkliste.
- Browser-Durchlauf mit Beispieldaten (Cover, 2-Sekunden-WAV, Textdatei): Vorschau und Player,
  Link hinzufügen/löschen (Nein/Ja), Checkliste, Release speichern, ISRC-Abgleich, Plattform – ohne Fehler;
  alle anderen Reiter danach erneut geprüft.
