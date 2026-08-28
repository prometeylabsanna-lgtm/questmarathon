from django.conf import settings
from django.core.cache import cache

from src.core.block_services import load_site_blocks
from src.core.i18n import path_for_language
from src.core.models import (
    SITE_SETTINGS_CACHE_KEY,
    STATS_CACHE_KEY,
    SiteSettings,
    SiteStats,
)

_CACHE_TTL = 30


def site_globals(request):
    count = cache.get(STATS_CACHE_KEY)
    if count is None:
        stats = SiteStats.get_solo()
        count = stats.participants_count
        cache.set(STATS_CACHE_KEY, count, _CACHE_TTL)

    site_settings = cache.get(SITE_SETTINGS_CACHE_KEY)
    if site_settings is None:
        site_settings = SiteSettings.get_solo()
        cache.set(SITE_SETTINGS_CACHE_KEY, site_settings, 60)

    path = request.get_full_path()
    return {
        "participants_count": count,
        "counter_display": f"{count:07d}",
        "language_urls": {
            code: path_for_language(path, code) for code, _name in settings.LANGUAGES
        },
        "site_settings": site_settings,
        "site_blocks": load_site_blocks(),
    }
