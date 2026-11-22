# Preview 47 – Hotfix 2

## Behobener Startfehler
`KeyError: 'info'` in `refresh_configuration_text_p34()` beim Aufbau des Konfigurationsreiters. Das QLabel `info` war erzeugt, jedoch nicht in `self.config_extra_p34` eingetragen. Es wird nun vor dem ersten Refresh unter dem Schlüssel `info` registriert.

## Tests
Drei neue Regressionstests prüfen die Registrierung vor dem Refresh, die Vollständigkeit der Konfigurationsschlüssel und die Python-Syntax. Keine praktische Windows-GUI-Abnahme.
