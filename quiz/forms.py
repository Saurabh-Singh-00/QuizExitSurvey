from django import forms
from quiz.models import Quiz, Question
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


QuestionFormSet = forms.formset_factory(QuestionForm, extra=5)


class QuizForm(forms.ModelForm):
    title = forms.CharField(max_length=1000)
    batches = forms.ModelMultipleChoiceField(queryset=Batch.objects.all(), required=True,
                                             widget=forms.CheckboxSelectMultiple)
    subject = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), required=True,
                                             widget=forms.CheckboxSelectMultiple)
    author = 1

    class Meta:
        model = Quiz
        fields = ['title', 'batches', 'author', 'subject']
