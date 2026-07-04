from django.db import models
from django.utils import timezone

from courses.models import CourseMember, CourseContent


class Progress(models.Model):

    member = models.ForeignKey(
        CourseMember,
        on_delete=models.CASCADE,
        related_name="progress"
    )

    lesson = models.ForeignKey(
        CourseContent,
        on_delete=models.CASCADE,
        related_name="progress"
    )

    completed = models.BooleanField(
        default=False
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = ("member", "lesson")
        ordering = ["lesson"]

    def __str__(self):
        status = "Completed" if self.completed else "Not Completed"
        return f"{self.member.user_id.username} - {self.lesson.name} ({status})"