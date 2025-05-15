from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='profile')
    avatar = models.ImageField(upload_to='avatars/',
                               default='avatars/default.png',
                               verbose_name='Аватар')
    description = models.TextField(blank=True,
                                   verbose_name='Описание')
    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True,
        through='Follow'
    )
    def __str__(self):
        return f'Профиль {self.user.username}'

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class Follow(models.Model):
    """Промежуточная таблица для M2M-profile→profile"""
    follower = models.ForeignKey(Profile,
                                 on_delete=models.CASCADE,
                                 related_name='outgoing_follows')
    followed = models.ForeignKey(Profile,
                                 on_delete=models.CASCADE,
                                 related_name='incoming_follows')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')