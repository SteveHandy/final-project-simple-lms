from ninja import Router
from django.db.models import Q, Avg, Count
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

from progress.models import Progress
from .models import Category, Course, CourseReview, CourseWishlist, CourseMember, CourseContent
from .schemas import (
    CourseOut,
    CourseCreate,
    CourseUpdate,
    CourseReviewCreate,
    CourseReviewUpdate,
    CourseReviewOut,
    CourseRatingSummaryOut,
    CourseWishlistOut,
    LessonCreate,
    LessonOut,
    LessonUpdate,
    CurriculumItemOut
)
from .schemas import EnrollmentCreate
from .schemas import EnrollmentOut

from authentication.jwt import LMSJwtAuth

router = Router(tags=["Courses"])
auth = LMSJwtAuth()


def serialize_review(item):
    return {
        "id": item.id,
        "course_id": item.course.id,
        "course_name": item.course.name,
        "user_id": item.user.id,
        "username": item.user.username,
        "rating": item.rating,
        "review": item.review,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }


def serialize_wishlist(item):
    return {
        "id": item.id,
        "course_id": item.course.id,
        "course_name": item.course.name,
        "user_id": item.user.id,
        "username": item.user.username,
        "created_at": item.created_at,
    }


def ensure_enrolled(user, course):
    is_member = CourseMember.objects.filter(
        course_id=course,
        user_id=user
    ).exists()

    if not is_member:
        raise HttpError(
            403,
            "Anda harus enroll course ini sebelum memberi rating dan review."
        )

@router.get("/", response=list[CourseOut], auth=LMSJwtAuth())
def list_courses(request):

    courses = Course.objects.select_related("teacher").all()

    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "price": c.price,
            "teacher": c.teacher.username,
        }
        for c in courses
    ]

@router.get(
    "/wishlist/me",
    response=list[CourseWishlistOut],
    auth=auth
)
def my_wishlist(request):
    wishlist = (
        CourseWishlist.objects
        .select_related("course", "user")
        .filter(user=request.auth)
        .order_by("-created_at")
    )

    return [
        serialize_wishlist(item)
        for item in wishlist
    ]

@router.post(
    "/{course_id}/wishlist",
    response=CourseWishlistOut,
    auth=auth
)
def add_course_to_wishlist(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)

    wishlist, created = CourseWishlist.objects.get_or_create(
        course=course,
        user=request.auth
    )

    return serialize_wishlist(wishlist)

@router.delete(
    "/{course_id}/wishlist",
    auth=auth
)
def remove_course_from_wishlist(request, course_id: int):
    wishlist = get_object_or_404(
        CourseWishlist,
        course_id=course_id,
        user=request.auth
    )

    wishlist.delete()

    return {
        "message": "Course berhasil dihapus dari wishlist."
    }

@router.get("/{course_id}", response=CourseOut, auth=LMSJwtAuth())
def detail_course(request, course_id: int):
    course = get_object_or_404(
        Course.objects.select_related("teacher", "category"),
        id=course_id,
    )

    return serialize_course(course)

@router.post("/", auth=LMSJwtAuth())
def create_course(request, payload: CourseCreate):
    category = None

    if payload.category_id:
        category = get_object_or_404(Category, id=payload.category_id)

    course = Course.objects.create(
        name=payload.name,
        description=payload.description,
        price=payload.price,
        category=category,
        level=payload.level,
        status=payload.status,
        teacher=request.auth,
    )

    return {
        "message": "Course created successfully",
        "id": course.id,
    }

@router.put("/{course_id}", auth=LMSJwtAuth())
def update_course(request, course_id: int, payload: CourseUpdate):
    course = get_object_or_404(Course, id=course_id)

    if payload.name is not None:
        course.name = payload.name

    if payload.description is not None:
        course.description = payload.description

    if payload.price is not None:
        course.price = payload.price

    if payload.category_id is not None:
        course.category = get_object_or_404(
            Category,
            id=payload.category_id,
        )

    if payload.level is not None:
        course.level = payload.level

    if payload.status is not None:
        course.status = payload.status

    course.save()

    return {
        "message": "Course updated successfully",
    }

@router.delete("/{course_id}", auth=LMSJwtAuth())
def delete_course(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)
    course.delete()

    return {
        "message": "Course deleted successfully",
    }

