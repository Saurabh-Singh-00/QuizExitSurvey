# Create your views here.
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from django.views.generic import ListView
from django.views.generic.base import View, ContextMixin

from Quizzes_Surveys.decorators import student_required, teacher_required
from quiz.models import Quiz
from users.models import User, Student, Subject, Teacher, Batch
from .forms import StudentRegisterForm, TeacherRegisterForm


class RegisterStudentView(SuccessMessageMixin, CreateView):
    model = User
    form_class = StudentRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')
    success_message = "Account for %(username)s created, you can login now"

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, username=self.object.username, )

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)


class RegisterTeacherView(SuccessMessageMixin, CreateView):
    model = User
    form_class = TeacherRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')
    success_message = "Account for %(username)s created, you can login now"

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, username=self.object.username, )

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'teacher'
        return super().get_context_data(**kwargs)


@method_decorator([login_required, student_required], name='dispatch')
class StudentQuizListView(UserPassesTestMixin, ListView, ContextMixin):
    template_name = 'users/quiz_list.html'
    context_object_name = 'quizzes'

    def get_queryset(self):
        self.user = get_object_or_404(User, pk=self.kwargs['pk'])
        quiz_set = Quiz.objects.filter(batches__student=self.user.student).order_by('subject__name')
        return quiz_set

    def get_subject_list(self):
        subject_list = []
        for quiz in Quiz.objects.filter(batches__student=self.user.student).order_by('subject__name'):
            subject = quiz.subject.name
            if subject not in subject_list:
                subject_list.append(subject)
        return subject_list

    def test_func(self):
        return self.kwargs['pk'] == self.request.user.pk


@method_decorator([login_required, teacher_required], name='dispatch')
class TeacherSubjectListView(UserPassesTestMixin, ListView):
    template_name = 'users/quiz_list.html'
    context_object_name = 'quizzes'

    def get_queryset(self):
        self.user = get_object_or_404(User, pk=self.kwargs['pk'])
        subjects = self.user.teacher.subjects.all()
        quiz_set = Quiz.objects.filter(subject__in=subjects).order_by('subject__name')
        return quiz_set

    def get_subject_list(self):
        subject_list = []
        self.user = get_object_or_404(User, pk=self.kwargs['pk'])
        subjects = self.user.teacher.subjects.all()
        for quiz in Quiz.objects.filter(subject__in=subjects).order_by('subject__name'):
            subject = quiz.subject.name
            if subject not in subject_list:
                subject_list.append(subject)
        subject_list.sort()
        return subject_list

    def test_func(self):
        return self.kwargs['pk'] == self.request.user.pk


class LoginView(View):

    def get(self, request):
        if self.request.user.is_authenticated:
            if self.request.user.is_teacher:
                return redirect('teacher-home', pk=self.request.user.pk)
            else:
                return redirect('student-home', pk=self.request.user.pk)
        return render(request, 'users/login.html', {'form': AuthenticationForm()})

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active and not user.is_teacher:
                login(request, user)
                return redirect('student-home', pk=user.pk)
            elif user.is_active and user.is_teacher:
                login(request, user)
                return redirect('teacher-home', pk=user.pk)

        return redirect('login')
