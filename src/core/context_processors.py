from django.core.cache import cache

from src.core.models import STATS_CACHE_KEY, SiteStats

_CACHE_TTL = 30  # seconds; counter is denormalized, short TTL is enough


def site_globals(request):
    count = cache.get(STATS_CACHE_KEY)
    if count is None:
        stats = SiteStats.get_solo()
        count = stats.participants_count
        cache.set(STATS_CACHE_KEY, count, _CACHE_TTL)
    return {
        "participants_count": count,
        "counter_display": f"{count:07d}",
    }
