from django.urls import path
from . import views


urlpatterns = [
    path('<int:pk>/attempt/', views.attempt_survey, name='attempt-survey'),
    path('add/', views.add_survey, name='add-survey'),
    path('<int:pk>/add/', views.add_survey, name='add-survey'),
    path('<int:pk>/view/', views.view_survey, name='view-survey'),
    path('<int:pk>/view/stats', views.view_survey_stats, name='view-survey-stats'),
    path('<int:pk>/view/response/', views.view_survey_response, name='view-survey-response'),
    path('<int:pk>/view/response/download/', views.generate_pdf, name='download-survey-response'),
    path('<int:opk>/<int:npk>/edit/', views.edit_survey, name='edit-survey'),
    path('<int:pk>/delete/', views.SurveyDeleteView.as_view(), name='delete-survey'),
    path('<int:pk>/update/', views.SurveyUpdateView.as_view(), name='update-survey'),
    path('<int:pk>/download/', views.generate_excel, name='download-excel')
]
