from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from .models import User, Problem, SolvedProblem, Lesson
from .leetcode import fetch_last_ac
import logging

logger = logging.getLogger(__name__)


def update_all_users():
    logger.info("Running LeetCode update job...")

    users = User.objects.all()

    for user in users:
        submissions = fetch_last_ac(user.leet_code_username)

        for sub in submissions:
            slug = sub["titleSlug"]
            title = sub["title"]

            problem, created = Problem.objects.get_or_create(
                slug=slug, defaults={"title": title, "lesson": None}
            )

            if created:
                logger.info(f"New problem added: {title} ({slug})")

            SolvedProblem.objects.get_or_create(
                user=user,
                problem=problem,
            )

    logger.info("LeetCode update job finished.")


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_all_users, "interval", minutes=30)
    scheduler.start()
