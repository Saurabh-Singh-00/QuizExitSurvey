from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from xhtml2pdf import pisa
from Quizzes_Surveys.decorators import teacher_required, student_required
from Quizzes_Surveys.utils import link_callback
from .models import Quiz, Question, QuizResponse, QuestionResponse
from django.views.generic import UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin
from .forms import QuestionFormSet, QuizForm, TakeQuizForm
from users.models import Batch


@login_required
@student_required
def attempt_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = Question.objects.filter(quiz=quiz)
    student = request.user.student

    if QuizResponse.objects.filter(quiz=quiz, student=student).exists():
        quiz_response = QuizResponse.objects.filter(quiz=quiz, student=student).first()
        return redirect('view-response', pk=quiz_response.pk)

    elif quiz.is_open:
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

    return render(request, 'quiz/attempt.html', {'form': form, 'quiz': quiz})


@login_required
@student_required
def view_response(request, pk):
    template = 'quiz/view_response.html'
    if pk != 0:
        quiz_response = get_object_or_404(QuizResponse, pk=pk)
        ques_responses = QuestionResponse.objects.filter(quiz_response=quiz_response)
        out_of = ques_responses.__len__()
        context = {'ques_responses': ques_responses, 'quiz_response': quiz_response, 'out_of': out_of}
    else:
        context = {'quiz_response': False}

    return render(request, template, context=context)


@student_required
@login_required
def generate_pdf(request, pk):
    quiz_response = get_object_or_404(QuizResponse, pk=pk)
    template_path = 'quiz/pdf_response.html'
    ques_responses = QuestionResponse.objects.filter(quiz_response=quiz_response)
    context = {'ques_responses': ques_responses, 'quiz_response': quiz_response}
    response = HttpResponse(content_type='application/pdf')
    batch = Batch.objects.filter(student=quiz_response.student).first()
    filename = batch.year + '_' + batch.division + '_' + str(
        quiz_response.student.roll_no) + '_' + quiz_response.quiz.title + '_' + quiz_response.quiz.subject.name
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)
    # create a pdf
    pisaStatus = pisa.CreatePDF(
        html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisaStatus.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


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
    batch_queryset = Batch.objects.filter(quiz=quiz)
    batches = ""
    for batch in batch_queryset:
        batches += str(batch) + ", "
    batches = batches[:-2]
    questions = Question.objects.filter(quiz=quiz)
    responses = QuizResponse.objects.filter(quiz=quiz).exists()
    no_responses = []
    if responses:
        for question in questions:
            chosen = [0, 0, 0, 0]
            q_responses = QuestionResponse.objects.filter(question=question)
            for q_response in q_responses:
                if q_response.que_response == "a":
                    chosen[0] += 1
                elif q_response.que_response == "b":
                    chosen[1] += 1
                elif q_response.que_response == "c":
                    chosen[2] += 1
                else:
                    chosen[3] += 1
            no_responses.append(chosen)
        print(no_responses)
    user = request.user.teacher
    context = {
        'questions': questions,
        'quiz': quiz,
        'author': user,
        'batches': batches,
        'responses': responses,
        'no_of_responses': no_responses,
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
    template_name = 'quiz/change_status.html'
    model = Quiz
    fields = ['title', 'is_open']

    def __init__(self, *args, **kwargs):
        super(QuizUpdateView, self).__init__(*args, **kwargs)

    def get_success_url(self):
        quiz = self.get_object()
        return reverse_lazy('view-quiz', kwargs={'pk': quiz.pk})







@login_required
@teacher_required
def generate_excel(request, pk):
    import xlwt
    quiz = get_object_or_404(Quiz, pk=pk)
    ques = Question.objects.filter(quiz=quiz)
    responses = QuizResponse.objects.values_list(
        'student__roll_no',
        'student__student__first_name',
        'student__student__last_name',
        'student__batch__division',
        'student'
    ).filter(quiz=quiz)
    response = HttpResponse(content_type='application/ms-excel')
    file_name = 'Quiz ' + '-'.join([str(x) for x in quiz.batches.all()])
    print(file_name)
    response['Content-Disposition'] = f'attachment; filename="{file_name}.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet(f'{quiz.subject.name}')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Roll No', 'First name', 'Last name', 'Division', 'Student']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    for col_num in range(len(columns), len(ques)+len(columns)):
        ws.write(row_num, col_num, ques[col_num-len(columns)].question, font_style)

    row_num += 1
    res_per_ques = [0 for x in range(len(ques))]
    for i in range(len(responses)):
        for j in range(len(responses[i])):
            ws.write(row_num, j, responses[i][j], font_style)
        for k in range(len(ques)):
            res = QuestionResponse.objects.filter(question=ques[k], quiz_response__student=responses[i][-1]).first()
            ws.write(row_num, k+len(responses[0]), res.que_response, font_style)
            if res.que_response.upper() == ques[k].correct_ans.upper():
                res_per_ques[k] += 1
        row_num += 1
    for i in range(len(ques)):
        ws.write(row_num, len(columns)+i, res_per_ques[i], font_style)
    wb.save(response)
    return response
    # return HttpResponse("<h2>Download Excel</h2>")
