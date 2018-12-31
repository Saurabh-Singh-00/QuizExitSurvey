# Create your views here.
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import ListView
from django.views.generic.base import View

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


class StudentSubjectListView(LoginRequiredMixin, ListView):
    template_name = 'users/student_home.html'
    context_object_name = 'subjects'

    def get_queryset(self):
        self.user = get_object_or_404(User, pk=self.kwargs['pk'])
        return Subject.objects.filter(batch__year=self.user.student.batch.year)


class TeacherSubjectListView(LoginRequiredMixin, ListView):
    template_name = 'users/teacher_home.html'
    context_object_name = 'subjects'

    def get_queryset(self):
        self.user = get_object_or_404(User, pk=self.kwargs['pk'])
        print(Subject.objects.all())
        print(self.user.teacher.subjects.all())
        return Subject.objects.all() and self.user.teacher.subjects.all()


class LoginView(View):

    def get(self, request):
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
