from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import get_language
from django.views.decorators.http import require_http_methods

from src.accounts.models import UserProfile
from src.quest.models import QuestRoom, normalize_keyword


def _get_profile(user) -> UserProfile:
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={"full_name": user.get_username(), "phone": ""},
    )
    return profile


def _can_access_room(profile: UserProfile, room_order: int) -> bool:
    if not profile.is_paid:
        return False
    return room_order <= profile.current_level + 1


@login_required
def room(request, n: int):
    if n < 1 or n > 5:
        return redirect("accounts:cabinet")
    profile = _get_profile(request.user)
    if not profile.is_paid:
        return redirect("accounts:cabinet")
    if not _can_access_room(profile, n):
        return render(
            request,
            "quest/denied.html",
            {"page_title": "Немає доступу", "room_number": n},
            status=403,
        )
    quest_room = get_object_or_404(QuestRoom, order=n, is_active=True)
    locale = get_language() or profile.locale or "uk"
    return render(
        request,
        "quest/room.html",
        {
            "page_title": quest_room.title_for(locale),
            "room": quest_room,
            "room_number": n,
            "profile": profile,
            "title": quest_room.title_for(locale),
            "body": quest_room.body_for(locale),
        },
    )


@login_required
@require_http_methods(["POST"])
def check_keyword(request, n: int):
    profile = _get_profile(request.user)
    if not profile.is_paid or not _can_access_room(profile, n):
        return render(
            request,
            "quest/partials/keyword_result.html",
            {"ok": False, "error": "Немає доступу"},
            status=403,
        )
    quest_room = get_object_or_404(QuestRoom, order=n, is_active=True)
    submitted = normalize_keyword(request.POST.get("keyword", ""))
    if not submitted or submitted != quest_room.keyword_normalized:
        return render(
            request,
            "quest/partials/keyword_result.html",
            {"ok": False, "error": "Невірне ключове слово"},
        )

    if profile.current_level < n:
        profile.current_level = n
        profile.save(update_fields=["current_level", "updated_at"])

    if n < 5:
        redirect_url = reverse("quest:room", kwargs={"n": n + 1})
        response = render(
            request,
            "quest/partials/keyword_result.html",
            {"ok": True, "redirect_url": redirect_url, "message": "Вірно!"},
        )
        response["HX-Redirect"] = redirect_url
        return response

    return render(
        request,
        "quest/partials/keyword_result.html",
        {
            "ok": True,
            "message": "Квест пройдено. Усі кімнати доступні.",
            "redirect_url": reverse("accounts:cabinet"),
        },
    )
