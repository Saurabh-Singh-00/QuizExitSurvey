"""Quizzes_Surveys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import RegisterStudentView, RegisterTeacherView, StudentQuizListView, LoginView, TeacherSubjectListView, \
    UserUpdateView, change_password, teacher_profile, student_profile, update_teacher, update_student
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/student/', view=RegisterStudentView.as_view(), name='register-student'),
    path('register/teacher/', view=RegisterTeacherView.as_view(), name='register-teacher'),
    # path('', view=LoginView.as_view(), name='login'),
    path('login/', view=LoginView.as_view(), name='login'),
    path('logout/', view=auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html"),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),
         name='password_reset_complete'),
    path('student/<int:pk>/home/', view=StudentQuizListView.as_view(), name='student-home'),
    path('teacher/<int:pk>/home/', view=TeacherSubjectListView.as_view(), name='teacher-home'),
    path('teacher/<int:pk>/profile/', view=teacher_profile, name='teacher-profile'),
    path('student/<int:pk>/profile/', view=student_profile, name='student-profile'),
    path('<int:pk>/update/', view=UserUpdateView.as_view(), name='user-update'),
    path('password/change/', change_password, name='change_password'),
    path('teacher/update/', view=update_teacher, name='teacher-update'),
    path('student/update/', view=update_student, name='student-update'),
]
