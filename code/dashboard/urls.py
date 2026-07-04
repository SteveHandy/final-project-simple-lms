from django.urls import path

from .views import (
    student_dashboard_page,
    student_course_detail_page,
    complete_lesson_from_dashboard,
    reset_lesson_progress_from_dashboard,
    remove_wishlist_from_dashboard,
    add_wishlist_from_dashboard,
)

urlpatterns = [
    path(
        "student/",
        student_dashboard_page,
        name="student_dashboard"
    ),

    path(
        "student/courses/<int:course_id>/",
        student_course_detail_page,
        name="student_course_detail"
    ),

    path(
        "student/lessons/<int:lesson_id>/complete/",
        complete_lesson_from_dashboard,
        name="dashboard_complete_lesson"
    ),

    path(
        "student/lessons/<int:lesson_id>/reset/",
        reset_lesson_progress_from_dashboard,
        name="dashboard_reset_lesson"
    ),

    path(
        "student/wishlist/<int:wishlist_id>/delete/",
        remove_wishlist_from_dashboard,
        name="dashboard_remove_wishlist"
    ),

    path(
        "student/courses/<int:course_id>/wishlist/",
        add_wishlist_from_dashboard,
        name="dashboard_add_wishlist"
    ),
]