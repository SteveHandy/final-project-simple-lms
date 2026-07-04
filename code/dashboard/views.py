from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render

from users.models import UserProfile

from courses.models import (
    CourseMember,
    CourseContent,
    CourseWishlist,
    CourseReview,
)

from progress.models import Progress


@login_required(login_url="/accounts/login/")
def student_dashboard_page(request):
    user = request.user

    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "role": UserProfile.Role.STUDENT
        }
    )

    if profile.role != UserProfile.Role.STUDENT:
        return HttpResponseForbidden(
            "Halaman ini hanya untuk student."
        )

    memberships = (
        CourseMember.objects
        .select_related(
            "course_id",
            "course_id__teacher",
            "course_id__category",
            "user_id",
        )
        .filter(user_id=user)
    )

    enrolled_courses = []

    total_lessons = 0
    completed_lessons = 0

    for member in memberships:
        course = member.course_id

        course_lessons = CourseContent.objects.filter(
            course_id=course
        )

        lesson_count = course_lessons.count()

        completed_count = Progress.objects.filter(
            member=member,
            lesson__course_id=course,
            completed=True
        ).count()

        percentage = 0

        if lesson_count > 0:
            percentage = round(
                (completed_count / lesson_count) * 100,
                2
            )

        total_lessons += lesson_count
        completed_lessons += completed_count

        enrolled_courses.append({
            "course_id": course.id,
            "course_name": course.name,
            "description": course.description,
            "price": course.price,
            "image": course.image.url if course.image else None,
            "category_name": course.category.name if course.category else "-",
            "level": course.level,
            "status": course.status,
            "teacher_name": course.teacher.username,
            "total_lessons": lesson_count,
            "completed_lessons": completed_count,
            "progress_percentage": percentage,
        })

    total_courses = memberships.count()
    not_completed_lessons = total_lessons - completed_lessons

    average_progress = 0

    if total_courses > 0:
        average_progress = round(
            sum(course["progress_percentage"] for course in enrolled_courses) / total_courses,
            2
        )

    wishlist_items = (
        CourseWishlist.objects
        .select_related(
            "course",
            "course__teacher",
        )
        .filter(user=user)
        .order_by("-created_at")[:5]
    )

    recent_completed_lessons = (
        Progress.objects
        .select_related(
            "lesson",
            "lesson__course_id",
            "member",
        )
        .filter(
            member__user_id=user,
            completed=True,
        )
        .order_by("-completed_at")[:5]
    )

    review_count = CourseReview.objects.filter(
        user=user
    ).count()

    context = {
        "total_courses": total_courses,
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "not_completed_lessons": not_completed_lessons,
        "average_progress": average_progress,
        "wishlist_count": CourseWishlist.objects.filter(user=user).count(),
        "review_count": review_count,
        "enrolled_courses": enrolled_courses,
        "wishlist_items": wishlist_items,
        "recent_completed_lessons": recent_completed_lessons,
    }

    return render(
        request,
        "dashboard/student_dashboard.html",
        context
    )