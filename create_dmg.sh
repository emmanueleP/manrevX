#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "${SCRIPT_DIR}"

APP_NAME="ManRevX"
APP_BUNDLE_PATH="dist/${APP_NAME}.app"
DMG_NAME="${APP_NAME}.dmg"
VOLUME_NAME="${APP_NAME}"
STAGING_DIR="dist/dmg-staging"
ENTRY_POINT="main.py"
ICONSET_DIR="src/assets/logo_manrev.png"
PYINSTALLER_BIN="${PYINSTALLER:-pyinstaller}"

usage() {
  echo "Uso: $0 [--app PathApp] [--dmg Nome.dmg]"
  echo "Predefiniti: app=${APP_BUNDLE_PATH}, dmg=${DMG_NAME}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --app)
      APP_BUNDLE_PATH="$2"; shift 2 ;;
    --dmg)
      DMG_NAME="$2"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Opzione sconosciuta: $1" >&2
      usage; exit 1 ;;
  esac
done

if [[ "$(uname)" != "Darwin" ]]; then
  echo "Questo script deve essere eseguito su macOS (hdiutil)." >&2
  exit 1
fi

if ! command -v "${PYINSTALLER_BIN}" >/dev/null 2>&1; then
  echo "PyInstaller non trovato. Installa con 'pip install pyinstaller'." >&2
  exit 1
fi

DIST_DIR="$(dirname "${APP_BUNDLE_PATH}")"

echo ">> Costruzione applicazione ${APP_NAME}.app con PyInstaller"
rm -rf "${DIST_DIR}" build "${APP_NAME}.spec"
"${PYINSTALLER_BIN}" --noconfirm --clean \
  --name "${APP_NAME}" \
  --windowed \
  --icon "${ICONSET_DIR}" \
  --osx-bundle-identifier "it.emmanuele.manrevx" \
  --add-data "src/assets:src/assets" \
  --paths "src" \
  --distpath "${DIST_DIR}" \
  --workpath build \
  --specpath . \
  "${ENTRY_POINT}"

if [[ ! -d "${APP_BUNDLE_PATH}" ]]; then
  echo "Errore: bundle non creato in ${APP_BUNDLE_PATH}" >&2
  exit 1
fi

rm -rf "${STAGING_DIR}" "${DMG_NAME}"
mkdir -p "${STAGING_DIR}"
cp -R "${APP_BUNDLE_PATH}" "${STAGING_DIR}/${APP_NAME}.app"

# crea alias a /Applications per drag&drop
ln -s /Applications "${STAGING_DIR}/Applications"

DMG_TEMP="${DMG_NAME%.dmg}.temp.dmg"

hdiutil create -volname "${VOLUME_NAME}" \
  -srcfolder "${STAGING_DIR}" \
  -ov -format UDRW "${DMG_TEMP}"

# Converti in immagine compressa leggibile
hdiutil convert "${DMG_TEMP}" -format UDZO -o "${DMG_NAME}"
rm -f "${DMG_TEMP}"

# ripulisci staging
rm -rf "${STAGING_DIR}"

echo "DMG creato: ${DMG_NAME}"
