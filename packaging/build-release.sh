#!/usr/bin/env bash
set -euo pipefail
root=$(git rev-parse --show-toplevel)
cd "$root"
[[ -z $(git status --porcelain) ]] || { echo 'Commit changes before building.' >&2; exit 1; }
[[ $(uname -m) == x86_64 ]] || { echo 'Only amd64 packaging supported.' >&2; exit 1; }
for tool in cmake ctest c++ pkg-config mpv ffmpeg ffprobe dpkg-deb zip unzip sha256sum xvfb-run timeout; do
  command -v "$tool" >/dev/null || { echo "Missing dependency: $tool" >&2; exit 1; }
done
pkg-config --exists Qt6Widgets Qt6Test || { echo 'Qt6 development dependencies missing.' >&2; exit 1; }
sha=$(git rev-parse HEAD)
output=${1:-"$root/../ivivid-artifacts-${sha:0:12}"}
output=$(realpath -m "$output")
[[ ! -e "$output" ]] || { echo 'Output already exists; refusing overwrite.' >&2; exit 1; }
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
git archive HEAD | tar -x -C "$work"
cd "$work"
export XDG_CONFIG_HOME="$work/test-config"
mkdir -p "$XDG_CONFIG_HOME"
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build --parallel 2
ctest --test-dir build --output-on-failure
bash tests/launcher_tests.sh
bash tests/playback_smoke.sh
bash tests/spatial-smoke.sh
code=0
timeout 5s xvfb-run -a ./build/iVivid || code=$?
[[ $code == 124 || $code == 0 ]]
bash packaging/build-deb.sh
shopt -s nullglob
packages=(dist/*.deb)
[[ ${#packages[@]} == 1 ]]
version=$(dpkg-deb -f "${packages[0]}" Version)
[[ $(dpkg-deb -f "${packages[0]}" Architecture) == amd64 ]]
dpkg-deb --contents "${packages[0]}"
bundle="ivivid-$version-linux-amd64"
mkdir -p "$bundle/bin"
install -m755 build/iVivid scripts/ivivid-play "$bundle/bin/"
cp packaging/iVivid.desktop "$bundle/"
printf 'Requires Qt6 Widgets and mpv. Run bin/iVivid.\n' > "$bundle/README.txt"
zip -qr "dist/$bundle.zip" "$bundle"
unzip -t "dist/$bundle.zip"
(cd dist && sha256sum -- *.deb *.zip > SHA256SUMS && sha256sum -c SHA256SUMS)
printf '%s\n' "$sha" > dist/SOURCE_COMMIT
mkdir "$output"
cp dist/* "$output/"
printf 'Verified build artifacts: %s\n' "$output"
