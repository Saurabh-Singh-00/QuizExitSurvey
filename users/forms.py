from django import forms
from .models import Student
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db import transaction
import re
from .models import Subject, Batch, User, Teacher


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
        return self.cleaned_data["first_name"].capitalize()

    def clean_last_name(self):
        if self.cleaned_data["last_name"].strip() == '':
            raise ValidationError("Last name is required.")
        return self.cleaned_data["last_name"].capitalize()

    def clean_email(self):
        if "@ternaengg.ac.in" not in self.cleaned_data['email']:
            raise ValidationError("Please use the email provided by the college")
        return self.cleaned_data["email"]

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = True
        if commit:
            user.save()
            teacher = Teacher.objects.create(teacher=user)
            teacher.batches.set(self.cleaned_data.get('batches'))
            teacher.subjects.set(self.cleaned_data.get('subjects'))
        return user


class StudentRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    batch = forms.ModelChoiceField(queryset=Batch.objects.all(), required=True, )
    roll_no = forms.IntegerField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'batch', 'roll_no']

    def clean_first_name(self):
        if self.cleaned_data["first_name"].strip() == '':
            raise ValidationError("First name is required.")
        return self.cleaned_data["first_name"].capitalize()

    def clean_last_name(self):
        if self.cleaned_data["last_name"].strip() == '':
            raise ValidationError("Last name is required.")
        return self.cleaned_data["last_name"].capitalize()

    def clean_username(self):
        username = self.cleaned_data['username'].upper()
        if username.strip() == '':
            raise ValidationError("username is required.")
        regex = re.compile(r"TUS?\d(F|S|SF)[12]\d[12]\d{3,4}")
        if regex.search(username):
            return username
        else:
            raise ValidationError("username should be your ID")

    def clean_roll_no(self):
        curr_roll = self.cleaned_data['roll_no']
        s = Student.objects.filter(roll_no=curr_roll).first()
        batch = self.cleaned_data['batch']
        try:
            if s.batch == batch:
                raise ValidationError("This roll number is currently assigned to " + str(s))
        except AttributeError:
            return curr_roll

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = False
        if commit:
            user.save()
            Student.objects.create(student=user, batch=self.cleaned_data.get('batch'),
                                             roll_no=self.cleaned_data.get('roll_no'))
        return user


class TeacherUpdateForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), required=True,
                                              widget=forms.CheckboxSelectMultiple)
    batches = forms.ModelMultipleChoiceField(queryset=Batch.objects.all(), required=True,
                                             widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Teacher
        exclude = ['teacher']

    def __init__(self, *args, **kwargs):
        super(TeacherUpdateForm, self).__init__(*args, **kwargs)
        self.fields["subjects"].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields["subjects"].help_text = ""
        self.fields["subjects"].queryset = Subject.objects.all()
        self.fields["batches"].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields["batches"].help_text = ""
        self.fields["batches"].queryset = Batch.objects.filter()


class StudentUpdateForm(forms.ModelForm):
    batch = forms.ModelChoiceField(queryset=Batch.objects.all(), required=True)
    roll_no = forms.IntegerField(required=True)

    class Meta:
        model = Student
        exclude = ['student']
