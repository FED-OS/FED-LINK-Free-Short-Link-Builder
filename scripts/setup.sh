#!/usr/bin/env bash
# FED-LINk — one-shot local environment setup.
# Creates a virtual environment, installs runtime + dev dependencies and
# runs the test suite so you know the setup worked.

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_DIR}"

PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> Using $(${PYTHON_BIN} --version)"

echo "==> Creating virtual environment (.venv)"
if [ ! -d .venv ]; then
  "${PYTHON_BIN}" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Installing dependencies"
pip install --upgrade pip
pip install -r requirements.txt
[ -f requirements-dev.txt ] && pip install -r requirements-dev.txt

echo "==> Running tests"
python -m pytest --quiet

echo
echo "Setup complete. Activate with:  source .venv/bin/activate"
echo "Try it out with:               python -m src.main list configs/links.json"
