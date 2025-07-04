# Generated by Django 5.2.1 on 2025-05-15 10:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0009_work_detail_work_openlibrary_id_work_poster_url_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="work",
            name="external_id",
            field=models.IntegerField(
                blank=True,
                help_text="TMDB ID, если импортировано из TMDB",
                null=True,
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name="work",
            name="genres_text",
            field=models.CharField(
                blank=True, help_text="Список жанров через запятую", max_length=255
            ),
        ),
        migrations.AddField(
            model_name="work",
            name="overview",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="work",
            name="poster_path",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
