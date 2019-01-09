from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import transaction
from django.http import HttpResponse
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
from users.models import Batch


@login_required
@student_required
def attempt_survey(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    squestions = SQuestion.objects.filter(survey=survey)
    student = request.user.student

    if SurveyResponse.objects.filter(survey=survey, student=student).exists():
        survey_response = SurveyResponse.objects.filter(survey=survey, student=student).first()
        return redirect('view-survey-response', pk=survey_response.pk)

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
    pisaStatus = pisa.CreatePDF(
        html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisaStatus.err:
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
    # responses = QuizResponse.objects.filter(survey=survey).exists()
    user = request.user.teacher
    context = {
        'questions': questions,
        'survey': survey,
        'author': user,
        'batches': batches,
        # 'responses': responses
    }
    return render(request, 'survey/view_survey.html', context)


@method_decorator([login_required, teacher_required], name='dispatch')
class SurveyDeleteView(UserPassesTestMixin, DeleteView):
    model = Survey
    template_name = 'quiz/quiz_confirm_delete.html'

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
    template_name = 'quiz/change_status.html'
    model = Survey
    fields = ['title', 'is_open']

    def __init__(self, *args, **kwargs):
        super(SurveyUpdateView, self).__init__(*args, **kwargs)

    def get_success_url(self):
        survey = self.get_object()
        return reverse_lazy('view-quiz', kwargs={'pk': survey.pk})
