# Generated by Django 5.2.1 on 2025-05-15 18:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0012_remove_work_external_url_alter_work_external_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="work",
            name="google_id",
            field=models.CharField(
                blank=True,
                help_text="ID тома в Google Books",
                max_length=40,
                null=True,
                unique=True,
            ),
        ),
    ]
