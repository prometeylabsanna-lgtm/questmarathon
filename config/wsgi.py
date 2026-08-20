import os

from django.core.wsgi import get_wsgi_application

if not os.environ.get("DJANGO_SETTINGS_MODULE"):
    os.environ["DJANGO_SETTINGS_MODULE"] = (
        "config.settings.staging"
        if os.environ.get("VERCEL")
        else "config.settings.production"
    )

application = get_wsgi_application()
