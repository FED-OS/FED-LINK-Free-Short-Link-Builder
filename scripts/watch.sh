#!/usr/bin/env bash
# FED-LINk — rebuild the bundle whenever a links or template file changes.
# Requires inotifywait (sudo apt-get install inotify-tools).

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_DIR}"

if ! command -v inotifywait >/dev/null 2>&1; then
  echo "error: inotifywait is required (sudo apt-get install inotify-tools)" >&2
  exit 1
fi

LINKS="${LINKS:-configs/links.json}"

if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "==> Building once at startup"
python -m src.main build "${LINKS}" || true

echo "==> Watching configs/ and templates/ for changes (Ctrl-C to stop)"
while true; do
  change="$(inotifywait --quiet --event close_write \
    --format '%w%f' \
    configs templates)"
  echo "--> ${change} changed, rebuilding"
  python -m src.main build "${LINKS}" || echo "    build failed; keeping previous output"
done
