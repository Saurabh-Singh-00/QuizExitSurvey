from django.urls import path
from . import views
from .views import QuizCreateView


urlpatterns = [
    path('quiz/<int:pk>/attempt/', views.attempt_quiz, name='attempt-quiz'),
    path('quiz/<int:pk>/create/', views.create_quiz, name='create-quiz'),
    path('quiz/add/', QuizCreateView.as_view(), name='add-quiz')
]
