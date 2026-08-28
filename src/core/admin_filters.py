"""Ukrainian dropdown filters for Unfold changelist (top bar)."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.utils.translation import gettext_lazy as _
from unfold.contrib.filters.admin import ChoicesDropdownFilter, DropdownFilter
from unfold.contrib.filters.admin.mixins import DropdownMixin, ValueMixin


class UkChoicesDropdownFilter(ChoicesDropdownFilter):
    """Choices dropdown: label = field title, default option «Всі»."""

    title_ua: str | None = None

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        if self.title_ua:
            self.title = self.title_ua

    def choices(self, changelist: ChangeList) -> Generator[dict[str, Any], None, None]:
        choices = [("", "Всі"), *self.field.flatchoices]
        current = self.value()
        yield {
            "form": self.form_class(
                label=str(self.title),
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: "" if current is None else current},
                multiple=False,
            ),
        }


class UkBooleanDropdownFilter(ValueMixin, DropdownMixin, admin.BooleanFieldListFilter):
    """Boolean as select: Всі / Так / Ні."""

    title_ua: str | None = None

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        if self.title_ua:
            self.title = self.title_ua

    def choices(self, changelist: ChangeList) -> Generator[dict[str, Any], None, None]:
        choices = [
            ("", "Всі"),
            ("1", "Так"),
            ("0", "Ні"),
        ]
        current = self.value()
        yield {
            "form": self.form_class(
                label=str(self.title),
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: "" if current is None else current},
                multiple=False,
            ),
        }


class MediaTypeFilter(UkChoicesDropdownFilter):
    title_ua = "Тип медіа"


class ActivityFilter(UkBooleanDropdownFilter):
    title_ua = "Активність"


class PublishedFilter(UkBooleanDropdownFilter):
    title_ua = "Публікація"


class PaymentStatusFilter(UkChoicesDropdownFilter):
    title_ua = "Статус"


class PaymentStatusProfileFilter(UkChoicesDropdownFilter):
    title_ua = "Статус оплати"


class LocaleFilter(DropdownFilter):
    title = _("Мова")
    parameter_name = "locale"

    def lookups(self, request, model_admin):
        return (
            ("uk", "UA"),
            ("ru", "RU"),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(locale=self.value())
        return queryset

    def choices(self, changelist: ChangeList) -> tuple[dict[str, Any], ...]:
        return (
            {
                "form": self.form_class(
                    label="Мова",
                    name=self.parameter_name,
                    choices=[("", "Всі"), *self.lookup_choices],
                    data={self.parameter_name: self.value() or ""},
                    multiple=False,
                ),
            },
        )


class ProviderFilter(DropdownFilter):
    title = _("Провайдер")
    parameter_name = "provider"

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        values = (
            qs.order_by("provider")
            .values_list("provider", flat=True)
            .distinct()
        )
        return [(v, v) for v in values if v]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(provider=self.value())
        return queryset

    def choices(self, changelist: ChangeList) -> tuple[dict[str, Any], ...]:
        return (
            {
                "form": self.form_class(
                    label="Провайдер",
                    name=self.parameter_name,
                    choices=[("", "Всі"), *self.lookup_choices],
                    data={self.parameter_name: self.value() or ""},
                    multiple=False,
                ),
            },
        )
