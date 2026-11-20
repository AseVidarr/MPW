# MPW v2.2.0 Alpha 21 Preview 46 – Hotfix 1

## Behobener Startfehler

Beim Programmstart wurde `build_media_explorer()` vor `build_configuration()` aufgerufen. Die Zeile `self.config_extra_p34['info'] = info` griff auf ein noch nicht angelegtes Attribut zu und verursachte `AttributeError`.

Die Zeile wurde entfernt. Das Label `info` bleibt Bestandteil des Medien-Explorers. `config_extra_p34` wird unverändert beim Aufbau der Konfiguration angelegt. Der Eingriff verändert keine Datenbank, Songs oder Medien.

Drei neue Regressionstests sichern die Reihenfolge und die fehlende Abhängigkeit ab.

**Hinweis:** Statische Tests und Syntaxprüfung ersetzen keinen tatsächlichen Programmstart unter Windows mit PySide6.