@router.get(
    "/{course_id}/reviews",
    response=list[CourseReviewOut],
    auth=auth
)
def list_course_reviews(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)

    reviews = (
        CourseReview.objects
        .select_related("course", "user")
        .filter(course=course)
        .order_by("-created_at")
    )

    return [
        serialize_review(item)
        for item in reviews
    ]

@router.post(
    "/{course_id}/reviews",
    response=CourseReviewOut,
    auth=auth
)
def create_course_review(request, course_id: int, payload: CourseReviewCreate):
    course = get_object_or_404(Course, id=course_id)

    ensure_enrolled(request.auth, course)

    if CourseReview.objects.filter(
        course=course,
        user=request.auth
    ).exists():
        raise HttpError(
            400,
            "Anda sudah memberi review untuk course ini."
        )

    review = CourseReview.objects.create(
        course=course,
        user=request.auth,
        rating=payload.rating,
        review=payload.review,
    )

    return serialize_review(review)

@router.put(
    "/{course_id}/reviews/me",
    response=CourseReviewOut,
    auth=auth
)
def update_my_course_review(
    request,
    course_id: int,
    payload: CourseReviewUpdate
):
    review = get_object_or_404(
        CourseReview.objects.select_related("course", "user"),
        course_id=course_id,
        user=request.auth
    )

    if payload.rating is not None:
        review.rating = payload.rating

    if payload.review is not None:
        review.review = payload.review

    review.save()

    return serialize_review(review)

@router.delete(
    "/{course_id}/reviews/me",
    auth=auth
)
def delete_my_course_review(request, course_id: int):
    review = get_object_or_404(
        CourseReview,
        course_id=course_id,
        user=request.auth
    )

    review.delete()

    return {
        "message": "Review berhasil dihapus."
    }

@router.get(
    "/{course_id}/rating",
    response=CourseRatingSummaryOut,
    auth=auth
)
def course_rating_summary(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)

    result = CourseReview.objects.filter(
        course=course
    ).aggregate(
        average_rating=Avg("rating"),
        total_reviews=Count("id")
    )

    average_rating = result["average_rating"] or 0
    total_reviews = result["total_reviews"] or 0

    return {
        "course_id": course.id,
        "course_name": course.name,
        "average_rating": round(float(average_rating), 2),
        "total_reviews": total_reviews,
    }


@router.get("/{course_id}/lessons", response=list[LessonOut], auth=LMSJwtAuth())
def lessons(request, course_id: int):

    lessons = CourseContent.objects.filter(
        course_id=course_id
    ).select_related("course_id")

    return [
        {
            "id": l.id,
            "name": l.name,
            "description": l.description,
            "video_url": l.video_url,
            "course": l.course_id.name,
        }
        for l in lessons
    ]

@router.get("/lesson/{lesson_id}", response=LessonOut, auth=LMSJwtAuth())
def lesson_detail(request, lesson_id: int):

    lesson = get_object_or_404(
        CourseContent.objects.select_related("course_id"),
        id=lesson_id
    )

    return {
        "id": lesson.id,
        "name": lesson.name,
        "description": lesson.description,
        "video_url": lesson.video_url,
        "course": lesson.course_id.name,
    }

@router.post("/lesson", auth=LMSJwtAuth())
def create_lesson(request, payload: LessonCreate):

    course = get_object_or_404(Course, id=payload.course_id)

    lesson = CourseContent.objects.create(
        name=payload.name,
        description=payload.description,
        video_url=payload.video_url,
        course_id=course,
        parent_id=CourseContent.objects.filter(
            id=payload.parent_id
        ).first()
    )

    return {
        "message": "Lesson created",
        "id": lesson.id
    }

@router.put("/lesson/{lesson_id}", auth=LMSJwtAuth())
def update_lesson(request, lesson_id: int, payload: LessonUpdate):

    lesson = get_object_or_404(
        CourseContent,
        id=lesson_id
    )

    if payload.name is not None:
        lesson.name = payload.name

    if payload.description is not None:
        lesson.description = payload.description

    if payload.video_url is not None:
        lesson.video_url = payload.video_url

    lesson.save()

    return {"message": "Lesson updated"}

