from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils import timezone

from src.accounts.models import UserProfile

User = get_user_model()


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autocomplete": "email", "class": "qm-input"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password"].widget.attrs.update({"class": "qm-input"})


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="Ел. пошта",
        widget=forms.EmailInput(attrs={"class": "qm-input", "autocomplete": "email"}),
    )
    full_name = forms.CharField(
        label="Ім'я",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "qm-input", "autocomplete": "name"}),
    )
    phone = forms.CharField(
        label="Телефон",
        max_length=32,
        widget=forms.TextInput(attrs={"class": "qm-input", "autocomplete": "tel"}),
    )
    consent_terms = forms.BooleanField(
        label="Згода з користувацькою угодою",
        widget=forms.CheckboxInput(attrs={"class": "qm-checkbox"}),
    )
    consent_age18 = forms.BooleanField(
        label="Мені виповнилось 18 років",
        widget=forms.CheckboxInput(attrs={"class": "qm-checkbox"}),
    )

    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({"class": "qm-input"})
        self.fields["password2"].widget.attrs.update({"class": "qm-input"})
        self.fields["password2"].label = "Підтвердження пароля"

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Користувач з таким email уже існує.")
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
