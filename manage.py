#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    # Prefer explicit env; on Vercel default to staging (do not use decouple here —
    # empty/missing env must not leave DJANGO_SETTINGS_MODULE unset).
    if not os.environ.get("DJANGO_SETTINGS_MODULE"):
        os.environ["DJANGO_SETTINGS_MODULE"] = (
            "config.settings.staging"
            if os.environ.get("VERCEL")
            else "config.settings.develop"
        )
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Is it installed and available on your PYTHONPATH?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
