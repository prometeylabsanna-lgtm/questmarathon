from django.shortcuts import get_object_or_404, render
from django.utils.translation import get_language, gettext as _

from src.pages.faq import parse_faq_items
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
    context = {"page": page, "page_title": page.title}
    if slug == "faq":
        context["faq_items"] = parse_faq_items(page.body)
        template = "pages/faq.html"
    else:
        template = "pages/info.html"
    return render(request, template, context)
