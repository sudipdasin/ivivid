#!/usr/bin/env bash
# Reuse existing iVivid build-release.sh; no signing, publishing or system install.
set -euo pipefail
umask 022
fail(){ printf 'BLOCKED: %s\n' "$1" >&2; exit 1; }
[[ $# == 1 && ($1 == prepare || $1 == build) ]] || fail 'usage: prepare|build'
[[ $EUID != 0 && ${APPVEYOR:-} == True || $EUID != 0 && ${APPVEYOR:-} == true ]] || fail 'non-root AppVeyor worker required'
[[ ${APPVEYOR_REPO_NAME:-} == sudipdasin/ivivid && ${APPVEYOR_REPO_BRANCH:-} == build/appveyor-2.6-preview ]] || fail 'repository or branch mismatch'
[[ -z ${APPVEYOR_PULL_REQUEST_NUMBER:-} && ${APPVEYOR_REPO_TAG:-false} =~ ^([Ff]alse|0)$ ]] || fail 'PR or tag build prohibited'
[[ ${APPVEYOR_REPO_COMMIT:-} =~ ^[0-9a-f]{40}$ ]] || fail 'full commit required'
export GIT_NO_REPLACE_OBJECTS=1
root=$(git rev-parse --show-toplevel); cd "$root"
[[ $(git rev-parse HEAD) == "$APPVEYOR_REPO_COMMIT" && -z $(git status --porcelain) ]] || fail 'source pin or clean tree mismatch'
if [[ $1 == prepare ]]; then
  source /etc/os-release
  [[ ${ID:-} == ubuntu && ${VERSION_ID:-} == 24.04 && $(uname -m) == x86_64 ]] || fail 'Ubuntu 24.04 amd64 required'
  sudo -n apt-get -o APT::Update::Error-Mode=any update
  sudo -n apt-get -y --no-remove --no-install-recommends install build-essential cmake pkg-config qt6-base-dev python3 openssl ffmpeg mpv dpkg-dev zip unzip xvfb xauth git ca-certificates
  exit 0
fi
out="$root/ivivid-ci-artifacts"
[[ ! -e $out && ! -L $out ]] || fail 'artifact destination already exists'
work=$(mktemp -d /tmp/ivivid-av.XXXXXXXX)
trap 'rm -rf -- "$work"' EXIT
mkdir -m 700 "$work/home" "$work/config" "$work/runtime" "$work/cache" "$work/data"
export HOME="$work/home" XDG_CONFIG_HOME="$work/config" XDG_RUNTIME_DIR="$work/runtime" XDG_CACHE_HOME="$work/cache" XDG_DATA_HOME="$work/data" IVIVID_DISABLE_UPDATE_CHECK=1
# Existing release script archives the exact clean tree, runs CTest, real mpv/FFmpeg and Xvfb checks.
bash packaging/build-release.sh "$work/results" 2>&1 | tee "$work/BUILD.log"
results="$work/results"; deb=ivivid_2.6.0-beta.1_amd64.deb; portable=ivivid-2.6.0-beta.1-linux-amd64.zip
[[ -d $results && ! -L $results ]] || fail 'missing results directory'
for f in "$deb" "$portable" SHA256SUMS SOURCE_COMMIT; do
  [[ -f $results/$f && ! -L $results/$f && -s $results/$f ]] || fail 'missing or invalid result'
done
[[ $(cat "$results/SOURCE_COMMIT") == "$APPVEYOR_REPO_COMMIT" ]] || fail 'artifact source mismatch'
# Rebuild manifest from exact two names, not provider-supplied arbitrary paths.
(cd "$results"; sha256sum -- "$deb" "$portable" > "$work/expected.sha"; cmp SHA256SUMS "$work/expected.sha"; sha256sum -c "$work/expected.sha")
[[ $(dpkg-deb -f "$results/$deb" Package) == ivivid && $(dpkg-deb -f "$results/$deb" Architecture) == amd64 && $(dpkg-deb -f "$results/$deb" Version) == 2.6.0~beta.1 ]] || fail 'DEB identity mismatch'
unzip -t "$results/$portable"
mkdir "$out"
for f in "$deb" "$portable" SHA256SUMS SOURCE_COMMIT; do install -m 0644 "$results/$f" "$out/$f"; done
install -m 0644 "$work/BUILD.log" "$out/BUILD.log"
printf 'Verified evaluation artifacts for %s\n' "$APPVEYOR_REPO_COMMIT"
