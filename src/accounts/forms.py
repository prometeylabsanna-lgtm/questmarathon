from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from src.accounts.models import UserProfile

User = get_user_model()


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Ел. пошта"),
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "username",
                "class": "qm-input",
                "inputmode": "email",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password"].label = _("Пароль")
        self.fields["password"].widget.attrs.update(
            {"class": "qm-input", "autocomplete": "current-password"}
        )


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Ел. пошта"),
        widget=forms.EmailInput(attrs={"class": "qm-input", "autocomplete": "email"}),
    )
    full_name = forms.CharField(
        label=_("Ім'я"),
        max_length=150,
        widget=forms.TextInput(attrs={"class": "qm-input", "autocomplete": "name"}),
    )
    phone = forms.CharField(
        label=_("Телефон"),
        max_length=32,
        widget=forms.TextInput(
            attrs={
                "class": "qm-input",
                "autocomplete": "tel",
                "inputmode": "tel",
                "type": "tel",
            }
        ),
    )
    consent_terms = forms.BooleanField(
        label=_("Згода з користувацькою угодою"),
        widget=forms.CheckboxInput(attrs={"class": "qm-checkbox"}),
    )
    consent_age18 = forms.BooleanField(
        label=_("Мені виповнилось 18 років"),
        widget=forms.CheckboxInput(attrs={"class": "qm-checkbox"}),
    )

    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = _("Пароль")
        self.fields["password1"].widget.attrs.update(
            {"class": "qm-input", "autocomplete": "new-password"}
        )
        self.fields["password2"].label = _("Підтвердження пароля")
        self.fields["password2"].widget.attrs.update(
            {"class": "qm-input", "autocomplete": "new-password"}
        )
        self.order_fields(
            [
                "email",
                "password1",
                "password2",
                "full_name",
                "phone",
                "consent_terms",
                "consent_age18",
            ]
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("Користувач з таким email уже існує."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"].strip().lower()
        user.username = email
        user.email = email
        if commit:
            user.save()
            now = timezone.now()
            UserProfile.objects.create(
                user=user,
                full_name=self.cleaned_data["full_name"].strip(),
                phone=self.cleaned_data["phone"].strip(),
                consent_terms_at=now,
                consent_age18_at=now,
            )
        return user


class QuestPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = _("Ел. пошта")
        self.fields["email"].widget.attrs.update(
            {"class": "qm-input", "autocomplete": "email", "inputmode": "email"}
        )


class QuestSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].label = _("Новий пароль")
        self.fields["new_password2"].label = _("Підтвердження пароля")
        self.fields["new_password1"].widget.attrs.update(
            {"class": "qm-input", "autocomplete": "new-password"}
        )
        self.fields["new_password2"].widget.attrs.update(
            {"class": "qm-input", "autocomplete": "new-password"}
        )
