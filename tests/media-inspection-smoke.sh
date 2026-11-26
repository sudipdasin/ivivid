#!/usr/bin/env bash
set -euo pipefail
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
file="$tmp/-test clip.mp4"
ffmpeg -nostdin -v error -f lavfi -i testsrc2=size=160x90:rate=10 -f lavfi -i sine=frequency=440 -t 1 -c:v mpeg4 -c:a aac "$file"
ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height -of json -- "$file" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert any(s.get("width")==160 and s.get("height")==90 for s in d["streams"]); assert any(s.get("codec_type")=="audio" for s in d["streams"]); assert float(d["format"]["duration"])>0; assert int(d["format"]["size"])>0'
if ffprobe -v error -show_entries format=duration -of json -- "$tmp/missing.mp4" >/dev/null 2>&1; then
  echo 'Missing file was unexpectedly accepted' >&2; exit 1
fi
printf 'Media inspection: valid media and missing file checks passed\n'
