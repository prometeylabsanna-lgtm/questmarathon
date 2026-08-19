from urllib.parse import urlparse

from django.conf import settings
from django.utils import translation


def _normalize_lang(code: str | None) -> str | None:
    if not code:
        return None
    lowered = code.replace("_", "-").lower()
    if lowered.startswith("ru"):
        return "ru"
    if lowered.startswith("uk"):
        return "uk"
    allowed = {item[0] for item in settings.LANGUAGES}
    return lowered if lowered in allowed else None


def language_from_path(path: str) -> str | None:
    path = path or "/"
    for code, _name in settings.LANGUAGES:
        if path == f"/{code}" or path.startswith(f"/{code}/"):
            return code
    return None


def activate_ui_language(request, profile=None) -> str:
    hx_url = request.headers.get("HX-Current-URL", "")
    hx_path = urlparse(hx_url).path if hx_url else ""
    lang = _normalize_lang(
        language_from_path(hx_path) or language_from_path(request.path)
    )
    if not lang:
        lang = _normalize_lang(
            translation.get_language_from_request(request, check_path=True)
        )
    if not lang and profile is not None:
        lang = _normalize_lang(getattr(profile, "locale", None))
    lang = lang or settings.LANGUAGE_CODE
    translation.activate(lang)
    request.LANGUAGE_CODE = lang
    return lang
