from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0003_uk_field_verbose_names"),
    ]

    operations = [
        migrations.DeleteModel(
            name="InfoPage",
        ),
    ]
