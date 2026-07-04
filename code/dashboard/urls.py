from django.urls import path

from .views import student_dashboard_page


urlpatterns = [
    path(
        "student/",
        student_dashboard_page,
        name="student_dashboard"
    ),
]