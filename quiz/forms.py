from django import forms
from quiz.models import Quiz, Question, QuizResponse
from users.models import Teacher, Batch, Subject


class QuestionForm(forms.Form):
    question = forms.CharField(max_length=500, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Enter question here.'
    }))
    option_a = forms.CharField(max_length=100)
    option_b = forms.CharField(max_length=100)
    option_c = forms.CharField(max_length=100)
    option_d = forms.CharField(max_length=100)
    options = [
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
    ]
    correct_answer = forms.ChoiceField(choices=options)


QuestionFormSet = forms.formset_factory(QuestionForm, min_num=1, extra=0)


class QuizForm(forms.ModelForm):
    title = forms.CharField(max_length=1000)
    batches = forms.ModelMultipleChoiceField(queryset=Batch.objects.all(), required=True,
                                             widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Quiz
        fields = ['title', 'batches', 'subject']

    def __init__(self, user, *args, **kwargs):
        try:
            hide_condition = kwargs.pop('hide_condition')
            super(QuizForm, self).__init__(*args, **kwargs)
            self.fields['subject'] = forms.ModelChoiceField(queryset=user.teacher.teacher.subjects,
                                                            required=True, widget=forms.HiddenInput())
            print(self.fields['subject'].initial)
        except KeyError:
            super(QuizForm, self).__init__(*args, **kwargs)
            self.fields['subject'] = forms.ModelChoiceField(queryset=user.teacher.teacher.subjects,
                                                            required=True)


class TakeQuizForm(forms.ModelForm):
    class Meta:
        model = QuizResponse
        exclude = ['student', 'responses', 'quiz']

    def __init__(self, quiz, *args, **kwargs):
        super(TakeQuizForm, self).__init__(*args, **kwargs)
        questions = Question.objects.filter(quiz=quiz)
        ques_no = 1
        for question in questions:
            choices = (
                ('a', question.option_a), ('b', question.option_b), ('c', question.option_c), ('d', question.option_d))
            field = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect, label=str(ques_no) + ") " + question.question, required=True)
            self.fields['question_no_%d' % ques_no] = field
            ques_no += 1
