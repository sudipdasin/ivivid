#!/usr/bin/env bash
set -euo pipefail
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/bin"
cat > "$tmp/bin/mpv" <<'EOF'
#!/bin/sh
printf '%s\n' "$@" > "$IVIVID_ARGS"
EOF
chmod +x "$tmp/bin/mpv"
mkdir -p "$tmp/config/iVivid"
printf '# test\n' > "$tmp/config/iVivid/mpv.conf"
HOME="$tmp" XDG_CONFIG_HOME="$tmp/config" PATH="$tmp/bin:$PATH" IVIVID_ARGS="$tmp/args" sh scripts/ivivid-play "a movie.mp4"
grep -Fx -- "--include=$tmp/config/iVivid/mpv.conf" "$tmp/args"
grep -Fx -- "a movie.mp4" "$tmp/args"
