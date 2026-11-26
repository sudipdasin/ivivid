#!/usr/bin/env bash
set -euo pipefail
version="$(build/iVivid --version | sed -n 's/^iVivid //p')"
[[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-beta\.[0-9]+)?$ ]] || { echo "Invalid application version" >&2; exit 1; }
stage="$PWD/build/package-root"
rm -rf "$stage"
DESTDIR="$stage" cmake --install build --prefix /usr
mkdir -p "$stage/DEBIAN"
cat > "$stage/DEBIAN/control" <<EOF
Package: ivivid
Version: $version
Section: video
Priority: optional
Architecture: amd64
Maintainer: iVivid Contributors <noreply@github.com>
Depends: libqt6widgets6 (>= 6.2), mpv, python3
Description: iVivid Linux video enhancement configurator
 C++ and Qt interface for mpv playback enhancement.
EOF
mkdir -p dist
dpkg-deb --build --root-owner-group "$stage" "dist/ivivid_${version}_amd64.deb"
