from .models import UserProfile


def get_profile(user):

    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "role": UserProfile.Role.STUDENT
        }
    )

    return profile