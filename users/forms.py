from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import Subject, Batch


class TeacherRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), required=True,
                                              widget=forms.CheckboxSelectMultiple)
    batches = forms.ModelMultipleChoiceField(queryset=Batch.objects.all(), required=True,
                                             widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'subjects', 'batches']

    def clean_first_name(self):
        if self.cleaned_data["first_name"].strip() == '':
            raise ValidationError("First name is required.")
        return self.cleaned_data["first_name"]

    def clean_last_name(self):
        if self.cleaned_data["last_name"].strip() == '':
            raise ValidationError("Last name is required.")
        return self.cleaned_data["last_name"]
