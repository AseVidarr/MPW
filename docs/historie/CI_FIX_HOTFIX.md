# MPW v2.2.0 RC1 – Korrekturen nach dem ersten GitHub-Lauf

Basis: MPW_v2.2.0_RC1_GitHub_Build_Hotfix. Keine Änderung an MPW selbst.

Erster Lauf „Tests und Pakete #1“: macOS und Windows je 1 von 215 Tests rot, Linux alle Tests grün, aber Selbsttest der Desktop-App gescheitert. Paket-Jobs nicht gestartet (warten auf grüne Tests).

| System | Ursache | Korrektur |
|---|---|---|
| macOS | Test verglich `/var/...` mit aufgelöstem `/private/var/...` | `tests/test_portable_isolation.py` vergleicht aufgelöste Pfade |
| Windows | Test verglich Kurzform `RUNNER~1` mit Langform | dieselbe Korrektur |
| Linux | Qt Multimedia fand `libpulse.so.0` nicht | Workflow installiert `libpulse0`, `libpulse-mainloop-glib0` |

MPW selbst hat in allen Fällen richtig gerechnet. Lokal: 214 Tests und alle Testskripte bestanden.
