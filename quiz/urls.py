from django.urls import path
from . import views


urlpatterns = [
    path('<int:pk>/attempt/', views.attempt_quiz, name='attempt-quiz'),
    path('add/', views.add_quiz, name='add-quiz'),
    path('<int:pk>/add/', views.add_quiz, name='add-quiz'),
    path('<int:pk>/view/', views.view_quiz, name='view-quiz'),
    path('<int:pk>/view/stats', views.view_quiz_stats, name='view-quiz-stats'),
    path('<int:pk>/view/response/', views.view_response, name='view-response'),
    path('<int:pk>/view/response/download/', views.generate_pdf, name='download-response'),
    path('<int:opk>/<int:npk>/edit/', views.edit_quiz, name='edit-quiz'),
    path('<int:pk>/delete/', views.QuizDeleteView.as_view(), name='delete-quiz'),
    path('<int:pk>/update/', views.QuizUpdateView.as_view(), name='update-quiz'),
    path('<int:pk>/download/', views.generate_excel, name='generate-excel')
]
