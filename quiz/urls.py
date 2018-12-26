from django.urls import path
from . import views
from .views import QuizListView, QuizCreateView


urlpatterns = [
    path('', QuizListView.as_view(), name='quiz-list'),
    # path('quiz/<int:pk>/', views.question_list, name='quiz-detail'),
    path('quiz/<int:pk>/', views.create_quiz, name='create-quiz'),
    path('quiz/add/', QuizCreateView.as_view(), name='add-quiz')
]
