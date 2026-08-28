from django.db import models


class QuestRoom(models.Model):
    class MediaType(models.TextChoices):
        NONE = "", "Без медіа"
        PDF = "pdf", "PDF"
        PNG = "png", "Зображення"
        MP3 = "mp3", "Аудіо"
        MP4 = "mp4", "Відео"

    order = models.PositiveSmallIntegerField("Номер кімнати", unique=True)
    title_uk = models.CharField("Назва (українською)", max_length=255)
    title_ru = models.CharField("Назва (російською)", max_length=255, blank=True)
    body_uk = models.TextField("Текст завдання (українською)", blank=True)
    body_ru = models.TextField("Текст завдання (російською)", blank=True)
    media_file = models.FileField("Файл медіа", upload_to="quest/", blank=True)
    media_type = models.CharField(
        "Тип медіа",
        max_length=8,
        choices=MediaType.choices,
        default=MediaType.NONE,
        blank=True,
    )
    keyword_normalized = models.CharField(
        "Ключове слово",
        max_length=128,
        help_text="Одне слово для української та російської. Зберігається нормалізованим.",
    )
    is_active = models.BooleanField("Активна", default=True)
    updated_at = models.DateTimeField("Оновлено", auto_now=True)
    created_at = models.DateTimeField("Створено", auto_now_add=True)

    class Meta:
        verbose_name = "Кімната квесту"
        verbose_name_plural = "Кімнати квесту"
        ordering = ["order"]

    def __str__(self) -> str:
        return f"Кімната {self.order}: {self.title_uk}"

    def save(self, *args, **kwargs):
        self.keyword_normalized = normalize_keyword(self.keyword_normalized)
        if self.media_file and not self.media_type:
            name = self.media_file.name.lower()
            if name.endswith(".pdf"):
                self.media_type = self.MediaType.PDF
            elif name.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
                self.media_type = self.MediaType.PNG
            elif name.endswith((".mp3", ".wav", ".ogg")):
                self.media_type = self.MediaType.MP3
            elif name.endswith((".mp4", ".webm")):
                self.media_type = self.MediaType.MP4
        super().save(*args, **kwargs)

    def title_for(self, locale: str) -> str:
        if locale == "ru" and self.title_ru:
            return self.title_ru
        return self.title_uk

    def body_for(self, locale: str) -> str:
        if locale == "ru" and self.body_ru:
            return self.body_ru
        return self.body_uk


def normalize_keyword(value: str) -> str:
    return (value or "").strip().casefold()
