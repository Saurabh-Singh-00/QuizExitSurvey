from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from Quizzes_Surveys.decorators import teacher_required, student_required
from Quizzes_Surveys.utils import render_to_pdf
from .models import Quiz, Question, QuizResponse, QuestionResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin
from .forms import QuestionFormSet, QuizForm, TakeQuizForm
from users.models import Teacher, Subject, Batch
from django.contrib.auth.mixins import LoginRequiredMixin
import copy


# Create your views Question

@login_required
@student_required
def attempt_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = Question.objects.filter(quiz=quiz)
    student = request.user.student

    if QuizResponse.objects.filter(quiz=quiz, student=student).exists():
        quiz_response = QuizResponse.objects.filter(quiz=quiz).first()
        ques_responses = QuestionResponse.objects.filter(quiz_response=quiz_response)
        return redirect('view-response', pk=quiz_response.pk)

    if quiz.is_open:
        if request.method == 'POST':
            form = TakeQuizForm(data=request.POST, quiz=quiz)
            if form.is_valid():
                with transaction.atomic():
                    quiz_response = form.save(commit=False)
                    quiz_response.student = student
                    quiz_response.quiz = quiz
                    quiz_response.score = 0
                    quiz_response.save()
                    ques_no = 1
                    score = 0
                    for question in questions:
                        ques_response = QuestionResponse.objects.create(question=question, quiz_response=quiz_response,
                                                                        que_response=form.cleaned_data[
                                                                            'question_no_%d' % ques_no])
                        ques_no += 1
                        if ques_response.que_response == question.correct_ans.lower():
                            score += 1
                    quiz_response.score = score
                    quiz_response.save()
                    return redirect('view-response', pk=quiz_response.pk)

        else:
            form = TakeQuizForm(quiz=quiz)
    else:
        return redirect('view-response', pk=0)

    return render(request, 'quiz/attempt.html', {'form': form})


@login_required
@student_required
def view_response(request, pk):
    template = 'quiz/view_response.html'
    if pk != 0:
        quiz_response = get_object_or_404(QuizResponse, pk=pk)
        ques_responses = QuestionResponse.objects.filter(quiz_response=quiz_response)
        context = {'ques_responses': ques_responses, 'quiz_response': quiz_response}
    else:
        context = {'quiz_response': False}

    return render(request, template, context=context)


@student_required
@login_required
def generate_pdf(request, pk):
    quiz_response = get_object_or_404(QuizResponse, pk=pk)
    template = 'quiz/pdf_response.html'
    ques_responses = QuestionResponse.objects.filter(quiz_response=quiz_response)
    context = {'ques_responses': ques_responses, 'quiz_response': quiz_response}
    pdf = render_to_pdf(template, context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = quiz_response.student.student.first_name + '_' + quiz_response.student.student.last_name + "_" + quiz_response.quiz.title + "_" + quiz_response.quiz.subject.name + ".pdf"
        content = "inline; filename='%s'" % (filename)
        download = request.GET.get('download')
        if download:
            content = "attachment; filename='%s'" % (filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse(pdf, content_type='application/pdf')


@teacher_required
@login_required
def add_quiz(request, pk=None):
    template_name = 'quiz/add_quiz.html'
    teacher = request.user.teacher
    if pk is None:
        if request.method == 'POST':
            form = QuizForm(teacher, request.POST)
            if form.is_valid():
                quiz = form.save(commit=False)
                quiz.title = form.cleaned_data['title']
                quiz.author = teacher
                quiz.subject = form.cleaned_data['subject']
                quiz.save()
                form.save_m2m()
                return redirect('edit-quiz', opk=0, npk=quiz.pk)
            else:
                messages.error(request, form.errors['no_subject'])
        else:
            form = QuizForm(teacher)
    else:
        quiz = Quiz.objects.get(pk=pk)
        if request.method == 'POST':
            form = QuizForm(teacher, request.POST, hide_condition=True, initial={'subject': quiz.subject})
            if form.is_valid():
                new_quiz = form.save(commit=False)
                new_quiz.title = form.cleaned_data['title']
                new_quiz.author = teacher
                new_quiz.subject = form.cleaned_data['subject']
                new_quiz.save()
                form.save_m2m()
                return redirect('edit-quiz', opk=quiz.pk, npk=new_quiz.pk)
            else:
                messages.error(request, "Please select a batch")
        else:
            form = QuizForm(teacher, hide_condition=True, initial={'subject': quiz.subject})

    return render(request, template_name, {'form': form})


@teacher_required
@login_required
def edit_quiz(request, opk, npk):
    template_name = 'quiz/edit_quiz.html'
    quiz = get_object_or_404(Quiz, pk=npk)
    try:
        o_quiz = Quiz.objects.filter(pk=opk)
        questions = Question.objects.filter(quiz=o_quiz[0]).values()
    except IndexError:
        questions = {}

    if request.method == 'GET':
        formset = QuestionFormSet(request.GET or None, initial=questions)
    elif request.method == 'POST':
        formset = QuestionFormSet(request.POST, initial=questions)
        if formset.is_valid():
            if opk == npk:
                Question.objects.filter(quiz=Quiz.objects.filter(pk=opk).first()).delete()
            for form in formset:
                # extract name from each form and save
                text = form.cleaned_data['question']
                a = form.cleaned_data['option_a']
                b = form.cleaned_data['option_b']
                c = form.cleaned_data['option_c']
                d = form.cleaned_data['option_d']
                ans = form.cleaned_data['correct_answer']
                # save book instance
                if text:
                    Question(question=text, quiz=quiz, option_a=a, option_b=b, option_c=c, option_d=d,
                             correct_ans=ans).save()
            # once all books are saved, redirect to book list view
            return redirect('view-quiz', pk=npk)
    return render(request, template_name, {
        'formset': formset,
    })


@login_required
@teacher_required
def view_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = Question.objects.filter(quiz=quiz)
    responses = QuizResponse.objects.filter(quiz=quiz).exists()
    user = request.user.teacher
    context = {
        'questions': questions,
        'quiz': quiz,
        'author': user,
        'responses': responses
    }
    return render(request, 'quiz/view_quiz.html', context)


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizDeleteView(UserPassesTestMixin, DeleteView):
    model = Quiz
    template_name = 'quiz/quiz_confirm_delete.html'

    def test_func(self):
        quiz = self.get_object()
        if self.request.user.teacher == quiz.author:
            return True
        else:
            return False

    def get_success_url(self):
        return reverse_lazy('teacher-home', kwargs={'pk': self.request.user.pk})


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizUpdateView(UpdateView):
    template_name = 'quiz/add_quiz.html'
    model = Quiz
    fields = ['title', 'is_open']

    def __init__(self, *args, **kwargs):
        super(QuizUpdateView, self).__init__(*args, **kwargs)

    def get_success_url(self):
        quiz = self.get_object()
        return reverse_lazy('view-quiz', kwargs={'pk': quiz.pk})
