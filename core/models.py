from django.db import models


class Lesson(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title

class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Problem(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="problems", null=True, blank=True
    )
    
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class User(models.Model):
    name = models.CharField(max_length=255)
    leet_code_username = models.CharField(max_length=255, unique=True)
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )

    def __str__(self):
        return self.name


class SolvedProblem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    solved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "problem")

    def __str__(self):
        return f"{self.user} → {self.problem}"
