from django.contrib.auth.models import User

from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth
from ninja_simple_jwt.jwt.token_operations import TokenTypes
from ninja_simple_jwt.jwt.token_operations import decode_token


class LMSJwtAuth(HttpJwtAuth):

    def authenticate(self, request, token):

        token = self.decode_authorization(
            request.headers["Authorization"]
        )

        payload = decode_token(
            token,
            token_type=TokenTypes.ACCESS,
            verify=True,
        )

        return User.objects.get(pk=payload["user_id"])