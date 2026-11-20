#!/bin/sh
# Build the web-only portable MPW for macOS or Linux. Must run on that system
# (GitHub Actions does this automatically, see .github/workflows/build.yml).
#
#   sh scripts/build-unix.sh                 # installs PyInstaller, builds, tests, packs
#   SKIP_INSTALL=1 PYTHON=python3.13 sh scripts/build-unix.sh
#
# Result in dist/:  MPW_Portable_<version>_<macOS|Linux>-<arch>.tar.gz (+ .sha256)
# Nothing outside the project folder is changed; existing outputs are never overwritten.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PYTHON:-python3}"
VERSION_TAG="v2.2.0_Alpha21_Preview52_RC1"

case "$(uname -s)" in
  Darwin) OS=macOS; START=Start-MPW-Web.command ;;
  Linux)  OS=Linux; START=start-mpw-web.sh ;;
  *) echo "Dieses Skript ist nur für macOS und Linux. Windows: build.ps1" >&2; exit 1 ;;
esac
ARCH="$(uname -m)"
[ "$ARCH" = "x86_64" ] && ARCH=x64
NAME="MPW_Portable_${VERSION_TAG}_${OS}-${ARCH}"
DIST="$ROOT/dist"
WORK="$ROOT/build/unix"
OUT="$DIST/$NAME"

for target in "$OUT" "$OUT.tar.gz"; do
  if [ -e "$target" ]; then
    echo "Ziel existiert bereits: $target – bitte sichern oder umbenennen (keine automatische Löschung)." >&2
    exit 1
  fi
done

if [ "${SKIP_INSTALL:-0}" != "1" ]; then
  "$PY" -m pip install --upgrade 'pyinstaller>=6.10,<7' 'mutagen>=1.47,<2'
fi

echo "== Selbsttests (Quellcode, ohne Qt)"
"$PY" "$ROOT/source/mpw_web.py" --self-test
"$PY" "$ROOT/source/mpw_mcp_server.py" --self-test

echo "== PyInstaller"
"$PY" -m PyInstaller --noconfirm --clean --distpath "$WORK/dist" --workpath "$WORK/work" "$ROOT/installer/MPW-Web.spec"

echo "== Portable-Paket $NAME"
mkdir -p "$OUT"
cp -R "$WORK/dist/App" "$OUT/App"
printf 'Standalone MPW portable build %s (%s, web only)\n' "$VERSION_TAG" "$OS" > "$OUT/.mpw-portable-v2"
cp "$ROOT/scripts/$START" "$OUT/$START"
cp "$ROOT/scripts/LIESMICH_MAC_LINUX.txt" "$OUT/LIESMICH_MAC_LINUX.txt"
printf 'Portable data is stored in Data. Do not delete this directory during updates.\n' > "$OUT/DATEN_HINWEIS.txt"
chmod +x "$OUT/$START" "$OUT/App/MPW-Web" "$OUT/App/MPW-MCP"

echo "== Selbsttests (fertige Programme)"
"$OUT/App/MPW-Web" --self-test
"$OUT/App/MPW-MCP" --self-test

echo "== Packen"
tar -C "$DIST" -czf "$OUT.tar.gz" "$NAME"
if command -v sha256sum >/dev/null 2>&1; then
  (cd "$DIST" && sha256sum "$NAME.tar.gz" > "$NAME.tar.gz.sha256")
else
  (cd "$DIST" && shasum -a 256 "$NAME.tar.gz" > "$NAME.tar.gz.sha256")
fi
echo "Fertig: $OUT.tar.gz"
