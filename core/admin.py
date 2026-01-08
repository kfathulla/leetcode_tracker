from django.contrib import admin
from .models import Lesson, Problem, User, SolvedProblem, Group


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id", "title")


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "slug", "lesson", "order")
    list_filter = ("lesson",)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "leet_code_username")


@admin.register(SolvedProblem)
class SolvedProblemAdmin(admin.ModelAdmin):
    list_display = ("user", "problem", "solved_at")
    list_filter = ("user", "problem")
    
    
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name")