"""Defaults, labels, content types for SiteBlock registry keys."""

from __future__ import annotations

BLOCK_DEFAULTS: dict[tuple[str, str], dict[str, str]] = {
    # home intro
    ("home", "intro_section_visible"): {"text_uk": "1", "text_ru": "1"},
    ("home", "intro_tagline"): {
        "text_uk": "П’ять кімнат, п’ять загадок. Один маршрут — без розвилок і підказок ззовні.",
        "text_ru": "Пять комнат, пять загадок. Один маршрут — без развилок и подсказок извне.",
    },
    ("home", "rules_heading"): {
        "text_uk": "Як проходить квест",
        "text_ru": "Как проходит квест",
    },
    ("home", "rule_1"): {
        "text_uk": "Зареєструйтесь і оплатіть участь, щоб увійти в гру.",
        "text_ru": "Зарегистрируйтесь и оплатите участие, чтобы войти в игру.",
    },
    ("home", "rule_2"): {
        "text_uk": "Йдіть по черзі: наступна кімната відкриється лише після попередньої.",
        "text_ru": "Идите по порядку: следующая комната откроется только после предыдущей.",
    },
    ("home", "rule_3"): {
        "text_uk": "У кімнаті — загадка. Відповідь — ключове слово.",
        "text_ru": "В комнате — загадка. Ответ — ключевое слово.",
    },
    ("home", "rule_4"): {
        "text_uk": "Прогрес зберігається: можна вийти і продовжити пізніше.",
        "text_ru": "Прогресс сохраняется: можно выйти и продолжить позже.",
    },
    ("home", "cta_register"): {"text_uk": "Реєстрація", "text_ru": "Регистрация"},
    ("home", "cta_login"): {"text_uk": "Увійти", "text_ru": "Войти"},
    ("home", "cta_cabinet"): {"text_uk": "До кабінету", "text_ru": "В кабинет"},
    ("home", "preview_image"): {},
    # header
    ("site", "header_nav_home"): {"text_uk": "Головна", "text_ru": "Главная"},
    ("site", "header_nav_about"): {"text_uk": "Про нас", "text_ru": "О нас"},
    ("site", "header_nav_contacts"): {"text_uk": "Контакти", "text_ru": "Контакты"},
    ("site", "header_nav_faq"): {"text_uk": "FAQ", "text_ru": "FAQ"},
    ("site", "header_brand_name"): {
        "text_uk": "kvest-marafon",
        "text_ru": "kvest-marafon",
    },
    ("site", "header_nav_home_visible"): {"text_uk": "1", "text_ru": "1"},
    ("site", "header_nav_about_visible"): {"text_uk": "1", "text_ru": "1"},
    ("site", "header_nav_contacts_visible"): {"text_uk": "1", "text_ru": "1"},
    ("site", "header_nav_faq_visible"): {"text_uk": "1", "text_ru": "1"},
    # footer
    ("site", "footer_link_terms"): {
        "text_uk": "Користувацька угода",
        "text_ru": "Пользовательское соглашение",
    },
    ("site", "footer_link_privacy"): {
        "text_uk": "Політика конфіденційності",
        "text_ru": "Политика конфиденциальности",
    },
    ("site", "footer_copyright"): {
        "text_uk": "Квест-марафон",
        "text_ru": "Квест-марафон",
    },
    ("site", "footer_credit"): {
        "text_uk": "Розроблено командою PrometeyLabs",
        "text_ru": "Разработано командой PrometeyLabs",
    },
    # about / faq / contacts page chrome
    ("about", "page_title"): {"text_uk": "Про нас", "text_ru": "О нас"},
    ("about", "page_lead"): {
        "text_uk": "Хто ми і як влаштований квест.",
        "text_ru": "Кто мы и как устроен квест.",
    },
    ("faq", "page_title"): {"text_uk": "FAQ", "text_ru": "FAQ"},
    ("faq", "page_lead"): {
        "text_uk": "Короткі відповіді про участь, кімнати та прогрес.",
        "text_ru": "Краткие ответы об участии, комнатах и прогрессе.",
    },
    ("contacts", "page_title"): {"text_uk": "Контакти", "text_ru": "Контакты"},
    ("contacts", "page_lead"): {
        "text_uk": "Оберіть зручний спосіб зв’язку — ми відповімо найближчим часом.",
        "text_ru": "Выберите удобный способ связи — мы ответим в ближайшее время.",
    },
    ("contacts", "label_phone"): {"text_uk": "Телефон", "text_ru": "Телефон"},
    ("contacts", "label_email"): {"text_uk": "Email", "text_ru": "Email"},
    ("contacts", "label_address"): {"text_uk": "Адреса", "text_ru": "Адрес"},
}

