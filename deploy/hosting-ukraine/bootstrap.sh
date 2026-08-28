#!/usr/bin/env bash
# One-time / update bootstrap on Hosting Ukraine (SSH). Not used as web start command.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3.12}"
SEED="${SEED:-0}"

if [[ ! -d .venv ]]; then
  echo "==> Creating venv ($PYTHON_BIN)"
  "$PYTHON_BIN" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.production}"

echo "==> Installing requirements"
pip install --upgrade pip
pip install -r requirements.txt

echo "==> migrate"
python manage.py migrate --noinput

if [[ "$SEED" == "1" ]]; then
  echo "==> seed_site_blocks + seed_demo"
  python manage.py seed_site_blocks
  python manage.py seed_demo
fi

echo "==> collectstatic"
python manage.py collectstatic --noinput

echo "==> Bootstrap done"
