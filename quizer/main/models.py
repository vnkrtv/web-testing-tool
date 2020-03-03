from django.db import models
from djongo.models import ListField, EmbeddedField


class Option(models.Model):
    option = models.CharField('Вариант ответа', max_length=200)
    is_true = models.BooleanField('Верный')

    def __str__(self):
        return self.option

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответа'


class Test(models.Model):
    test_theme = models.CharField('Тема теста', max_length=200)
    #tasks = ListField(EmbeddedField('Task'), default={})

    def __str__(self):
        return self.test_theme

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'


class Task(models.Model):
    task = models.ForeignKey(Test, name='Тест', on_delete=models.CASCADE)
    question = models.TextField('Формулировка вопроса', max_length=200)
    options_1 = EmbeddedField(Option, name='Вариант 1', default={})
    options_2 = EmbeddedField(Option, name='Вариант 2', default={})
    options_3 = EmbeddedField(Option, name='Вариант 3', default={})
    options_4 = EmbeddedField(Option, name='Вариант 4', default={})

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'