import json
import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import User, Problem, SolvedProblem, Lesson, Group
from .leetcode import fetch_last_ac

logger = logging.getLogger(__name__)


@require_POST
def refresh_leetcode(request):
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        body = {}

    group_id = body.get("group") or None
    lesson_id = body.get("lesson") or None

    users = User.objects.all()
    if group_id:
        users = users.filter(group_id=group_id)

    lessons = Lesson.objects.prefetch_related("problems")
    if lesson_id:
        lessons = lessons.filter(id=lesson_id)
    target_slugs = set(lessons.values_list("problems__slug", flat=True))

    updated = 0
    errors = []

    for user in users:
        try:
            submissions = fetch_last_ac(user.leet_code_username)
            for sub in submissions:
                slug = sub["titleSlug"]
                title = sub["title"]

                problem, _ = Problem.objects.get_or_create(
                    slug=slug, defaults={"title": title, "lesson": None}
                )
                _, created = SolvedProblem.objects.get_or_create(
                    user=user, problem=problem,
                )
                if created and (not target_slugs or slug in target_slugs):
                    updated += 1
        except Exception:
            logger.exception("Failed to sync user %s", user.name)
            errors.append(user.name)

    return JsonResponse({
        "ok": True,
        "updated": updated,
        "synced_users": users.count(),
        "errors": errors,
    })


def matrix_view(request):
    group_id = request.GET.get("group")
    lesson_id = request.GET.get("lesson")

    users = User.objects.all()
    if group_id:
        users = users.filter(group_id=group_id)

    lessons = Lesson.objects.prefetch_related("problems").order_by("title")
    if lesson_id:
        lessons = lessons.filter(id=lesson_id)

    users = users.annotate(
        solved_count=Count(
            "solvedproblem", filter=Q(solvedproblem__problem__lesson__in=lessons)
        )
    ).order_by("-solved_count", "name")

    solved_qs = SolvedProblem.objects.filter(
        problem__lesson__in=lessons,
    ).select_related("user", "problem")

    solved_set = {(s.user_id, s.problem_id) for s in solved_qs}

    total_problems = 0
    lesson_groups = {}
    for lesson in lessons:
        problems_list = []
        for problem in lesson.problems.all().order_by("order", "title"):
            total_problems += 1
            solved_status = [(user.id, problem.id) in solved_set for user in users]
            problems_list.append({
                "problem": problem,
                "solved_status": solved_status,
            })
        lesson_groups[lesson.title] = problems_list

    return render(request, "table.html", {
        "users": users,
        "lesson_groups": lesson_groups,
        "groups": Group.objects.all(),
        "lessons": Lesson.objects.all(),
        "selected_group": group_id,
        "selected_lesson": lesson_id,
        "total_problems": total_problems,
    })


@staff_member_required
def admin_dashboard_stats(request):
    groups = Group.objects.annotate(user_count=Count("users"))
    lessons = Lesson.objects.annotate(problem_count=Count("problems"))
    top_users = (
        User.objects.annotate(solved=Count("solvedproblem"))
        .order_by("-solved")[:10]
    )
    recent = (
        SolvedProblem.objects.select_related("user", "problem")
        .order_by("-solved_at")[:10]
    )

    return JsonResponse({
        "groups": Group.objects.count(),
        "users": User.objects.count(),
        "lessons": Lesson.objects.count(),
        "problems": Problem.objects.count(),
        "solutions": SolvedProblem.objects.count(),
        "top_users": [
            {
                "name": u.name,
                "solved": u.solved,
                "url": reverse("admin:core_user_change", args=[u.pk]),
            }
            for u in top_users
        ],
        "recent": [
            {
                "user": s.user.name,
                "problem": s.problem.title,
                "date": s.solved_at.strftime("%b %d"),
                "user_url": reverse("admin:core_user_change", args=[s.user_id]),
                "problem_url": reverse("admin:core_problem_change", args=[s.problem_id]),
            }
            for s in recent
        ],
        "group_list": [
            {
                "name": g.name,
                "users": g.user_count,
                "url": reverse("admin:core_group_change", args=[g.pk]),
            }
            for g in groups
        ],
        "lesson_list": [
            {
                "title": l.title,
                "problems": l.problem_count,
                "url": reverse("admin:core_lesson_change", args=[l.pk]),
            }
            for l in lessons
        ],
    })
