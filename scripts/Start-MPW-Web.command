#!/bin/sh
# MPW im Browser (macOS, Portable): Doppelklick startet MPW-Web im Terminal.
# Daten liegen im Ordner "Data" neben dieser Datei.
cd "$(dirname "$0")" || exit 1
if [ ! -f ./.mpw-portable-v2 ]; then
  echo "Portable-Marker fehlt. Start abgebrochen."
  printf "Eingabetaste zum Schließen ... "; read -r _
  exit 1
fi
mkdir -p ./Data
if [ ! -x ./App/MPW-Web ]; then
  echo "App/MPW-Web fehlt oder ist nicht ausführbar."
  echo "Tipp: Im Terminal ausführen:  chmod +x \"$(pwd)/App/MPW-Web\""
  printf "Eingabetaste zum Schließen ... "; read -r _
  exit 1
fi
./App/MPW-Web "$@"
status=$?
if [ "$status" -ne 0 ]; then
  echo
  echo "MPW-Web wurde mit Fehler $status beendet."
  echo "Falls macOS den Start blockiert: siehe LIESMICH_MAC_LINUX.txt (Quarantäne entfernen)."
  printf "Eingabetaste zum Schließen ... "; read -r _
fi
exit "$status"
