from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from .models import Quiz, Question, QuizResponse, QuestionResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import AccessMixin
from .forms import QuestionFormSet, QuizForm
from users.models import Teacher


# Create your views Question

class QuizListView(ListView):
    model = Quiz
    template_name = 'quiz/home.html'
    context_object_name = 'quizzes'


def question_list(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    context = {
        'questions': Question.objects.filter(quiz=quiz)

    }
    return render(request, 'quiz/show_quiz.html', context)


def create_quiz(request, pk):
    template_name = 'quiz/show_quiz.html'
    heading_message = 'Formset Demo'
    quiz = get_object_or_404(Quiz, pk=pk)
    if request.method == 'GET':
        formset = QuestionFormSet(request.GET or None)
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
            response = HttpResponse()
            response.write("<p>Congratulations</p>")
            return HttpResponse(request, response)
    return render(request, template_name, {
        'formset': formset,
        'heading': heading_message,
    })


# def add_quiz(request):
#     if request.method == 'GET':
#         return render(request, 'quiz/add_quiz.html', {'form': QuizForm})
#     elif request.method == 'POST':
#         form = QuizForm(request.POST)
#         if form.is_valid():
#             text = form.cleaned_data.get('text')
#             if text:
#                 teacher = Teacher.objects.first()
#
#                 Quiz(title=text, author=teacher).save()
#                 quiz = Quiz.objects.latest('id')
#                 return redirect('create-quiz', pk=quiz.pk)


class QuizCreateView(CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = 'quiz/add_quiz.html'

    def form_valid(self, form):
        _form = form.save()
        # TODO: Setup success url after creating a Quiz
        return HttpResponse("<h1>Quiz Added<h1>")
