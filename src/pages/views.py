from django.shortcuts import get_object_or_404, render
from django.utils.translation import get_language, gettext as _

from src.pages.models import InfoPage

INFO_SLUGS = ("about", "faq", "contacts", "terms", "privacy")


def home(request):
    return render(
        request,
        "pages/home.html",
        {"page_title": _("Квест-марафон")},
    )


def info_page(request, slug: str):
    if slug not in INFO_SLUGS:
        return render(request, "errors/404.html", status=404)
    locale = get_language() or "uk"
    if locale.startswith("ru"):
        locale = "ru"
    else:
        locale = "uk"
    page = get_object_or_404(InfoPage, slug=slug, locale=locale, is_published=True)
    return render(
        request,
        "pages/info.html",
        {"page": page, "page_title": page.title},
    )
