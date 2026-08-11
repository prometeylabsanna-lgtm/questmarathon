from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from src.core.views import health
from src.pages.sitemaps import InfoPageSitemap, StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "info": InfoPageSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/health/", health, name="health"),
    path("api/v1/quest/", include("src.quest.api_urls")),
    path("api/v1/payment/", include("src.payments.api_urls")),
    path("i18n/", include("django.conf.urls.i18n")),
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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
