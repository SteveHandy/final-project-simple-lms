from datetime import datetime
from ninja import Schema


class StudentDashboardSummaryOut(Schema):
    total_enrolled_courses: int
    total_lessons: int
    completed_lessons: int
    not_completed_lessons: int
    average_progress: float
    wishlist_count: int
    review_count: int


class StudentDashboardCourseOut(Schema):
    course_id: int
    course_name: str
    description: str
    price: int
    image: str | None = None

    category_id: int | None = None
    category_name: str | None = None

    level: str
    status: str

    teacher_id: int
    teacher_name: str

    total_lessons: int
    completed_lessons: int
    progress_percentage: float


class StudentDashboardRecentLessonOut(Schema):
    lesson_id: int
    lesson_name: str
    course_id: int
    course_name: str
    completed_at: datetime | None = None


class StudentDashboardWishlistOut(Schema):
    wishlist_id: int
    course_id: int
    course_name: str
    price: int
    image: str | None = None
    teacher_name: str
    created_at: datetime


class StudentDashboardOut(Schema):
    summary: StudentDashboardSummaryOut
    enrolled_courses: list[StudentDashboardCourseOut]
    recent_completed_lessons: list[StudentDashboardRecentLessonOut]
    wishlist: list[StudentDashboardWishlistOut]