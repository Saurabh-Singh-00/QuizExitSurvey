# Create your views here.
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import *
from django.views.generic.base import View, ContextMixin
from Quizzes_Surveys.decorators import student_required, teacher_required
from exit.models import Survey
from quiz.models import Quiz
from users.models import User, Student, Subject, Teacher, Batch
from .forms import StudentRegisterForm, TeacherRegisterForm, TeacherUpdateForm, StudentUpdateForm


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

    def get_subject_with_open_quiz_list(self):
        subject_list = []
        for quiz in Quiz.objects.filter(batches__student=self.user.student).order_by('subject__name'):
            if quiz.is_open:
                subject = quiz.subject.name
                if subject not in subject_list:
                    subject_list.append(subject)
        return subject_list

    def get_subject_with_close_quiz_list(self):
        subject_list = []
        for quiz in Quiz.objects.filter(batches__student=self.user.student).order_by('subject__name'):
            if not quiz.is_open:
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

    def get_my_subject_list(self):
        subject_list = []
        for quiz in Quiz.objects.filter(author=self.user.teacher).order_by('subject__name'):
            subject = quiz.subject.name
            if subject not in subject_list:
                subject_list.append(subject)
        return subject_list

    def test_func(self):
        return self.kwargs['pk'] == self.request.user.pk


@method_decorator([login_required, student_required], name='dispatch')
class StudentExitListView(UserPassesTestMixin, ListView, ContextMixin):
    template_name = 'users/survey_list.html'
    context_object_name = 'surveys'

    def get_queryset(self):
        self.user = get_object_or_404(User, pk=self.kwargs['pk'])
        exit_set = Survey.objects.filter(batches__student=self.user.student).order_by('subject__name')
        return exit_set

    def get_subject_list(self):
        subject_list = []
        for survey in Survey.objects.filter(batches__student=self.user.student).order_by('subject__name'):
            subject = survey.subject.name
            if subject not in subject_list:
                subject_list.append(subject)
        return subject_list

    def get_subject_with_open_quiz_list(self):
        subject_list = []
        for survey in Survey.objects.filter(batches__student=self.user.student).order_by('subject__name'):
            if survey.is_open:
                subject = survey.subject.name
                if subject not in subject_list:
                    subject_list.append(subject)
        return subject_list

    def get_subject_with_close_quiz_list(self):
        subject_list = []
        for survey in Survey.objects.filter(batches__student=self.user.student).order_by('subject__name'):
            if not survey.is_open:
                subject = survey.subject.name
                if subject not in subject_list:
                    subject_list.append(subject)
        return subject_list

    def test_func(self):
        return self.kwargs['pk'] == self.request.user.pk


@method_decorator([login_required, teacher_required], name='dispatch')
class TeacherSurveyListView(UserPassesTestMixin, ListView):
    template_name = 'users/survey_list.html'
    context_object_name = 'surveys'

    def get_queryset(self):
        self.user = get_object_or_404(User, pk=self.kwargs['pk'])
        subjects = self.user.teacher.subjects.all()
        exit_set = Survey.objects.filter(subject__in=subjects).order_by('subject__name')
        return exit_set

    def get_subject_list(self):
        subject_list = []
        self.user = get_object_or_404(User, pk=self.kwargs['pk'])
        subjects = self.user.teacher.subjects.all()
        for survey in Survey.objects.filter(subject__in=subjects).order_by('subject__name'):
            subject = survey.subject.name
            if subject not in subject_list:
                subject_list.append(subject)
        subject_list.sort()
        return subject_list

    def get_my_subject_list(self):
        subject_list = []
        for survey in Survey.objects.filter(author=self.user.teacher).order_by('subject__name'):
            subject = survey.subject.name
            if subject not in subject_list:
                subject_list.append(subject)
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
        else:
            messages.error(request, 'Error! The username and password do not match.')
            return redirect('login')


@method_decorator([login_required], name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    template_name = 'users/update_profile.html'
    fields = ['first_name', 'last_name', 'email']

    def get_success_url(self):
        user = self.get_object()
        if user.is_teacher:
            return reverse_lazy('teacher-profile', kwargs={'pk': user.pk})
        else:
            return reverse_lazy('student-profile', kwargs={'pk': user.pk})


@teacher_required
@login_required
def teacher_profile(request, pk):
    batch_queryset = Batch.objects.filter(teacher__teacher_id=pk)
    subject_queryset = Subject.objects.filter(teacher__teacher_id=pk)
    subjects = ""
    batches = ""
    for batch in batch_queryset:
        batches += str(batch) + ", "
    for subject in subject_queryset:
        subjects += subject.name + ", "
    batches = batches[:-2]
    subjects = subjects[:-2]
    context = {
        'batches': batches,
        'subjects': subjects,
    }
    return render(request, 'users/user_detail.html', context)


@login_required
@student_required
def student_profile(request, pk):
    student = Student.objects.filter(student_id=pk).first()
    roll_no = str(student.roll_no)
    batch = Batch.objects.get(student__student_id=pk)
    subject_queryset = Subject.objects.filter(batch=batch)
    subjects = ""
    for subject in subject_queryset:
        subjects += subject.name + ", "
    subjects = subjects[:-2]
    context = {
        'batch': str(batch),
        'subjects': subjects,
        'roll_no': roll_no
    }
    return render(request, 'users/user_detail.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('login')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {
        'form': form
    })


@login_required
@teacher_required
def update_teacher(request):
    if request.method == 'POST':
        form = TeacherUpdateForm(request.POST)
        if form.is_valid():
            form = TeacherUpdateForm(request.POST)
            Teacher.objects.filter(teacher_id=request.user.pk).delete()
            teacher = form.save(commit=False)
            teacher.teacher = request.user
            teacher.save()
            form.save_m2m()
            return redirect('teacher-profile', pk=request.user.pk)
    else:
        form = TeacherUpdateForm()
    return render(request, 'users/register_new_sem.html', {'form': form})


@login_required
@student_required
def update_student(request):
    if request.method == 'POST':
        form = StudentUpdateForm(request.POST)
        if form.is_valid():
            form = StudentUpdateForm(request.POST)
            Student.objects.filter(student_id=request.user.pk).delete()
            student = form.save(commit=False)
            student.student = request.user
            student.roll_no = form.cleaned_data['roll_no']
            student.batch = form.cleaned_data['batch']
            student.save()
            return redirect('student-profile', pk=request.user.pk)
    else:
        form = StudentUpdateForm()
    return render(request, 'users/register_new_sem.html', {'form': form})
