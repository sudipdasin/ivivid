#!/usr/bin/env bash
set -euo pipefail
app="${1:?path to iVivid binary required}"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
export XDG_CONFIG_HOME="$tmp"
"$app" --version | grep -Fx 'iVivid 1.0.0-beta.1'
"$app" --help | grep -F -- '--check-config'
"$app" --check-config | grep -Fx 'iVivid configuration valid'
"$app" --print-config | grep -Fx 'saturation=10'
mkdir -p "$tmp/iVivid"
printf 'saturation=25\nbrightness=5\n' > "$tmp/iVivid/mpv.conf"
"$app" --check-config | grep -Fx 'iVivid configuration valid'
"$app" --print-config | grep -Fx 'saturation=25'
"$app" --print-config | grep -Fx 'brightness=5'
# Export must not mutate the active configuration, and must preserve exact output.
"$app" --export-config "$tmp/export.conf"
cmp "$tmp/export.conf" <("$app" --print-config) || exit 1
if "$app" --export-config "$tmp/iVivid/mpv.conf"; then
  echo 'Expected active configuration overwrite protection' >&2
  exit 1
fi
if "$app" --export-config; then
  echo 'Expected missing export argument to fail' >&2
  exit 1
fi
test -s "$tmp/export.conf"
\printf 'saturation=invalid\n' > "$tmp/iVivid/mpv.conf"
if "$app" --check-config > "$tmp/out" 2> "$tmp/err"; then
  echo 'Expected invalid config to fail' >&2
  exit 1
fi
grep -F 'iVivid config error:' "$tmp/err"
test ! -e "$tmp/mpv/mpv.conf"

