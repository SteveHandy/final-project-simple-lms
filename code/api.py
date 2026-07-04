from ninja import NinjaAPI
from ninja_simple_jwt.auth.views.api import mobile_auth_router
from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth

api = NinjaAPI(
    title="Simple LMS API",
    version="1.0.0",
)

# Endpoint JWT
api.add_router("/auth/", mobile_auth_router)

# Digunakan untuk endpoint yang membutuhkan login
apiAuth = HttpJwtAuth()

@api.get("/profile", auth=apiAuth)
def profile(request):
    return {
        "username": request.user.username
    }