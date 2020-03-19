from django.db import models
from djongo.models import ArrayField, EmbeddedField
from djongo.models import ListField
from django.conf import settings
from django.contrib.auth.models import User


'''
class LectureUser(AbstractUser):
    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'


class StudentUser(AbstractUser):
    class Meta:
        verbose_name = 'Слушатель'
        verbose_name_plural = 'Слушатели'
'''


class Subject(models.Model):
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Преподаватель',
        on_delete=models.CASCADE
    )
    name = models.CharField('Название дисциплины', max_length=50)
    description = models.TextField('Описание дисциплины', default="")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Дисциплина'
        verbose_name_plural = 'Дисциплины'


class Option(models.Model):
    option = models.CharField('Вариант ответа', max_length=200)
    is_true = models.BooleanField('Верный')

    def __str__(self):
        return self.option

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответа'


class Test(models.Model):
    subject = models.ForeignKey(
        Subject,
        verbose_name='Предмет',
        on_delete=models.CASCADE
    )
    name = models.CharField('Тема теста', max_length=200)
    description = models.TextField('Описание теста', default="")
    tasks_num = models.IntegerField('Количество заданий в тесте', default=0)
    duration = models.IntegerField('Длительность теста в секундах', default=300)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'


class Task(models.Model):
    test = models.ForeignKey(
        Test,
        verbose_name='Тест',
        on_delete=models.CASCADE
    )
    question = models.CharField('Формулировка вопроса', max_length=200)
    options_1 = EmbeddedField(Option, verbose_name='Вариант 1', default={})
    options_2 = EmbeddedField(Option, verbose_name='Вариант 2', default={})
    options_3 = EmbeddedField(Option, verbose_name='Вариант 3', default={})
    options_4 = EmbeddedField(Option, verbose_name='Вариант 4', default={})

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class TaskAnswer(models.Field):
    task_id = models.IntegerField('Идентификатор задания')
    true_answer = models.IntegerField('Правильный ответ')
    selected_answer = models.IntegerField('Выбранный ответ')


class TestResult(models.Model):
    username = models.ForeignKey(
        User,# settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    test = models.ForeignKey(
        Test,
        verbose_name='Тест',
        on_delete=models.CASCADE
    )
    #answers = ListField(
    #    verbose_name='Вопросы теста',
    #    default=[]
    #)

    result = models.IntegerField('Число правильных ответов')

    def __str__(self):
        return 'Тест по теме %s\nСлушатель: %s\nРезультат: %d/%d' % \
               (self.test, self.username, self.result, self.test.tasks_num)

    class Meta:
        verbose_name = 'Результат теста'
        verbose_name_plural = 'Результаты теста'
