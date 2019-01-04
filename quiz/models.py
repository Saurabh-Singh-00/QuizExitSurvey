from django.db import models
from django.shortcuts import reverse


class Quiz(models.Model):
    title = models.CharField(max_length=50)
    author = models.ForeignKey('users.Teacher', on_delete=models.CASCADE)
    subject = models.ForeignKey('users.Subject', on_delete=models.CASCADE)
    batches = models.ManyToManyField('users.Batch')

    class Meta:
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse('create-quiz', kwargs={'pk': self.pk})


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.TextField()
    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()

    options = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D')
    ]
    correct_ans = models.CharField(max_length=10, choices=options, help_text="Which is the correct answer")

    def __str__(self):
        return f"{self.quiz.title.upper() + ' Question'}"


class QuestionResponse(models.Model):
    quiz_response = models.ForeignKey('quiz.QuizResponse', on_delete=models.CASCADE)
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    options = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D')
    ]

    que_response = models.CharField(max_length=10, choices=options, help_text="Response entered by the student")

    def __str__(self):
        return f"Response to {self.question.quiz.title.upper()} + Question - {self.question.question}"


class QuizResponse(models.Model):
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = 0

    def __str__(self):
        return f"{self.quiz.title.upper() + ' Question'}"

    def get_result(self):
        if self.responses.question.answer_set[0] == self.responses.answer:
            self.score += 1
        return self.score
