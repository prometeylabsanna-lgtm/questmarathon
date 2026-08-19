from urllib.parse import urlparse, urlunparse

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
    pathname = urlparse(path or "/").path or "/"
    for code, _name in settings.LANGUAGES:
        if pathname == f"/{code}" or pathname.startswith(f"/{code}/"):
            return code
    return None


def path_without_language(path: str) -> str:
    parsed = urlparse(path or "/")
    pathname = parsed.path or "/"
    for code, _name in settings.LANGUAGES:
        if pathname == f"/{code}":
            pathname = "/"
            break
        prefix = f"/{code}/"
        if pathname.startswith(prefix):
            pathname = pathname[len(code) + 1 :]
            if not pathname.startswith("/"):
                pathname = f"/{pathname}"
            break
    return urlunparse(("", "", pathname, "", parsed.query, parsed.fragment))


def path_for_language(path: str, code: str) -> str:
    stripped = path_without_language(path)
    parsed = urlparse(stripped)
    pathname = parsed.path or "/"
    if code == settings.LANGUAGE_CODE:
        new_path = pathname
    elif pathname == "/":
        new_path = f"/{code}/"
    else:
        new_path = f"/{code}{pathname}"
    return urlunparse(("", "", new_path, "", parsed.query, parsed.fragment))


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
