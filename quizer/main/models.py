# pylint: disable=invalid-name, too-few-public-methods, missing-class-docstring, import-error
"""
Models for working with MongoDB and objects stored in it
"""
from typing import List, Dict, Any
from datetime import datetime, timezone

from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.conf import settings
from django.utils import timezone
from djongo import models

DEFAULT_AUTHOR_ID = 0
DEFAULT_TEST_ID = 0
TZ_TIMEDELTA = timezone.now() - datetime.now(timezone.utc)


class Profile(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=30, default='')
    web_url = models.URLField(default='')
    group = models.IntegerField(default=0)
    admission_year = models.IntegerField(default=0)
    number = models.IntegerField(default=0)
    objects = models.DjongoManager()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(id=instance.id, user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Subject(models.Model):
    name = models.CharField('Название дисциплины', max_length=50)
    description = models.TextField('Описание дисциплины', default="")
    objects = models.DjongoManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Дисциплина'
        verbose_name_plural = 'Дисциплины'


class TestManager(models.DjongoManager):

    def get_running(self):
        return super().get_queryset().filter(testing_results__is_running=True)

    def get_not_running(self):
        running_test_ids = [test.id for test in self.get_running()]
        return super().get_queryset().exclude(id__in=running_test_ids)


class Test(models.Model):
    subject = models.ForeignKey(
        Subject,
        verbose_name='Предмет',
        related_name='tests',
        on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Составитель',
        related_name='tests',
        on_delete=models.CASCADE,
        default=DEFAULT_AUTHOR_ID)
    name = models.CharField('Тема теста', max_length=200)
    description = models.TextField('Описание теста', default="")
    tasks_num = models.IntegerField('Количество заданий в тесте', default=0)
    duration = models.IntegerField('Длительность теста в секундах', default=300)
    objects = TestManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'


class QuestionOption(models.Model):
    option = models.CharField(max_length=1_000)
    is_true = models.BooleanField()
    num = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class Question(models.Model):
    _id = models.ObjectIdField()
    formulation = models.CharField('Формулировка вопроса', max_length=1_000)
    multiselect = models.BooleanField('Вопрос с мультивыбором')
    tasks_num = models.IntegerField('Число вариантов ответа')
    test = models.ForeignKey(
        Test,
        verbose_name='Тест',
        related_name='questions',
        on_delete=models.CASCADE,
        default=DEFAULT_TEST_ID)
    options = models.ArrayField(model_container=QuestionOption)
    type = models.CharField('Тип вопроса', max_length=50)
    objects = models.DjongoManager()

    @property
    def object_id(self):
        return self._id

    @classmethod
    def parse_options(cls, options: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                'option': option['option'],
                'is_true': option['is_true'],
                'num': option.get('num')
            } for option in options
        ]

    class Type:
        """
        Class for storing various questions types
        """
        REGULAR = ''
        WITH_IMAGES = 'image'
        SEQUENCE = 'sequence'
        SEQUENCE_WITH_IMAGES = 'sequence-image'

    class Meta:
        db_table = 'questions'
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class QuestionRightAnswer(models.Model):
    question_num = models.IntegerField()
    question_id = models.CharField()
    right_options = models.JSONField()

    class Meta:
        abstract = True


class RunningTestsAnswers(models.Model):
    _id = models.ObjectIdField()
    test_duration = models.IntegerField('Длительность теста')
    start_date = models.DateTimeField('Время запуска теста', default=timezone.now)
    test = models.ForeignKey(
        Test,
        null=True,
        verbose_name='Запущенный тест',
        related_name='right_answers',
        on_delete=models.SET_NULL,
        default=DEFAULT_TEST_ID)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        verbose_name='Пользователь, проходящий тест',
        related_name='right_answers',
        on_delete=models.SET_NULL,
        default=DEFAULT_AUTHOR_ID)
    right_answers = models.ArrayField(model_container=QuestionRightAnswer)
    objects = models.DjongoManager()

    @property
    def time_left(self) -> float:
        delta = timezone.now() - self.start_date
        return self.test_duration - delta.total_seconds()

    class Meta:
        db_table = 'main_running_tests_answers'
        verbose_name = 'Ответы за запущенные тесты'
        verbose_name_plural = 'Ответы за запущенные тесты'


class TestResult(models.Model):
    _id = models.ObjectIdField()
    id = models.IntegerField(unique=True)
    is_running = models.BooleanField('Тест еще запущен')
    comment = models.TextField('Комментарий преподавателя', default='')
    date = models.DateTimeField('Время запуска тестирования', default=timezone.now)
    launched_lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        verbose_name='Пользователь, запустивный тест',
        related_name='testing_results',
        on_delete=models.SET_NULL)
    test = models.ForeignKey(
        Test,
        null=True,
        verbose_name='Тест',
        related_name='testing_results',
        on_delete=models.SET_NULL)
    subject = models.ForeignKey(
        Subject,
        null=True,
        verbose_name='Предмет',
        related_name='testing_results',
        on_delete=models.SET_NULL)
    objects = models.DjongoManager()

    @property
    def object_id(self):
        return self._id

    class Meta:
        db_table = 'main_tests_results'
        verbose_name = 'Результат тестирования'
        verbose_name_plural = 'Результаты тестирований'


# class UserQuestionAnswer(models.Model):
#     question_id = models.CharField()
#     is_true = models.BooleanField(default=False)
#     selected_options = models.JSONField()
#     right_options = models.JSONField()
#
#     class Meta:
#         abstract = True


class UserResult(models.Model):
    _id = models.ObjectIdField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        verbose_name='Прошедший тестирование',
        related_name='results',
        on_delete=models.SET_NULL)
    testing_result = models.ForeignKey(
        TestResult,
        null=True,
        verbose_name='Результаты тестирования',
        related_name='results',
        on_delete=models.SET_NULL)
    time = models.IntegerField('Продолжительность тестирования')
    tasks_num = models.IntegerField('Число заданий в тесте')
    right_answers_count = models.IntegerField('Число правильных ответов')
    date = models.DateTimeField('Время прохождения тестирования', default=timezone.now)
    questions = models.JSONField()
    objects = models.DjongoManager()

    class Meta:
        db_table = 'main_user_results'
        verbose_name = 'Персональный результат тестирования'
        verbose_name_plural = 'Персональные результаты тестирований'
