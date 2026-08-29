#!/usr/bin/env bash
set -euo pipefail

echo "==> Waiting for database..."
python <<'PY'
import os, sys, time

url = os.environ.get("DATABASE_URL", "")
if not url:
    sys.exit(0)

scheme = url.split(":", 1)[0].split("+")[0].lower()

for _ in range(30):
    try:
        if scheme in ("postgres", "postgresql"):
            import psycopg2

            psycopg2.connect(url)
        elif scheme == "mysql":
            import urllib.parse as urlparse

            import pymysql

            parsed = urlparse.urlparse(url)
            pymysql.connect(
                host=parsed.hostname,
                port=parsed.port or 3306,
                user=urlparse.unquote(parsed.username or ""),
                password=urlparse.unquote(parsed.password or ""),
                database=parsed.path.lstrip("/"),
                connect_timeout=3,
            ).close()
        else:
            print(f"FATAL: unsupported DATABASE_URL scheme {scheme!r}")
            sys.exit(1)
        print("==> DB ready")
        break
    except Exception:
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
