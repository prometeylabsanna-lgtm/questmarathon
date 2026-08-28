#!/usr/bin/env bash
# Web start command for Hosting Ukraine «Налаштування веб-застосунку».
# Set HU_BIND_HOST / HU_BIND_PORT in .env from the panel proxy block.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if [[ ! -f .venv/bin/activate ]]; then
  echo "FATAL: .venv missing. Run: bash deploy/hosting-ukraine/bootstrap.sh" >&2
  exit 1
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

: "${HU_BIND_HOST:?Set HU_BIND_HOST in .env (panel: Проксування HTTP-трафіку)}"
: "${HU_BIND_PORT:?Set HU_BIND_PORT in .env (usually 3000)}"

exec gunicorn config.wsgi:application \
  --bind "${HU_BIND_HOST}:${HU_BIND_PORT}" \
  --workers "${GUNICORN_WORKERS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-120}"
