from django.shortcuts import get_object_or_404, render
from django.utils.translation import get_language, gettext as _

from src.core.block_services import get_block_file, get_block_text, normalize_locale
from src.core.models import SiteSettings
from src.pages.faq import is_faq_email_answer
from src.pages.models import AboutCard, FAQItem, LegalPage


def _locale() -> str:
    return normalize_locale(get_language())


def home(request):
    return render(
        request,
        "pages/home.html",
        {"page_title": _("Квест-марафон")},
    )


def rating(request):
    locale = _locale()
    file_block = get_block_file("rating", "rating_file")
    rating_file_url = ""
    rating_file_kind = ""
    if file_block is not None:
        rating_file_url = file_block.file.url
        rating_file_kind = file_block.file_kind()

    return render(
        request,
        "pages/rating.html",
        {
            "page_title": get_block_text("rating", "page_title", locale=locale),
            "rating_file_url": rating_file_url,
            "rating_file_kind": rating_file_kind,
            "rating_has_file": bool(rating_file_url and rating_file_kind),
        },
    )


def legal_page(request, slug: str):
    locale = _locale()
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


def faq_page(request):
    locale = _locale()
    faq_items = []
    for item in FAQItem.objects.filter(is_active=True):
        answer = item.answer_for(locale)
        faq_items.append(
            {
                "question": item.question_for(locale),
                "answer": answer,
                "is_email": is_faq_email_answer(answer),
            }
        )
    return render(
        request,
        "pages/accordion.html",
        {
            "page_title": get_block_text("faq", "page_title", locale=locale),
            "faq_items": faq_items,
        },
    )


def about_page(request):
    locale = _locale()
    about_cards = [
        {
            "question": card.title_for(locale),
            "answer": card.text_for(locale),
        }
        for card in AboutCard.objects.filter(is_active=True)
    ]
    return render(
        request,
        "pages/about.html",
        {
            "page_title": get_block_text("about", "page_title", locale=locale),
            "about_cards": about_cards,
        },
    )


def contacts_page(request):
    locale = _locale()
    settings_obj = SiteSettings.get_solo()
    return render(
        request,
        "pages/contacts.html",
        {
            "page_title": get_block_text("contacts", "page_title", locale=locale),
            "contact": {
                "phone": settings_obj.phone,
                "phone_href": settings_obj.phone_href(),
                "email": settings_obj.email,
                "address": settings_obj.address_for(locale),
                "socials": settings_obj.socials(),
            },
        },
    )
