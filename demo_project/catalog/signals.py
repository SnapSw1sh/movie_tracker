from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Review, Comment, ListEntry, Activity, Follow

@receiver(post_save, sender=Review)
def on_new_review(sender, instance, created, **kwargs):
    if created:
        Activity.objects.create(
            user=instance.user,
            description=f'Оставил рецензию к «{instance.work.title}»'
        )

@receiver(post_save, sender=Comment)
def on_new_comment(sender, instance, created, **kwargs):
    if created:
        Activity.objects.create(
            user=instance.user,
            description=f'Оставил комментарий к рецензии #{instance.review.id}'
        )

@receiver(post_save, sender=ListEntry)
def on_new_list_entry(sender, instance, created, **kwargs):
    if created:
        Activity.objects.create(
            user=instance.user,
            description=f'Добавил «{instance.work.title}» в свой список'
        )

@receiver(post_save, sender=Follow)
def on_new_follow(sender, instance, created, **kwargs):
    if created:
        Activity.objects.create(
            user=instance.follower,
            description=f'Подписался на пользователя {instance.followed.username}'
        )