#!/usr/bin/env bash
# Readiness probe only: never installs packages or launches a build.
set -u
missing=0
for tool in git cmake ctest c++ pkg-config python3 openssl ffmpeg ffprobe mpv dpkg dpkg-deb zip unzip sha256sum xvfb-run timeout; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf 'OK tool %s\n' "$tool"
  else
    printf 'MISSING tool %s\n' "$tool"
    missing=1
  fi
done
for module in Qt6Widgets Qt6Test; do
  if command -v pkg-config >/dev/null 2>&1 && pkg-config --atleast-version=6.2 "$module"; then
    printf 'OK Qt module %s\n' "$module"
  else
    printf 'MISSING Qt module %s (>=6.2)\n' "$module"
    missing=1
  fi
done
if [[ $(uname -m) != x86_64 ]]; then
  printf 'UNSUPPORTED architecture: %s\n' "$(uname -m)"
  missing=1
fi
if (( missing )); then
  printf 'BLOCKED: native build prerequisites incomplete\n'
else
  printf 'READY: native build prerequisites found (build not yet tested)\n'
fi
exit "$missing"
