from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from .models import Lesson, Problem, User, SolvedProblem, Group


# ── Inlines ──────────────────────────────────────────────

class ProblemInline(admin.TabularInline):
    model = Problem
    extra = 0
    fields = ("title", "slug", "order", "solved_count_display")
    readonly_fields = ("solved_count_display",)
    show_change_link = True
    ordering = ("order", "title")

    def solved_count_display(self, obj):
        if not obj.pk:
            return "-"
        count = SolvedProblem.objects.filter(problem=obj).count()
        url = reverse("admin:core_solvedproblem_changelist") + f"?problem__id__exact={obj.pk}"
        return format_html('<a href="{}">{} solved</a>', url, count)
    solved_count_display.short_description = "Solutions"


class UserInline(admin.TabularInline):
    model = User
    extra = 0
    fields = ("name", "leet_code_username", "solved_count_display")
    readonly_fields = ("solved_count_display",)
    show_change_link = True

    def solved_count_display(self, obj):
        if not obj.pk:
            return "-"
        count = SolvedProblem.objects.filter(user=obj).count()
        url = reverse("admin:core_solvedproblem_changelist") + f"?user__id__exact={obj.pk}"
        return format_html('<a href="{}">{} solved</a>', url, count)
    solved_count_display.short_description = "Solutions"


class SolvedProblemInlineForUser(admin.TabularInline):
    model = SolvedProblem
    extra = 0
    fields = ("problem_link", "lesson_display", "solved_at")
    readonly_fields = ("problem_link", "lesson_display", "solved_at")
    ordering = ("-solved_at",)
    verbose_name = "Solved Problem"
    verbose_name_plural = "Solved Problems"

    def problem_link(self, obj):
        url = reverse("admin:core_problem_change", args=[obj.problem_id])
        return format_html('<a href="{}">{}</a>', url, obj.problem.title)
    problem_link.short_description = "Problem"

    def lesson_display(self, obj):
        if obj.problem.lesson:
            url = reverse("admin:core_lesson_change", args=[obj.problem.lesson_id])
            return format_html('<a href="{}">{}</a>', url, obj.problem.lesson.title)
        return "-"
    lesson_display.short_description = "Lesson"

    def has_add_permission(self, request, obj=None):
        return False


class SolvedProblemInlineForProblem(admin.TabularInline):
    model = SolvedProblem
    extra = 0
    fields = ("user_link", "group_display", "solved_at")
    readonly_fields = ("user_link", "group_display", "solved_at")
    ordering = ("-solved_at",)
    verbose_name = "Solution"
    verbose_name_plural = "Who Solved This"

    def user_link(self, obj):
        url = reverse("admin:core_user_change", args=[obj.user_id])
        return format_html('<a href="{}">{}</a>', url, obj.user.name)
    user_link.short_description = "User"

    def group_display(self, obj):
        if obj.user.group:
            url = reverse("admin:core_group_change", args=[obj.user.group_id])
            return format_html('<a href="{}">{}</a>', url, obj.user.group.name)
        return "-"
    group_display.short_description = "Group"

    def has_add_permission(self, request, obj=None):
        return False


