from ninja import NinjaAPI

from users.api import router as user_router
from courses.api import router as course_router
from enrollments.api import router as enrollment_router
from progress.api import router as progress_router
from dashboard.api import router as dashboard_router
from ninja_simple_jwt.auth.views.api import mobile_auth_router

api = NinjaAPI(
    title="Simple LMS API",
    version="1.0.0",
)

api.add_router("/auth/", mobile_auth_router)
api.add_router("/users/", user_router)
api.add_router("/courses/", course_router)
api.add_router("/enrollments/", enrollment_router)
api.add_router("/progress/", progress_router)
api.add_router("/dashboard/", dashboard_router)