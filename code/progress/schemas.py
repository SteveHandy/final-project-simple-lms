from ninja import Schema


class ProgressOut(Schema):
    lesson_id: int
    lesson: str
    completed: bool
    completed_at: str | None


class ProgressSummary(Schema):
    total: int
    completed: int
    percentage: float