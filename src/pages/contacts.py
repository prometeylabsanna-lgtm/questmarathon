SOCIAL_LINKS = [
    {
        "id": "telegram",
        "label": "Telegram",
        "href": "https://t.me/kvestmarafon",
    },
    {
        "id": "instagram",
        "label": "Instagram",
        "href": "https://www.instagram.com/kvestmarafon/",
    },
    {
        "id": "facebook",
        "label": "Facebook",
        "href": "https://www.facebook.com/kvestmarafon",
    },
]


def contact_details(locale: str) -> dict:
    if locale == "ru":
        address = "ул. Крещатик, 1, г. Киев"
    else:
        address = "вул. Хрещатик, 1, м. Київ"
    return {
        "phone": "+38 (093) 000-11-22",
        "phone_href": "tel:+380930001122",
        "email": "info@example.com",
        "address": address,
        "socials": SOCIAL_LINKS,
    }
