#!/usr/bin/env bash
set -euo pipefail

echo "==> Waiting for PostgreSQL..."
python <<'PY'
import os, sys, time
url = os.environ.get("DATABASE_URL", "")
if not url:
    sys.exit(0)
import psycopg2
for i in range(30):
    try:
        psycopg2.connect(url)
        print("==> DB ready")
        break
    except psycopg2.OperationalError:
        time.sleep(2)
else:
    print("FATAL: DB not ready")
    sys.exit(1)
PY

echo "==> Django migrate + collectstatic"
python manage.py migrate --noinput
python manage.py seed_site_blocks
python manage.py seed_demo
python manage.py collectstatic --noinput

exec "$@"