# ── Admin classes ────────────────────────────────────────

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "user_count", "total_solved")
    search_fields = ("name",)

    def get_inlines(self, request, obj=None):
        return [UserInline] if obj else []

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _user_count=Count("users", distinct=True),
            _solved_count=Count("users__solvedproblem", distinct=True),
        )

    def user_count(self, obj):
        url = reverse("admin:core_user_changelist") + f"?group__id__exact={obj.pk}"
        return format_html('<a href="{}">{}</a>', url, obj._user_count)
    user_count.short_description = "Users"
    user_count.admin_order_field = "_user_count"

    def total_solved(self, obj):
        url = reverse("admin:core_solvedproblem_changelist") + f"?user__group__id__exact={obj.pk}"
        return format_html('<a href="{}">{}</a>', url, obj._solved_count)
    total_solved.short_description = "Total Solved"
    total_solved.admin_order_field = "_solved_count"


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "problem_count", "total_solved")
    search_fields = ("title",)

    def get_inlines(self, request, obj=None):
        return [ProblemInline] if obj else []

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _problem_count=Count("problems", distinct=True),
            _solved_count=Count("problems__solvedproblem", distinct=True),
        )

    def problem_count(self, obj):
        url = reverse("admin:core_problem_changelist") + f"?lesson__id__exact={obj.pk}"
        return format_html('<a href="{}">{}</a>', url, obj._problem_count)
    problem_count.short_description = "Problems"
    problem_count.admin_order_field = "_problem_count"

    def total_solved(self, obj):
        return obj._solved_count
    total_solved.short_description = "Total Solutions"
    total_solved.admin_order_field = "_solved_count"


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "lesson_link", "order", "solved_by_count")
    list_filter = ("lesson",)
    search_fields = ("title", "slug")
    list_editable = ("order",)

    def get_inlines(self, request, obj=None):
        return [SolvedProblemInlineForProblem] if obj else []

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_solved_count=Count("solvedproblem"))

    def lesson_link(self, obj):
        if obj.lesson:
            url = reverse("admin:core_lesson_change", args=[obj.lesson_id])
            return format_html('<a href="{}">{}</a>', url, obj.lesson.title)
        return "-"
    lesson_link.short_description = "Lesson"

    def solved_by_count(self, obj):
        url = reverse("admin:core_solvedproblem_changelist") + f"?problem__id__exact={obj.pk}"
        return format_html('<a href="{}">{} users</a>', url, obj._solved_count)
    solved_by_count.short_description = "Solved by"
    solved_by_count.admin_order_field = "_solved_count"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("name", "leet_code_username", "group_link", "solved_count")
    list_filter = ("group",)
    search_fields = ("name", "leet_code_username")

    def get_inlines(self, request, obj=None):
        return [SolvedProblemInlineForUser] if obj else []

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_solved_count=Count("solvedproblem"))

    def group_link(self, obj):
        if obj.group:
            url = reverse("admin:core_group_change", args=[obj.group_id])
            return format_html('<a href="{}">{}</a>', url, obj.group.name)
        return "-"
    group_link.short_description = "Group"

    def solved_count(self, obj):
        url = reverse("admin:core_solvedproblem_changelist") + f"?user__id__exact={obj.pk}"
        return format_html('<a href="{}">{}</a>', url, obj._solved_count)
    solved_count.short_description = "Solved"
    solved_count.admin_order_field = "_solved_count"


@admin.register(SolvedProblem)
class SolvedProblemAdmin(admin.ModelAdmin):
    list_display = ("user_link", "problem_link", "lesson_display", "group_display", "solved_at")
    list_filter = ("user__group", "problem__lesson", "user")
    search_fields = ("user__name", "problem__title", "problem__slug")
    list_select_related = ("user", "user__group", "problem", "problem__lesson")

    def user_link(self, obj):
        url = reverse("admin:core_user_change", args=[obj.user_id])
        return format_html('<a href="{}">{}</a>', url, obj.user.name)
    user_link.short_description = "User"

    def problem_link(self, obj):
        url = reverse("admin:core_problem_change", args=[obj.problem_id])
        return format_html('<a href="{}">{}</a>', url, obj.problem.title)
    problem_link.short_description = "Problem"

    def lesson_display(self, obj):
        if obj.problem.lesson:
            url = reverse("admin:core_lesson_change", args=[obj.problem.lesson_id])
            return format_html('<a href="{}">{}</a>', url, obj.problem.lesson.title)
        return "-"
    lesson_display.short_description = "Lesson"

    def group_display(self, obj):
        if obj.user.group:
            url = reverse("admin:core_group_change", args=[obj.user.group_id])
            return format_html('<a href="{}">{}</a>', url, obj.user.group.name)
        return "-"
    group_display.short_description = "Group"


# ── Site config ──────────────────────────────────────────

admin.site.site_header = "LC Tracker"
admin.site.site_title = "LC Tracker Admin"
admin.site.index_title = "Dashboard"
