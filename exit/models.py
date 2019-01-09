from django.db import models

# Create your models here.


class Survey(models.Model):
    title = models.CharField(max_length=50)
    author = models.ForeignKey('users.Teacher', on_delete=models.CASCADE)
    subject = models.ForeignKey('users.Subject', on_delete=models.CASCADE)
    batches = models.ManyToManyField('users.Batch')
    is_open = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Surveys'

    def __str__(self):
        return f"{self.title}"


class SQuestion(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    squestion = models.TextField()

    def __str__(self):
        return f"{self.survey.title.upper() + ' Question'}"


class SQuestionResponse(models.Model):
    survey_response = models.ForeignKey('exit.SurveyResponse', on_delete=models.CASCADE)
    squestion = models.ForeignKey(SQuestion, on_delete=models.CASCADE)
    options = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')
    ]
    que_response = models.CharField(max_length=10, choices=options, help_text="Response entered by the student")

    def __str__(self):
        return f"Response to {self.squestion.survey.title.upper()} + Question - {self.squestion.squestion}"


class SurveyResponse(models.Model):
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    feedback = models.TextField()

    def __str__(self):
        return f"{self.survey.title.upper() + ' Response'}"
