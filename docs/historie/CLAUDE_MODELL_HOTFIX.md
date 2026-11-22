# MPW v2.2.0 RC1 – Claude-Modell Hotfix

Basis: MPW_v2.2.0_RC1_API_Fehler_Hotfix. Keine Datenbankmigration erforderlich.

## AI Prompt Launcher – Claude über API
- Voreingestelltes Modell für Claude: `claude-sonnet-5-5` (vorher `claude-sonnet-4-5`). Für höchste Qualität `claude-opus-5-5` ins Feld „API-Modell“ eintragen (doppelter Preis).
- Antwortlimit `max_tokens` von 6000 auf 16000 erhöht. Aktuelle Claude-Modelle denken vor der Antwort, das zählt mit; bei 6000 wurden Antworten abgeschnitten („Antwort abgeschnitten“).
- Wartezeit für API-Anfragen (alle Anbieter) von 90 auf 180 Sekunden verlängert; Zeitüberschreitungs-Meldung in DE/EN/FR/ES/IT angepasst.
- Ein bereits geändertes Modellfeld wird erst beim nächsten Plattformwechsel auf den neuen Standard gesetzt.

## Unverändert
Standardmodelle für ChatGPT (`gpt-4.1-mini`) und Gemini (`gemini-2.5-flash`) – nicht geprüft, ob sie noch angeboten werden. CLI-Weg: Feld „CLI-Modell“ akzeptiert `opus` oder `sonnet`.

## Tests
`tests/test_ai_api_errors.py` prüft Standardmodell, Tokenlimit und Wartezeit. 145 Tests bestanden, Selbsttest bestanden.

## Grenzen
Nicht mit echtem API-Schlüssel und nicht in der laufenden Windows-Oberfläche getestet. Kein Windows-EXE-Build erstellt.
