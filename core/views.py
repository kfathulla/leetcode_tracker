from django.shortcuts import render, redirect
from django.db.models import Count, Q
from django.contrib import messages
from .models import User, Problem, Lesson, SolvedProblem, Group
from .scheduler import update_all_users

from django.db.models import Prefetch


def refresh_leetcode(request):
    # Only allow POST for safety
    if request.method == "POST":
        update_all_users()
        messages.success(request, "LeetCode data updated successfully!")
    else:
        messages.error(request, "Invalid request method.")
        
    return redirect("")

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

    # Fetch all solved problems that have a lesson
    solved_qs = SolvedProblem.objects.filter(
        problem__lesson__in=lessons,
    ).select_related("user", "problem")

    # Build a set of (user_id, problem_id) for fast lookup
    solved_set = {(s.user_id, s.problem_id) for s in solved_qs}

    # Build lesson_groups: {lesson_title: [ {problem, solved_by_user_list} ]}
    lesson_groups = {}
    for lesson in lessons:
        problems_list = []
        for problem in lesson.problems.all().order_by("order", "title"):
            # For each problem, compute solved status per user
            solved_status = [(user.id, problem.id) in solved_set for user in users]
            problems_list.append(
                {
                    "problem": problem,
                    "solved_status": solved_status,  # same order as users
                }
            )
        lesson_groups[lesson.title] = problems_list

    return render(
        request,
        "table.html",
        {
            "users": users,
            "lesson_groups": lesson_groups,
            "groups": Group.objects.all(),
            "lessons": Lesson.objects.all(),
            "selected_group": group_id,
            "selected_lesson": lesson_id,
        },
    )
