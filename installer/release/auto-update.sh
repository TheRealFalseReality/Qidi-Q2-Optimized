#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"
if [ ! -f installer/runtime/bootstrap.py ]; then
  cd "$(dirname -- "$(dirname -- "$SCRIPT_DIR")")"
fi
command -v python3 >/dev/null 2>&1 || {
  echo "Missing required tool: python3" >&2
  exit 1
}
if [ "$#" -eq 1 ] && { [ "$1" = "--version" ] || [ "$1" = "-v" ]; }; then
  exec python3 -I -S installer/runtime/bootstrap.py "$1"
fi
exec python3 -I -S installer/runtime/bootstrap.py auto-update --plain "$@"