BLOCK_LABELS: dict[tuple[str, str], str] = {
    ("home", "intro_section_visible"): "Показувати intro",
    ("home", "intro_tagline"): "Слоган",
    ("home", "rules_heading"): "Заголовок правил",
    ("home", "rule_1"): "Правило 1",
    ("home", "rule_2"): "Правило 2",
    ("home", "rule_3"): "Правило 3",
    ("home", "rule_4"): "Правило 4",
    ("home", "cta_register"): "Кнопка «Реєстрація»",
    ("home", "cta_login"): "Кнопка «Увійти»",
    ("home", "cta_cabinet"): "Кнопка «Кабінет»",
    ("home", "preview_image"): "Прев’ю зображення",
    ("site", "header_nav_home"): "Пункт «Головна»",
    ("site", "header_nav_about"): "Пункт «Про нас»",
    ("site", "header_nav_contacts"): "Пункт «Контакти»",
    ("site", "header_nav_faq"): "Пункт «FAQ»",
    ("site", "header_brand_name"): "Назва бренду",
    ("site", "header_nav_home_visible"): "Показувати «Головна»",
    ("site", "header_nav_about_visible"): "Показувати «Про нас»",
    ("site", "header_nav_contacts_visible"): "Показувати «Контакти»",
    ("site", "header_nav_faq_visible"): "Показувати «FAQ»",
    ("site", "footer_link_terms"): "Посилання «Угода»",
    ("site", "footer_link_privacy"): "Посилання «Конфіденційність»",
    ("site", "footer_copyright"): "Назва в copyright",
    ("about", "page_title"): "Заголовок сторінки",
    ("about", "page_lead"): "Підзаголовок",
    ("faq", "page_title"): "Заголовок сторінки",
    ("faq", "page_lead"): "Підзаголовок",
    ("contacts", "page_title"): "Заголовок сторінки",
    ("contacts", "page_lead"): "Підзаголовок",
    ("contacts", "label_phone"): "Підпис «Телефон»",
    ("contacts", "label_email"): "Підпис «Email»",
    ("contacts", "label_address"): "Підпис «Адреса»",
}

BLOCK_CONTENT_TYPES: dict[tuple[str, str], str] = {
    ("home", "preview_image"): "image",
}

INLINE_KEYS = frozenset(
    {
        "rules_heading",
        "cta_register",
        "cta_login",
        "cta_cabinet",
        "header_nav_home",
        "header_nav_about",
        "header_nav_contacts",
        "header_nav_faq",
        "header_brand_name",
        "footer_link_terms",
        "footer_link_privacy",
        "footer_copyright",
        "page_title",
        "label_phone",
        "label_email",
        "label_address",
    }
)

MULTILINE_KEYS = frozenset(
    {
        "intro_tagline",
        "rule_1",
        "rule_2",
        "rule_3",
        "rule_4",
        "page_lead",
        "footer_credit",
    }
)


def is_visibility_key(key: str) -> bool:
    return key.endswith("_visible")


def default_for(page: str, key: str, locale: str = "uk") -> str:
    data = BLOCK_DEFAULTS.get((page, key), {})
    if is_visibility_key(key):
        return data.get("text_uk", "1")
    if locale == "ru":
        return data.get("text_ru") or data.get("text_uk", "")
    return data.get("text_uk", "")
