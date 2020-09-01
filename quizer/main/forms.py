# pylint: disable=too-few-public-methods, no-member, missing-function-docstring, missing-class-docstring
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


class SubjectForm(BaseForm):
    name = forms.CharField(label='Название предмета', max_length=100, required=True)
    description = forms.CharField(label='Описание', widget=forms.Textarea)


class TestForm(BaseForm):
    subject = forms.ModelChoiceField(label='Автор', queryset=Subject.objects.all())
    name = forms.CharField(label='Название теста', required=True)
    description = forms.CharField(label='Описание', widget=forms.Textarea)
    tasks_num = forms.IntegerField(label='Количество заданий', min_value=1)
    duration = forms.IntegerField(label='Длительность теста в секундах', min_value=1)
