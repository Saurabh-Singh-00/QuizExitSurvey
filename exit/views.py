from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import transaction
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DeleteView, UpdateView
from xhtml2pdf import pisa
from Quizzes_Surveys.decorators import teacher_required, student_required
from Quizzes_Surveys.utils import link_callback
from exit.forms import SurveyForm, SQuestionFormSet, TakeSurveyForm
from exit.models import Survey, SQuestion, SurveyResponse, SQuestionResponse
from users.models import Batch, Student


@login_required
@student_required
def attempt_survey(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    squestions = SQuestion.objects.filter(survey=survey)
    student = request.user.student
    if SurveyResponse.objects.filter(survey=survey, student=student).exists():
        survey_response = SurveyResponse.objects.filter(survey=survey, student=student).first()
        return redirect('view-survey-response', pk=survey_response.pk)
    elif request.user.student.batch not in survey.batches.all():
        return HttpResponseForbidden("You're not supposed to be here!")
    elif survey.is_open:
        if request.method == 'POST':
            form = TakeSurveyForm(data=request.POST, survey=survey)
            if form.is_valid():
                with transaction.atomic():
                    survey_response = form.save(commit=False)
                    survey_response.student = student
                    survey_response.survey = survey
                    survey_response.feedback = form.cleaned_data['survey_feedback']
                    survey_response.save()
                    ques_no = 1
                    for squestion in squestions:
                        SQuestionResponse.objects.create(squestion=squestion,
                                                         survey_response=survey_response,
                                                         que_response=form.cleaned_data['question_no_%d' % ques_no])
                        ques_no += 1
                    survey_response.save()
                    return redirect('view-survey-response', pk=survey_response.pk)
        else:
            form = TakeSurveyForm(survey=survey)
    else:
        return redirect('view-survey-response', pk=0)
    return render(request, 'survey/attempt.html', {'form': form, 'survey': survey})


@login_required
@student_required
def view_survey_response(request, pk):
    template = 'survey/view_response.html'
    if pk != 0:
        survey_response = get_object_or_404(SurveyResponse, pk=pk)
        ques_responses = SQuestionResponse.objects.filter(survey_response=survey_response)
        context = {'ques_responses': ques_responses, 'survey_response': survey_response}
    else:
        context = {'survey_response': False}

    return render(request, template, context=context)


@student_required
@login_required
def generate_pdf(request, pk):
    survey_response = get_object_or_404(SurveyResponse, pk=pk)
    template_path = 'survey/pdf_response.html'
    ques_responses = SQuestionResponse.objects.filter(survey_response=survey_response)
    context = {'ques_responses': ques_responses, 'survey_response': survey_response}
    response = HttpResponse(content_type='application/pdf')
    batch = Batch.objects.filter(student=survey_response.student).first()
    filename = batch.year + '_' + batch.division + '_' + str(
        survey_response.student.roll_no) + '_' + survey_response.survey.title + '_' + survey_response.survey.subject.name
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)
    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


@teacher_required
@login_required
def add_survey(request, pk=None):
    template_name = 'survey/add_survey.html'
    teacher = request.user.teacher
    if pk is None:
        if request.method == 'POST':
            form = SurveyForm(teacher, request.POST)
            if form.is_valid():
                survey = form.save(commit=False)
                survey.title = form.cleaned_data['title']
                survey.author = teacher
                survey.subject = form.cleaned_data['subject']
                survey.save()
                form.save_m2m()
                return redirect('edit-survey', opk=0, npk=survey.pk)
            else:
                messages.error(request, form.errors['no_subject'])
        else:
            form = SurveyForm(teacher)
    else:
        survey = Survey.objects.get(pk=pk)
        if request.method == 'POST':
            form = SurveyForm(teacher, request.POST, hide_condition=True, initial={'subject': survey.subject})
            if form.is_valid():
                new_survey = form.save(commit=False)
                new_survey.title = form.cleaned_data['title']
                new_survey.author = teacher
                new_survey.subject = form.cleaned_data['subject']
                new_survey.save()
                form.save_m2m()
                return redirect('edit-survey', opk=survey.pk, npk=new_survey.pk)
            else:
                messages.error(request, "Please select a batch")
        else:
            form = SurveyForm(teacher, hide_condition=True, initial={'subject': survey.subject})

    return render(request, template_name, {'form': form})


