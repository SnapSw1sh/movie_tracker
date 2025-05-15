from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class WorkQuerySet(models.QuerySet):
    def of_type(self, t):
        return self.filter(type=t) if t else self
    def of_genre(self, g):
        return self.filter(genre__icontains=g) if g else self

class Work(models.Model):
    MOVIE = 'movie'
    SERIES = 'series'
    BOOK = 'book'
    TYPE_CHOICES = [
        (MOVIE, 'Фильм'),
        (SERIES, 'Сериал'),
        (BOOK, 'Книга'),
    ]
    title        = models.CharField(max_length=200, verbose_name='Название')
    type         = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='Тип')
    genre        = models.CharField(max_length=100, blank=True, verbose_name='Жанр')
    rating       = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name='Рейтинг')
    release_date = models.DateField(null=True, blank=True, verbose_name='Дата релиза')
    objects      = WorkQuerySet.as_manager()
    detail       = models.TextField(blank=True)
    poster_url   = models.URLField(blank=True)

    tmdb_id       = models.PositiveIntegerField(null=True, blank=True, unique=True)
    openlibrary_id= models.CharField(max_length=50, null=True, blank=True, unique=True)

    external_id = models.IntegerField(
        null=True, blank=True, unique=True,
        help_text="TMDB ID, если импортировано из TMDB"
    )
    overview     = models.TextField(blank=True)
    poster_path  = models.CharField(max_length=255, blank=True)
    genres_text  = models.CharField(max_length=255, blank=True,
                                    help_text="Список жанров через запятую")

    external_id = models.CharField(
        max_length=20, unique=True, null=True, blank=True,
        help_text="TMDB external id вида 'movie:123' / 'tv:456'"
    ) 

    google_id   = models.CharField(
        max_length=40, blank=True, null=True, unique=True,
        help_text='ID тома в Google Books'
    )
    
    def get_poster_url(self):
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w300{self.poster_path}"
        return ""

    def __str__(self):
        return self.title

class Comment(models.Model):
    review     = models.ForeignKey(
        'Review',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    parent     = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    text       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f'Comment #{self.pk} by {self.user}'

class Review(models.Model):
    work       = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='reviews', verbose_name='Произведение')
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Автор')
    text       = models.TextField(verbose_name='Текст рецензии')
    rating     = models.PositiveSmallIntegerField(default=0, verbose_name='Оценка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    def __str__(self):
        return f'{self.user.username} — {self.work.title}'
    
class ReviewVote(models.Model):
    review = models.ForeignKey(
        'Review',
        on_delete=models.CASCADE,
        related_name='votes'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    value = models.SmallIntegerField(
        choices=((1, '👍'), (-1, '👎'))
    )

    class Meta:
        unique_together = ('review', 'user')

class ListEntry(models.Model):
    STATUS_WANT       = 'want'
    STATUS_READING    = 'reading'
    STATUS_COMPLETED  = 'completed'
    STATUS_REWATCHING = 'rewatching'
    STATUS_PAUSED     = 'paused'
    STATUS_DROPPED    = 'dropped'
    STATUS_CHOICES = [
        (STATUS_WANT,       'Хочу посмотреть/Хочу прочитать'),
        (STATUS_READING,    'Смотрю/Читаю'),
        (STATUS_COMPLETED,  'Просмотрено/Прочитано'),
        (STATUS_REWATCHING, 'Пересматриваю/Перечитываю'),
        (STATUS_PAUSED,     'Приостановлено/На паузе'),
        (STATUS_DROPPED,    'Брошено/Брошено'),
    ]

    work       = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='list_entries', verbose_name='Произведение')
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='list_entries', verbose_name='Пользователь')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_WANT, verbose_name='Статус')
    score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    progress   = models.PositiveIntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    finish_date= models.DateField(null=True, blank=True)
    rewatch_count = models.PositiveIntegerField(default=0)
    notes      = models.TextField(blank=True)
    favorite   = models.BooleanField(default=False)
    added_at   = models.DateTimeField(auto_now_add=True)
    position   = models.PositiveIntegerField(default=0)

    STATUS_LABELS = {
        'movie': {
            'want':       'Хочу посмотреть',
            'reading':    'Смотрю',
            'completed':  'Просмотрено',
            'rewatching': 'Пересматриваю',
            'paused':     'Приостановлено',
            'dropped':    'Брошено',
        },
        'series': {
            'want':       'Хочу посмотреть',
            'reading':    'Смотрю',
            'completed':  'Просмотрено',
            'rewatching': 'Пересматриваю',
            'paused':     'Приостановлено',
            'dropped':    'Брошено',
        },
        'book': {
            'want':       'Хочу прочитать',
            'reading':    'Читаю',
            'completed':  'Прочитано',
            'rewatching': 'Перечитываю',
            'paused':     'Приостановлено',
            'dropped':    'Брошено',
        },
    }

    class Meta:
        unique_together = ('work', 'user')
        verbose_name = 'Запись списка'
        verbose_name_plural = 'Записи списка'

    def __str__(self):
        return f'{self.user.username}: {self.work.title} ({self.get_status_display()})'

User = get_user_model()

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')

class Activity(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    timestamp   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        get_latest_by = 'timestamp'