#!/usr/bin/env bash
# FED-LINk — deployment helper.
# Produces a timestamped bundle and prints the manual upload checklist for
# the InfinityFree control panel. InfinityFree has no upload API for free
# accounts, so the actual upload stays a two-click manual step.

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_DIR}"

LINKS="${LINKS:-configs/links.json}"
STAMP="$(date -u +%Y%m%d-%H%M%S)"
DEPLOY_DIR="build/deploy-${STAMP}"

if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "==> Building deployable bundle for ${LINKS}"
python -m src.main build "${LINKS}" --output "${DEPLOY_DIR}/output" --zip "${DEPLOY_DIR}/links.zip"

echo
echo "Bundle ready: ${DEPLOY_DIR}/links.zip"
echo
echo "InfinityFree upload checklist:"
echo "  1. Log in to the InfinityFree client area."
echo "  2. Open Control Panel -> File Manager for the hosting account."
echo "  3. Navigate to the htdocs folder of link.fedpromptly.com."
echo "  4. Remove the old .htaccess and short link folders (or overwrite)."
echo "  5. Upload ${DEPLOY_DIR}/links.zip."
echo "  6. Use Extract in the file manager to unpack it into htdocs."
echo "  7. Verify https://link.fedpromptly.com/portfolio redirects correctly."
echo
echo "Keep ${DEPLOY_DIR}/links.zip as a rollback copy of this deployment."
