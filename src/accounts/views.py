from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import get_language, gettext as _
from django.views.decorators.http import require_http_methods

from src.accounts.forms import (
    EmailAuthenticationForm,
    QuestPasswordResetForm,
    QuestSetPasswordForm,
    RegisterForm,
)
from src.accounts.models import UserProfile
from src.core.i18n import activate_ui_language


class QuestLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        activate_ui_language(request)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("accounts:cabinet")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Вхід")
        return context


class QuestLogoutView(LogoutView):
    next_page = reverse_lazy("pages:home")


@require_http_methods(["GET", "POST"])
def register(request):
    activate_ui_language(request)
    if request.user.is_authenticated:
        return redirect("accounts:cabinet")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        profile = user.profile
        profile.locale = get_language() or "uk"
        profile.save(update_fields=["locale", "updated_at"])
        login(request, user)
        return redirect("payments:start")
    return render(
        request,
        "accounts/register.html",
        {"form": form, "page_title": _("Реєстрація")},
    )


def _cabinet_rooms(profile: UserProfile) -> list[dict]:
    level = profile.current_level
    rooms = []
    for n in range(1, 6):
        if n <= level:
            state = "done"
            status_label = _("Пройдено")
            url = reverse("quest:room", kwargs={"n": n})
        elif n == level + 1 and level < 5:
            state = "current"
            status_label = _("Поточна")
            url = reverse("quest:room", kwargs={"n": n})
        else:
            state = "locked"
            status_label = _("Заблоковано")
            url = None
        rooms.append(
            {
                "n": n,
                "number": f"{n:02d}",
                "state": state,
                "status_label": status_label,
                "url": url,
            }
        )
    return rooms


def _cabinet_game_cta(profile: UserProfile) -> tuple[str, str]:
    level = profile.current_level
    if level <= 0:
        return _("Почати гру"), reverse("quest:room", kwargs={"n": 1})
    if level >= 5:
        return _("Переглянути кімнати"), reverse("quest:room", kwargs={"n": 1})
    return _("Продовжити гру"), reverse("quest:room", kwargs={"n": level + 1})


@login_required
def cabinet(request):
    activate_ui_language(request)
    profile = UserProfile.for_user(request.user)
    context = {
        "profile": profile,
        "page_title": _("Кабінет"),
        "rooms": [],
        "game_cta_label": "",
        "game_cta_url": "",
    }
    if profile.is_paid:
        context["rooms"] = _cabinet_rooms(profile)
        label, url = _cabinet_game_cta(profile)
        context["game_cta_label"] = label
        context["game_cta_url"] = url
    return render(request, "accounts/cabinet.html", context)


class QuestPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/email/password_reset_email.txt"
    subject_template_name = "accounts/email/password_reset_subject.txt"
    form_class = QuestPasswordResetForm
    success_url = reverse_lazy("accounts:password_reset_done")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Відновлення пароля")
        return context


class QuestPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Лист надіслано")
        return context


class QuestPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    form_class = QuestSetPasswordForm
    success_url = reverse_lazy("accounts:password_reset_complete")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Новий пароль")
        return context


class QuestPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Пароль змінено")
        return context
