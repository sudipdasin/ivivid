#!/usr/bin/env bash
set -euo pipefail
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/config/iVivid"
cat > "$tmp/config/iVivid/mpv.conf" <<'EOF'
hwdec=no
scale=bilinear
cscale=bilinear
deband=yes
saturation=10
brightness=0
contrast=0
af=lavfi=[equalizer=f=100:t=h:w=200:g=3],lavfi=[equalizer=f=6000:t=h:w=200:g=3]
EOF
ffmpeg -hide_banner -loglevel error -y -f lavfi -i testsrc2=size=160x90:rate=15 -f lavfi -i sine=frequency=440:sample_rate=44100 -t 2 -c:v mpeg4 -c:a aac "$tmp/test.mp4"
HOME="$tmp" XDG_CONFIG_HOME="$tmp/config" mpv --no-config --include="$tmp/config/iVivid/mpv.conf" --vo=null --ao=null --hwdec=no --no-terminal --frames=25 "$tmp/test.mp4"
sed -i '/^af=/d' "$tmp/config/iVivid/mpv.conf"
printf '%s\n' 'af=lavfi=[loudnorm=I=-16:TP=-1.5:LRA=11]' >> "$tmp/config/iVivid/mpv.conf"
HOME="$tmp" XDG_CONFIG_HOME="$tmp/config" mpv --no-config --include="$tmp/config/iVivid/mpv.conf" --vo=null --ao=null --hwdec=no --no-terminal --frames=25 "$tmp/test.mp4"
