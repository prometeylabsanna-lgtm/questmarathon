from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django.views.generic import RedirectView, TemplateView
from django.views.static import serve

from src.core.views import health
from src.pages.sitemaps import InfoPageSitemap, StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "info": InfoPageSitemap,
}

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
    path("api/v1/health/", health, name="health"),
    path("api/v1/quest/", include("src.quest.api_urls")),
    path("api/v1/payment/", include("src.payments.api_urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path(
        "favicon.ico",
        RedirectView.as_view(url="/static/images/favicon.ico", permanent=False),
        name="favicon",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots",
    ),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

urlpatterns += i18n_patterns(
    path("", include("src.accounts.urls")),
    path("payment/", include("src.payments.urls")),
    path("quest/", include("src.quest.urls")),
    path("", include("src.pages.urls")),
    prefix_default_language=False,
)

handler404 = "src.core.views.handler404"
handler500 = "src.core.views.handler500"

# Media via Django (DEBUG=False too): Hosting Ukraine proxies all traffic to Gunicorn.
# Do not use django.conf.urls.static.static() — it is a no-op when DEBUG is False.
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
