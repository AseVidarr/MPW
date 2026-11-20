MPW v2.2.0 Alpha 15 – Systematische Übersetzungsinventur

Basis: Alpha 14. Diese Ausgabe verändert die Anwendung nicht.

Neu:
- audit_translations.py: reproduzierbare statische Prüfung der direkt im Quellcode definierten QPushButton-, QLabel-, QCheckBox- und QGroupBox-Texte.
- ALPHA15_UEBERSETZUNGS_AUDIT.md: Bestandsaufnahme der Katalogabdeckung und noch offenen Texte.

Ausführung: python audit_translations.py

Wichtig: Die Zahlen beschreiben nur die Abdeckung von statischen Konstruktor-Texten durch Wörterbücher, nicht die tatsächliche Vollständigkeit der Übersetzung zur Laufzeit. Dynamische Texte, Meldungen, Menüs und Laufzeitprüfungen müssen separat geprüft werden. Die Stable-Version 2.1.0 bleibt unverändert.
