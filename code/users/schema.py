from ninja import Schema


class UserProfileResponse(Schema):
    id: int
    username: str
    email: str

    role: str
    phone: str | None = None
    avatar: str | None = None
    bio: str | None = None

class UpdateProfileSchema(Schema):
    phone: str | None = None
    bio: str | None = None