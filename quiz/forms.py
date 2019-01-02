from django import forms
from quiz.models import Quiz, Question, QuizResponse
from users.models import Teacher, Batch, Subject


class QuestionForm(forms.Form):
    question = forms.CharField(max_length=500, widget=forms.Textarea)
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
    correct_ans = forms.ChoiceField(choices=options)


QuestionFormSet = forms.formset_factory(QuestionForm, extra=3)


class QuizForm(forms.ModelForm):
    title = forms.CharField(max_length=1000)
    batches = forms.ModelMultipleChoiceField(queryset=Batch.objects.all(), required=True,
                                             widget=forms.CheckboxSelectMultiple)
    subject = forms.ModelChoiceField(queryset=Subject.objects.none(), required=True)

    class Meta:
        model = Quiz
        fields = ['title', 'batches', 'subject']
        # exclude = ['author']

    def __init__(self, user, *args, **kwargs):
        super(QuizForm, self).__init__(*args, **kwargs)
        author = user.teacher.teacher
        subjects = author.subjects
        self.fields['subject'].queryset = subjects


class TakeQuizForm(forms.Form):
    def __init__(self, quiz, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
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
