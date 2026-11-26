#!/usr/bin/env bash
set -euo pipefail
filter='stereowiden=delay=20:feedback=0.3:crossfeed=0.3:drymix=0.8'
for rate in 44100 48000; do
  ffmpeg -nostdin -hide_banner -loglevel error -f lavfi -i "aevalsrc=0.2*sin(2*PI*440*t)|0.2*sin(2*PI*660*t):s=$rate:d=1" -af "$filter" -f null -
  ffmpeg -nostdin -hide_banner -loglevel error -f lavfi -i "aevalsrc=0.2*sin(2*PI*440*t)|0.2*sin(2*PI*440*t):s=$rate:d=1" -af "$filter,loudnorm=I=-16:TP=-1.5:LRA=11" -f null -
done
printf 'Spatial filter: four synthetic stereo cases passed\n'
