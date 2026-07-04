from ninja import Router
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Progress
from authentication.jwt import LMSJwtAuth

from courses.models import Course, CourseContent, CourseMember
from .models import Progress
from .schemas import CourseProgressDetailOut, CourseProgressSummaryOut

router = Router(tags=["Progress"])
auth = LMSJwtAuth()

def get_course_member(user, course):
    member = CourseMember.objects.filter(
        course_id=course,
        user_id=user
    ).first()

    if not member:
        raise HttpError(
            403,
            "Anda belum terdaftar pada course ini."
        )

    return member


def serialize_lesson_progress(lesson, progress_map):
    progress = progress_map.get(lesson.id)

    return {
        "lesson_id": lesson.id,
        "lesson_name": lesson.name,
        "description": lesson.description,
        "video_url": lesson.video_url,
        "file_attachment": lesson.file_attachment.url if lesson.file_attachment else None,
        "parent_id": lesson.parent_id.id if lesson.parent_id else None,
        "parent_name": lesson.parent_id.name if lesson.parent_id else None,
        "order": lesson.order,
        "completed": progress.completed if progress else False,
        "completed_at": progress.completed_at if progress else None,
    }

@router.get(
    "/course/{course_id}/summary",
    response=CourseProgressSummaryOut,
    auth=auth
)
def course_progress_summary(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)
    member = get_course_member(request.auth, course)

    lessons = CourseContent.objects.filter(
        course_id=course
    )

    total_lessons = lessons.count()

    completed_lessons = Progress.objects.filter(
        member=member,
        lesson__course_id=course,
        completed=True
    ).count()

    not_completed_lessons = total_lessons - completed_lessons

    percentage = 0
    if total_lessons > 0:
        percentage = round((completed_lessons / total_lessons) * 100, 2)

    return {
        "course_id": course.id,
        "course_name": course.name,
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "not_completed_lessons": not_completed_lessons,
        "percentage": percentage,
    }

@router.get(
    "/course/{course_id}/detail",
    response=CourseProgressDetailOut,
    auth=auth
)
def course_progress_detail(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)
    member = get_course_member(request.auth, course)

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

    lesson_results = [
        serialize_lesson_progress(lesson, progress_map)
        for lesson in lessons
    ]

    total_lessons = lessons.count()
    completed_lessons = sum(
        1 for item in lesson_results
        if item["completed"]
    )

    not_completed_lessons = total_lessons - completed_lessons

    percentage = 0
    if total_lessons > 0:
        percentage = round((completed_lessons / total_lessons) * 100, 2)

    return {
        "course_id": course.id,
        "course_name": course.name,
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "not_completed_lessons": not_completed_lessons,
        "percentage": percentage,
        "lessons": lesson_results,
    }

@router.post(
    "/lesson/{lesson_id}/complete",
    auth=auth
)
def complete_lesson(request, lesson_id: int):
    lesson = get_object_or_404(
        CourseContent.objects.select_related("course_id"),
        id=lesson_id
    )

    member = get_course_member(
        request.auth,
        lesson.course_id
    )

    progress, created = Progress.objects.get_or_create(
        member=member,
        lesson=lesson
    )

    progress.completed = True
    progress.completed_at = timezone.now()
    progress.save()

    return {
        "message": "Lesson berhasil ditandai selesai.",
        "lesson_id": lesson.id,
        "lesson_name": lesson.name,
        "completed": True,
        "completed_at": progress.completed_at,
    }

@router.delete(
    "/lesson/{lesson_id}",
    auth=auth
)
def reset_lesson_progress(request, lesson_id: int):
    lesson = get_object_or_404(
        CourseContent.objects.select_related("course_id"),
        id=lesson_id
    )

    member = get_course_member(
        request.auth,
        lesson.course_id
    )

    progress = get_object_or_404(
        Progress,
        member=member,
        lesson=lesson
    )

    progress.delete()

    return {
        "message": "Progress lesson berhasil di-reset.",
        "lesson_id": lesson.id,
        "lesson_name": lesson.name,
    }