from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils import timezone

from users.models import UserProfile

from courses.models import (
    Course,
    CourseMember,
    CourseContent,
    CourseWishlist,
    CourseReview,
)

from progress.models import Progress


def ensure_student(user):
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "role": UserProfile.Role.STUDENT
        }
    )

    if profile.role != UserProfile.Role.STUDENT:
        return None

    return profile


def calculate_course_progress(member):
    course = member.course_id

    total_lessons = CourseContent.objects.filter(
        course_id=course
    ).count()

    completed_lessons = Progress.objects.filter(
        member=member,
        lesson__course_id=course,
        completed=True
    ).count()

    not_completed_lessons = total_lessons - completed_lessons

    percentage = 0

    if total_lessons > 0:
        percentage = round(
            (completed_lessons / total_lessons) * 100,
            2
        )

    return {
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "not_completed_lessons": not_completed_lessons,
        "percentage": percentage,
    }


def serialize_student_course(member):
    course = member.course_id
    progress = calculate_course_progress(member)

    return {
        "id": course.id,
        "name": course.name,
        "description": course.description,
        "price": course.price,
        "image": course.image.url if course.image else None,
        "category": course.category.name if course.category else "-",
        "level": course.level,
        "status": course.status,
        "teacher": course.teacher.username,
        "total_lessons": progress["total_lessons"],
        "completed_lessons": progress["completed_lessons"],
        "not_completed_lessons": progress["not_completed_lessons"],
        "percentage": progress["percentage"],
    }


@login_required
def student_dashboard_page(request):
    user = request.user

    profile = ensure_student(user)

    if profile is None:
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

    enrolled_courses = [
        serialize_student_course(member)
        for member in memberships
    ]

    total_courses = memberships.count()

    total_lessons = sum(
        course["total_lessons"]
        for course in enrolled_courses
    )

    completed_lessons = sum(
        course["completed_lessons"]
        for course in enrolled_courses
    )

    not_completed_lessons = total_lessons - completed_lessons

    average_progress = 0

    if total_courses > 0:
        average_progress = round(
            sum(course["percentage"] for course in enrolled_courses) / total_courses,
            2
        )

    wishlist_items = (
        CourseWishlist.objects
        .select_related(
            "course",
            "course__teacher",
            "course__category",
        )
        .filter(user=user)
        .order_by("-created_at")
    )

    recent_completed_lessons = (
        Progress.objects
        .select_related(
            "lesson",
            "lesson__course_id",
            "lesson__course_id__teacher",
            "member",
        )
        .filter(
            member__user_id=user,
            completed=True,
        )
        .order_by("-completed_at")[:5]
    )

    my_reviews = (
        CourseReview.objects
        .select_related(
            "course",
            "course__teacher",
        )
        .filter(user=user)
        .order_by("-created_at")[:5]
    )

    enrolled_course_ids = memberships.values_list(
        "course_id_id",
        flat=True
    )

    wishlist_course_ids = wishlist_items.values_list(
        "course_id",
        flat=True
    )

    available_courses = (
        Course.objects
        .select_related("teacher", "category")
        .exclude(id__in=enrolled_course_ids)
        .order_by("-created_at")[:6]
    )

    context = {
        "total_courses": total_courses,
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "not_completed_lessons": not_completed_lessons,
        "average_progress": average_progress,

        "wishlist_count": wishlist_items.count(),
        "review_count": CourseReview.objects.filter(user=user).count(),

        "enrolled_courses": enrolled_courses,
        "wishlist_items": wishlist_items,
        "recent_completed_lessons": recent_completed_lessons,
        "my_reviews": my_reviews,
        "available_courses": available_courses,
        "wishlist_course_ids": list(wishlist_course_ids),
    }

    return render(
        request,
        "dashboard/student_dashboard.html",
        context
    )


@login_required
def student_course_detail_page(request, course_id):
    user = request.user

    profile = ensure_student(user)

    if profile is None:
        return HttpResponseForbidden(
            "Halaman ini hanya untuk student."
        )

    course = get_object_or_404(
        Course.objects.select_related("teacher", "category"),
        id=course_id
    )

    member = get_object_or_404(
        CourseMember,
        course_id=course,
        user_id=user
    )

    lessons = (
        CourseContent.objects
        .select_related("course_id", "parent_id")
        .filter(course_id=course)
        .order_by("parent_id__id", "order", "id")
    )

    progress_items = Progress.objects.filter(
        member=member,
        lesson__course_id=course
    )

    progress_map = {
        item.lesson_id: item
        for item in progress_items
    }

    lesson_results = []

    for lesson in lessons:
        progress = progress_map.get(lesson.id)

        lesson_results.append({
            "id": lesson.id,
            "name": lesson.name,
            "description": lesson.description,
            "video_url": lesson.video_url,
            "file_attachment": lesson.file_attachment.url if lesson.file_attachment else None,
            "parent": lesson.parent_id.name if lesson.parent_id else None,
            "order": lesson.order,
            "completed": progress.completed if progress else False,
            "completed_at": progress.completed_at if progress else None,
        })

    total_lessons = lessons.count()

    completed_lessons = sum(
        1 for lesson in lesson_results
        if lesson["completed"]
    )

    not_completed_lessons = total_lessons - completed_lessons

    percentage = 0

    if total_lessons > 0:
        percentage = round(
            (completed_lessons / total_lessons) * 100,
            2
        )

    context = {
        "course": course,
        "lessons": lesson_results,
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "not_completed_lessons": not_completed_lessons,
        "percentage": percentage,
    }

    return render(
        request,
        "dashboard/student_course_detail.html",
        context
    )


@login_required
@require_POST
def complete_lesson_from_dashboard(request, lesson_id):
    user = request.user

    lesson = get_object_or_404(
        CourseContent.objects.select_related("course_id"),
        id=lesson_id
    )

    member = get_object_or_404(
        CourseMember,
        user_id=user,
        course_id=lesson.course_id
    )

    progress, created = Progress.objects.get_or_create(
        member=member,
        lesson=lesson
    )

    progress.completed = True
    progress.completed_at = timezone.now()
    progress.save()

    return redirect(
        "student_course_detail",
        course_id=lesson.course_id.id
    )


@login_required
@require_POST
def reset_lesson_progress_from_dashboard(request, lesson_id):
    user = request.user

    lesson = get_object_or_404(
        CourseContent.objects.select_related("course_id"),
        id=lesson_id
    )

    member = get_object_or_404(
        CourseMember,
        user_id=user,
        course_id=lesson.course_id
    )

    Progress.objects.filter(
        member=member,
        lesson=lesson
    ).delete()

    return redirect(
        "student_course_detail",
        course_id=lesson.course_id.id
    )


@login_required
@require_POST
def remove_wishlist_from_dashboard(request, wishlist_id):
    wishlist = get_object_or_404(
        CourseWishlist,
        id=wishlist_id,
        user=request.user
    )

    wishlist.delete()

    return redirect("student_dashboard")


@login_required
@require_POST
def add_wishlist_from_dashboard(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    CourseWishlist.objects.get_or_create(
        course=course,
        user=request.user
    )

    return redirect("student_dashboard")