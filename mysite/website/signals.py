from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from .models import UserMenu

user = get_user_model()


@receiver(post_save, sender=user)
def create_user_menu(sender, instance, created, **kwargs):
    if created:
        UserMenu.objects.create(user=instance)
