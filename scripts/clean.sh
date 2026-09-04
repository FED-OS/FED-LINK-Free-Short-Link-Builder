#!/usr/bin/env bash
# FED-LINk — remove build artifacts.
# Deletes generated bundles, zips and caches but never touches source,
# configs or the version-controlled .keep placeholder files.

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_DIR}"

echo "==> Cleaning generated artifacts"

# Generated bundle folder (keep the .keep placeholder)
if [ -d output ]; then
  find output -mindepth 1 ! -name '.keep' -delete
  echo "    cleaned output/"
fi

# Build scratch folder
if [ -d build ]; then
  find build -mindepth 1 ! -name '.keep' -delete
  echo "    cleaned build/"
fi

# Distribution output
if [ -d dist ]; then
  find dist -mindepth 1 ! -name '.keep' -delete
  echo "    cleaned dist/"
fi

# Loose zips at the project root
rm -f links.zip .htaccess.preview
echo "    removed links.zip / .htaccess.preview"

# Caches and logs
rm -rf .pytest_cache .ruff_cache .mypy_cache __pycache__
find . -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
if [ -d logs ]; then
  find logs -type f -name '*.log' -delete
  echo "    cleaned logs/*.log"
fi

echo "==> Clean complete"
