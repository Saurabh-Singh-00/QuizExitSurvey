from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.utils.decorators import method_decorator
from Quizzes_Surveys.decorators import teacher_required, student_required
from .models import Quiz, Question, QuizResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import AccessMixin
from .forms import QuestionFormSet, QuizForm, TakeQuizForm
from users.models import Teacher
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views Question

@login_required
@student_required
def attempt_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = Question.objects.filter(quiz=quiz)
    student = request.user.student

    if QuizResponse.objects.filter(quiz=quiz) == QuizResponse.objects.filter(student=student):
        return render(request, 'users/student_home.html')

    total_questions = questions.__len__()

    if request.method == 'POST':
        form = TakeQuizForm(data=request.POST, quiz=quiz)
        # if form.is_valid():
        #     with transaction.atomic():
        #         student_answer = form.save(commit=False)
        #         student_answer.student = student
        #         student_answer.save()
        #         for question in questions:
        #             student.
        #         # if student.get_unanswered_questions(quiz).exists():
        #         #     return redirect('students:take_quiz', pk)
        #         # else:
        #         #     correct_answers = student.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).count()
        #         #     score = round((correct_answers / total_questions) * 100.0, 2)
        #         #     QuizResponse.objects.create(student=student, quiz=quiz, score=score)
        #         #     if score < 50.0:
        #         #         messages.warning(request, 'Better luck next time! Your score for the quiz %s was %s.' % (quiz.name, score))
        #         #     else:
        #         #         messages.success(request, 'Congratulations! You completed the quiz %s with success! You scored %s points.' % (quiz.name, score))
        #         #     return redirect('students:quiz_list')
    else:
        form = TakeQuizForm(quiz=quiz)

    return render(request, 'quiz/attempt.html', {'form': form})


@teacher_required
@login_required
def create_quiz(request, pk):
    template_name = 'quiz/show_quiz.html'
    heading_message = 'Formset Demo'
    quiz = get_object_or_404(Quiz, pk=pk)
    if request.method == 'GET':
        formset = QuestionFormSet(request.GET or None,  )
    elif request.method == 'POST':
        formset = QuestionFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                # extract name from each form and save
                text = form.cleaned_data.get('question')
                a = form.cleaned_data.get('option_a')
                b = form.cleaned_data.get('option_b')
                c = form.cleaned_data.get('option_c')
                d = form.cleaned_data.get('option_d')
                ans = form.cleaned_data.get('correct_ans')
                # save book instance
                if text:
                    Question(question=text, quiz=quiz, option_a=a, option_b=b, option_c=c, option_d=d,
                             correct_ans=ans).save()
            # once all books are saved, redirect to book list view
            return HttpResponse("<html><body>Created</body></html>")
    return render(request, template_name, {
        'formset': formset,
        'heading': heading_message,
    })


@method_decorator([login_required, teacher_required],  name='dispatch')
class QuizCreateView(CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = 'quiz/add_quiz.html'

    def form_valid(self, form):
        if self.request.user.is_teacher:
            obj = form.save(commit=False)
            obj.author = self.request.user.teacher
            obj.save()
            return redirect('create-quiz', pk=obj.pk)
        else:
            return HttpResponse("<h1>You are not supposed to be here!</h1>")
