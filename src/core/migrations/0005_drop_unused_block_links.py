from django.db import migrations, models


def retype_url_blocks(apps, schema_editor):
    SiteBlock = apps.get_model("core", "SiteBlock")
    SiteBlock.objects.filter(content_type="url").update(content_type="text")


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_rating_page_file"),
    ]

    operations = [
        migrations.RunPython(retype_url_blocks, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="siteblock",
            name="link_label",
        ),
        migrations.RemoveField(
            model_name="siteblock",
            name="link_url",
        ),
        migrations.AlterField(
            model_name="siteblock",
            name="content_type",
            field=models.CharField(
                choices=[
                    ("text", "Текст"),
                    ("image", "Фото"),
                    ("file", "Файл"),
                ],
                default="text",
                max_length=16,
                verbose_name="Тип контенту",
            ),
        ),
    ]
