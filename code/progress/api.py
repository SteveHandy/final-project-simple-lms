from ninja import Router
from django.shortcuts import get_object_or_404
from django.utils import timezone

from courses.models import CourseMember
from courses.models import CourseContent

from .models import Progress
from .schemas import ProgressOut
from users.api import LMSJwtAuth

router = Router(tags=["Progress"])

@router.get(
    "/",
    response=list[ProgressOut],
    auth=LMSJwtAuth()
)
def my_progress(request):

    member = get_object_or_404(
        CourseMember,
        user_id=request.auth
    )

    progress = (
        Progress.objects
        .select_related("lesson")
        .filter(member=member)
    )

    return [
        {
            "lesson_id": p.lesson.id,
            "lesson": p.lesson.name,
            "completed": p.completed,
            "completed_at": p.completed_at,
        }
        for p in progress
    ]

@router.get(
    "/course/{course_id}",
    auth=LMSJwtAuth()
)
def progress_course(request, course_id: int):

    member = get_object_or_404(
        CourseMember,
        course_id=course_id,
        user_id=request.auth
    )

    lessons = CourseContent.objects.filter(
        course_id=course_id
    )

    total = lessons.count()

    completed = Progress.objects.filter(
        member=member,
        lesson__course_id=course_id,
        completed=True
    ).count()

    percentage = 0

    if total > 0:
        percentage = round((completed / total) * 100, 2)

    return {
        "course_id": course_id,
        "total_lessons": total,
        "completed_lessons": completed,
        "percentage": percentage
    }

@router.post(
    "/lesson/{lesson_id}/complete",
    auth=LMSJwtAuth()
)
def complete_lesson(request, lesson_id: int):

    lesson = get_object_or_404(
        CourseContent,
        id=lesson_id
    )

    member = get_object_or_404(
        CourseMember,
        user_id=request.auth,
        course_id=lesson.course_id
    )

    progress, created = Progress.objects.get_or_create(
        member=member,
        lesson=lesson
    )

    progress.completed = True
    progress.completed_at = timezone.now()

    progress.save()

    return {
        "message": "Lesson completed"
    }

@router.delete(
    "/lesson/{lesson_id}",
    auth=LMSJwtAuth()
)
def reset_progress(request, lesson_id: int):

    lesson = get_object_or_404(
        CourseContent,
        id=lesson_id
    )

    member = get_object_or_404(
        CourseMember,
        user_id=request.auth,
        course_id=lesson.course_id
    )

    progress = get_object_or_404(
        Progress,
        member=member,
        lesson=lesson
    )

    progress.delete()

    return {
        "message": "Progress reset"
    }