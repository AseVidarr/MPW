# Preview 51 Hotfix 2 – vereinfachter Windows-Start

Das ZIP enthaelt die Projektdateien **direkt auf oberster Ebene**. `BUILD_STARTEN.cmd` und `build.ps1` liegen neben `scripts/`, `source/` und `installer/`.

1. ZIP in einen **neuen, leeren Ordner** entpacken.
2. `BUILD_STARTEN.cmd` doppelklicken, alternativ im selben Ordner: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\build.ps1`.
3. Das vorhandene `scripts/build.ps1` bleibt der eigentliche Build-Ablauf.
4. Vorhandene produktive `Data`-Ordner nicht loeschen oder ueberschreiben.

Dieser Hotfix behebt die Verzeichnis-/Einstiegsproblematik, nicht nachgewiesene Windows-Buildfehler. Der Windows-Build muss vor Ort getestet werden.
