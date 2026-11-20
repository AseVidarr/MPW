#!/bin/sh
# MPW im Browser (Linux, Portable): startet MPW-Web; Daten liegen im Ordner "Data" daneben.
cd "$(dirname "$0")" || exit 1
if [ ! -f ./.mpw-portable-v2 ]; then
  echo "Portable-Marker fehlt. Start abgebrochen." >&2
  exit 1
fi
mkdir -p ./Data
if [ ! -x ./App/MPW-Web ]; then
  echo "App/MPW-Web fehlt oder ist nicht ausführbar: chmod +x \"$(pwd)/App/MPW-Web\"" >&2
  exit 1
fi
exec ./App/MPW-Web "$@"
