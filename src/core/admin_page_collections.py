"""ModelFormSets for About cards / FAQ items inside CMS page sections."""

from __future__ import annotations

from django import forms
from django.forms import BaseModelFormSet, modelformset_factory

from src.core.admin_site_content_widgets import (
    CmsAdminTextareaWidget,
    CmsAdminTextInputWidget,
)
from src.pages.models import AboutCard, FAQItem


class AboutCardForm(forms.ModelForm):
    class Meta:
        model = AboutCard
        fields = (
            "sort_order",
            "is_active",
            "title_uk",
            "text_uk",
            "title_ru",
            "text_ru",
        )
        widgets = {
            "sort_order": forms.HiddenInput(),
            "title_uk": CmsAdminTextInputWidget(),
            "title_ru": CmsAdminTextInputWidget(),
            "text_uk": CmsAdminTextareaWidget(attrs={"rows": 4}),
            "text_ru": CmsAdminTextareaWidget(attrs={"rows": 4}),
        }
        labels = {
            "sort_order": "Порядок",
            "is_active": "Активна",
            "title_uk": "Заголовок",
            "text_uk": "Текст",
            "title_ru": "Заголовок",
            "text_ru": "Текст",
        }

    def clean(self):
        cleaned = super().clean()
        if not self.instance.pk and not (cleaned.get("title_uk") or "").strip():
            cleaned["DELETE"] = True
        return cleaned


class FAQItemForm(forms.ModelForm):
    class Meta:
        model = FAQItem
        fields = (
            "sort_order",
            "is_active",
            "question_uk",
            "answer_uk",
            "question_ru",
            "answer_ru",
        )
        widgets = {
            "sort_order": forms.HiddenInput(),
            "question_uk": CmsAdminTextInputWidget(),
            "question_ru": CmsAdminTextInputWidget(),
            "answer_uk": CmsAdminTextareaWidget(attrs={"rows": 3}),
            "answer_ru": CmsAdminTextareaWidget(attrs={"rows": 3}),
        }
        labels = {
            "sort_order": "Порядок",
            "is_active": "Активний",
            "question_uk": "Питання",
            "answer_uk": "Відповідь",
            "question_ru": "Питання",
            "answer_ru": "Відповідь",
        }

    def clean(self):
        cleaned = super().clean()
        if not self.instance.pk and not (cleaned.get("question_uk") or "").strip():
            cleaned["DELETE"] = True
        return cleaned


class OrderedBaseFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()
        order = 0
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            if not form.cleaned_data:
                continue
            form.cleaned_data["sort_order"] = order
            form.instance.sort_order = order
            order += 1


AboutCardFormSet = modelformset_factory(
    AboutCard,
    form=AboutCardForm,
    formset=OrderedBaseFormSet,
    extra=0,
    can_delete=True,
)

FAQItemFormSet = modelformset_factory(
    FAQItem,
    form=FAQItemForm,
    formset=OrderedBaseFormSet,
    extra=0,
    can_delete=True,
)


def build_about_card_formset(data=None, files=None):
    qs = AboutCard.objects.all().order_by("sort_order", "pk")
    return AboutCardFormSet(data=data, files=files, queryset=qs, prefix="about_cards")


def build_faq_item_formset(data=None, files=None):
    qs = FAQItem.objects.all().order_by("sort_order", "pk")
    return FAQItemFormSet(data=data, files=files, queryset=qs, prefix="faq_items")
