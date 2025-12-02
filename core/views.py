from django.shortcuts import render
from .models import User, Problem, Lesson, SolvedProblem


from django.db.models import Prefetch


def matrix_view(request):
    users = list(User.objects.all().order_by("name"))
    lessons = Lesson.objects.prefetch_related("problems").order_by("title")

    # Fetch all solved problems that have a lesson
    solved_qs = SolvedProblem.objects.filter(
        problem__lesson__isnull=False
    ).select_related("user", "problem")

    # Build a set of (user_id, problem_id) for fast lookup
    solved_set = {(s.user_id, s.problem_id) for s in solved_qs}

    # Build lesson_groups: {lesson_title: [ {problem, solved_by_user_list} ]}
    lesson_groups = {}
    for lesson in lessons:
        problems_list = []
        for problem in lesson.problems.all().order_by("title"):
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
        request, "table.html", {"users": users, "lesson_groups": lesson_groups}
    )
