from django.urls import path
from . import views

# from .views import QuizCreateView


urlpatterns = [
    path('quiz/<int:pk>/attempt/', views.attempt_quiz, name='attempt-quiz'),
    path('quiz/add/', views.add_quiz, name='add-quiz'),
    path('quiz/<int:pk>/add/', views.add_quiz, name='add-quiz'),
    path('quiz/<int:pk>/view/', views.view_quiz, name='view-quiz'),
    path('quiz/<int:pk>/edit/', views.edit_quiz, name='edit-quiz')
]
