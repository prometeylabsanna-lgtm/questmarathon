from django.shortcuts import get_object_or_404, render
from django.utils.translation import get_language, gettext as _

from src.core.block_services import get_block_text, normalize_locale
from src.core.models import SiteSettings
from src.pages.models import AboutCard, FAQItem, LegalPage

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

    locale = normalize_locale(get_language())

    if slug in ("terms", "privacy"):
        page = get_object_or_404(LegalPage, slug=slug, is_published=True)
        context = {
            "page": page,
            "page_title": page.title_for(locale),
            "page_lead": page.updated_label_for(locale),
            "legal_body": page.body_for(locale),
        }
        if slug == "terms":
            context["legal_alt_url"] = "pages:privacy"
            context["legal_alt_label"] = _("Політика конфіденційності")
        else:
            context["legal_alt_url"] = "pages:terms"
            context["legal_alt_label"] = _("Користувацька угода")
        return render(request, "pages/legal.html", context)

    if slug == "faq":
        items = FAQItem.objects.filter(is_active=True)
        faq_items = []
        for item in items:
            answer = item.answer_for(locale)
            compact = answer.replace(" ", "")
            faq_items.append(
                {
                    "question": item.question_for(locale),
                    "answer": answer,
                    "is_email": "@" in compact and "\n" not in answer and " " not in answer,
                }
            )
        context = {
            "page_title": get_block_text("faq", "page_title", locale=locale),
            "page_lead": get_block_text("faq", "page_lead", locale=locale),
            "faq_items": faq_items,
        }
        return render(request, "pages/accordion.html", context)

    if slug == "about":
        cards = AboutCard.objects.filter(is_active=True)
        about_cards = [
            {
                "question": card.title_for(locale),
                "answer": card.text_for(locale),
            }
            for card in cards
        ]
        context = {
            "page_title": get_block_text("about", "page_title", locale=locale),
            "page_lead": get_block_text("about", "page_lead", locale=locale),
            "about_cards": about_cards,
        }
        return render(request, "pages/about.html", context)

    if slug == "contacts":
        settings_obj = SiteSettings.get_solo()
        context = {
            "page_title": get_block_text("contacts", "page_title", locale=locale),
            "page_lead": get_block_text("contacts", "page_lead", locale=locale),
            "contact": {
                "phone": settings_obj.phone,
                "phone_href": settings_obj.phone_href(),
                "email": settings_obj.email,
                "address": settings_obj.address_for(locale),
                "socials": settings_obj.socials(),
            },
        }
        return render(request, "pages/contacts.html", context)

    return render(request, "errors/404.html", status=404)
