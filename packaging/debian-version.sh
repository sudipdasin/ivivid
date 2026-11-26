#!/usr/bin/env bash
set -euo pipefail
[[ $# == 1 ]] || { echo 'Expected one application version' >&2; exit 1; }
v=$1
[[ $v =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-beta\.(0|[1-9][0-9]*))?$ ]] || { echo 'Invalid application version' >&2; exit 1; }
printf '%s\n' "${v/-beta./~beta.}"