@router.delete("/lesson/{lesson_id}", auth=LMSJwtAuth())
def delete_lesson(request, lesson_id: int):

    lesson = get_object_or_404(
        CourseContent,
        id=lesson_id
    )

    lesson.delete()

    return {"message": "Lesson deleted"}

@router.get(
    "/{course_id}/members",
    response=list[EnrollmentOut],
    auth=LMSJwtAuth()
)
def list_members(request, course_id: int):

    members = (
        CourseMember.objects
        .select_related("user_id")
        .filter(course_id=course_id)
    )

    return [
        {
            "id": m.id,
            "username": m.user_id.username,
            "role": m.roles,
        }
        for m in members
    ]

@router.post(
    "/{course_id}/enroll",
    auth=LMSJwtAuth()
)
def enroll_student(request, course_id: int, payload: EnrollmentCreate):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    user = get_object_or_404(
        User,
        id=payload.user_id
    )

    if CourseMember.objects.filter(
        course_id=course,
        user_id=user
    ).exists():

        return {
            "message": "User already enrolled"
        }

    member = CourseMember.objects.create(
        course_id=course,
        user_id=user,
        roles=payload.roles
    )

    return {
        "message": "Enrolled successfully",
        "id": member.id
    }

@router.delete(
    "/{course_id}/members/{user_id}",
    auth=LMSJwtAuth()
)
def remove_member(request, course_id: int, user_id: int):

    member = get_object_or_404(
        CourseMember,
        course_id=course_id,
        user_id=user_id
    )

    member.delete()

    return {
        "message": "Member removed"
    }

def serialize_course(course):
    return {
        "id": course.id,
        "name": course.name,
        "description": course.description,
        "price": course.price,
        "image": course.image.url if course.image else None,

        "category_id": course.category.id if course.category else None,
        "category_name": course.category.name if course.category else None,

        "level": course.level,
        "status": course.status,

        "teacher_id": course.teacher.id,
        "teacher_name": course.teacher.username,

        "created_at": course.created_at,
        "updated_at": course.updated_at,
    }

@router.get("/", response=list[CourseOut], auth=LMSJwtAuth())
def list_courses(
    request,
    search: str = None,
    category: int = None,
    instructor: int = None,
    level: str = None,
    status: str = None,
    min_price: int = None,
    max_price: int = None,
    sort: str = "newest",
):
    courses = Course.objects.select_related(
        "teacher",
        "category",
    ).all()

    if search:
        courses = courses.filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(teacher__username__icontains=search)
            | Q(category__name__icontains=search)
        )

    if category:
        courses = courses.filter(category_id=category)

    if instructor:
        courses = courses.filter(teacher_id=instructor)

    if level:
        courses = courses.filter(level=level)

    if status:
        courses = courses.filter(status=status)

    if min_price is not None:
        courses = courses.filter(price__gte=min_price)

    if max_price is not None:
        courses = courses.filter(price__lte=max_price)

    sort_options = {
        "newest": "-created_at",
        "oldest": "created_at",
        "price_low": "price",
        "price_high": "-price",
        "name_asc": "name",
        "name_desc": "-name",
        "updated": "-updated_at",
    }

    courses = courses.order_by(
        sort_options.get(sort, "-created_at")
    )

    return [
        serialize_course(course)
        for course in courses
    ]

@router.get(
    "/{course_id}/curriculum",
    response=list[CurriculumItemOut],
    auth=auth
)
def course_curriculum(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)

    member = CourseMember.objects.filter(
        course_id=course,
        user_id=request.auth
    ).first()

    progress_map = {}

    if member:
        progress_items = Progress.objects.filter(
            member=member,
            lesson__course_id=course
        )

        progress_map = {
            item.lesson_id: item
            for item in progress_items
        }

    contents = (
        CourseContent.objects
        .select_related("parent_id", "course_id")
        .filter(course_id=course)
        .order_by("parent_id__id", "order", "id")
    )

    return [
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "video_url": item.video_url,
            "file_attachment": item.file_attachment.url if item.file_attachment else None,
            "parent_id": item.parent_id.id if item.parent_id else None,
            "parent_name": item.parent_id.name if item.parent_id else None,
            "order": item.order,
            "completed": progress_map.get(item.id).completed if item.id in progress_map else False,
        }
        for item in contents
    ]