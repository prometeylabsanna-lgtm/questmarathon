from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from src.pages.models import LegalPage


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return [
            "pages:home",
            "pages:about",
            "pages:faq",
            "pages:contacts",
            "pages:rating",
        ]

    def location(self, item):
        return reverse(item)


class LegalPageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return LegalPage.objects.filter(is_published=True)

    def location(self, obj):
        return reverse(f"pages:{obj.slug}")
