# pylint: disable=too-few-public-methods, no-member, missing-function-docstring, missing-class-docstring, line-too-long
"""
App models' forms:
- BaseForm - set 'form-control' class for all fields
- SubjectForm
- TestForm
"""
from django import forms
from .models import Subject


class BaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class UserForm(BaseForm):
    fullname = forms.CharField(label='Полное имя с gitlab', required=False)
    username = forms.CharField(label='Имя', required=True)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput, required=False)


class SubjectForm(BaseForm):
    name = forms.CharField(label='Название предмета', max_length=100)
    description = forms.CharField(label='Описание', widget=forms.Textarea, required=False)


class TestForm(BaseForm):
    subject = forms.ModelChoiceField(label='Предмет', queryset=Subject.objects.all(), empty_label=None)
    name = forms.CharField(label='Название теста')
    description = forms.CharField(label='Описание', widget=forms.Textarea, required=False)
    tasks_num = forms.IntegerField(label='Количество заданий', min_value=1)
    duration = forms.IntegerField(label='Длительность теста в секундах', min_value=1)
