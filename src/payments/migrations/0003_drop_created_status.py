from django.db import migrations, models


def pending_instead_of_created(apps, schema_editor):
    Payment = apps.get_model("payments", "Payment")
    Payment.objects.filter(status="created").update(status="pending")


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0002_uk_field_verbose_names"),
    ]

    operations = [
        migrations.RunPython(pending_instead_of_created, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="payment",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Очікує"),
                    ("success", "Успішно"),
                    ("failure", "Помилка"),
                    ("sandbox", "Sandbox / bypass"),
                ],
                db_index=True,
                default="pending",
                max_length=16,
                verbose_name="Статус",
            ),
        ),
    ]
