# MPW Alpha 20 – Quellcodebasierte Übersetzungsprüfung

Prüfung: AST-Auswertung von `source/workstation.py` und Kontrolle des Renderpfads `general_detailed_guide_html`.

| Reiter | Anleitungseinträge | Im Renderer abgedeckt (EN/FR/ES/IT) |
|---|---:|---|
| Bands | 16 | 0/16 |
| Song/Projekte | 11 | 0/11 |
| Genre-Katalog | 5 | 0/5 |
| Songs & Suno | 43 | 0/43 |
| Medien & Player | 20 | 0/20 |
| Medien Explorer | 10 | 0/10 |
| Releases Distri | 18 | 0/18 |
| Plattensammlung | 8 | 0/8 |
| Album-Details | 12 | 0/12 |
| Album-Druckansicht | 4 | 0/4 |
| Backup – Einstellungen | 9 | 0/9 |
| Backup – Archiv | 15 | 0/15 |
| Konfiguration | 36 | 29/36 |
| System & Diagnose | 11 | 11/11 |

## Kritischer Befund

Die Renderfunktion `general_detailed_guide_html` übersetzt im derzeitigen Code nur Einträge für `Konfiguration` und `System & Diagnose`. Bei den übrigen Reitern werden `group`, `label` und `explanation` unverändert aus den deutschen `DETAILED_TAB_GUIDES` übernommen. Frühere Aussagen, dass deren Detailanleitungen bereits vollständig eingebunden seien, lassen sich anhand dieses Renderpfads nicht bestätigen.

Die Konfiguration hat darüber hinaus noch unübersetzte Zusatzeinträge. Das Positionsmapping der Grundanleitungen ist anfällig, wenn Einträge später umsortiert werden.

## Nächste Implementierung

1. Für jeden Reiter eine explizite Übersetzungstabelle nach stabilen Eintragsschlüsseln einführen.
2. Im Renderer alle Reiter über diese Tabelle abdecken und bei fehlender Übersetzung einen prüfbaren Fallback melden.
3. Alle zusätzlichen Anleitungen vollständig in EN/FR/ES/IT übersetzen.
4. Automatisierten Test für Vollständigkeit und Sprachwechsel ergänzen.
5. Windows-Abnahmetest durchführen.

Keine produktiven Daten verändert. Kein Zwischen-ZIP erstellt.
