"""Registry of CMS content sections for Unfold sidebar + forms."""

from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings


@dataclass(frozen=True)
class FieldGroup:
    title: str
    keys: tuple[str, ...]


@dataclass(frozen=True)
class ContentSection:
    slug: str
    page_slug: str
    title: str
    blocks: tuple[tuple[str, str], ...]
    sidebar_title: str = ""
    sidebar_icon: str = "edit_note"
    preview_url: str = "/"
    description: str = ""
    visibility_key: str = ""
    field_groups: tuple[FieldGroup, ...] = ()
    admin_model_name: str = ""
    collection: str = ""  # "about_cards" | "faq_items"


CONTENT_SECTIONS: tuple[ContentSection, ...] = (
    ContentSection(
        slug="intro",
        page_slug="home",
        title="Головна",
        sidebar_title="Головна",
        sidebar_icon="home",
        preview_url="/",
        description="Слоган, правила, прев’ю та кнопки на головній.",
        visibility_key="intro_section_visible",
        admin_model_name="homeintrosettings",
        blocks=(
            ("home", "intro_section_visible"),
            ("home", "intro_tagline"),
            ("home", "rules_heading"),
            ("home", "rule_1"),
            ("home", "rule_2"),
            ("home", "rule_3"),
            ("home", "rule_4"),
            ("home", "preview_image"),
            ("home", "cta_register"),
            ("home", "cta_login"),
            ("home", "cta_cabinet"),
        ),
        field_groups=(
            FieldGroup("Текст", ("intro_tagline", "rules_heading")),
            FieldGroup("Правила", ("rule_1", "rule_2", "rule_3", "rule_4")),
            FieldGroup("Медіа", ("preview_image",)),
            FieldGroup("CTA", ("cta_register", "cta_login", "cta_cabinet")),
        ),
    ),
    ContentSection(
        slug="header",
        page_slug="site",
        title="Шапка сайту",
        sidebar_title="Шапка",
        sidebar_icon="menu",
        preview_url="/",
        description="Пункти меню та назва бренду. Логотип — у «Налаштування сайту».",
        admin_model_name="siteheadersettings",
        blocks=(
            ("site", "header_brand_name"),
            ("site", "header_nav_home"),
            ("site", "header_nav_home_visible"),
            ("site", "header_nav_about"),
            ("site", "header_nav_about_visible"),
            ("site", "header_nav_contacts"),
            ("site", "header_nav_contacts_visible"),
            ("site", "header_nav_faq"),
            ("site", "header_nav_faq_visible"),
        ),
        field_groups=(
            FieldGroup("Бренд", ("header_brand_name",)),
            FieldGroup(
                "Навігація",
                (
                    "header_nav_home",
                    "header_nav_home_visible",
                    "header_nav_about",
                    "header_nav_about_visible",
                    "header_nav_contacts",
                    "header_nav_contacts_visible",
                    "header_nav_faq",
                    "header_nav_faq_visible",
                ),
            ),
        ),
    ),
    ContentSection(
        slug="footer",
        page_slug="site",
        title="Підвал сайту",
        sidebar_title="Підвал",
        sidebar_icon="vertical_align_bottom",
        preview_url="/",
        description="Юридичні посилання та copyright.",
        admin_model_name="sitefootersettings",
        blocks=(
            ("site", "footer_link_terms"),
            ("site", "footer_link_privacy"),
            ("site", "footer_copyright"),
        ),
        field_groups=(
            FieldGroup(
                "Посилання та тексти",
                (
                    "footer_link_terms",
                    "footer_link_privacy",
                    "footer_copyright",
                ),
            ),
        ),
    ),
    ContentSection(
        slug="main",
        page_slug="about",
        title="Про нас",
        sidebar_title="Про нас",
        sidebar_icon="info",
        preview_url="/about/",
        description="Заголовки сторінки та картки контенту.",
        admin_model_name="aboutpagesettings",
        collection="about_cards",
        blocks=(("about", "page_title"), ("about", "page_lead")),
        field_groups=(FieldGroup("Заголовки", ("page_title", "page_lead")),),
    ),
    ContentSection(
        slug="main",
        page_slug="faq",
        title="FAQ",
        sidebar_title="FAQ",
        sidebar_icon="help",
        preview_url="/faq/",
        description="Заголовки сторінки та пункти запитань.",
        admin_model_name="faqpagesettings",
        collection="faq_items",
        blocks=(("faq", "page_title"), ("faq", "page_lead")),
        field_groups=(FieldGroup("Заголовки", ("page_title", "page_lead")),),
    ),
    ContentSection(
        slug="main",
        page_slug="contacts",
        title="Контакти",
        sidebar_title="Контакти",
        sidebar_icon="call",
        preview_url="/contacts/",
        description="Тексти сторінки. Телефон, email і соцмережі — у «Налаштування сайту».",
        admin_model_name="contactspagesettings",
        blocks=(
            ("contacts", "page_title"),
            ("contacts", "page_lead"),
            ("contacts", "label_phone"),
            ("contacts", "label_email"),
            ("contacts", "label_address"),
        ),
        field_groups=(
            FieldGroup("Заголовки", ("page_title", "page_lead")),
            FieldGroup("Мітки полів", ("label_phone", "label_email", "label_address")),
        ),
    ),
)


def get_section(page_slug: str, section_slug: str) -> ContentSection | None:
    for section in CONTENT_SECTIONS:
        if section.page_slug == page_slug and section.slug == section_slug:
            return section
    return None


def all_registry_block_keys() -> list[tuple[str, str]]:
    keys: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for section in CONTENT_SECTIONS:
        for pair in section.blocks:
            if pair not in seen:
                seen.add(pair)
                keys.append(pair)
    return keys


def iter_section_blocks(section: ContentSection) -> list[tuple[str, str]]:
    return list(section.blocks)


def _admin_link(model_name: str) -> str:
    # Plain str — Vercel JSON-encodes UNFOLD settings; reverse_lazy breaks deploy.
    prefix = f"/{getattr(settings, 'ADMIN_URL', 'kvest-cms/').strip('/')}/"
    return f"{prefix}core/{model_name}/"


def build_content_sidebar_items() -> list[dict]:
    return [
        {
            "title": section.sidebar_title or section.title,
            "icon": section.sidebar_icon,
            "link": _admin_link(section.admin_model_name),
        }
        for section in CONTENT_SECTIONS
    ]


def validate_registry() -> None:
    names = [s.admin_model_name for s in CONTENT_SECTIONS]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate admin_model_name in CONTENT_SECTIONS")
    keys = all_registry_block_keys()
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate (page, key) in CONTENT_SECTIONS")
    for section in CONTENT_SECTIONS:
        if section.visibility_key:
            pair = (section.page_slug, section.visibility_key)
            if pair not in section.blocks:
                raise ValueError(
                    f"visibility_key {pair} missing from section {section.admin_model_name}"
                )
