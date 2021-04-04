# pylint: disable=invalid-name, too-few-public-methods, missing-class-docstring, import-error
"""
Models for working with MongoDB and objects stored in it
"""
from typing import List, Dict, Any

from djongo import models
from django.conf import settings

DEFAULT_AUTHOR_ID = 1
DEFAULT_TEST_ID = 1


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

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'


class Option(models.Model):
    option = models.CharField(max_length=1_000)
    is_true = models.BooleanField()
    num = models.IntegerField(null=True)

    class Meta:
        abstract = True
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответа'


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
    options = models.ArrayField(model_container=Option)
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
