from datetime import datetime
from ninja import Schema


class LessonProgressOut(Schema):
    lesson_id: int
    lesson_name: str
    description: str
    video_url: str | None = None
    file_attachment: str | None = None
    parent_id: int | None = None
    parent_name: str | None = None
    order: int
    completed: bool
    completed_at: datetime | None = None


class CourseProgressSummaryOut(Schema):
    course_id: int
    course_name: str
    total_lessons: int
    completed_lessons: int
    not_completed_lessons: int
    percentage: float


class CourseProgressDetailOut(Schema):
    course_id: int
    course_name: str
    total_lessons: int
    completed_lessons: int
    not_completed_lessons: int
    percentage: float
    lessons: list[LessonProgressOut]