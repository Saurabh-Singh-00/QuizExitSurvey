from django import forms
from exit.models import Survey, SurveyResponse, SQuestion
from users.models import Batch, Subject


class SurveyForm(forms.ModelForm):
    title = forms.CharField(max_length=1000)

    class Meta:
        model = Survey
        fields = ['title', 'batches', 'subject', 'is_open']

    def __init__(self, user, *args, **kwargs):
        try:
            hide_condition = kwargs.pop('hide_condition')
            super(SurveyForm, self).__init__(*args, **kwargs)
            self.fields['subject'] = forms.ModelChoiceField(queryset=user.teacher.teacher.subjects,
                                                            required=True, widget=forms.HiddenInput())

        except KeyError:
            super(SurveyForm, self).__init__(*args, **kwargs)
            self.fields['subject'] = forms.ModelChoiceField(queryset=user.teacher.teacher.subjects,
                                                            required=True)
        finally:
            self.fields['batches'] = forms.ModelMultipleChoiceField(
                queryset=Batch.objects.filter(teacher=user.teacher.teacher), required=True,
                widget=forms.CheckboxSelectMultiple)

    def is_valid(self):
        valid = super(SurveyForm, self).is_valid()
        if not valid:
            return valid
        subject = self.cleaned_data['subject']
        for batch in self.cleaned_data['batches']:
            if subject not in Subject.objects.filter(batch=batch):
                self.errors['no_subject'] = 'This subject is not available for Batch: ' + str(batch)
                return False

        return True


class SQuestionForm(forms.Form):
    squestion = forms.CharField(max_length=500, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Enter question here.'
    }))


SQuestionFormSet = forms.formset_factory(SQuestionForm, min_num=1, extra=0)


class TakeSurveyForm(forms.ModelForm):
    class Meta:
        model = SurveyResponse
        exclude = ['student', 'responses', 'survey', 'feedback']

    def __init__(self, survey, *args, **kwargs):
        super(TakeSurveyForm, self).__init__(*args, **kwargs)
        squestions = SQuestion.objects.filter(survey=survey)
        ques_no = 1
        for squestion in squestions:
            choices = (
                ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'))
            field = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect, label=str(ques_no) + ") " + squestion.squestion, required=True)
            self.fields['question_no_%d' % ques_no] = field
            ques_no += 1
        self.fields['survey_feedback'] = forms.CharField(max_length=500, widget=forms.Textarea())
