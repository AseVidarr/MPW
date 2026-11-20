# Music Production Workstation v0.4 – AI Prompt Launcher

## Windows-Installation
1. ZIP-Datei in einen eigenen Ordner entpacken.
2. Python 3.10 oder neuer mit `py`-Launcher installieren.
3. `start_windows.bat` doppelklicken (installiert PySide6 über pip).
4. Vor dem Upgrade den kompletten Ordner `%USERPROFILE%\MusicProductionWorkstation` sichern.

## Neue Funktionen in v0.4
- Registerkarte **AI Prompt Launcher** mit Ziel-Song und Anbieter ChatGPT / Gemini / Claude.
- Direkte API-Anfragen per HTTP mit nutzerseitigem API-Schlüssel oder Umgebungsvariablen `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`.
- Modellnamen können bei Bedarf angepasst werden; Beispielvorgaben sind nicht garantiert für jedes Konto verfügbar.
- Projekt- und Instrumentendaten sowie Persona-Regeln werden in die Anweisung übernommen.
- API-Aufruf im Hintergrund-Thread, um die Oberfläche nicht zu blockieren.
- KI-Antwort als JSON `{ "style": "...", "lyrics": "..." }` oder MPW-Tags `[STYLE]` / `[LYRICS]` importierbar.
- Zeichenlimitprüfung (Style 1.000, Lyrics 5.000) und Speicherung in neuer Tabelle `prompt_versions`.
- Alte Song-Prompts werden nicht automatisch überschrieben.
- Browsermodus öffnet ChatGPT, Gemini oder Claude und kopiert die vorbereitete Projektanweisung in die Zwischenablage. Die fertige Antwort muss manuell zurückkopiert werden.
- Bisherige Projekt-, Song-, Medien- und Release-Funktionen bleiben erhalten.

## Sicherheit und Einschränkungen
- API-Schlüssel werden nicht in SQLite gespeichert; das Passwortfeld wird nach einem API-Aufruf geleert. Umgebungsvariablen werden vom Betriebssystem verwaltet.
- Beim API-Modus werden Band-/Songinformationen, Instrumente und Songidee an den ausgewählten KI-Anbieter übertragen. Dies kann API-Kosten verursachen.
- Für den API-Modus ist Internetzugang und ein separater API-Zugang des jeweiligen Anbieters erforderlich.
- Keine automatische Synchronisation privater Web-Chatverläufe. Kein Browser-Connector implementiert.
- KI-Ausgaben sind nicht garantiert valide; vor Verwendung prüfen.
- Die Versionsliste zeigt bisher nur Metadaten; ein Versionsvergleich und das Übernehmen einer Version in den aktiven Song-Editor sind noch offen.
- Python-Syntaxprüfung bestanden; kein vollständiger Windows-/API-Integrationstest durchgeführt.
- Noch keine eigenständige EXE.

