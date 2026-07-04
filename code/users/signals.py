from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:

        role = UserProfile.Role.STUDENT

        if instance.is_superuser:
            role = UserProfile.Role.ADMIN

        UserProfile.objects.create(
            user=instance,
            role=role
        )


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()