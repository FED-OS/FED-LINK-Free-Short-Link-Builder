#!/usr/bin/env bash
# FED-LINk — build the short link bundle locally.
# Usage: scripts/build.sh [links-file] [output-dir] [zip-name]

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_DIR}"

LINKS="${1:-configs/links.json}"
OUTPUT="${2:-output}"
ZIP="${3:-links.zip}"

# Use the project virtualenv when present, fall back to system python.
if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "==> Validating ${LINKS}"
python -m src.main validate "${LINKS}"

echo "==> Building bundle into ${OUTPUT}"
python -m src.main build "${LINKS}" --output "${OUTPUT}" --zip "${ZIP}"

echo
echo "Done. Upload ${ZIP} to the InfinityFree htdocs folder, or extract"
echo "it with the control panel file manager."
