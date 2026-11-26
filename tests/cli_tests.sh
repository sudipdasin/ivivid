#!/usr/bin/env bash
set -euo pipefail
app="${1:?path to iVivid binary required}"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
export XDG_CONFIG_HOME="$tmp"
"$app" --version | grep -Fx "iVivid ${2:?expected version required}"
"$app" --help | grep -F -- '--check-config'
if "$app" --version --unknown; then exit 1; fi
if "$app" --help --export-config "$tmp/unexpected.conf"; then exit 1; fi
test ! -e "$tmp/unexpected.conf"
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
# Reject unexpected flags and operands instead of silently ignoring them.
if "$app" --export-config "$tmp/extra.conf" --unknown; then exit 1; fi
test ! -e "$tmp/extra.conf"
if "$app" --check-config --unknown; then exit 1; fi
if "$app" --print-config --check-config; then exit 1; fi
# Round-trip import and verify rejected imports never change saved settings.
printf 'saturation=50\n' > "$tmp/iVivid/mpv.conf"
"$app" --import-config "$tmp/export.conf"
cmp "$tmp/iVivid/mpv.conf" "$tmp/export.conf"
cp "$tmp/iVivid/mpv.conf" "$tmp/before.conf"
ln -s "$tmp/iVivid/mpv.conf" "$tmp/active-alias.conf"
if "$app" --import-config "$tmp/active-alias.conf"; then exit 1; fi
if "$app" --export-config "$tmp/active-alias.conf"; then exit 1; fi
cmp "$tmp/iVivid/mpv.conf" "$tmp/before.conf"
printf 'saturation=not-a-number\n' > "$tmp/bad.conf"
if "$app" --import-config "$tmp/bad.conf"; then exit 1; fi
if "$app" --import-config "$tmp/missing.conf"; then exit 1; fi
printf 'saturation=10\nvo=gpu-next\n' > "$tmp/unknown.conf"
if "$app" --import-config "$tmp/unknown.conf"; then exit 1; fi
printf 'saturation=10\nsaturation=20\n' > "$tmp/duplicate.conf"
if "$app" --import-config "$tmp/duplicate.conf"; then exit 1; fi
if "$app" --import-config "$tmp/iVivid/mpv.conf"; then exit 1; fi
head -c 70000 /dev/zero | tr '\0' 'x' > "$tmp/oversized.conf"
if "$app" --import-config "$tmp/oversized.conf"; then exit 1; fi
printf 'saturation=10\n\377\n' > "$tmp/invalid-utf8.conf"
if "$app" --import-config "$tmp/invalid-utf8.conf"; then exit 1; fi
printf 'saturation=10\000\n' > "$tmp/nul.conf"
if "$app" --import-config "$tmp/nul.conf"; then exit 1; fi
# Reject duplicate audio filter stages and preserve the active configuration.
printf 'af=lavfi=[equalizer=f=100:t=h:w=200:g=5],lavfi=[equalizer=f=100:t=h:w=200:g=8]\n' > "$tmp/duplicate-bass.conf"
if "$app" --import-config "$tmp/duplicate-bass.conf"; then exit 1; fi
printf 'af=lavfi=[equalizer=f=6000:t=h:w=200:g=5],lavfi=[equalizer=f=6000:t=h:w=200:g=8]\n' > "$tmp/duplicate-treble.conf"
if "$app" --import-config "$tmp/duplicate-treble.conf"; then exit 1; fi
printf 'af=lavfi=[loudnorm=I=-16:TP=-1.5:LRA=11],lavfi=[loudnorm=I=-16:TP=-1.5:LRA=11]\n' > "$tmp/duplicate-normalize.conf"
if "$app" --import-config "$tmp/duplicate-normalize.conf"; then exit 1; fi
cmp "$tmp/iVivid/mpv.conf" "$tmp/before.conf"
\printf 'saturation=invalid\n' > "$tmp/iVivid/mpv.conf"
if "$app" --check-config > "$tmp/out" 2> "$tmp/err"; then
  echo 'Expected invalid config to fail' >&2
  exit 1
fi
grep -F 'iVivid config error:' "$tmp/err"
test ! -e "$tmp/mpv/mpv.conf"

