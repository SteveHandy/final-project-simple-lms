from django.contrib import admin
from .models import Category, Course, CourseMember, CourseContent, Comment
from .models import CourseReview, CourseWishlist

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "level",
        "status",
        "price",
        "teacher",
        "created_at",
    )
    list_filter = ("category", "level", "status", "teacher")
    search_fields = ("name", "description", "teacher__username")
    ordering = ('-created_at',)


@admin.register(CourseMember)
class CourseMemberAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'user_id', 'roles')
    list_filter = ('roles',)


@admin.register(CourseContent)
class CourseContentAdmin(admin.ModelAdmin):
    list_display = ('name', 'course_id', 'parent_id')
    list_filter = ('course_id',)
    search_fields = ('name', 'description')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content_id', 'member_id', 'comment')
    list_filter = ('content_id',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "user",
        "rating",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "rating",
        "created_at",
    )
    search_fields = (
        "course__name",
        "user__username",
        "review",
    )


@admin.register(CourseWishlist)
class CourseWishlistAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "user",
        "created_at",
    )
    search_fields = (
        "course__name",
        "user__username",
    )