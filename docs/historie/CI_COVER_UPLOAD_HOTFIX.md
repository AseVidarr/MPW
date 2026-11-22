# CI-Korrektur: Cover-Upload über der Größengrenze

## Problem

GitHub-Actions-Lauf #11 (Stufe 9: Plattensammlung) schlug auf Windows, macOS und Linux fehl:
Der Test, der ein Cover über 12 MB hochlädt, bekam „Broken pipe“ statt der Antwort
„zu groß“ (HTTP 413). Der Server hatte sofort geantwortet und die Verbindung geschlossen,
ohne den restlichen Upload zu lesen; der Absender schrieb noch und lief ins Leere.
Lokal unter Windows ging das zufällig gut.

## Korrektur

- **Server (`source/mpw_web.py`)**: Ein zu großer Upload bis zum Vierfachen der Grenze wird
  zu Ende gelesen und verworfen, danach kommt sauber die Antwort 413 `too_large`. Nur bei
  extrem großen Uploads wird die Verbindung getrennt. So sieht auch ein Browser die richtige
  Meldung statt eines Verbindungsfehlers. (Die Oberfläche prüft die Größe zusätzlich vorher.)
- **Test (`tests/test_web_server.py`)**: prüft die Regel mit vorübergehend auf 1.000 Byte
  gesenkter Grenze und 2.000 Byte Upload – dieselbe Regel, aber ohne 12 MB über die lokale
  Verbindung (das war auf den GitHub-Rechnern im vollen Testlauf zu langsam). Zusätzlich wird
  geprüft, dass dabei keine Datei gespeichert wird.

## Geprüft

- Web-Tests 8× hintereinander ohne Fehler; volle Suite 243 Tests grün (mit
  `-W error::ResourceWarning`), Einzelskripte, Audit-Skripte, Selbsttests, Kern ohne Qt.
