#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/.." && pwd)
map() { bash "$root/packaging/debian-version.sh" "$@"; }
[[ $(map 2.6.0-beta.1) == '2.6.0~beta.1' ]]
[[ $(map 2.6.0) == 2.6.0 ]]
dpkg --compare-versions "$(map 2.6.0-beta.2)" lt "$(map 2.6.0-beta.10)"
dpkg --compare-versions "$(map 2.6.0-beta.10)" lt "$(map 2.6.0)"
dpkg --compare-versions 2.5.0-beta.1 lt "$(map 2.6.0-beta.1)"
for invalid in '02.6.0' '2.6.0-rc.1' '2.6.0-beta.01' '2.6.0/evil' ''; do
  if map "$invalid" >/dev/null 2>&1; then echo "Accepted invalid version: $invalid" >&2; exit 1; fi
done
printf 'Debian version mapping: 10 checks passed\n'
