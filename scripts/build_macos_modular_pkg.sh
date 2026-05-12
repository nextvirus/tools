#!/usr/bin/env bash
# Build tools-macos-selectable.pkg from dist/installer/mac/{runtime,pdf,photo,meeting}.
# Run after: python scripts/package_tools.py
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VER="${1:-0.0.0}"
VER="${VER#v}"
VER="${VER%%+*}"
export TOOLS_PKG_VERSION="$VER"
python "$ROOT/scripts/stage_installer_components.py" --platform darwin
ST="$ROOT/dist/installer/mac"
DIST_XML="$ST/distribution.xml"
if [[ ! -f "$DIST_XML" ]]; then
  echo "Missing $DIST_XML after staging." >&2
  exit 1
fi
PKGDIR="$ROOT/dist/mac-pkg-work"
mkdir -p "$PKGDIR"
cd "$PKGDIR"
pkgbuild --root "$ST/runtime" --identifier com.tools.pkg.runtime --version "$VER" --install-location /Applications runtime.pkg
pkgbuild --root "$ST/pdf" --identifier com.tools.pkg.pdf --version "$VER" --install-location /Applications pdf.pkg
pkgbuild --root "$ST/photo" --identifier com.tools.pkg.photo --version "$VER" --install-location /Applications photo.pkg
pkgbuild --root "$ST/meeting" --identifier com.tools.pkg.meeting --version "$VER" --install-location /Applications meeting.pkg
productbuild --distribution "$DIST_XML" --package-path "$PKGDIR" "$ROOT/dist/tools-macos-selectable.pkg"
echo "OK: $ROOT/dist/tools-macos-selectable.pkg"