## Datenablage
`%USERPROFILE%\MusicProductionWorkstation\workstation.db` und `media\`.

## Patch v0.4.1
- Fehler beim Erstellen eines Releases behoben: Distributor-QComboBox wird mit currentText() ausgelesen.
- Keine Datenbankmigration nötig. Vorher trotzdem Backup erstellen.


## Version 0.4.2 – SoundCloud
- SoundCloud for Artists als Distributor im Release-Auswahlmenü ergänzt.
- SoundCloud bleibt als separate Streaming-/Veröffentlichungsplattform auswählbar.
- Fehlerkorrektur aus v0.4.1 für QComboBox.currentText() bleibt enthalten.
- Vor dem Update eine Sicherung des bisherigen MPW-Datenordners anlegen.

## Neu in MPW v0.4.3 – ISRC-Abgleich
- Beim Speichern eines Releases wird die ISRC **über alle Songs hinweg** abgeglichen.
- Leerzeichen und Bindestriche werden für den Abgleich ignoriert; Groß-/Kleinschreibung ist egal.
- Bei einer bereits vorhandenen ISRC zeigt MPW die vorhandenen und neuen Release-Daten an und fragt **Ja/Nein**, ob der vorhandene Datensatz aktualisiert werden soll. Standard ist **Nein**.
- **Ja** aktualisiert den bestehenden Release-Datensatz (einschließlich Song-Zuordnung, Distributor, Datum, UPC/EAN). Plattformzuordnungen bleiben erhalten. **Nein** ändert nichts und legt keinen doppelten Release an.
- Falls die ISRC bereits mehrfach in Altdaten vorkommt, erfolgt aus Sicherheitsgründen keine automatische Änderung.
- Ohne ISRC ist weiterhin das Anlegen eines neuen Release-Datensatzes möglich.
- Vor dem Update bitte ein Datenbank-Backup erstellen. Windows-Oberfläche wurde hier nicht ausgeführt.

## Neu in v0.4.4 – KI-Prompt-Versionsvergleich
- Zwei Prompt-Stände (auch der aktive Song-Prompt) vergleichen, zeilenweise für Style und Lyrics.
- Gespeicherte Version B nach Bestätigungsdialog direkt in den aktiven Song-Prompt übernehmen.
- Vor jeder Übernahme wird der bisherige aktive Prompt automatisch in `prompt_versions` gesichert.
- Versionen anderer Songs können nicht versehentlich übernommen werden.
- Limits Style 1000 / Lyrics 5000 werden vor Übernahme kontrolliert.
- Bisherige ISRC-Duplikatprüfung und SoundCloud for Artists bleiben erhalten.
- Nach dem Übernehmen zum Reiter „Songs & Suno“ wechseln, um den aktiven Prompt zu sehen.

## MPW v0.4.5 – ISRC-Rückfrage
- Bei vorhandener ISRC erscheint „Datensatz ändern“ mit Ja/Nein. Ja aktualisiert den vorhandenen Release, Nein bricht ohne Änderung ab.
- Wenn mehrere alte Datensätze dieselbe ISRC besitzen, wird vor der Ja/Nein-Frage der zu aktualisierende Datensatz ausgewählt; andere Datensätze bleiben unangetastet.
- Release-Plattformdaten des aktualisierten Datensatzes bleiben erhalten.


## v0.4.6 Backup wiederherstellen
Im Reiter Backup: ZIP auswählen, prüfen, Sicherheitsabfrage bestätigen. MPW legt vor dem Ersetzen automatisch ein Backup des aktuellen Standes neben dem MPW-Datenordner an. Nach erfolgreicher Wiederherstellung MPW neu starten.

## Version 0.4.7 – Plattformmedien
- Reiter Medien & Player: Plattform auswählen, URL eingeben und zum Song verlinken.
- Verlinkte Medien im Browser öffnen. Spotify/SoundCloud/YouTube-Seiten werden NICHT als Audio heruntergeladen.
- Direkte öffentlich zugängliche HTTPS-Datei-URLs können bis 200 MB in die lokale Medienbibliothek importiert werden (nur mit Nutzungsrechten).
- Links werden in neuer SQLite-Tabelle `media_links` gespeichert; alte Datensätze bleiben bestehen.
- Achtung: Direkter Download ist derzeit synchron; bei langsamen Downloads kann die Oberfläche vorübergehend blockieren.
- Plattform-Login, DRM-Umgehung, API-Authentifizierung und Streaming-Wiedergabe aus Webseiten sind nicht implementiert.


MPW v0.4.8: Medien-Plattformauswahl nur ChatGPT, Gemini, Claude und Direktdatei. Distributor- und Release-Plattformen bleiben unveraendert. Bestehende Medienlinks bleiben erhalten.


## v0.4.9 – Verlinkte KI-Plattform-Medien
Die Liste zeigt die für den gewählten Song gespeicherten URLs. Doppelklick öffnet den Link im Browser; Auswahl übernimmt URL, Plattform und Bezeichnung in die Eingabefelder. Zusätzlich: Öffnen, Kopieren, Entfernen mit Sicherheitsabfrage. Erst Song auswählen, dann Plattform und URL eintragen und „Link speichern“ klicken. Plattformseiten werden nur verlinkt, nicht heruntergeladen.

## Neu in MPW v0.5.0: Genre-Auswahlmenüs
- Hauptgenre und Zweitgenre sind editierbare Auswahlmenüs.
- Beide Menüs zeigen alle bisher in Bandprofilen gespeicherten Haupt- und Zweitgenres an (ohne doppelte Einträge).
- Neue Genres können weiterhin direkt eingegeben werden und stehen nach dem Anlegen des Bandprofils in beiden Menüs bereit.
- Bereits gespeicherte Daten bleiben unverändert.


## v0.5.1
Reiter 2 und 3 getauscht: AI Prompt Launcher ist jetzt Reiter 2, Songs & Suno ist Reiter 3. Keine Datenbankänderungen.


## v0.5.2 – Dauerhafter Genre-Katalog
- Neue Genres im Reiter Bands & Song/Projekte über „Genre hinzufügen“ erfassen.
- Alle Genres erscheinen in Hauptgenre und Zweitgenre.
- Bestehende Genres werden automatisch aus Bandprofilen übernommen.
- Der Katalog bleibt erhalten, auch wenn ein Genre in keinem Bandprofil mehr verwendet wird.
- Datenbank wird beim Start automatisch ergänzt, keine Löschung vorhandener Daten.


## v0.5.3 – Bandprofile und Song/Projekte bearbeiten
Band oder Projekt in der jeweiligen Liste anklicken, Felder ändern und „Ausgewähltes … speichern“ klicken. Datensatz-IDs und zugehörige Songs bleiben erhalten. Vor dem Update Backup erstellen.


## v0.5.4 – Instrumente & Hardware bearbeiten
Eintrag in der Liste auswählen, Gruppe und Hardware ändern und „Ausgewählte Hardware speichern“ drücken. „Ausgewählte Hardware löschen“ fragt vor dem Löschen nach. Bestehende Song-/Projektdaten bleiben erhalten.


## v0.5.5 Hardware-Preset-Bibliothek
Band-Hardware als benanntes Preset speichern, Preset auf eine andere Band anwenden oder Preset loeschen. Beim Anwenden werden bestehende Hardware-Eintraege der Zielband nach Bestaetigung ersetzt. Vorher Backup erstellen.


## v0.5.6 – Bestehende KI-Prompts importieren
Im AI Prompt Launcher Ziel-Song und Plattform (ChatGPT, Gemini, Claude) auswählen.
Vorhandene Prompt-Texte aus der Zwischenablage oder aus .txt/.md/.json importieren.
Import unterstützt MPW-Tags [STYLE], [LYRICS], [END MPW] oder JSON mit style/lyrics.
Nach der Prüfung „Als neue Version speichern“ wählen. Der aktive Song-Prompt wird nicht überschrieben.
Private Chats werden nicht automatisch aus den KI-Plattformen ausgelesen.


## v0.5.7 – KI-Prompt-Import per Weblink
Im AI Prompt Launcher über „Prompt über Weblink“ eine öffentlich erreichbare HTTPS-URL auf eine .txt-, .md- oder .json-Datei eingeben. Import wird wie gewohnt geprüft und erst nach Klick auf „Als neue Version speichern“ gespeichert. Maximal 2 MB. Private Chatverläufe und normale Freigabe-Webseiten von ChatGPT/Gemini/Claude werden nicht automatisch ausgelesen; hierfür den Prompt kopieren und über Zwischenablage importieren.


## v0.5.8 Hardware-Presets im AI Prompt Launcher
- Im AI Prompt Launcher Hardware des Bandprofils oder ein gespeichertes Preset waehlen.
- Das Preset gilt nur fuer die Prompt-Erstellung; Band-Hardware wird nicht geaendert.
- Nach dem Speichern/Loeschen von Presets wird die Auswahl aktualisiert.


## v0.5.9 – Layout Bands & Song/Projekte
- Breitere Eingabespalten (mindestens 360 px) und Inhaltsbereich.
- Vertikaler Scrollbalken rechts dauerhaft sichtbar.
- Bei sehr schmalem Fenster zusätzlich horizontales Scrollen möglich.
- Keine Datenbankänderung.


## v0.6.0 - Genre-Katalog als eigener Reiter
Der Genre-Katalog wurde aus Bands & Song/Projekte in einen eigenen Reiter direkt dahinter verschoben. Hauptgenre und Zweitgenre bleiben mit demselben gespeicherten Katalog verbunden. Die Datenbank wird nicht geloescht oder zurueckgesetzt.

## v0.6.1 – Bands und Song/Projekte getrennt
- Eigene Registerkarten „Bands“ und „Song/Projekte“.
- Bands: Bandprofile, Instrumente/Hardware und Hardware-Presets.
- Song/Projekte: Song/Projekte anlegen, auswählen und bearbeiten.
- Genre-Katalog bleibt eigenständig; alle bisherigen Datensätze bleiben erhalten.
- Beide Registerkarten besitzen bei Bedarf vertikale Scrollbalken.


## v0.6.2
Projekt-Suche im Reiter Song/Projekte: Filter nach Bandname oder Projektname und Trefferanzeige. Keine Datenbankmigration.
\n## v0.6.3 – Datenbank leeren\nIm Backup-Reiter: zwei Bestätigungsschritte (Ja + exakt DATENBANK LEEREN), verpflichtendes Sicherheitsbackup, transaktionales Löschen aller Anwendungsdaten. Mediendateien auf der Festplatte bleiben erhalten.\n

## v0.6.4 Windows-Dateisperre behoben
SQLite-Backup- und Pruefverbindungen werden vor dem Entfernen temporaerer Dateien explizit geschlossen. Vor dem Leeren wird der Medienplayer freigegeben. Die zwei Bestaetigungen und das Pflichtbackup bleiben bestehen.


## v0.6.5
Fix: Datenbank leeren prueft die Existenz der internen SQLite-Tabelle sqlite_sequence vor dem Zuruecksetzen. Doppelte Sicherheitsabfrage und Backup bleiben unveraendert.


## v0.6.6 Backup-Ziel
Im Backup-Reiter ein Laufwerk bzw. Verzeichnis auswaehlen. Die Einstellung wird in ~/MusicProductionWorkstation/backup_settings.json gespeichert und gilt fuer manuelle Backups (Vorauswahl) und automatische Sicherheitsbackups bei Datenbankleerung und Wiederherstellung. Bei nicht erreichbarem Ziel wird die Datenbankleerung abgebrochen.


## v0.6.7
Backup-Datei auf Integritaet pruefen (ZIP und SQLite) ohne Wiederherstellung. Behebt zudem zwei fehlerhafte f-Strings in der Fehlerbehandlung von v0.6.6.


## v0.6.8
Backup-Uebersicht im Backup-Reiter: ZIP-Dateien im festgelegten Ordner mit Datum und Groesse auflisten, Liste aktualisieren und ausgewaehlte Sicherung pruefen.

## v0.6.9 – Automatische Backups
Im Backup-Reiter kann ein automatisches Sicherungsintervall (täglich, alle 3 Tage, wöchentlich, alle 14 Tage oder 30 Tage) und eine Aufbewahrungsanzahl (3, 5, 10, 20 oder 50) gewählt werden. Standardmäßig ist die Automatik deaktiviert. Beim Programmstart wird geprüft, ob die letzte automatische Sicherung älter als das Intervall ist. Nur automatisch erzeugte MPW_auto_-Sicherungen werden bereinigt; manuelle und Sicherheitsbackups werden niemals automatisch entfernt. Das gewählte Backup-Laufwerk wird verwendet. Einstellungen bleiben nach Neustart gespeichert.


## v0.7.0 Backup-Statusanzeige
Im Backup-Reiter zeigt MPW die letzte automatische Sicherung, den nächsten Fälligkeitstermin (Prüfung beim Programmstart) und eine Warnung, wenn das gewählte Backup-Laufwerk nicht erreichbar ist. Der Status wird bei Ordnerwechsel, Einstellungen und Aktualisierung der Backupliste aktualisiert.


## v0.7.1 – Wiederherstellung aus der Backup-Liste
Im Backup-Reiter eine ZIP-Sicherung markieren und „Ausgewähltes Backup wiederherstellen“ anklicken. Das Backup wird geprüft, eine Bestätigung verlangt und vor der Wiederherstellung eine Sicherheitskopie des aktuellen Standes erstellt. Der bisherige Datei-Auswahldialog bleibt erhalten.


## v0.7.2 – Alle Backups prüfen
Schaltfläche „Alle Backups prüfen“ prüft jede ZIP-Sicherung im ausgewählten Ordner samt SQLite-Integrität. Grün: gültig; Rot: beschädigt oder nicht lesbar. Fehlerdetails stehen im Tooltip. Die Prüfung verändert weder Backups noch aktuelle Datenbank.


## v0.7.3 – Automatische Backup-Prüfung und Prüfprotokoll
Nach jeder Backup-Erstellung werden ZIP und SQLite geprüft. Das Ergebnis wird als JSONL im gewählten Backup-Ordner in MPW_Backup_Pruefprotokoll.jsonl protokolliert. Der Reiter Backup zeigt über die Schaltfläche Backup-Prüfprotokoll anzeigen die letzten 100 Einträge. Eine Protokoll-Schreibstörung macht ein bereits erfolgreich verifiziertes Backup nicht ungültig.


## v0.7.4 Backup-Statistik und Warnung
Im Reiter Backup werden protokollierte erfolgreiche und fehlgeschlagene Sicherungen gezaehlt. Falls der neueste Protokolleintrag einen Fehler meldet, wird die Ursache hervorgehoben. Bei nicht erreichbarem Backup-Laufwerk erscheint eine Warnung.


## v0.7.5 Backup-Startprüfung
Beim Programmstart werden die fünf neuesten Backups im ausgewählten Ordner auf ZIP- und SQLite-Integrität geprüft. Beschädigte Sicherungen werden per Warnfenster gemeldet; bei nicht erreichbarem Laufwerk erscheint ebenfalls eine Warnung. Alle übrigen Backups lassen sich weiterhin manuell mit „Alle Backups prüfen“ prüfen. Die Startprüfung verändert keine Dateien.


v0.7.6: Neuer Reiter Plattensammlung. Alben erstellen, vorhandene Songs als geordnete Trackliste zuweisen, Cover importieren, Reihenfolge ändern und Platten löschen. Songs bleiben erhalten. Cover liegen in media/album_covers und werden mitgesichert.

## v0.7.7 – Genre-Index
Der Reiter Genre-Katalog zeigt alle angelegten Genres alphabetisch sortiert, mit Suchfilter und Anzahl. Der Index aktualisiert sich beim Hinzufügen und beim Neuladen der Daten.


## v0.7.8 – Interpret als Auswahlmenü
Im Reiter Plattensammlung wird der Interpret beim Anlegen eines Albums aus den im Reiter Bands angelegten Interpreten ausgewählt. Die Liste aktualisiert sich mit den Banddaten. Bestehende Albumdaten bleiben erhalten.


## v0.7.9 – Songauswahl nach Albuminterpret
Beim Auswaehlen einer Platte zeigt die Songauswahl standardmaessig nur Songs der zugeordneten Band. Fuer Sampler und Gastbeitraege kann die Checkbox „Auch Songs anderer Interpreten anzeigen“ aktiviert werden. Bereits hinzugefuegte Tracks bleiben unveraendert.


## v0.8.0 Album-Metadaten
Im Reiter Plattensammlung: Erscheinungsdatum (optional), Genre aus dem Katalog oder Freitext, Label und UPC/EAN. Speichern ueber Album-Metadaten speichern. Bestehende Alben werden beim Start additiv migriert.


## v0.8.1 – Album-Trackliste als CSV exportieren
Im Reiter Plattensammlung kann die ausgewählte Platte mit ihren Tracks in sortierter Reihenfolge als UTF-8-CSV (mit BOM, Semikolon-Trennung für Excel) exportiert werden. Die Datei enthält Albumtitel, Interpret, Veröffentlichungsdatum, Genre, Label, UPC/EAN, Tracknummer, Songtitel, Songinterpret, Projekt und Songstatus. Die Datenbank wird dabei nicht verändert.


## v0.8.2 Albumübersicht
Die Plattensammlung zeigt Trackanzahl, Veröffentlichungsstand aus den Release-Datensätzen und bekannte Gesamtlaufzeit. Laufzeit wird für lokal importierte WAV-Dateien ermittelt; andere Formate bleiben als unbekannt gekennzeichnet.


## v0.8.3 – Albumlaufzeit mehrerer Audioformate
MP3, FLAC, M4A, OGG, AIFF und WAV werden über Mutagen ausgewertet; WAV besitzt zusätzlich einen Standardbibliothek-Fallback. Nur tatsächlich lesbare Tracks zählen zur Laufzeit. Neue Abhängigkeit: mutagen (siehe requirements.txt).


## v0.8.4 – Aufgeräumte Reiter
Album-Metadaten und CSV-Export sind in den neuen Reiter „Album-Details“ ausgelagert. Im Reiter „Plattensammlung“ bleiben Albumliste, Cover und Trackverwaltung. Album zuerst in der Plattensammlung auswählen.
\n\n## v0.8.5 – Album-Druckansicht\nEigener Reiter für die Vorschau und den HTML-Export einer druckbaren Albumübersicht inklusive eingebettetem Cover, Metadaten und Trackliste. Die HTML-Datei lässt sich im Browser drucken oder als PDF speichern.\n

## v0.8.6 – System & Diagnose
Eigener Reiter für Python-/Paketversionen, Mutagen-Import, SQLite-quick_check, Verzeichnis-Erreichbarkeit und TXT-Diagnoseexport. Die Prüfungen sind lesend; Schreibrechte werden nur indikativ ermittelt.


## v0.8.7 – Zentrale Fehlerprotokollierung
Unbehandelte Python-Fehler werden unter ~/MusicProductionWorkstation/logs/mpw_errors.log protokolliert. Die Datei rotiert bei 2 MB; bis zu drei ältere Dateien werden aufbewahrt. Im Reiter System & Diagnose gibt es Schaltflächen zum Anzeigen der letzten 100 KB und zum Exportieren des aktuellen Protokolls. Fehlerprotokolle können Dateipfade und technische Details enthalten; vor dem Teilen prüfen.

## v0.8.8 – Fehlerprotokolle durchsuchen
Im Reiter „System & Diagnose“ lassen sich das aktuelle Fehlerprotokoll und bis zu drei rotierte Protokolldateien auswählen, nach Text durchsuchen und einzeln exportieren. Die Vorschau liest höchstens 200 KB pro Datei; die Exportfunktion kopiert die vollständige ausgewählte Datei. Protokolle werden dabei nicht verändert.


## v0.8.9 – App-Name
Der Fenstertitel lautet jetzt „MPW - Music Production Workstation -“ (mit Versionsnummer).


## v0.9.0 – Fehlerstatistik
Im Reiter System & Diagnose zeigt die Schaltfläche „Fehlerstatistik anzeigen“ die Häufigkeit protokollierter Python-Ausnahmetypen aus dem aktuellen und bis zu drei archivierten Fehlerprotokollen. Die Auswertung liest nur Protokolle und verändert keine Daten.


## v0.9.1
Fehlerstatistik im Reiter System & Diagnose als Excel-kompatible CSV (UTF-8 BOM, Semikolon) exportieren. Bei nicht lesbaren Protokollen erfolgt eine Warnung.

## v0.9.2 – Fehlerstatistik nach Zeitraum
Im Reiter System & Diagnose kann die Fehlerstatistik für alle Zeiträume, die letzten 7 Tage oder die letzten 30 Tage gefiltert und als CSV exportiert werden. Undatierte Protokolleinträge werden nur bei Alle Zeiträume berücksichtigt.


## v0.9.3
Fehlerverlauf nach Tagen im Reiter System & Diagnose; Zeitraumfilter wird beruecksichtigt.


## v0.9.4 – Fehlerverlauf als CSV exportieren
Im Reiter System & Diagnose kann der taegliche Fehlerverlauf fuer den gewaehlten Zeitraum als Excel-kompatible CSV (UTF-8 BOM, Semikolon) exportiert werden. Nicht lesbare Logs werden vor dem Export gemeldet.
\n\n## v0.9.5 – Diagnosepaket\nIm Reiter System & Diagnose kann ein ZIP mit Systembericht und vorhandenen Fehlerprotokollen exportiert werden. Es enthält keine Datenbank oder Medien. Vor der Weitergabe auf persönliche Dateipfade prüfen.\n\n\n## v0.9.6 – Backup-Speicherplatzdiagnose\nDie Systemprüfung zeigt freien Speicherplatz auf dem ausgewählten Backup-Laufwerk und schätzt den Platzbedarf aus Datenbank und lokalen Medien. Warnung bei knapper Reserve, Fehler bei voraussichtlich unzureichendem Speicher. Keine Dateien werden verändert.\n

## v0.9.7 – Backup-Speicherplatzprüfung vor dem Schreiben
Vor jeder Sicherung wird das Zielverzeichnis und der freie Speicherplatz geprüft. Bei voraussichtlich zu wenig Platz wird vor dem Schreiben abgebrochen. Der Schätzwert ist konservativ (Datenbank + Medien + 100 MiB).
\n\n## v0.9.8 – Backup-Ziel testen\nIm Backup-Reiter kann das ausgewählte Laufwerk vor einer Sicherung auf Erreichbarkeit, Schreibzugriff und freien Speicher getestet werden. Es werden keine Daten verändert.\n\n\n## v0.9.9 – Backup-Inventar als CSV\nIm Backup-Reiter kann eine CSV-Liste aller ZIP-Dateien des ausgewählten Backup-Ordners exportiert werden (Dateiname, Größe, Änderungsdatum, Typ). Excel-kompatibel (UTF-8 BOM, Semikolon). Die Funktion prüft keine ZIP-Integrität und verändert keine Backups.\n

## v1.0.0 – Backup-Übersicht
Im Backup-Reiter zeigt eine kompakte Übersicht Anzahl und Gesamtgröße der ZIP-Archive, die Anzahl automatisch benannter Archive und das Alter des neuesten Backups. Warnung bei fehlenden Backups oder wenn das neueste älter als 30 Tage ist. Die Prüfung liest nur Dateimetadaten und prüft keine Archivintegrität.


## v1.0.1 – Backup-Größenvergleich
Die Backup-Übersicht vergleicht die Größen der zwei neuesten ZIP-Archive und warnt, wenn das jüngste mindestens 30 % kleiner ist. Ab 30 % Zuwachs erscheint ein Hinweis. Der Größenvergleich ist keine Integritäts- oder Vollständigkeitsprüfung und verändert keine Dateien.


## v1.0.2 – Backup-Suche
Im Reiter Backup steht über der Archivliste ein Suchfeld mit Löschsymbol. Es filtert die angezeigten Sicherungen sofort nach Dateinamen, ohne Dateien zu ändern. Die Filterung bleibt beim Aktualisieren der Liste aktiv; die Backup-Gesamtstatistik bezieht sich weiterhin auf alle Archive.


## v1.0.3 – Backup-Liste sortieren
Die Backup-Liste kann nach Datum (neu/alt), Dateiname (A–Z/Z–A) oder Dateigröße (groß/klein) sortiert werden. Der Dateinamenfilter bleibt aktiv. Die Backup-Übersicht vergleicht weiterhin die zwei tatsächlich neuesten Backups, unabhängig von der angezeigten Sortierung.


## v1.0.4 – Backup-Inhaltsvorschau
Im Backup-Reiter zeigt „Backup-Inhalt anzeigen“ Dateianzahl, Medienanzahl, komprimierte und unkomprimierte Größe sowie bis zu 500 Dateinamen aus dem ausgewählten ZIP. Es werden keine Dateien extrahiert oder verändert. Die Vorschau ersetzt keine Integritätsprüfung.


## v1.0.5 – Backup-Dateiliste als CSV
Im Backup-Reiter lässt sich für das ausgewählte ZIP-Archiv eine vollständige Dateiliste mit Dateipfad, Original- und komprimierter Größe, ZIP-Zeitstempel und CRC32-Metadatum exportieren. Kein Entpacken oder Verändern des Archivs; CRC32 ist keine ausgeführte Integritätsprüfung.


## v1.0.6 – Backup-Dateivergleich
Im Reiter Backup vergleicht „Mit vorherigem Backup vergleichen“ das markierte ZIP mit dem zeitlich unmittelbar älteren Archiv. Angezeigt werden neue, entfernte, geänderte und unveränderte Dateien. Grundlage sind Dateiname, unkomprimierte Größe und gespeicherter CRC32-Wert; es erfolgt keine vollständige Integritätsprüfung. Die Archive bleiben unverändert.


Hotfix v1.0.6a: korrigiert NameError QPush -> QPushButton beim Aufbau des Backup-Reiters.


## v1.0.7 – Backup-Bedienung übersichtlicher
Die Aktionen im Backup-Reiter sind auf drei Zeilen verteilt. Dies verhindert die sehr breite Schaltflächenleiste auf kleineren Bildschirmen. Enthält den Startfehler-Hotfix aus v1.0.6a.


## v1.0.8 – Backup-Auswahldetails
Der Backup-Reiter zeigt direkt unter der Liste Dateiname, Größe und Änderungsdatum der markierten Sicherung. Bei einer Aktualisierung oder Sortieränderung bleibt die Auswahl nach Möglichkeit erhalten. Nur lesender Zugriff auf Dateimetadaten.


## v1.0.9 – Trefferzähler für Backup-Suche
Unter der Backup-Suche zeigt MPW jetzt die Anzahl sichtbarer Archive im Verhältnis zur Gesamtzahl an. Der Zähler aktualisiert sich beim Tippen, Sortieren und Neuladen. Statusmeldungen werden nicht als Archive mitgezählt. Keine Dateien werden verändert.


## v1.1.0 – Backup-Bedienung aufgeräumt
Die fünf unteren Aktionen sind in drei klar benannte Gruppen unterteilt: „Sicherung erstellen und prüfen“, „Wiederherstellung und Protokoll“ und „Gefahrenbereich – Datenbank löschen“. Die Löschfunktion ist optisch und räumlich getrennt. Vorhandene Funktionen und Daten bleiben unverändert.


## v1.1.1 – Backup auf zwei Reiter verteilt
**Backup – Einstellungen:** Laufwerk, Zieltest, Automatik und Vollbackup erstellen. **Backup – Archiv:** Suche, Sortierung, Archivdetails, Integritätsprüfungen, Vergleiche, CSV-Exporte, Wiederherstellung, Prüfprotokoll und Datenbank-Leeren (Gefahrenbereich). Die vorhandenen Daten bleiben unverändert.


## v1.1.2 – Aufklappbare Archiv-Werkzeuge
Im Reiter Backup – Archiv sind selten genutzte Werkzeuge (Vergleich, CSV-Exporte, Gesamtprüfung und Wiederherstellung der Auswahl) in einem standardmäßig geschlossenen Bereich „Weitere Archiv-Werkzeuge“ zusammengefasst. Liste, Suche, Einzelauswahl und Inhaltsvorschau bleiben direkt sichtbar.


## v1.1.3 – Backup-Aktionen kontextabhängig
Im Reiter Backup – Archiv sind Aktionen für ein einzelnes Backup erst nach Auswahl einer vorhandenen ZIP-Datei aktiv. Wird die Auswahl durch den Suchfilter ausgeblendet, wird sie aufgehoben. So werden versehentliche Aktionen auf unsichtbare oder nicht ausgewählte Archive vermieden.


## v1.1.4 – Backup-Typfilter
Im Reiter Backup – Archiv kann zusätzlich zur Dateinamensuche zwischen allen, automatischen und anderen Backups gefiltert werden. Trefferzähler und Auswahl werden synchronisiert. Nur Listenanzeige; keine Änderungen an Dateien.


## v1.1.5 – Backup-Zeitraumfilter
Im Reiter Backup – Archiv lassen sich Backups zusätzlich nach den letzten 7, 30 oder 90 Tagen filtern. „Filter zurücksetzen“ löscht Suchtext und setzt Typ und Zeitraum zurück. Die Gesamtstatistik bleibt ungefiltert. Es werden keine Archive verändert.


## v1.1.6 – Backup-Inventar gezielt exportieren
Beim CSV-Export kann zwischen allen Sicherungen und nur den aktuell sichtbaren, durch Suche/Typ/Zeitraum gefilterten Sicherungen gewählt werden. Die Sortierung der sichtbaren Liste bleibt im Export erhalten. Keine Änderungen an ZIP-Archiven.


## v1.1.7 – Backup-Ordner direkt öffnen
Im Reiter „Backup – Archiv“ öffnet die neue Schaltfläche „Backup-Ordner öffnen“ den aktuell eingestellten Backup-Ordner im Datei-Explorer. Nicht erreichbare Ordner werden mit einer Meldung behandelt; die Funktion verändert keine Dateien.


## v1.1.8 – Ausgewähltes Backup im Explorer zeigen
Im Reiter Backup – Archiv kann das markierte ZIP-Backup direkt im Windows-Explorer ausgewählt werden. Die Schaltfläche ist nur bei vorhandener sichtbarer Auswahl aktiv. Auf anderen Systemen wird der übergeordnete Ordner geöffnet. Es werden keine Archivdaten verändert.


## v1.1.9 – Backup-Doppelklick
Doppelklick auf eine Sicherung öffnet die schreibgeschützte Inhaltsvorschau.


## v1.2.0 – Backup-Pfad kopieren
Im Reiter Backup – Archiv kopiert die Schaltfläche „Backup-Pfad kopieren“ den vollständigen Pfad des ausgewählten vorhandenen ZIP-Backups in die Zwischenablage. Die Schaltfläche ist nur bei gültiger Auswahl aktiv. Es werden keine Dateien verändert.


## v1.2.1 – Kontextmenü im Backup-Archiv
Rechtsklick auf ein vorhandenes ZIP-Backup öffnet ein Kontextmenü für Inhaltsvorschau, Integritätsprüfung, Anzeige im Explorer und Kopieren des Dateipfads. Kein Wiederherstellen oder Löschen per Kontextmenü.


## v1.2.2 – Backup-Dateiname kopieren
Im Backup-Archiv lässt sich über Rechtsklick jetzt auch nur der Dateiname einer vorhandenen Sicherung kopieren. Die bisherige Aktion zum Kopieren des vollständigen Pfads bleibt bestehen.


## v1.2.3 – Backup-Details kopieren
Rechtsklick auf ein Backup > „Backup-Details kopieren“ kopiert Dateiname, Backup-Typ, Größe in Bytes und MiB, Änderungsdatum und vollständigen Pfad als formatierten Text. Keine Archivänderungen.


## v1.2.4 – Konfiguration
Neuer Reiter „Konfiguration“ mit wählbarem Startreiter (letzter Reiter, Bands, Songs & Suno, Song/Projekte oder Konfiguration), Anzeige der lokalen Datenpfade und Schaltfläche zum Öffnen des MPW-Datenordners. Einstellungen werden in ~/MusicProductionWorkstation/app_configuration.json gespeichert.


## v1.2.5 – Alle Reiter beim Programmstart auswählbar
Unter Konfiguration → Beim Start anzeigen stehen jetzt automatisch sämtliche tatsächlich vorhandenen Reiter in ihrer sichtbaren Reihenfolge zur Auswahl, zusätzlich zu „Zuletzt verwendeten Reiter öffnen“. Bereits gespeicherte Einstellungen bleiben erhalten.
\n\n## v1.2.6 – Band-Verzeichnisse\nIm Reiter Konfiguration kann ein Basisordner für neue Bands ausgewählt werden (Standard: ~/MusicProductionWorkstation/Bands). Beim Erstellen einer neuen Band wird dort ein gleichnamiges Verzeichnis angelegt. Existiert der Bandname bereits in der Datenbank oder als Ordner, erscheint „Band bereits vorhanden“, ohne vorhandene Dateien zu verändern. Ungültige Windows-Dateinamen werden abgewiesen.\n

## v1.2.7 – Band-Unterordner
Beim Anlegen einer Band werden Bilder, Dokumente, Musik, OLD und Video angelegt. Existiert der Bandordner bereits, werden nur fehlende Unterordner ergänzt; vorhandene Inhalte bleiben unangetastet.


## MPW v1.2.8 – Bandprofil-Kontextmenü
- Rechtsklick auf eine vorhandene Band in der Liste im Reiter Bands: „Im Explorer öffnen“.
- Verwendet den unter Konfiguration festgelegten Band-Speicherort und den in der Datenbank gespeicherten Bandnamen.
- Bestehende Bandordner werden nur geöffnet; es werden keine Ordner erstellt, überschrieben oder gelöscht.
- Fehlende oder nicht erreichbare Bandordner werden mit einer Meldung angezeigt.
\n\n## v1.2.9 – Band löschen\nIm Reiter Bands bietet das Rechtsklickmenü nun „Band löschen …“. Die Aktion erfordert eine Ja/Nein-Sicherheitsabfrage und anschließend die exakte Eingabe des Bandnamens. Zugehörige Song/Projekte, Songs und Datenbankverknüpfungen werden transaktional gelöscht; Bandordner und Mediendateien auf der Festplatte bleiben unangetastet. Vorher ein Backup erstellen!\n

## v1.3.0 – Bestehende Bandordner vervollständigen
Rechtsklick auf eine Band → „Fehlende Standard-Unterordner ergänzen“. Ergänzt Bilder, Dokumente, Musik, OLD und Video im bestehenden Bandverzeichnis. Vorhandene Ordner und Dateien bleiben unangetastet. Fehlende Band-Hauptordner werden nicht automatisch neu angelegt; bei Konflikten erscheint eine Fehlermeldung.


## v1.3.1 – Band / Projekt / Medien-Unterordner
- Neue Band: ausschließlich Band-Hauptordner unter dem konfigurierten Speicherort.
- Neues Projekt: Projektordner unter dem Bandordner sowie Bilder, Dokumente, Musik, OLD, Video.
- Vorhandene Projektordner und Unterordner werden nicht überschrieben. Fehlende Unterordner werden ergänzt.
- Reiter Song/Projekte: Rechtsklick auf Projekt -> Fehlende Projekt-Unterordner ergänzen.
- Die frühere Ergänzungsfunktion auf Bandebene wurde entfernt.
- Vorhandene Ordnerstrukturen werden nicht automatisch verschoben; bitte vor Änderungen sichern.


## v1.3.2 – Projektordner im Explorer öffnen
Im Reiter Song/Projekte bietet das Rechtsklick-Menü auf bestehende Song/Projekte nun „Im Explorer öffnen“. Der Projektordner wird anhand des konfigurierten Band-Basisordners und des zugeordneten Band- und Projektnamens ermittelt. Fehlende Ordner werden nicht angelegt; vorhandene Dateien bleiben unverändert. Die Funktion zum Ergänzen fehlender Standard-Unterordner bleibt bestehen.


## v1.3.3 – Vorhandene Projektordner importieren
Im Reiter Song/Projekte Band wählen und „Vorhandene Projektordner in Datenbank übernehmen“ klicken. MPW liest ausschließlich direkte Unterordner des konfigurierten Bandordners, zeigt eine Bestätigungsliste und übernimmt neue Song/Projekte in die SQLite-Datenbank. Bestehende DB-Song/Projekte werden übersprungen. Keine Dateien oder Ordner werden verändert.
\n\n## v1.3.4 – Unterordner für alle Song/Projekte ergänzen\nIm Reiter Song/Projekte gibt es die Schaltfläche „Fehlende Unterordner für alle Song/Projekte ergänzen“. Nach Bestätigung werden alle in der Datenbank registrierten Song/Projekte geprüft und nur fehlende Standard-Unterordner (Bilder, Dokumente, Musik, OLD, Video) ergänzt. Fehlende Projekt-Hauptordner werden übersprungen, bestehende Dateien nicht überschrieben. Eine Ergebnisübersicht zeigt Ergänzungen, Überspringungen und Fehler.\n

## v1.3.5 – Projektänderungen sicher speichern
Die Schaltflächen heißen jetzt „Neues Projekt anlegen“ und „Projektänderungen speichern“. Beim Ändern des Projektnamens oder der Band wird nach Bestätigung der zugehörige Projektordner umbenannt bzw. verschoben. Zielkonflikte werden abgewiesen, bestehende Dateien nicht überschrieben. Bei Datenbankfehlern versucht MPW, die Ordnerbewegung zurückzunehmen. Vor produktiver Nutzung ein Backup erstellen.


## v1.3.6 – Info zu Projekt-Schaltflächen
Im Reiter Song/Projekte befindet sich neben „Neues Projekt anlegen“ und „Projektänderungen speichern“ jeweils eine Info-Schaltfläche. Ein Klick zeigt die Aufgaben und Sicherheitsregeln in einem Hinweisfenster.


## v1.3.7 – Kompakte Info-Schaltflächen
Die beiden Info-Schaltflächen im Reiter Song/Projekte verwenden nur noch ihre benötigte Breite; die eigentlichen Projektaktionen behalten den übrigen Platz.


## v1.3.8 – Projektpfad kopieren
Im Reiter Song/Projekte ist im Rechtsklick-Kontextmenü die Funktion „Projektpfad kopieren“ hinzugekommen. Der vollständige Pfad des bestehenden Projektordners wird in die Zwischenablage übernommen. Bei fehlendem Band- oder Projektordner erscheint eine Fehlermeldung; es werden keine Dateien verändert.
\n\n## v1.3.9 – Bandordner und Datenbank abgleichen\nExistiert der Bandordner, aber noch kein Bandprofil in der Datenbank, kann der vorhandene Ordner nach ausdrücklicher Bestätigung übernommen werden. Existiert die Band bereits in der Datenbank, wird der Eintrag in der Übersicht ausgewählt. Neue Ordner werden nur bei neuen Bands erstellt; bei Datenbankfehlern wird ein neu angelegter leerer Ordner wieder entfernt.\n

## v1.4.0 – Medien Explorer
Neuer Reiter „Medien Explorer“ neben „Medien & Player“. Schreibgeschützte Dateisystemansicht mit Ordnerbaum, Dateigröße, Dateityp, Sortierung, Auswahl eines eigenen Stammordners, Wechsel zwischen Band-/Projektordnern und MPW-Medienordner, Aktualisieren, Doppelklick zum Öffnen und Anzeige im Windows-Explorer. Keine Lösch- oder Verschiebefunktion.


## v1.4.1 – Startfehler Medien Explorer behoben
QFileSystemModel wird korrekt aus PySide6.QtWidgets importiert (statt QtGui). Behebt den gemeldeten ImportError beim Programmstart.


## v1.4.2 – Medien Explorer in Mittelgrau
Die Dateiansicht und ihre alternierenden Zeilen sowie die Spaltenüberschriften im Reiter Medien Explorer verwenden jetzt ein mittelgraues Farbschema statt des weißen Windows-Standards. Auswahl bleibt blau hervorgehoben.


## v1.4.3 – Dunkle Schrift im Medien Explorer
Die Datei- und Ordnerliste sowie Spaltenüberschriften nutzen dunkle Schrift auf mittelgrauem Hintergrund. Markierte Zeilen behalten weiße Schrift auf blaugrauem Auswahlhintergrund. Nur der Medien Explorer wird geändert.
\n\n## v1.4.4 – Song/Projekte löschen\nRechtsklick auf ein Projekt: nur aus Datenbank löschen oder mit Projektordner und Dateien löschen. Beide Aktionen benötigen Sicherheitsbestätigung und exakte Eingabe des Projektnamens. Zugeordnete Datenbankdatensätze werden in einer Transaktion entfernt. Bei vollständiger Löschung wird der Ordner vor der Datenbanktransaktion temporär umbenannt und bei DB-Fehler zurückbenannt. Dateien außerhalb des Projektordners bleiben bestehen.\n

## v1.4.5 – Genre-Katalog: Kontextmenü
Rechtsklick im Genre-Index bietet „Genre bearbeiten“ und „Genre löschen“. Umbenennen aktualisiert Band- und Albumzuordnungen. Löschen ist nur bei unbenutzten Genres nach Bestätigung möglich, damit Zuordnungen nicht verloren gehen.
\n\n## v1.4.6 – Band und Ziel-Song im AI Prompt Launcher\nIn einer gemeinsamen Zeile wird zuerst die Band und anschließend das zugehörige Projekt (Ziel-Song) gewählt. Die Projektauswahl wird nach Band gefiltert. Falls zum Projekt noch kein Song-Datenbankeintrag existiert, kann dieser mit ausdrücklicher Bestätigung über „Song-Eintrag anlegen“ erstellt werden. Ordner und Dateien bleiben unverändert.\n

## v1.4.7 – Projekt über Kontextmenü umbenennen
Im Reiter Song/Projekte gibt es im Rechtsklickmenü den Punkt „Projekt umbenennen …“. Der neue Name wird in einem Dialog abgefragt. Anschließend verwendet MPW die vorhandene abgesicherte Umbenennung für Datenbank und Projektordner mit Bestätigung, Prüfung auf Namenskonflikte und Rücknahmeversuch bei Datenbankfehlern. Vorhandene Projektdateien bleiben erhalten.


## v1.4.8 – PNG-Hintergrund
Unter Konfiguration → Erscheinungsbild kann ein PNG als Hintergrund für alle Reiter ausgewählt oder der ursprüngliche Hintergrund wiederhergestellt werden. Das Bild wird proportional zentriert und mit reduzierter Deckkraft hinter den Bedienelementen angezeigt. Der Dateipfad wird in app_configuration.json gespeichert; die PNG-Datei muss am gewählten Speicherort verbleiben.


## v1.4.9 – Startfehler behoben
- QPixmap wird nicht mehr vor QApplication initialisiert.
- PNG-Hintergrundfunktion aus v1.4.8 bleibt erhalten.
- Bestehende Datenbank und Song/Projekte bleiben unverändert.


MPW v1.5.0 – PNG-Hintergrund: Bildvorschau, Deckkraftregler (0–100 %), Skalierungsmodus (Füllen, Ganzes Bild, Strecken). Einstellungen bleiben in app_configuration.json gespeichert. Standardhintergrund weiterhin verfügbar.


## v1.5.1 – PNG-Hintergrund dauerhaft sichern
Beim Auswählen wird eine geprüfte Kopie unter ~/MusicProductionWorkstation/appearance/background.png gespeichert. Der ursprüngliche Dateipfad ist danach nicht mehr erforderlich. Maximal 30 MB pro PNG; atomarer Austausch, vorhandenes Bild bleibt bei Kopierfehler erhalten. Bestehende v1.5.0-Bildpfade funktionieren weiter.
\n\n## v1.5.2 – PNG-Bildergalerie\nUnter Konfiguration → Erscheinungsbild können mehrere PNG-Motive (max. 30 MB je Bild) importiert, aus einer Liste ausgewählt und nach Bestätigung wieder gelöscht werden. Identische Imports werden anhand eines SHA-256-Hashs erkannt. Bereits vorhandene background.png aus v1.5.1 bleibt als Galeriemotiv erhalten. Das Entfernen eines aktiven Motivs schaltet zunächst auf den Standardhintergrund. Dateien außerhalb des MPW-Galerieordners werden niemals durch die Löschfunktion entfernt.\n\n\n## v1.5.3 – PNG-Galerie: Motive umbenennen\nIn Konfiguration → Erscheinungsbild lassen sich gespeicherte PNG-Motive umbenennen. Die Funktion akzeptiert nur Dateien innerhalb der MPW-Bildergalerie, prüft Windows-Dateinamen und verhindert das Überschreiben existierender Motive. Bei einem aktiven Hintergrund wird der gespeicherte Pfad automatisch angepasst.\n

## v1.5.4 – Miniaturansicht der PNG-Hintergrundgalerie
Unter Konfiguration → Erscheinungsbild gibt es jetzt eine scrollbare Kachelübersicht mit Miniaturbildern und Motivnamen. Ein Klick aktiviert das Motiv sofort; Dropdown, Kachelmarkierung und Bildvorschau bleiben synchron. Umbenennen und Löschen funktionieren weiter über das Dropdown. Keine Datenbankänderung erforderlich.


## v1.5.5 – Anpassbares Farbschema
Unter Konfiguration → Erscheinungsbild – Farbschema können Hintergrund, Felder/Tabellen, Schrift, Akzent, Schaltflächen, Rahmen, inaktive Reiter und Auswahlfarbe mit dem Windows-Farbdialog individuell gewählt werden. Änderungen werden sofort angewendet und in app_configuration.json gespeichert. Die Standardfarben können mit Bestätigung wiederhergestellt werden. PNG-Hintergrundbilder bleiben verfügbar.


## v1.5.6 – Startfehler behoben
- `QColorDialog` wird korrekt aus `PySide6.QtWidgets` statt `PySide6.QtGui` importiert.
- Alle Funktionen von v1.5.5 bleiben bestehen.
- Syntax- und ZIP-Prüfung durchgeführt; Windows-GUI-Test ausstehend.


## MPW v1.5.7 – Qt-Stylesheet-Warnungen behoben
- Ungültige doppelte schließende CSS-Klammer bei den acht Farbauswahl-Schaltflächen entfernt.
- FFmpeg-Startinformation ist keine Fehlermeldung.
- Datenbank und Benutzereinstellungen bleiben unverändert.
- Python-Syntax und ZIP geprüft; kein vollständiger Windows-GUI-Test.


## v1.5.8 – Farbschema-Vorlagen
Unter Konfiguration → Erscheinungsbild – Farbschema stehen vier sofort nutzbare Vorlagen zur Verfügung: MPW Dunkel, Nachtblau, Anthrazit und Hell. Eine Vorlage wird erst nach Klick auf „Farbschema übernehmen …“ und Bestätigung gespeichert. Individuelle Farben bleiben weiterhin einzeln einstellbar. PNG-Hintergrundbilder werden nicht verändert.


## MPW v1.5.9 – Eigene Farbschema-Vorlagen
- Unter Konfiguration → Erscheinungsbild → Farbschema lassen sich die acht aktuell eingestellten Farben als eigene benannte Vorlage speichern.
- Eigene Vorlagen erscheinen neben den vier integrierten Vorlagen in der Auswahlliste und können übernommen werden.
- Eigene Vorlagen lassen sich nach Sicherheitsabfrage löschen; integrierte Vorlagen sind geschützt.
- Bei gleichen Namen wird vor dem Überschreiben gefragt.
- Speicherung in app_configuration.json unter custom_theme_presets. Bestehende Einstellungen und PNG-Motive bleiben erhalten.


## MPW v1.6.0 – Farbvorlagen importieren und exportieren
- Konfiguration > Erscheinungsbild – Farbschema: ausgewählte Farbvorlage als portable JSON-Datei exportieren.
- Farbvorlage aus JSON importieren; strenge Prüfung auf Formatversion und acht HEX-Farbwerte.
- Bei Namenskonflikten neuen Namen vergeben; integrierte Vorlagen bleiben geschützt.
- Importierte Vorlage wird nicht automatisch aktiviert.
- Keine Änderung an Datenbank, Song/Projekten oder PNG-Galerie.


## MPW v1.6.1 – Live-Vorschau für Farbvorlagen
- Konfiguration > Erscheinungsbild > Farbschema: „Live-Vorschau anzeigen“ zeigt die ausgewählte Vorlage sofort an, ohne app_configuration.json zu ändern.
- „Vorschau beenden“ stellt das zuletzt gespeicherte Farbschema wieder her.
- Beim Verlassen des Reiters Konfiguration wird eine aktive Vorschau automatisch zurückgesetzt.
- „Farbschema übernehmen …“ speichert wie bisher erst nach Bestätigung.
- Während der Vorschau zeigen auch die acht Farbfelder die Vorschauwerte.
- Alle bestehenden PNG- und Datenbankeinstellungen bleiben unberührt.
- Python-Syntax und ZIP-Integrität geprüft; Windows-GUI-Test ausstehend.


## MPW v1.6.2 – Projektindex filtern und sortieren
- Reiter Song/Projekte: Bandfilter mit „Alle Bands“ oder einer konkreten Band.
- Sortierung nach Band/Projekt, Projektname auf-/absteigend oder neuester Projekt-ID.
- Suchfeld und Bandfilter sind kombinierbar; Trefferzähler zeigt sichtbare Song/Projekte.
- Auswahl und Bandfilter bleiben beim Aktualisieren soweit möglich erhalten.
- Keine Datenbankmigration und keine Änderungen an Dateien oder Ordnern.


## v1.6.3 – Projektstatus
- Im Projektindex per Rechtsklick: Projektstatus setzen (Geplant, In Arbeit, Fertiggestellt, Veröffentlicht, Pausiert).
- Statusanzeige pro Projekt und kombinierbarer Statusfilter neben Bandfilter und Sortierung.
- Bestehende Datenbanken werden beim Start um die Spalte `projects.status` ergänzt; Altprojekte erhalten `In Arbeit`.
- Projektstatus ist unabhängig vom Status einzelner Songs; Dateien und Projektordner werden nicht verändert.


## MPW v1.6.4 – Medien Explorer: heller Listenhintergrund korrigiert
- Dateiliste erhält explizite Hintergrund-, Alternativzeilen-, Schrift- und Auswahlfarben aus dem gewählten Farbschema.
- Tabellenkopf folgt ebenfalls dem Farbschema.
- Keine Änderung an Datenbank, Song/Projekten oder Dateien.
- Die grafische Darstellung unter Windows muss nach Installation geprüft werden.


## MPW v1.6.5 – AI Prompt Launcher & Suno
- Live-Zeichenzähler für Style (maximal 1000) und Lyrics (maximal 5000).
- Speichern nur bei gültigem Format und eingehaltenen Limits möglich.
- Bereits vorhandener Vergleich zweier Prompt-Versionen bleibt erhalten.
- Neue Funktion: Version B als TXT in den bestehenden Projektordner `Dokumente` exportieren; vor Überschreiben erfolgt eine Rückfrage.
- Die Datenbank-Versionen bleiben dem Song und damit dem Projekt zugeordnet.
- Projektordner werden beim Export nicht automatisch erstellt.


## v1.6.6 – Vorbelegte Style-/Lyrics-Felder im AI Prompt Launcher
- Im KI-Ergebnisfeld stehen bereits [STYLE] und [/STYLE] sowie [LYRICS] und [/LYRICS].
- Style- und Lyrics-Inhalte einfach zwischen die jeweiligen Markierungen einfügen.
- Die Zeichenprüfung zählt ausschließlich den Inhalt zwischen den Markierungen.
- Ältere MPW-Ausgaben mit [STYLE], [LYRICS] und [END MPW] sowie JSON bleiben lesbar.
- Import aus Datei/Zwischenablage/Weblink ersetzt weiterhin den gesamten Feldinhalt.


## MPW v1.6.7 – Getrennte Style-/Lyrics-Eingabe
- AI Prompt Launcher besitzt zwei eigenständige Textfelder für Style und Lyrics.
- Markierungen werden nicht in den Feldern angezeigt; beim TXT-Song/Projektexport automatisch gesetzt.
- Gespeicherte Datenbankversionen halten Style und Lyrics weiterhin in getrennten Spalten.
- KI-Antworten und Datei-/Zwischenablage-Importe werden automatisch in beide Felder aufgeteilt.
- Zeichenlimits: Style 1.000, Lyrics 5.000 (ohne Markierungen).


## v1.6.8 – zentraler MPW-Speicherort
- Unter Konfiguration > Speicherort für neue Bands den gewünschten Stammordner auswählen.
- MPW kopiert die bestehende Datenbank (SQLite-Backup), Medien, Einstellungen, Erscheinungsbilder und Logs in `<Band-Stammordner>/MPW/`.
- Der ursprüngliche Datenordner bleibt als Sicherheitskopie bestehen; nach der Übertragung MPW neu starten.
- Windows speichert nur den Verzeichnispfad in HKCU\Software\MPW; alle eigentlichen MPW-Daten liegen im neuen MPW-Ordner.
- Standardmäßige automatische Backups liegen unter `<Band-Stammordner>/MPW/backups/`, sofern kein eigener Backup-Speicherort konfiguriert ist.
- Band- und Projektverzeichnisse bleiben direkt unter dem Band-Stammordner und werden nicht verschoben.
- Ein belegter MPW-Zielordner wird nicht überschrieben.
- Bereits explizit konfigurierte externe Backup-Ziele bleiben unverändert.


MPW v1.6.9 – Feldhilfen per Mouseover
----------------------------------
Alle Formular-Feldbezeichnungen erhalten Mouseover-Beschreibungen (Qt-Tooltips). Wichtige Felder haben spezifische Erklärungen, weitere Formularfelder eine allgemeine Feldhilfe. Bestehende Tooltips auf Eingabefeldern bleiben erhalten. Die Hilfen werden nach dem Aufbau aller Reiter eingerichtet.


## v1.7.0 – Mouseover-Farbabgleich
Die Feldbeschreibungs-Tooltips verwenden dieselbe Hintergrundfarbe wie die Eingabefelder (Farbwert `surface`), dieselbe Textfarbe und passende Rahmenfarbe aus dem aktiven Farbthema. Der Tooltip-Stil wird auch auf Anwendungsebene gesetzt, damit eigenständige Qt-Tooltip-Fenster unter Windows die Farben übernehmen. Der Wechsel von Farbvorlagen aktualisiert die Tooltip-Farben.


## MPW v1.7.1 – Reiter-Anleitungen
- Oben rechts in der Registerkartenleiste erscheint ein Info-Symbol (ⓘ). Es öffnet ein separates, schließbares Informationsfenster für den aktuell ausgewählten Reiter.
- Alle 15 Reiter erhalten individuelle Beschreibungen zu Zweck, Aufgaben, Bedienung und wichtigen Hinweisen.
- Die Hilfetexte sind in der Anwendung integriert und funktionieren ohne Internet.
- Keine Änderung an Datenbank oder vorhandenen Benutzerdaten.


## v1.7.2 – Reiter-Hilfe direkt auf dem Blatt
- Info-Symbol befindet sich oben rechts **innerhalb jeder Reiter-Seite**, nicht mehr in der Registerkartenleiste.
- Die Reiter-Titel haben wieder die volle Breite.
- Beim Ändern der Fenstergröße bleibt das Symbol rechts oben auf der jeweiligen Seite.
- Jeder Button öffnet weiterhin die Anleitung genau seiner Seite.


## v1.7.3 – Detaillierte Anleitung AI Prompt Launcher
Die Info-Schaltfläche auf dem Reiterblatt öffnet jetzt eine ausführliche, scrollbare Offline-Anleitung zu sämtlichen Feldern, Schaltflächen, Importwegen, Zeichenlimits, Versionsvergleich, Übernahme, Export, Arbeitsablauf und häufigen Fehlermeldungen. Andere Reiter-Anleitungen bleiben unverändert.


## v1.7.4 – Ausführliche Reiter-Anleitungen
Alle 15 Reiter besitzen nun detaillierte, funktionsorientierte Hilfeseiten. Die bestehende ausführliche AI-Prompt-Launcher-Anleitung bleibt erhalten. Der Info-Button bleibt oben rechts innerhalb des Reiterblatts.


MPW v1.7.5: Die Anleitungen für Songs & Suno, Medien & Player, Releases Distri sowie System & Diagnose wurden anhand der vorhandenen Eingabefelder und Funktionen detailliert erweitert. Bestehende Hilfen bleiben erhalten.


MPW v1.7.6: Alle 15 separaten Reiter-Hilfefenster haben eine Suchleiste. Treffer werden im Hilfetext markiert; Weiter, Zurück und Eingabe navigieren zwischen Fundstellen (mit Umbruch zum Anfang/Ende). Ohne Treffer erscheint eine Meldung. Die ausführlichen Anleitungstexte bleiben unverändert.


## v1.7.7 – Fehlerkorrektur Hilfezuordnung
Die ausführlichen Anleitungen der Reiter Songs & Suno, Medien & Player, Releases Distri und System & Diagnose werden nun über ihren vollständigen Reiternamen aufgerufen. Das Ampersand (&) wird nicht mehr entfernt. Die Hilfesuche aus v1.7.6 bleibt bestehen.


## MPW v1.7.8 – Info-Schaltfläche ohne Überlagerung
- Die Anleitungsschaltfläche erhält auf jedem der 15 Reiter einen eigenen, 39 Pixel hohen Kopfbereich.
- Keine absolute Positionierung mehr: Inhalte und Schaltflächen der Reiter werden nicht verdeckt.
- Die Schaltfläche ist farblich durch die Akzentfarbe des gewählten Themes abgesetzt; Textkontrast und Hoverfarbe werden dynamisch angepasst.
- Reiternamen, Reihenfolge, bestehende Hilfeinhalte und Hilfesuche bleiben erhalten.
- Beim Wechsel des Farbschemas wird auch die Schaltfläche neu eingefärbt.
- Syntax- und Archivprüfung durchgeführt; vollständiger Windows-GUI-Test nicht durchgeführt.

## MPW v1.7.9 – Qt-Warnungen und Reiter-Layout korrigiert
- Kritische Reihenfolge beim Umbau der Reiter korrigiert: erst `removeTab`, dann das ursprüngliche Seiten-Widget in die Hilfekopfzeile umhängen. Verhindert, dass Qt versehentlich den nächsten Reiter entfernt oder leere Widgets entstehen.
- Veralteten Aufruf `QColor.isValidColor` durch `QColor(...).isValid()` ersetzt.
- CSS der Anleitungsschaltfläche mit explizitem Abschluss der Hover-Regel vereinfacht.
- Fehlende Reiter-Widgets werden protokolliert und übersprungen, statt sie dem Layout hinzuzufügen.
- Die FFmpeg-Ausgabe ist eine reine Information der Qt-Multimedia-Bibliothek.
- Syntax und ZIP geprüft; ein GUI-Test unter Windows ist weiterhin erforderlich.
\n\nMPW v1.8.0: Kritischer Fix: Hilfekopfzeile wird direkt in das bestehende QVBoxLayout eingefuegt. Keine Tab-Entfernung, keine Reparenting-Wrapper; alle Reiterinhalte bleiben erhalten.\n\n\nMPW v1.8.1: Info-Buttons auch für die sechs in QScrollArea eingebetteten Reiter; korrigierte QSS-Schaltflächenformatierung und veraltete QColor-Prüfung.\n

## v1.8.2 – AI Prompt Launcher: lesbare obere Bedienelemente
- Band und Ziel-Song/Projekt stehen in getrennten Formularzeilen; die Schaltfläche zum Anlegen des Song-Eintrags erhält eine eigene Zeile.
- API-, Browser- und Speicheraktionen sowie die vier Importaktionen sind auf zweispaltige Schaltflächenraster mit Mindesthöhe verteilt.
- Die Inhalte und Speicherlogik bleiben unverändert.


## v1.8.3 – AI Prompt Launcher: Standardlayout und Scrollen
Die Schaltflächen sind wieder im ursprünglichen horizontalen Standardlayout. Der AI Prompt Launcher ist jetzt eine QScrollArea mit vertikaler Bildlaufleiste bei Bedarf. Die Inhaltsbreite bleibt mindestens 1080 Pixel, damit Buttontexte nicht zusammengedrückt werden; auf schmalen Fenstern kann zusätzlich horizontal gescrollt werden.


## MPW v1.8.4 – Stabilitätsdiagnose
- Zusätzliche nur lesende SQLite-Fremdschlüsselprüfung und Prüfung der Datenbankdatei.
- Diagnose zeigt Anzahl und jüngstes ZIP-Backup, ohne dessen Inhalt zu behaupten oder Daten zu verändern.
- Versionsangabe im Diagnosebericht aktualisiert.
- Bestehende Reiterlayouts und AI Prompt Launcher bleiben unverändert.
- Hinweis: Ein vollständiger Windows-GUI-Test wurde in dieser Umgebung nicht durchgeführt.


## MPW v1.8.5 – Songs & Suno: sichere Prompt-Historie
- Beim Speichern eines Songs wird der vorherige aktive Style-/Lyrics-Prompt automatisch in `prompt_versions` archiviert, sofern sich Style oder Lyrics tatsächlich geändert haben und der vorherige Prompt nicht leer war.
- Ausschließliche Änderungen von Status, Distributor oder Plattformen erzeugen keine unnötigen Prompt-Versionen.
- Sicherung und Song-Aktualisierung laufen in einer SQLite-Transaktion; eine fehlgeschlagene Speicherung hinterlässt keine halbfertige Sicherung.
- Gesicherte Fassungen sind im AI Prompt Launcher über die bestehende Versionsauswahl und den Versionsvergleich verfügbar und können dort wieder als aktiver Prompt übernommen werden.
- Bestehende Reiterlayouts, insbesondere das scrollbare AI-Prompt-Launcher-Layout, bleiben unverändert.
- Syntax und ZIP werden geprüft; Windows-GUI-Tests sind hier nicht verfügbar.
\n\n## v1.8.6 – Audioanalyse\nIm Reiter Medien & Player: Audiodatei auswählen und „Audioqualität analysieren“ klicken. Die nicht-blockierende FFmpeg-loudnorm-Messung zeigt integrierte LUFS, True Peak (dBTP) und LRA. FFmpeg muss installiert und über PATH erreichbar sein. Keine Veränderung an Audiodateien. Die Messung erkennt keine einzelnen Klicks/Artefakte und liefert keine garantierte Clipping-Diagnose.\n

## MPW v1.8.7 – Medien Explorer und aktualisierte Anleitung
- Dateitypfilter für Audio, Bilder, Video und Dokumente; Alle Dateien setzt den Filter zurück. Ordner bleiben sichtbar.
- Schaltfläche „Pfad kopieren“ für markierte Dateien und Ordner.
- Detailanzeige ergänzt um das Änderungsdatum.
- Integrierte Hilfe für Medien Explorer vollständig aktualisiert.
- Hilfe für Medien & Player um die Audioanalyse aus v1.8.6 (LUFS, dBTP, LRA und FFmpeg/PATH) ergänzt.
- Keine Änderungen am bewährten Layout des AI Prompt Launchers, keine Datenbankmigration.
- Die Dateiansicht ist weiterhin nur lesend; Öffnen einer Datei erfolgt mit der System-Standardanwendung.
- Python-Syntax und ZIP werden geprüft; Windows-GUI-Tests stehen aus.


## MPW v1.8.8 – Release-Checkliste

Im Reiter **Releases Distri** gibt es die Schaltfläche **Release-Checkliste prüfen (ohne Speichern)**. Sie prüft den gewählten Song, Distributor, Datum, ISRC-Format und mögliche doppelte ISRCs sowie das 12-/13-stellige UPC/EAN-Format einschließlich Prüfziffer. Die Ergebnisse erscheinen im Feld **Prüfergebnis**. Die Prüfung ist rein lesend und speichert nichts. Eine korrekte Prüfziffer bedeutet nicht, dass eine Kennung offiziell registriert ist. Die Checkliste ersetzt keine Rechte-, Cover- oder Distributor-Prüfung.

Die integrierte Hilfe für Releases Distri wurde entsprechend ergänzt. Das bestehende Layout des AI Prompt Launchers bleibt unverändert.


## MPW v1.8.9 – Backup-Export und Wiederherstellung

- Backup – Archiv → Weitere Archiv-Werkzeuge anzeigen → „Ausgewähltes Backup als ZIP exportieren“.
- Vor dem Export wird das ZIP inklusive enthaltener SQLite-Datenbank geprüft.
- Das ZIP wird an den gewählten Ort kopiert; SHA-256 wird vor und nach dem Kopieren verglichen und das Zielarchiv erneut geprüft.
- Vorhandene Zieldateien werden nicht überschrieben; das Originalarchiv bleibt erhalten.
- Eine Wiederherstellung ist weiterhin eine gesonderte, ausdrücklich zu bestätigende Aktion mit vorgeschalteter Sicherheitskopie.
- Integrierte Hilfe unter „Backup – Archiv“ entsprechend ergänzt.
- Die ZIP-Sicherung umfasst die MPW-Datenbank und importierte MPW-Medien; externe Band-/Projektverzeichnisse außerhalb des zentralen MPW-Medienordners sind nicht automatisch enthalten.

Prüfung: Syntax und Archivstruktur im Entwicklungscontainer; Windows-GUI und praktische Wiederherstellung nicht getestet.


## MPW v1.8.10 – Einheitliche weiße Buttontexte

- Alle normalen Schaltflächen erhalten weiße Beschriftungen, unabhängig von der gewählten Vordergrundfarbe.
- Die Schaltflächen „ⓘ Anleitung“ verwenden ebenfalls durchgehend weiße Schrift.
- Die Farbauswahl-Schaltflächen zeigen ihre jeweilige Farbe als farbigen Rahmen auf dunklem Untergrund, damit auch bei sehr hellen Farben weiße Beschriftungen lesbar bleiben.
- Vorhandene Reiterlayouts, Datenbank und gespeicherte Einstellungen werden nicht verändert.
- Bei sehr hell eingestellten Button- oder Akzentfarben kann der Kontrast weiterhin gering sein; für optimale Lesbarkeit dunklere Button- und Akzentfarben auswählen.


## MPW v1.9.0 – Produktions-Workflow

Im Reiter Songs & Suno steht die neue Schaltfläche „Produktions-Workflow für ausgewählten Song anzeigen“ bereit. Sie zeigt eine rein lesende Übersicht zu Band, Projekt, Songstatus, aktivem Prompt, archivierten Prompt-Versionen, importierten Medien, externen Links, Releases und Plattform-Einträgen. Buttons führen zu den zuständigen Reitern. Die integrierte Anleitung „Songs & Suno“ beschreibt die Funktion. Die Übersicht führt keine Audioanalyse durch und prüft keine externen Streamingdienste. Bestehende Daten, Layouts und Backup-Einstellungen bleiben unverändert.


## MPW v1.9.1 – Produktionsstatus und nächste Arbeitsschritte

Im Reiter **Songs & Suno** öffnet **„Produktions-Workflow & nächste Schritte anzeigen“**
eine lesende Übersicht zum gewählten Song. Neben dem bisherigen Produktionsstatus
zeigt sie konkrete Vorschläge, sofern der aktive Suno-Prompt, lokale Medien,
ein Release-Datensatz oder (bei vorhandenem Release) eine Plattformzuordnung fehlen.
Sind diese Daten vorhanden, empfiehlt MPW die manuelle Endkontrolle von Audioqualität,
Metadaten und Veröffentlichungsstatus. Externe Links zählen nicht als lokale Mediendateien.

Die Aufgabenliste ist eine Momentaufnahme aus der Datenbank, keine automatische
Qualitätsprüfung und kein Task-Management: Sie speichert oder verändert keine Daten.
Die integrierte Hilfe **Songs & Suno → ⓘ Anleitung** wurde entsprechend erweitert.
Das funktionierende Layout der 15 Reiter bleibt unverändert.


## MPW v1.9.2 – Zentrale Produktionsübersicht

Im Reiter „Songs & Suno“ öffnet „Zentrale Produktionsübersicht aller Songs anzeigen“ eine lesende Tabelle über alle Songs. Sie enthält Band, Projekt, Titel, Songstatus, vorhandenen Suno-Prompt, Anzahl lokaler Mediendateien, Releases und noch offene Produktionsschritte. Das Suchfeld filtert Band, Projekt und Titel. Der Statusfilter bietet offene Schritte, fehlenden Prompt, fehlende Medien, fehlenden Release, fehlende Plattform und vollständig erfasste Phasen. Doppelklick wählt den Song in der Songauswahl aus, sofern verfügbar. Die Daten werden beim Öffnen geladen; für aktuelle Werte das Fenster erneut öffnen. Keine automatischen Änderungen an Dateien oder Datenbank. „Alle Phasen erfasst“ ist keine Freigabe für die Veröffentlichung.

Die Schaltfläche „Produktions-Workflow für ausgewählten Song anzeigen“ trägt wieder ihre ursprüngliche Beschriftung und zeigt weiterhin die Empfehlungen zu nächsten Schritten. Die integrierte Reiter-Anleitung wurde entsprechend ergänzt.


## v1.9.3 – Farbkorrektur Produktionsübersicht
Die Tabelle in „Zentrale Produktionsübersicht“ verwendet jetzt die MPW-Themefarben auch für Tabellenhintergrund, abwechselnde Zeilen, Text, Auswahl und Spaltenköpfe. Such- und Filterfunktionen bleiben unverändert.


## v1.9.4 – Direktnavigation aus der Produktionsübersicht
- In der zentralen Produktionsübersicht können markierte Songs über drei neue Schaltflächen direkt in Songs & Suno, Medien & Player oder Releases Distri geöffnet werden.
- Der ausgewählte Song wird im Zielreiter vorausgewählt. Wenn er dort fehlt, erscheint eine Meldung statt einer falschen Zuordnung.
- Die integrierte Anleitung für Songs & Suno wurde entsprechend erweitert.
- Datenbank und Mediendateien werden durch die Navigation nicht verändert.
- Python-Syntax und ZIP-Datei geprüft; Windows-GUI nicht praktisch getestet.


## v1.9.5 – „Nächster Schritt“ direkt anklicken
- In der Zentralen Produktionsübersicht ist die letzte Tabellenspalte direkt anklickbar.
- Der erste fehlende Schritt wird geöffnet: Prompt in Songs & Suno, Medien in Medien & Player, Release/Plattform in Releases Distri. Der jeweilige Song wird vorausgewählt.
- Die Spalte ist bei offenen Schritten unterstrichen und besitzt einen Mouseover-Hinweis.
- Wenn alle erfassten Phasen vorhanden sind, erscheint ein Hinweis zur manuellen Abschlussprüfung.
- Die drei Navigationsbuttons bleiben erhalten; keine Datenbankänderung durch die Navigation.
- Die integrierte Anleitung Songs & Suno ist aktualisiert.
- Python-Syntax und ZIP-Integrität geprüft; Windows-GUI nicht getestet.


## v1.9.6 – Offene Produktionsschritte gezielt auswählen
- In „Zentrale Produktionsübersicht“ zeigt „Nächster Schritt“ den ersten fehlenden Punkt und die Zahl weiterer offener Punkte.
- Ein Mouseover zeigt alle noch fehlenden Phasen. Bei mehreren offenen Phasen öffnet ein Klick eine Auswahlliste; bei genau einer Phase wird direkt navigiert.
- Die gewählte Phase öffnet Songs & Suno, Medien & Player oder Releases Distri mit der passenden Songauswahl. Abbrechen ändert nichts.
- Die integrierte Anleitung unter Songs & Suno wurde aktualisiert.
- Die Produktionsübersicht bleibt lesend; nach Änderungen erneut öffnen, um den Datenstand zu aktualisieren.
- Python-Syntax und ZIP-Integrität geprüft; Windows-GUI nicht getestet.


## v1.9.7 – Detaillierte Produktionskontrolle
- In der Zentralen Produktionsübersicht Song markieren und „Detaillierte Produktionskontrolle für markierten Song“ wählen.
- Prüft lesend: Style/Lyrics, zugeordnete Audio- und Coverdateien, Release-Metadaten (Distributor, Datum, ISRC, UPC/EAN), Plattformen und Plattformlinks.
- Zeigt offene Angaben und vorhandene Einträge separat. Keine Datenänderungen, keine automatischen Qualitäts- oder Rechteprüfungen.
- Die integrierte Anleitung unter Songs & Suno ist aktualisiert.
- Python-Syntax und ZIP-Integrität geprüft; Windows-GUI nicht getestet.


## MPW v1.9.8 – Fehlerbehebung Produktionskontrolle
- Korrigierte SQL-Zeichenketten in der Detailkontrolle der Zentralen Produktionsübersicht.
- Die Prüfung von Style/Lyrics verwendet jetzt gültige SQLite-COALESCE-Ausdrücke und funktioniert auch bei NULL-Werten.
- Keine Datenbankmigration und keine Änderung an gespeicherten Daten.
- Die integrierte Anleitung und die Oberfläche bleiben ansonsten unverändert.


## MPW v1.9.9 – Direkte Bearbeitung aus der Detailkontrolle
- In Songs & Suno → Zentrale Produktionsübersicht → Detaillierte Produktionskontrolle kann ein offener Eintrag ausgewählt und über „Ausgewählten offenen Punkt bearbeiten“ geöffnet werden.
- Der zugehörige Song wird im Zielreiter vorausgewählt. Bei Style/Lyrics, Distributor, Datum, ISRC und UPC/EAN wird das passende Feld fokussiert; Audio/Cover führen zur Medienverwaltung und Plattformprobleme zur Release-Liste.
- Keine automatische Datenänderung oder Dateiübernahme. Die vorhandenen Reiterlayouts bleiben unverändert.
- Die integrierte Anleitung Songs & Suno wurde erweitert.
- Python-Syntax und ZIP-Integrität geprüft; vollständiger Windows-GUI-Test nicht möglich.


## MPW v2.0.0 – Integrations- und Stabilitätsprüfung
- Die bestehende Oberfläche und alle 15 Reiter bleiben unverändert.
- Neuer isolierter Selbsttest für Datenbankschema, SQLite-Integrität, Fremdschlüssel, die SQL-Abfrage der Produktions-Detailkontrolle sowie Vollständigkeit der integrierten Reiterhilfen.
- Aufruf im Programmordner: `python workstation.py --self-test` (mit installierten Abhängigkeiten).
- Der Selbsttest verwendet ein temporäres Testverzeichnis und öffnet keine produktive MPW-Datenbank.
- Ein bestandener Selbsttest ersetzt keinen vollständigen Windows-GUI-Test und prüft nicht jede Funktion.
- Die Hilfe im Programm bleibt inhaltlich unverändert, da keine neuen Bedienfelder hinzukommen.


## MPW v2.0.1 – Korrektur des Selbsttests
- Die Hilfen-Prüfung berücksichtigt jetzt die separate ausführliche HTML-Anleitung des AI Prompt Launchers.
- Für die anderen Reiter wird weiterhin geprüft, ob die Detailanleitung vorhanden und nicht leer ist.
- Keine Änderungen an Datenbank, Bedienoberfläche oder produktiven Daten.
- Selbsttest: `python workstation.py --self-test`.
- Python-Syntax und ZIP-Integrität geprüft; vollständiger Selbsttest erfordert PySide6 und wurde hier nicht ausgeführt.


## MPW v2.0.2 – Grafische Produktionsfortschrittsanzeige
- In Songs & Suno → Zentrale Produktionsübersicht zeigt eine neue Spalte den Fortschritt pro Song als Balken mit Prozentwert (0, 25, 50, 75 oder 100 %).
- Grundlage sind vier erfasste Datenphasen: Suno-Prompt, lokale Medien, Release und Plattformzuordnung. Die Werte sind eine Momentaufnahme beim Öffnen des Fensters.
- Der Fortschritt ist kein Nachweis für Audioqualität, Coverfreigabe, Rechte oder eine tatsächliche Veröffentlichung.
- Die anklickbare Spalte „Nächster Schritt“, Filter und Navigation bleiben erhalten.
- Die integrierte Anleitung „Songs & Suno“ erklärt die Fortschrittsanzeige.
- Kein Eingriff in Datenbank oder bestehende Projektdateien.


## MPW v2.0.3 – Sortierung der Produktionsübersicht

In Songs & Suno → Zentrale Produktionsübersicht gibt es eine zusätzliche Sortierung nach Band/Projekt/Song, Fortschritt aufsteigend oder absteigend sowie Anzahl offener Schritte. Die Statuszeile zeigt, wie viele der aktuell sichtbaren Songs noch offene Schritte haben. Suche und Filter werden zuerst angewendet; Sortierung verändert keine Daten. Die integrierte Hilfe für Songs & Suno wurde entsprechend ergänzt.


## MPW v2.0.4 – Erweiterte Produktionsfilter

- In Songs & Suno → Zentrale Produktionsübersicht stehen zusätzliche Filter für Band, Songstatus und Veröffentlichungsstand zur Verfügung.
- Songstatus: Alle, In Bearbeitung, Fertig, Veröffentlicht, Ohne Status.
- Veröffentlichungsstand: Alle, Noch kein Release, Release ohne Plattform, Release mit Plattform, Vier Phasen erfasst.
- Die Filter wirken gemeinsam mit Textsuche, bisherigen Phasenfiltern und Sortierung. Die Statuszählung bezieht sich auf die gefilterten Songs.
- Der Veröffentlichungsstand beschreibt ausschließlich vorhandene Datenbankeinträge; keine externe Veröffentlichung wird überprüft.
- Keine Schemaänderung oder Datenmigration; alle 15 Reiter und bestehende Bedienfunktionen bleiben erhalten.
- Die integrierte Hilfe für Songs & Suno ist aktualisiert.
- Windows-Selbsttest: `python workstation.py --self-test`.


## MPW v2.0.5 – CSV-Export der Produktionsübersicht

- In Songs & Suno → Zentrale Produktionsübersicht gibt es „Gefilterte Übersicht als CSV exportieren“.
- Exportiert ausschließlich aktuell sichtbare Songs unter Berücksichtigung sämtlicher Suchfilter und der eingestellten Sortierung.
- Spalten: Band, Projekt, Song, Songstatus, Prompt, Medienanzahl, Releaseanzahl, Plattformanzahl, Fortschritt (%), Nächster Schritt.
- Excel-kompatibles CSV: Semikolon als Trennzeichen und UTF-8 mit BOM; CSV-Werte werden korrekt quotiert.
- Export enthält den Datenstand beim Öffnen der Übersicht. Der Export ändert keine Datenbankeinträge.
- Bei leerem Filterergebnis wird keine Datei erzeugt.
- Integrierte Anleitung für Songs & Suno aktualisiert; 15 Reiter und bestehendes Layout unverändert.
- Windows-Selbsttest: `python workstation.py --self-test`.


## v2.0.6 – Bezeichnung Song/Projekte
Die sichtbare Bezeichnung „Projekte“ wurde in der Anwendung, den Hilfetexten und der Dokumentation in „Song/Projekte“ geändert. Die interne SQLite-Tabelle `projects`, gespeicherte Projektnamen und bestehende Ordner bleiben unverändert, um die Datenkompatibilität zu gewährleisten.


## MPW v2.0.7 – Produktionsstatistik

In Songs & Suno → Zentrale Produktionsübersicht öffnet die Schaltfläche „Produktionsstatistik anzeigen“ eine lesende Auswertung der **aktuell gefilterten** Songliste. Die Übersicht enthält Songanzahl, durchschnittlichen Fortschritt, offene Produktionsschritte und Anzahl der Songs mit vier erfassten Phasen – insgesamt sowie aufgeschlüsselt nach Band. Die Auswertung ändert keine Daten und ersetzt keine Qualitäts- oder Veröffentlichungsprüfung. Die integrierte Hilfe wurde ergänzt.


## MPW v2.0.8 – Korrektur weißer Felder in der Produktionsstatistik

Die Tabelle im Dialog „Produktionsstatistik anzeigen“ übernimmt nun die bereits für die Zentrale Produktionsübersicht festgelegte Farbpalette und Tabellenformatierung. Damit werden weiße Tabellenflächen bei dunklen MPW-Farbschemata vermieden. Keine Änderung an Datenbank, Berechnungen oder bestehenden 15 Reitern.

Selbsttest: `python workstation.py --self-test`


## MPW v2.0.9 – Grafische Produktionsstatistik

In **Songs & Suno → Zentrale Produktionsübersicht → Produktionsstatistik anzeigen** enthält die Statistik jetzt eine grafische Spalte für den durchschnittlichen Produktionsfortschritt je Band und eine zusätzliche Tabelle mit Songstatus, Anzahl und Prozentanteil. Beide Darstellungen basieren auf der aktuell gefilterten Songliste. Die Tabellen und Balken verwenden das eingestellte MPW-Farbschema (keine weißen Standardflächen). Die vier Produktionsphasen sind reine Vollständigkeitsindikatoren und kein Nachweis für Audioqualität oder Veröffentlichung. Datenbankschema, gespeicherte Daten, alle 15 Reiter und bestehende Funktionen bleiben unverändert.


## MPW v2.0.10 – CSV-Export der Produktionsstatistik

Im Fenster **Produktionsstatistik anzeigen** steht nun **Statistik als CSV exportieren** zur Verfügung. Exportiert werden die Kennzahlen der aktuell gefilterten Songs, eine Auswertung je Band sowie die Songstatus-Verteilung in einer gemeinsamen CSV-Datei. Das Format ist UTF-8 mit BOM und Semikolon-Trennzeichen (Excel-kompatibel). Der Export ist rein lesend und verändert keine Datenbankeinträge. Die Prozentwerte basieren auf vier erfassten Produktionsphasen und bestätigen keine tatsächliche Veröffentlichung oder Audioqualität.


## MPW v2.0.11 – Produktionsstatistik nach Song/Projekten

- In **Songs & Suno → Zentrale Produktionsübersicht → Produktionsstatistik anzeigen** gibt es eine zusätzliche Tabelle **Song/Projekte** mit Band, Projekt, Songanzahl, durchschnittlichem Fortschritt, offenen Schritten, vier erfassten Phasen und einem Fortschrittsbalken.
- Gleichnamige Projekte verschiedener Bands werden getrennt ausgewertet.
- Alle Auswertungen basieren auf der aktuellen Filterauswahl und verändern keine Daten.
- **Statistik als CSV exportieren** enthält jetzt auch einen eigenen Abschnitt mit den Song/Projekt-Kennzahlen. CSV: Semikolon, UTF-8 BOM.
- Die Tabellen übernehmen das bestehende MPW-Farbschema; bestehende 15 Reiter und Datenbankschema bleiben unverändert.
- Prüfung: `python workstation.py --self-test`; anschließend Statistikfenster und CSV-Export unter Windows testen.


## MPW v2.0.12 – Song/Projekt-Detailansicht
In „Songs & Suno → Zentrale Produktionsübersicht → Produktionsstatistik anzeigen“ kann eine Zeile der Song/Projekt-Tabelle doppelt angeklickt werden. Ein neues Fenster zeigt die einzelnen Songs des Projekts mit Songstatus, Fortschritt in Prozent, offenen Produktionsphasen und nächstem Schritt. Die Ansicht berücksichtigt die Filter der Produktionsübersicht. Über „Ausgewählten Song in Songs & Suno öffnen“ kann der markierte Song direkt geöffnet werden. Die Auswertung ist lesend; bestehende Daten und Datenbankstruktur bleiben unverändert.


## MPW v2.0.13 – Filter für offene Produktionsphasen

In **Songs & Suno → Zentrale Produktionsübersicht → Produktionsstatistik anzeigen** ein Song/Projekt doppelt anklicken. Die Detailansicht bietet jetzt **Offene Produktionsphase**: Alle Songs, mindestens ein offener Schritt, Prompt fehlt, lokale Medien fehlen, Release fehlt, Plattform fehlt oder keine offenen Schritte. Die Anzeige „X von Y Songs“ aktualisiert sich sofort. Die Auswahl filtert nur die angezeigten Zeilen und verändert weder Datenbank noch Projektdateien. Die direkte Navigation öffnet nur einen sichtbaren ausgewählten Song. Die vorhandenen 15 Reiter und die MPW-Farben bleiben erhalten.

Selbsttest: `python workstation.py --self-test`. Unter Windows zusätzlich alle Filter und die Navigation prüfen.


## MPW v2.0.14 – Song-Produktionscheckliste

Unter **Songs & Suno → Zentrale Produktionsübersicht → Produktionsstatistik anzeigen** ein Song/Projekt doppelt anklicken, einen sichtbaren Song markieren und **Produktionscheckliste anzeigen** wählen. Das neue Fenster prüft automatisch die vier vorhandenen Produktionsphasen (Prompt, lokale Medien, Release, Plattform) und listet zusätzlich manuelle Abschlussprüfungen für Audioqualität, Cover, Rechte und Metadaten. Mit **Checkliste kopieren** wird der Prüftext in die Zwischenablage übertragen. Die Ansicht ist rein lesend; manuelle Häkchen werden **nicht** dauerhaft gespeichert. Die bestehende Datenbank und alle 15 Reiter bleiben unverändert.

Prüfung: `python workstation.py --self-test`; unter Windows anschließend Detailansicht, Checkliste und Kopierfunktion prüfen.


## MPW v2.0.15 – Manuelle Produktionsprüfungen speichern

In Songs & Suno → Zentrale Produktionsübersicht → Produktionsstatistik anzeigen → Song/Projekt doppelklicken → Song auswählen → Produktionscheckliste anzeigen lassen sich vier manuelle Abschlussprüfungen per Checkbox abhaken: Audioqualität/Peaks, Cover/Bildrechte, Musik-/Nutzungsrechte und Metadaten/ISRC/UPC. Jede Änderung wird unmittelbar pro Song in der lokalen SQLite-Datenbank gespeichert. Die Kopierfunktion berücksichtigt den aktuellen Zustand.

Die Datenbankmigration ist additiv: Neue Tabelle `song_manual_checks`, keine Umbenennung oder Änderung vorhandener Song- und Projekttabellen. Bei Songlöschung werden die zugehörigen Prüfungen per Fremdschlüssel automatisch entfernt. Die vier automatischen Produktionsphasen bleiben unverändert und zählen weiterhin allein für die Fortschrittsanzeige. Der isolierte Selbsttest überprüft auch Speichern und Löschweitergabe.


## MPW v2.0.16 – Manuelle Prüfungen in der Produktionsstatistik

Die Produktionsstatistik zeigt zusätzlich die vier manuell gespeicherten Prüfpunkte Audio, Cover, Rechte und Metadaten für jeden Song der aktuellen Filterauswahl. Eine Zusammenfassung zählt erledigte Prüfungen und Songs mit allen vier Häkchen. Der Statistik-CSV-Export enthält eine entsprechende Song-Tabelle. Die vier automatischen Produktionsphasen und ihre Fortschrittsberechnung bleiben unverändert. Die Tabelle übernimmt die MPW-Farben. Statistikwerte sind eine Momentaufnahme beim Öffnen; für aktuelle Werte das Statistikfenster erneut öffnen.

Test: `python workstation.py --self-test`; unter Windows die Statistik und den CSV-Export prüfen.


## MPW v2.0.17 – Getrennte Produktionsbereitschaft

Unter **Songs & Suno → Zentrale Produktionsübersicht → Produktionsstatistik anzeigen**
zeigt die neue Tabelle **Produktionsbereitschaft** für jeden Song zwei unabhängige Werte:
vier automatisch erfasste Phasen (Prompt, Medien, Release, Plattform) und vier
manuell bestätigte Prüfpunkte (Audio, Cover, Rechte, Metadaten). Beide werden
als X/4 und Prozentwert dargestellt. **Offen gesamt** zählt die fehlenden Punkte
beider Bereiche. **8/8 erfasst** bedeutet nur, dass alle acht Datenpunkte
eingetragen bzw. abgehakt sind – keine Qualitätszertifizierung und kein Nachweis
einer tatsächlichen Veröffentlichung. Die Statistik-CSV enthält diese Werte.
Die Ansicht berücksichtigt die aktuellen Filter. Keine Änderung am DB-Schema.
Die Farbanpassung der Statistik wird für die neue Tabelle übernommen.


## MPW v2.0.18 – Filter für Produktionsbereitschaft

Im Statistikfenster gibt es oberhalb der Tabelle **Produktionsbereitschaft** einen Filter:
**Alle Songs**, **Manuelle Prüfungen offen**, **Automatische Phasen offen**,
**Mindestens ein Punkt offen** und **8/8 erfasst**. Der Zähler zeigt die
Anzahl sichtbarer Songs. Die Filterung betrifft ausschließlich diese Tabelle;
alle anderen Statistikbereiche behalten die Filterauswahl der Zentralen
Produktionsübersicht. Beim CSV-Export wird **nur der Abschnitt
Produktionsbereitschaft** zusätzlich nach dieser Auswahl gefiltert; die anderen
Abschnitte bleiben vollständig. Der Filter verändert keine Daten.
Die 15 Reiter, bestehende SQLite-Daten und Farbschemata bleiben erhalten.


## MPW v2.0.19 – Projektübergreifende offene Aufgaben

In Songs & Suno → Zentrale Produktionsübersicht öffnet „Projektübergreifende offene Aufgaben anzeigen“ eine Liste der noch fehlenden automatischen Phasen und manuellen Prüfungen aller aktuell gefilterten Songs. Filter nach automatischen oder manuellen Aufgaben; Doppelklick oder Button navigiert zum betreffenden Song im passenden Reiter. Keine Datenänderung beim Anzeigen; manuelle Häkchen werden weiterhin über die Song-Produktionscheckliste gesetzt.


## MPW v2.0.20 – Fehlerkorrektur: offene Aufgaben

Die projektübergreifende Aufgabenübersicht liest abgeschlossene manuelle Prüfungen
aus der tatsächlich vorhandenen SQLite-Spalte `song_manual_checks.completed`
(statt der nicht existierenden Spalte `checked`). Die bisherige Fehlermeldung
`sqlite3.OperationalError: no such column: checked` wird damit behoben.
Der isolierte Selbsttest prüft nun zusätzlich diese Abfrage bei gesetztem und
wieder entferntem Häkchen. Bestehende Daten und Datenbankschema bleiben unverändert.


## MPW v2.0.21 – Navigation aus offenen Aufgaben korrigiert

Beim Öffnen einer Aufgabe werden nun zuerst die beiden modalen Dialoge geschlossen.
Anschließend wird der Zielreiter im Hauptfenster aktiviert und der betroffene Song
ausgewählt. Das verhindert, dass die Produktionsübersicht den Reiterwechsel verdeckt.
Die Auswahl wird erneut geprüft; fehlende Songs führen zu einer Fehlermeldung.
Keine Änderung an Datenbank, Songdaten oder Reiterstruktur.


## MPW v2.0.22 – Priorisierung offener Aufgaben

Die projektübergreifende Aufgabenübersicht zeigt eine zusätzliche Prioritätsspalte (Hoch, Mittel, Normal) und eine Sortierauswahl. Rechte- und Bildrechteprüfungen werden als Hoch vorgeschlagen; andere Aufgaben folgen einer einfachen regelbasierten Reihenfolge. Die Priorität ist nicht editierbar und wird nicht in der Datenbank gespeichert. Die bestehenden Filter und die direkte Navigation zum Song bleiben erhalten.


## v2.0.23 – Reiterbezeichnung
Die Reiterkarte „Releases & Distributor“ heißt nun „Releases Distri“. Die internen Navigationsziele und Hilfeschlüssel wurden entsprechend angepasst; die SQLite-Datenbank bleibt unverändert.


## v2.0.24 – Album-Druckansicht als Fenster in Album-Details

- Der separate Reiter „Album-Druckansicht“ entfällt; die Anwendung hat jetzt 14 Hauptreiter.
- Im Reiter „Album-Details“ öffnet die Schaltfläche „Album-Druckansicht öffnen“ ein eigenständiges Dialogfenster.
- Vorschau aktualisieren, HTML-Export und Schließen sind direkt im Dialog erreichbar.
- Die Vorschau verwendet weiterhin das in „Plattensammlung“ ausgewählte Album.
- Die integrierte Hilfe für „Album-Details“ erklärt die neuen Bedienelemente.
- Keine Änderung an der Datenbank, Albumdaten oder vorhandenen HTML-Exportfunktionen.
- Selbsttest: `python workstation.py --self-test`.


## v2.0.25 – Kontrastkorrektur der Album-Druckansicht

- Die Album-Druckvorschau hat unabhängig vom globalen Farbschema einen weißen Hintergrund und dunkel lesbare Schrift.
- HTML-Elemente einschließlich Tabellenzeilen, Tabellenköpfen, Metadaten und Songanzahl erhalten explizite Textfarben.
- Der HTML-Export verwendet dieselben druckfreundlichen Farben.
- Albumdaten und Datenbankstruktur bleiben unverändert.
- Selbsttest: `python workstation.py --self-test`.


## v2.0.26 – Erscheinungsbild in eigenem Fenster

- Auf „Konfiguration“ ersetzt „Erscheinungsbild einstellen …“ die beiden großen Bereiche für Farbschema und Hintergrundbild.
- Das neue separate, scrollbar ausgestattete Fenster enthält alle bisherigen Farbvorlagen, Farbfelder, PNG-Galerie, Bildvorschau, Deckkraft und Bildanpassung.
- Schließen des Fensters verwirft keine bereits angewendeten Einstellungen; die bestehende Speicherlogik bleibt unverändert.
- Keine Änderung an Datenbank, Songdaten oder der Anzahl der 14 Hauptreiter.
- Integrierte Hilfe für „Konfiguration“ ergänzt.
- Selbsttest: `python workstation.py --self-test`.


## v2.0.27 – Konfigurierbare Song/Projekt-Unterordner

Unter **Konfiguration → Song/Projekt-Unterordner konfigurieren …** öffnet sich ein eigenes Fenster. Dort lassen sich Anzahl (1 bis 10) und Namen der bei neuen Song/Projekten angelegten Unterordner bearbeiten. Standardmäßig sind Bilder, Dokumente, Musik, OLD und Video eingestellt. Die Vorlage wird in `app_configuration.json` gespeichert.

**Datenschutz und Bestandsschutz:** Beim Speichern der Vorlage werden keine existierenden Band- oder Projektordner verändert. Es wird nichts umbenannt, verschoben oder gelöscht. Neue Projekte erhalten die neue Vorlage. Die bestehende Funktion „Fehlende Unterordner für alle Song/Projekte ergänzen“ ist eine separate, ausdrücklich zu bestätigende Aktion, die ausschließlich fehlende Verzeichnisse hinzufügt und vorhandene Inhalte beibehält.


## v2.0.28 – Automatisches Prompt-TXT-Archiv je Band

- Jeder neu angelegte bzw. übernommene Bandordner erhält zusätzlich den festen Unterordner `Song-Prompts`.
- Dieser Band-Unterordner erscheint **nicht** in der editierbaren Liste der maximal zehn Song/Projekt-Unterordner und kann dort nicht umbenannt werden.
- Im AI Prompt Launcher legt **„Als neue Version speichern“** zusätzlich zur Datenbankversion eine UTF-8-Textdatei mit Songtitel, Zeitstempel und Versions-ID an. Enthalten sind Style und Lyrics.
- Dateischema: `Songtitel_YYYY-MM-DD_HH-MM-SS_Mikrosekunden_V123.txt`.
- Bereits vorhandene Dateien und Ordner werden niemals gelöscht, verschoben oder überschrieben. Bei älteren Bandordnern wird `Song-Prompts` erst beim nächsten erfolgreichen Speichern eines Prompts ergänzt.
- Kann die TXT-Datei nicht erstellt werden, meldet MPW den Fehler; die bereits gespeicherte Datenbankversion bleibt erhalten.


## MPW v2.0.29 – Song-Prompt-Archiv direkt öffnen

Im AI Prompt Launcher gibt es die neue Schaltfläche **„Song-Prompts-Ordner öffnen“**. Sie öffnet den bereits vorhandenen, fest benannten Archivordner der ausgewählten Band im Windows-Explorer. Fehlt der Archivordner, wird ein Hinweis angezeigt: Die Schaltfläche legt selbst keine Ordner oder Dateien an. Der Archivordner wird weiterhin erst beim Speichern einer Prompt-Version automatisch angelegt. Die bis zu zehn konfigurierbaren Song/Projekt-Unterordner bleiben davon unabhängig. Vorhandene Bandordner, Prompt-Dateien und Songdaten werden nicht verändert oder gelöscht.


## MPW v2.0.30 – Eigene Medienordner pro Song (erste Umstellungsstufe)

Jeder neu angelegte Song erhält unter Band/Projekt einen eigenen Ordner mit stabiler Song-ID und den vier festen Unterordnern `Cover`, `Audio`, `Dokumente`, `Video`. Medienimporte kopieren Dateien direkt in diese Ordner; neue Medien werden **nicht** in `media_assets` registriert. Gleichnamige Dateien werden niemals überschrieben. Bestehende Datenbankeinträge und alte Mediendateien bleiben erhalten und werden in Medien & Player zusätzlich angezeigt. Die vier festen Felder in der Ordnerkonfiguration sind schreibgeschützt, bis zu sechs weitere Ordner können ergänzt werden.

**Wichtig – gestaffelte Migration:** Vorhandene Songs erhalten nicht automatisch neue Verzeichnisse; diese entstehen beim nächsten Import. Alte Medien werden nicht automatisch verschoben. Einige Auswertungen und Album-Funktionen verwenden weiterhin den alten Medienindex und müssen in einer Folgeversion auf die Dateisystem-Erkennung umgestellt werden. Vor dem Produktiveinsatz Backup erstellen und die Pfade mit einem Test-Song prüfen.


## v2.0.31 – Alte Musikordner gesammelt übernehmen
Unter Konfiguration → „Alte Musikordner gesammelt übernehmen …“ gibt es eine Vorschau für alle Bands und Projekte. Dateien aus alten Projektordnern „Musik“ werden nur dann Songordnern „Audio“ zugeordnet, wenn die Zuordnung eindeutig ist: bei einem Song im Projekt automatisch, bei mehreren Songs nur über einen eindeutigen Songtitel im Dateinamen. Unklare Dateien bleiben unberührt. Standardmäßig werden Dateien kopiert; optional ist Verschieben nach SHA-256-Prüfung möglich. Gleichnamige Dateien werden nie überschrieben. Leere alte Ordner werden nicht gelöscht. Ein TXT-Protokoll wird im MPW-Datenordner abgelegt. Vor dem Verschieben unbedingt ein Backup erstellen.


## v2.0.32 – Vollständige Audio-Sammelmigration
Die Sammelmigration berücksichtigt **alle erkannten Audiodateien** aus alten Projekt/Musik-Ordnern, einschließlich Unterordnern. Bei mehreren Songs werden Dateien mit eindeutigem Songtitel nur diesem Song zugeordnet; ohne eindeutige Zuordnung werden sie in **alle Song/Audio-Verzeichnisse des Projekts** kopiert. Damit gehen unklare Dateien nicht verloren. Projekte ohne Songziel sowie unsichere symbolische Verzeichnisse bleiben aus Sicherheitsgründen ausgenommen und werden protokolliert. Bei „Verschieben“ wird die Quelldatei erst gelöscht, wenn **alle** Zielkopien per SHA-256 verifiziert sind. Alte Verzeichnisse werden nie gelöscht. Vorher Backup erstellen.


## v2.0.33 – Gemeinsame Medienordner pro Projekt

**Neue Struktur:** `Band/Projekt/Cover`, `Band/Projekt/Audio`, `Band/Projekt/Dokumente`, `Band/Projekt/Video`. Alle Songs desselben Projekts verwenden diese vier gemeinsamen Verzeichnisse. Bis zu sechs zusätzliche Unterordner können konfiguriert werden. Die vier festen Ordnernamen bleiben schreibgeschützt.

Neue Medienimporte werden im gemeinsamen Projektordner gespeichert. Die Medienansicht berücksichtigt weiterhin vorhandene alte Song-Unterordner (`Songtitel [Song-ID]`) lesend. **Es werden keine bestehenden Ordner gelöscht, verschoben oder umbenannt.** Die Sammelmigration aus `Projekt/Musik` kopiert jede Audiodatei nur einmal nach `Projekt/Audio`, auch wenn das Projekt mehrere Songs hat. Verschieben entfernt die Quelle erst nach SHA-256-Prüfung. Vor dem Einsatz bitte ein Backup erstellen.

**Hinweis:** Die Medienansicht zeigt gemeinsame Projektdateien bei allen Songs des Projekts. Bereits bestehende Medienindex-Einträge und ältere Album-Auswertungen bleiben als Kompatibilität erhalten; vollständige Bereinigung des alten Medienindex ist nicht Teil dieses Updates.


## v2.0.34 – Rekursive Übernahme aller Audiodateien

Unter Konfiguration → „Alte Musikordner gesammelt übernehmen …“ werden alle unterstützten Audiodateien aus jedem alten Projektordner `Musik` **einschließlich sämtlicher Unterordner** erfasst. Die ursprüngliche Unterordnerstruktur wird unter `Projekt/Audio` erhalten (z. B. `Musik/Stems/Drums.wav` → `Audio/Stems/Drums.wav`). Gleichnamige, unterschiedliche Zieldateien werden nicht überschrieben, sondern nummeriert. „Sicher kopieren“ erhält die Quellen. „Verschieben“ entfernt die jeweilige Quelldatei erst nach erfolgreicher SHA-256-Prüfung. Verzeichnisse selbst werden nicht gelöscht. Projekte ohne Song-Zuordnung und unsichere symbolische Links werden protokolliert und übersprungen.


## v2.0.35 – Projektordner-Cover als Windows-Ordnersymbol

Beim Import eines Coverbildes in `Band/Projekt/Cover` erstellt MPW unter Windows automatisch ein Windows-Explorer-Ordnersymbol für den **Projektordner** `Band/Projekt`. Es wird das alphabetisch erste lesbare Bild aus dem Cover-Ordner verwendet. MPW erzeugt `mpw_project_cover.ico` und `desktop.ini` direkt im Projektordner; der Windows-Explorer zeigt das Cover nach einer Aktualisierung gegebenenfalls verzögert als Ordnersymbol. Unter Konfiguration → „Projektordner-Symbole aus Covern erstellen …“ lassen sich bereits vorhandene Projekte gesammelt nachrüsten. Bestehende `desktop.ini`-Dateien oder Symboldateien werden nicht überschrieben. Coverbilder und andere Medien werden weder verschoben noch gelöscht. Bei Änderungen am Cover bleibt ein bereits gesetztes Symbol unverändert; eine automatische Neugenerierung findet bewusst nicht statt. Diese Funktion ist nur unter Windows wirksam.


## v2.0.36 – Projektdateien gesammelt nach Medientyp sortieren

Unter **Konfiguration → Projektdateien nach Bilder / Audio / Video sortieren …** lassen sich Medien-Dateien, die direkt im Stammverzeichnis eines Song/Projekts liegen, für alle Projekte gesammelt verschieben. Bilddateien gehen nach `Bilder`, Audiodateien nach `Audio`, Videodateien nach `Video`. Bereits vorhandene Unterordner werden nicht rekursiv umsortiert. `folder.*` (unabhängig von Groß-/Kleinschreibung), `.ico`, `desktop.ini` und `Thumbs.db` sind ausgeschlossen, damit Windows-Ordnersymbole erhalten bleiben. Zieldateien werden nie überschrieben. Nach einer Vorschau und Bestätigung werden Dateien kopiert, per SHA-256 verifiziert und erst danach am alten Ort entfernt. Eine TXT-Protokolldatei wird im MPW-Datenverzeichnis angelegt. Vor der Sammelverschiebung unbedingt ein Backup erstellen.


## v2.0.37 – CSV-Export der Projektdateien-Sortiervorschau

Im Dialog **Konfiguration → Projektdateien nach Bilder / Audio / Video sortieren …** gibt es jetzt **Vorschau als CSV exportieren**. Die CSV-Datei enthält alle geplanten Verschiebungen mit Quell- und Zielpfad sowie geschützte beziehungsweise übersprungene Dateien mit Begründung. UTF-8 mit BOM und Semikolon-Trennung erleichtert die Anzeige in deutschem Excel. Der CSV-Export verändert keine Dateien; die eigentliche Verschiebung erfordert weiterhin eine separate ausdrückliche Bestätigung. Ordnersymbole (`folder.*`, `.ico`, `desktop.ini`) bleiben geschützt.


## v2.0.38 – Bandfilter bei der Projektdateien-Sortierung
Im Fenster Konfiguration → Projektdateien nach Bilder / Audio / Video sortieren kann jetzt eine einzelne Band oder Alle Bands ausgewählt werden. Der Filter gilt für Vorschau, CSV-Export und die bestätigte Sammelverschiebung. Die Sortierung bleibt auf Dateien direkt in den Projekt-Stammordnern begrenzt; folder.*, ICO und desktop.ini sind geschützt. Vor dem Verschieben eine Datensicherung erstellen.


## v2.0.39 – Neutraler Beispiel-Bandname

Im Reiter Bands verwendet die Funktion „Mondfunken Kollektiv Beispielprofil anlegen“ ab sofort ausschließlich den frei erfundenen Beispielnamen „Mondfunken Kollektiv“. Die Bezeichnung wurde in der Schaltfläche, der integrierten Hilfe, den Beispiel-Datenbankabfragen und der Bestätigung ersetzt. Bereits bestehende Banddatensätze, Projektordner und Dateien werden ausdrücklich nicht umbenannt oder geändert.


## v2.0.40 – Bereinigte Anleitungen

Im Fenster „Anleitung – Bands“ wird der Abschnitt „Fester Prompt-Ordner“ nur noch einmal angezeigt. Die identischen mehrfach angehängten Hilfetexte wurden aus dem Programmcode entfernt. Auch die Wiederholungen des Hinweises in „Konfiguration“ wurden bereinigt. Es werden keine Banddaten, Medien oder Verzeichnisse geändert.


## v2.0.41 – Automatischer Button-Textkontrast

Die Textfarbe normaler Schaltflächen wird aus der tatsächlichen Button-Hintergrundfarbe nach WCAG-Kontrastberechnung gewählt: dunkle Schrift auf hellen Buttons, helle Schrift auf dunklen Buttons. Das gilt auch für Hover und deaktivierte Schaltflächen sowie für die Farbauswahlknöpfe im Erscheinungsbild-Fenster. Bei Änderung oder Live-Vorschau des Farbschemas wird der Kontrast unmittelbar neu berechnet. Die Farbschemata und gespeicherten Daten bleiben unverändert.


## v2.0.42 – Lesbarkeit des Farbschemas prüfen

Unter Konfiguration → Erscheinungsbild einstellen → Farbschema gibt es den Button „Lesbarkeit des Farbschemas prüfen …“. Er zeigt einen rein lesenden Bericht mit WCAG-2.x-Kontrastverhältnissen für normale und überfahrene Buttons, Eingabeflächen, Hintergrund, Reiter und ausgewählte Texte. Der Bericht berücksichtigt auch eine aktive Live-Vorschau, verändert keine Farben und speichert nichts. Als Orientierungswerte gelten 4,5:1 für normalen und 3:1 für großen Text. Dies ist keine vollständige Barrierefreiheitsprüfung aller Widgets.


## v2.0.43 – Kontrastbericht als TXT exportieren

Im Fenster Konfiguration → Erscheinungsbild einstellen → Farbschema kann der Kontrastbericht mit „Kontrastbericht als TXT exportieren …“ als UTF-8-Textdatei gespeichert werden. Der Export berücksichtigt die aktuelle Live-Vorschau und enthält die gleichen WCAG-Kontrastwerte wie der bestehende Prüfbericht. Es werden keine Einstellungen verändert.


## v2.0.44 – Kontrastwerte als CSV exportieren

Im Fenster **Konfiguration → Erscheinungsbild einstellen → Farbschema** gibt es jetzt die Schaltfläche **Kontrastwerte als CSV exportieren …**. Der Export verwendet dieselben sieben Prüfwerte wie die bestehende Kontrastprüfung und der TXT-Bericht. Die Datei wird mit UTF-8-BOM und Semikolon-Trennung geschrieben, sodass sie sich in deutschsprachigen Excel-Versionen einfach öffnen lässt. Sie enthält den Namen des Farbschemas (gegebenenfalls mit dem Zusatz Vorschau), die geprüften Vorder- und Hintergrundfarben, das Kontrastverhältnis, die Bewertung und die beiden WCAG-Schwellen (4,5:1 und 3:1). Der Export verändert weder Farbschema noch Datenbank.


## v2.0.45 – Farbschemata vergleichen

Unter Konfiguration → Erscheinungsbild einstellen → Farbschema zeigt „Alle Farbschemata vergleichen …“ eine lesende Tabelle mit den Standardvorlagen, eigenen Vorlagen und aktuell gespeicherten Farben. Angezeigt werden die bestandenen Prüfungen (mindestens 4,5:1) und der kleinste gemessene Kontrast. Es werden weder Farbschemata noch Projektdateien verändert.


## v2.0.46 – Vollbackup ohne eingefrorene Oberfläche

Manuelle Vollbackups laufen in einem eigenen Qt-Arbeitsthread mit separater SQLite-Verbindung. Während der Sicherung zeigt MPW einen Aktivitätsdialog; das Hauptfenster bleibt reaktionsfähig. Erst nach ZIP- und Datenbankprüfung wird die temporäre `.zip.incomplete`-Datei in den endgültigen ZIP-Namen umbenannt. Bei einem Fehler bleibt die unvollständige Datei zur Untersuchung erhalten. Bestehende Backups werden nicht überschrieben. Die Anwendung darf während des Backups nicht beendet werden.


## v2.0.47 – Datenbankbackup ohne Mediendateien
- Alle MPW-Backups (manuell, automatisch, Sicherheitsbackup) enthalten ausschließlich `workstation.db` und eine kleine `backup_info.txt`.
- Weder `media/` noch Band-/Projektverzeichnisse, Audio, Cover, Videos oder Stems werden gesichert.
- Wiederherstellung verändert ausschließlich die Datenbank, niemals Medienordner.
- Die externe geklonte Datensicherung der Medien bleibt unabhängig notwendig.
- Bestehende ältere ZIP-Backups werden nicht verändert.


## v2.0.48 – Sichere Datenbank-Wiederherstellung und Altsicherungen
- Der Bestätigungsdialog beschreibt jetzt korrekt, dass nur die MPW-Datenbank ersetzt wird; Medien und Band-/Projektordner bleiben unverändert.
- Beim Wiederherstellen älterer ZIP-Archive mit `media/`-Einträgen erscheint ein deutlicher Hinweis: Diese Dateien werden ignoriert.
- Die Archivvorschau kennzeichnet Backups mit bzw. ohne Medien.
- Der Tooltip der Vollbackup-Schaltfläche nennt nun ausschließlich das Datenbankbackup.
- Vor der Wiederherstellung wird weiterhin eine Datenbank-Sicherheitskopie erstellt.


## MPW v2.0.49 – Songtitel in Auswahllisten ohne Dopplung

Die Songauswahllisten in „Songs & Suno“, „Medien & Player“ und „Releases Distri“ zeigen bei identischem Projekt- und Songnamen nur noch „Band / Songtitel“ an. Bei unterschiedlichen Namen bleibt „Band / Projekt / Songtitel“ erhalten. Groß-/Kleinschreibung und führende/abschließende Leerzeichen werden beim Vergleich ignoriert. Song-IDs, Datenbankeinträge, Ordner und Mediendateien werden nicht verändert.


## v2.0.50 – Band- und Songauswahl getrennt
Im Reiter Songs & Suno ist die zweite Zeile jetzt in Band und Song aufgeteilt. Die Bandauswahl filtert die Songliste; bei ausgewählter Band wird der Bandname nicht erneut angezeigt. „Alle Bands“ bietet die Gesamtliste. Navigation aus anderen Reitern funktioniert weiterhin, bei Bedarf über „Alle Bands“. Es werden keine Datenbankeinträge oder Dateien verändert.


## v2.0.51 – Schnellsuche in Songs & Suno
In der zweiten Auswahlzeile ergänzt das Feld „Song suchen …“ die getrennte Band- und Songauswahl. Es filtert nach Songtitel, Projektname und Gesamtbeschriftung ohne Änderung der Datenbank. Treffer werden alphabetisch angezeigt. Der Suchfilter kann über das X im Eingabefeld gelöscht werden. Die interne Auswahlsteuerung wurde korrigiert: Beim Filtern wird die Band nicht mehr versehentlich auf „Alle Bands“ zurückgesetzt; externe Navigation kann Suchfilter bei Bedarf aufheben.


## v2.0.52 – Song-Trefferzahl und Filter zurücksetzen
Im Reiter Songs & Suno zeigt die zweite Auswahlzeile jetzt die Anzahl der Songs an, die zum Bandfilter und zur Schnellsuche passen. Die Schaltfläche „Filter zurücksetzen“ stellt „Alle Bands“ ein und leert die Schnellsuche. Diese Funktionen verändern weder Songdaten noch Projektordner oder Medien.


## v2.0.53 – Datenbank-Integritätsprüfung vor Backups
Im Reiter „Backup – Einstellungen“ prüft die neue Schaltfläche „Datenbank-Integrität prüfen“ die aktuelle SQLite-Datenbank schreibgeschützt (PRAGMA integrity_check und PRAGMA foreign_key_check). Vor jeder manuellen, automatischen und Sicherheits-Sicherung wird dieselbe Prüfung durchgeführt; nach der SQLite-Snapshot-Erstellung wird auch der Snapshot kontrolliert. Fehler brechen die Sicherung ab und werden im Backup-Prüfprotokoll dokumentiert. Die vorhandene ZIP-Validierung prüft zusätzlich die SQLite-Integrität und Fremdschlüssel. Die Sicherung enthält weiterhin ausschließlich die Datenbank, keine Medien oder Projektordner. Bei Fehlermeldungen die Datenbank nicht eigenmächtig reparieren; zuerst bestehende Sicherungen sichern und das Protokoll auswerten.


## v2.0.54 – Medien-Verknüpfungen prüfen
Unter Medien & Player: lesende Prüfung der gespeicherten Altbestands-Medienpfade mit TXT-Export. Keine Löschung, kein Umzug, keine Änderung an Datenbank oder Medien. Projektordner-Medien werden separat im Dateisystem geführt.


## v2.0.55 – Song-Versionen vergleichen
Der vorhandene zeilenbasierte Style-/Lyrics-Vergleich im AI Prompt Launcher lässt sich nun als UTF-8-TXT exportieren. Vergleich und Export sind lesend; das bestehende explizite Übernehmen von Versionen bleibt unverändert.


## v2.0.56 – Audio-Qualitätskontrolle
Medien & Player: FFmpeg-QC für Sample-Peak, geclippte Samples (soweit FFmpeg meldet) und längere Stilleabschnitte (mindestens 2 s unter -60 dB). Separat von bestehender LUFS-/True-Peak-Analyse. Originaldateien werden nicht verändert; FFmpeg erforderlich. Kein verlässlicher Artefakt-/Klickdetektor.


## MPW v2.0.57 – Separate Ergebnisfenster für Audioanalysen
Im Reiter Medien & Player öffnen „Audioqualität analysieren“ und „Audio-QC: Clipping und Stille“ ihre Ergebnisse jetzt in eigenen, vergrößerbaren Fenstern. Berichte können kopiert oder als UTF-8-TXT exportiert werden. Im Medienreiter bleibt nur ein kurzer Status. Auch Analysefehler werden im separaten Fenster angezeigt. Die Analysen bleiben lesend und verändern weder Datenbank noch Mediendateien.


## MPW v2.0.58 – Audioqualität: Soll-Ist-Vergleich
Im Reiter Medien & Player wertet das separate Ergebnisfenster der Lautheitsanalyse jetzt die integrierte Lautheit, den True Peak, die LRA und die EBU-R128-Lautheitsschwelle aus. Die Vergleichswerte (-14 LUFS als Streaming-Orientierung, höchstens -1 dBTP und 4–12 LU LRA als grobe musikalische Orientierung) sind keine universellen Mastering-Vorgaben. Die Lautheitsschwelle ist ein Gating-Messparameter und hat keinen Optimalwert. Warnungen zu möglichem Clipping, hoher Lautheit und geringer Dynamik sind Hinweise, keine automatische Freigabe. Dateien und Datenbank bleiben unverändert.


## MPW v2.0.59 – Laufzeitdiagnose
Neue lesende Laufzeitprüfung im Reiter System & Diagnose: Datenbank-Integrität, freier Speicherplatz und Status des manuellen Backup-Threads. Protokolliert technische Fehler; keine Änderung an Songs oder Medien.


## MPW v2.0.60 – Isolierte_Backuptests
Erweiterter isolierter --self-test: SQLite-Snapshot-Backup, ZIP-Validierung, Wiederherstellung in ein temporäres Verzeichnis und Ausschluss von Mediendateien. Keine produktiven Daten werden geöffnet.


## MPW v2.0.61 – Audiofenster_Bedienung
Audio-Ergebnisdialoge: besser lesbare Monospace-Darstellung, Mindestgröße, Tastenkürzel Strg+C für Kopieren und Esc zum Schließen. Keine Veränderung der Analysen.


## MPW v2.1.0 – Release_Kandidat
Release-Kandidat: alle vorangegangenen Änderungen enthalten. Statische Prüfungen und isolierte Tests; Windows-Praxistests und Langzeittest vor einer Stable-Freigabe erforderlich.
