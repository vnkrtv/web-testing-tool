# pylint: disable=invalid-name, too-few-public-methods, missing-class-docstring, import-error
"""
Models for working with MongoDB and objects stored in it
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta

from djongo import models
from django.conf import settings

DEFAULT_AUTHOR_ID = 1
DEFAULT_TEST_ID = 0
TZ_TIMEDELTA = timedelta(hours=3)


class Subject(models.Model):
    name = models.CharField('Название дисциплины', max_length=50)
    description = models.TextField('Описание дисциплины', default="")
    objects = models.DjongoManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Дисциплина'
        verbose_name_plural = 'Дисциплины'


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
    objects = models.DjongoManager()

    def to_dict(self) -> Dict[str, Any]:
        """
        Test model representation as dictionary

        :return: <dict>
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'tasks_num': self.tasks_num,
            'duration': self.duration,
            'subject': {
                'id': self.subject.id,
                'name': self.subject.name
            },
            'author': {
                'id': self.author.id,
                'username': self.author.username
            }
        }

    @classmethod
    def get_all(cls) -> List[Dict[str, Any]]:
        return [test.to_dict() for test in Test.objects.all()]

    @classmethod
    def get_running_tests(cls) -> List[Dict[str, Any]]:
        return [
            {
                **res.test.to_dict(),
                'questions_num': res.test.questions.count(),
                'launched_lecturer': {
                    'id': res.launched_lecturer.id,
                    'username': res.launched_lecturer.username
                }
            } for res in TestResult.objects.filter(is_running=True)
        ]

    @classmethod
    def get_not_running_tests(cls) -> List[Dict[str, Any]]:
        return [
            {
                **test.to_dict(),
                'questions_num': test.questions.count()
            } for test in Test.objects.all()
            if test.id not in [_['id'] for _ in cls.get_running_tests()]
        ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'


class QuestionOption(models.Model):
    option = models.CharField(max_length=1_000)
    is_true = models.BooleanField()
    num = models.IntegerField(null=True)

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

    @classmethod
    def from_dict(cls, question_dict: Dict[str, Any], test_id: int):
        return cls(
            formulation=question_dict['formulation'],
            multiselect=question_dict['multiselect'],
            tasks_num=question_dict['tasks_num'],
            type=question_dict['type'],
            test=Test.objects.get(id=test_id),
            options=cls.parse_options(question_dict['options']))

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
    question_id = models.ObjectIdField()
    question_num = models.IntegerField()
    right_options = models.ArrayField(model_container=QuestionOption)

    class Meta:
        abstract = True


class RunningTestsAnswers(models.Model):
    _id = models.ObjectIdField()
    test_duration = models.IntegerField('Длительность теста')
    start_date = models.DateTimeField('Время запуска теста')
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
    right_answers = models.EmbeddedField(model_container=QuestionRightAnswer)
    objects = models.DjongoManager()

    @property
    def time_left(self) -> float:
        delta = datetime.now() - self.start_date.scheduled_at.date() + TZ_TIMEDELTA
        return self.test_duration - delta.total_seconds()

    class Meta:
        db_table = 'running_tests_answers'
        verbose_name = 'Ответы за запущенные тесты'
        verbose_name_plural = 'Ответы за запущенные тесты'


class Option(models.Model):
    option = models.CharField(max_length=1_000)

    class Meta:
        abstract = True


class UserQuestionAnswer(models.Model):
    id = models.ObjectIdField()
    selected_answers = models.JSONField()
    right_answers = models.JSONField()
    is_true = models.BooleanField(default=False)

    # selected_answers = models.ArrayField(model_container=Option)
    # right_answers = models.ArrayField(model_container=Option)

    class Meta:
        abstract = True


class UserResult(models.Model):
    user_id = models.IntegerField()
    username = models.CharField(max_length=50)
    time = models.IntegerField()
    tasks_num = models.IntegerField()
    right_answers_count = models.IntegerField()
    date = models.DateTimeField()
    questions = models.ArrayField(model_container=UserQuestionAnswer)

    class Meta:
        abstract = True


class TestResult(models.Model):
    _id = models.ObjectIdField()
    is_running = models.BooleanField('Тест еще запущен')
    comment = models.TextField('Комментарий преподавателя', default='')
    date = models.DateTimeField('Время запуска тестирования',
                                default=lambda: datetime.now() + TZ_TIMEDELTA)
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
    results = models.ArrayField(model_container=UserResult)
    objects = models.DjongoManager()

    class Meta:
        db_table = 'tests_results'
        verbose_name = 'Результат тестирования'
        verbose_name_plural = 'Результаты тестирований'
