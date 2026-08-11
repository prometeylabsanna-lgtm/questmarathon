from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from src.pages.models import InfoPage


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ["pages:home", "pages:about", "pages:faq", "pages:contacts", "pages:terms", "pages:privacy"]

    def location(self, item):
        return reverse(item)


class InfoPageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return InfoPage.objects.filter(is_published=True, locale="uk")

    def location(self, obj):
        return reverse(f"pages:{obj.slug}")
