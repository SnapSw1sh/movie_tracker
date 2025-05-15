from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = False
    dependencies = [
        ('catalog', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewVote',
            fields=[
                ('id', models.BigAutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('value', models.SmallIntegerField(
                     choices=[(1, '👍'), (-1, '👎')])),
                ('review', models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='votes',
                     to='catalog.review')),
                ('user', models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='reviewvote',
            unique_together={('review', 'user')},
        ),
    ]
