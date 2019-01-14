from django.contrib import admin
from .models import Survey, SQuestion,SurveyResponse, SQuestionResponse


admin.site.register(Survey)
admin.site.register(SQuestion)
admin.site.register(SurveyResponse)
admin.site.register(SQuestionResponse)
