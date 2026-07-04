from ninja import Router

from authentication.jwt import LMSJwtAuth

from .schema import (
    UserProfileResponse,
    UpdateProfileSchema,
)

from .services import get_profile

router = Router()

@router.get(
    "/me",
    auth=LMSJwtAuth(),
    response=UserProfileResponse,
)
def me(request):

    user = request.auth
    profile = get_profile(user)

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": profile.role,
        "phone": profile.phone,
        "avatar": profile.avatar.url if profile.avatar else None,
        "bio": profile.bio,
    }

@router.put(
    "/me",
    auth=LMSJwtAuth(),
    response=UserProfileResponse,
)
def update_profile(request, payload: UpdateProfileSchema):

    user = request.auth
    profile = get_profile(user)

    if payload.phone is not None:
        profile.phone = payload.phone

    if payload.bio is not None:
        profile.bio = payload.bio

    profile.save()

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": profile.role,
        "phone": profile.phone,
        "avatar": profile.avatar.url if profile.avatar else None,
        "bio": profile.bio,
    }

