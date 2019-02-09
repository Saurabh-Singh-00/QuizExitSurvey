from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_teacher = models.BooleanField('teacher_status', default=False)


class Student(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_no = models.SmallIntegerField()
    batch = models.ForeignKey('users.Batch', on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.student.first_name.capitalize() + ' ' + self.student.last_name.capitalize()}"


class Subject(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name.capitalize()}"


class Teacher(models.Model):
    teacher = models.OneToOneField(User, on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject)
    batches = models.ManyToManyField('users.Batch')

    def __str__(self):
        return f"Prof. {self.teacher.first_name.capitalize() + ' ' + self.teacher.last_name.capitalize()}"


class Batch(models.Model):
    subjects = models.ManyToManyField(Subject)

    YEAR_CHOICES = (
        ("SE", "SE"),
        ("TE", "TE"),
        ("BE", "BE")
    )

    year = models.CharField(max_length=10, choices=YEAR_CHOICES, default="SE")

    DIVISION_CHOICES = (
        ("A", "A"),
        ("B", "B"),
        ("C", "C")
    )

    division = models.CharField(max_length=10, choices=DIVISION_CHOICES, default="A")

    BATCH_CHOICES = {
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
    }

    batch = models.CharField(max_length=10, choices=BATCH_CHOICES, default="1")

    def __str__(self):
        return f"{(str(self.year) + '-' + str(self.division) + str(self.batch)).upper()}"
