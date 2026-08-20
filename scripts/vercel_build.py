#!/usr/bin/env python3
"""Vercel build hook: migrate + seed. Requires env vars at Build time."""
from __future__ import annotations

import os
import sys


def main() -> int:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.staging")

    missing = [k for k in ("SECRET_KEY", "DATABASE_URL") if not os.environ.get(k)]
    if missing:
        print(
            "ERROR: missing Vercel env (enable for Build): " + ", ".join(missing),
            file=sys.stderr,
        )
        return 1

    from django.core.management import execute_from_command_line

    execute_from_command_line(["manage.py", "migrate", "--noinput"])
    execute_from_command_line(["manage.py", "seed_demo"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
