from django.db import models
from django.contrib.auth.models import AbstractUser

# from quiz.models import Quiz
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    is_teacher = models.BooleanField('teacher_status', default=False)


class Student(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE)
    batch = models.ForeignKey('users.Batch', on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.student.username.capitalize()}"


class Subject(models.Model):
    name = models.CharField(max_length=50)
    has_lab = models.BooleanField()

    def __str__(self):
        return f"{self.name.capitalize()}"


class Teacher(models.Model):
    teacher = models.OneToOneField(User, on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject)
    batches = models.ManyToManyField('users.Batch')

    def __str__(self):
        return f"Prof {self.teacher.username.capitalize()}"


# @receiver(post_save, sender=User)
# def update_user_profile(sender, instance, created, **kwargs):
#     if created:
#
#         try:
#             if instance.is_teacher:
#                 Teacher.objects.create(teacher=instance)
#                 instance.teacher.save()
#         except:
#             pass


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
