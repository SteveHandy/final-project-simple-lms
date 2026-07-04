from ninja import Router
from ninja.errors import HttpError

from authentication.jwt import LMSJwtAuth

from users.models import UserProfile

from courses.models import (
    CourseContent,
    CourseMember,
    CourseReview,
    CourseWishlist,
)

from progress.models import Progress

from .schemas import (
    StudentDashboardOut,
    StudentDashboardCourseOut,
    StudentDashboardWishlistOut,
)

router = Router(tags=["Student Dashboard"])
auth = LMSJwtAuth()

def ensure_student(user):
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "role": UserProfile.Role.STUDENT
        }
    )

    if profile.role != UserProfile.Role.STUDENT:
        raise HttpError(
            403,
            "Dashboard ini hanya untuk user dengan role student."
        )

    return profile

def get_course_progress(member):
    course = member.course_id

    total_lessons = CourseContent.objects.filter(
        course_id=course
    ).count()

    completed_lessons = Progress.objects.filter(
        member=member,
        lesson__course_id=course,
        completed=True
    ).count()

    percentage = 0

    if total_lessons > 0:
        percentage = round(
            (completed_lessons / total_lessons) * 100,
            2
        )

    return {
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "progress_percentage": percentage,
    }

def serialize_dashboard_course(member):
    course = member.course_id
    progress = get_course_progress(member)

    return {
        "course_id": course.id,
        "course_name": course.name,
        "description": course.description,
        "price": course.price,
        "image": course.image.url if course.image else None,

        "category_id": course.category.id if course.category else None,
        "category_name": course.category.name if course.category else None,

        "level": course.level,
        "status": course.status,

        "teacher_id": course.teacher.id,
        "teacher_name": course.teacher.username,

        "total_lessons": progress["total_lessons"],
        "completed_lessons": progress["completed_lessons"],
        "progress_percentage": progress["progress_percentage"],
    }

@router.get(
    "/student",
    response=StudentDashboardOut,
    auth=auth
)
def student_dashboard(request):
    user = request.auth

    ensure_student(user)

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
        serialize_dashboard_course(member)
        for member in memberships
    ]

    total_enrolled_courses = memberships.count()

    total_lessons = sum(
        item["total_lessons"]
        for item in enrolled_courses
    )

    completed_lessons = sum(
        item["completed_lessons"]
        for item in enrolled_courses
    )

    not_completed_lessons = total_lessons - completed_lessons

    average_progress = 0

    if total_enrolled_courses > 0:
        average_progress = round(
            sum(
                item["progress_percentage"]
                for item in enrolled_courses
            ) / total_enrolled_courses,
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

    wishlist = [
        {
            "wishlist_id": item.id,
            "course_id": item.course.id,
            "course_name": item.course.name,
            "price": item.course.price,
            "image": item.course.image.url if item.course.image else None,
            "teacher_name": item.course.teacher.username,
            "created_at": item.created_at,
        }
        for item in wishlist_items
    ]

    recent_progress = (
        Progress.objects
        .select_related(
            "lesson",
            "lesson__course_id",
            "member",
        )
        .filter(
            member__user_id=user,
            completed=True
        )
        .order_by("-completed_at")[:5]
    )

    recent_completed_lessons = [
        {
            "lesson_id": item.lesson.id,
            "lesson_name": item.lesson.name,
            "course_id": item.lesson.course_id.id,
            "course_name": item.lesson.course_id.name,
            "completed_at": item.completed_at,
        }
        for item in recent_progress
    ]

    review_count = CourseReview.objects.filter(
        user=user
    ).count()

    wishlist_count = CourseWishlist.objects.filter(
        user=user
    ).count()

    return {
        "summary": {
            "total_enrolled_courses": total_enrolled_courses,
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "not_completed_lessons": not_completed_lessons,
            "average_progress": average_progress,
            "wishlist_count": wishlist_count,
            "review_count": review_count,
        },
        "enrolled_courses": enrolled_courses,
        "recent_completed_lessons": recent_completed_lessons,
        "wishlist": wishlist,
    }

@router.get(
    "/student/courses",
    response=list[StudentDashboardCourseOut],
    auth=auth
)
def student_courses(request):
    user = request.auth

    ensure_student(user)

    memberships = (
        CourseMember.objects
        .select_related(
            "course_id",
            "course_id__teacher",
            "course_id__category",
        )
        .filter(user_id=user)
    )

    return [
        serialize_dashboard_course(member)
        for member in memberships
    ]

@router.get(
    "/student/wishlist",
    response=list[StudentDashboardWishlistOut],
    auth=auth
)
def student_wishlist(request):
    user = request.auth

    ensure_student(user)

    wishlist_items = (
        CourseWishlist.objects
        .select_related(
            "course",
            "course__teacher",
        )
        .filter(user=user)
        .order_by("-created_at")
    )

    return [
        {
            "wishlist_id": item.id,
            "course_id": item.course.id,
            "course_name": item.course.name,
            "price": item.course.price,
            "image": item.course.image.url if item.course.image else None,
            "teacher_name": item.course.teacher.username,
            "created_at": item.created_at,
        }
        for item in wishlist_items
    ]