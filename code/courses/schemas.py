from ninja import Schema
from typing import Optional
from datetime import datetime
from pydantic import Field

class CourseOut(Schema):
    id: int
    name: str
    description: str
    price: int
    image: Optional[str] = None

    category_id: Optional[int] = None
    category_name: Optional[str] = None

    level: str
    status: str

    teacher_id: int
    teacher_name: str

    average_rating: float = 0
    total_reviews: int = 0
    is_wishlisted: bool = False

    created_at: datetime
    updated_at: datetime


class CourseCreate(Schema):
    name: str
    description: str = "-"
    price: int = 10000
    category_id: Optional[int] = None
    level: str = "beginner"
    status: str = "draft"


class CourseUpdate(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    category_id: Optional[int] = None
    level: Optional[str] = None
    status: Optional[str] = None

class LessonCreate(Schema):
    name: str
    description: str
    video_url: str | None = None
    course_id: int
    parent_id: int | None = None


class LessonUpdate(Schema):
    name: str | None = None
    description: str | None = None
    video_url: str | None = None


class LessonOut(Schema):
    id: int
    name: str
    description: str
    video_url: str | None
    course: str


class EnrollmentCreate(Schema):
    user_id: int
    roles: str = "std"


class EnrollmentOut(Schema):
    id: int
    username: str
    role: str

class CourseReviewCreate(Schema):
    rating: int = Field(..., ge=1, le=5)
    review: str = ""


class CourseReviewUpdate(Schema):
    rating: int | None = Field(default=None, ge=1, le=5)
    review: str | None = None


class CourseReviewOut(Schema):
    id: int
    course_id: int
    course_name: str
    user_id: int
    username: str
    rating: int
    review: str
    created_at: datetime
    updated_at: datetime


class CourseRatingSummaryOut(Schema):
    course_id: int
    course_name: str
    average_rating: float
    total_reviews: int


class CourseWishlistOut(Schema):
    id: int
    course_id: int
    course_name: str
    user_id: int
    username: str
    created_at: datetime