@login_required
@teacher_required
def edit_survey(request, opk, npk):
    template_name = 'survey/edit_survey.html'
    survey = get_object_or_404(Survey, pk=npk)
    try:
        o_survey = Survey.objects.filter(pk=opk)
        squestions = SQuestion.objects.filter(survey=o_survey[0]).values()
        print(squestions)
    except IndexError:
        squestions = {}
    if request.method == 'GET':
        formset = SQuestionFormSet(request.GET or None, initial=squestions)
    elif request.method == 'POST':
        formset = SQuestionFormSet(request.POST, initial=squestions)
        if formset.is_valid():
            if opk == npk:
                SQuestion.objects.filter(survey=Survey.objects.filter(pk=opk).first()).delete()
            for form in formset:
                # extract name from each form and save
                text = form.cleaned_data['squestion']
                if text:
                    SQuestion(squestion=text, survey=survey).save()
            return redirect('view-survey', pk=npk)
    return render(request, template_name, {
        'formset': formset,
    })


@login_required
@teacher_required
def view_survey(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    batch_queryset = Batch.objects.filter(survey=survey)
    batches = ""
    for batch in batch_queryset:
        batches += str(batch) + ", "
    batches = batches[:-2]
    questions = SQuestion.objects.filter(survey=survey)
    responses = SurveyResponse.objects.filter(survey=survey).exists()
    user = request.user.teacher
    if responses:
        for question in questions:
            chosen = [0, 0, 0, 0, 0]
            q_responses = SQuestionResponse.objects.filter(squestion=question)
            for q_response in q_responses:
                if q_response.que_response == "1":
                    chosen[0] += 1
                elif q_response.que_response == "2":
                    chosen[1] += 1
                elif q_response.que_response == "3":
                    chosen[2] += 1
                elif q_response.que_response == "4":
                    chosen[3] += 1
                else:
                    chosen[4] += 1
    context = {
        'questions': questions,
        'survey': survey,
        'author': user,
        'batches': batches,
    }
    return render(request, 'survey/view_survey.html', context)


@login_required
@teacher_required
def view_survey_stats(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    batch_queryset = Batch.objects.filter(survey=survey)
    batches = []
    for batch in batch_queryset:
        no_res = str(batch) + ": "
        stu_list = Student.objects.filter(batch=batch)
        print(stu_list)
        for student in stu_list:
            s = SurveyResponse.objects.filter(student=student, survey=survey).first()
            if s is None:
                no_res += str(student.roll_no) + ", "
        batches.append(no_res[:-2])
    context = {
        'batches': batches
    }
    return render(request, 'survey/view_survey_stats.html', context)


@method_decorator([login_required, teacher_required], name='dispatch')
class SurveyDeleteView(UserPassesTestMixin, DeleteView):
    model = Survey
    template_name = 'survey/survey_confirm_delete.html'

    def test_func(self):
        survey = self.get_object()
        if self.request.user.teacher == survey.author:
            return True
        else:
            return False

    def get_success_url(self):
        return reverse_lazy('teacher-home', kwargs={'pk': self.request.user.pk})


@method_decorator([login_required, teacher_required], name='dispatch')
class SurveyUpdateView(UpdateView):
    template_name = 'survey/change_status_survey.html'
    model = Survey
    fields = ['title', 'is_open']

    def __init__(self, *args, **kwargs):
        super(SurveyUpdateView, self).__init__(*args, **kwargs)

    def get_success_url(self):
        survey = self.get_object()
        return reverse_lazy('view-survey', kwargs={'pk': survey.pk})


@login_required
@teacher_required
def generate_excel(request, pk):
    import xlwt
    survey = get_object_or_404(Survey, pk=pk)
    ques = SQuestion.objects.filter(survey=survey)
    responses = SurveyResponse.objects.values_list(
        'student__roll_no',
        'student__student__first_name',
        'student__student__last_name',
        'student__batch__division',
        'student'
    ).filter(survey=survey).order_by('student__roll_no')
    response = HttpResponse(content_type='application/ms-excel')
    file_name = 'Survey ' + '-'.join([str(x) for x in survey.batches.all()])
    print(file_name)
    response['Content-Disposition'] = f'attachment; filename="{file_name}.xls"'
    print(responses)
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet(f'{survey.title}')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Roll No', 'First name', 'Last name', 'Division', 'Student']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    for col_num in range(len(columns), len(ques)+len(columns)):
        ws.write(row_num, col_num, ques[col_num-len(columns)].squestion, font_style)
    ws.write(row_num, len(columns)+len(ques), 'Feedback', font_style)
    row_num += 1
    for i in range(len(responses)):
        for j in range(len(responses[i])):
            ws.write(row_num, j, responses[i][j], font_style)
        for k in range(len(ques)):
            res = SQuestionResponse.objects.filter(squestion=ques[k], survey_response__student=responses[i][-1]).first()
            ws.write(row_num, k+len(responses[0]), res.que_response, font_style)
        feedback = SurveyResponse.objects.filter(survey=survey, student=responses[i][-1]).values('feedback').first()
        ws.write(row_num, len(columns)+len(ques), feedback['feedback'], font_style)
        row_num += 1
    wb.save(response)
    return response
