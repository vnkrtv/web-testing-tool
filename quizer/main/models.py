# pylint: disable=invalid-name, too-few-public-methods, missing-class-docstring, import-error
"""
Models for working with MongoDB and objects stored in it
"""
from django.db import models
from django.conf import settings


DEFAULT_AUTHOR_ID = 1


class Subject(models.Model):
    name = models.CharField('Название дисциплины', max_length=50)
    description = models.TextField('Описание дисциплины', default="")

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

    def to_dict(self) -> dict:
        """
        Test model representation as dictionary

        :return: <dict>
        """
        d = {
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
        return d

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'


class QuestionType:
    """
    Class for storing various questions types
    """
    REGULAR = ''
    WITH_IMAGES = 'image'
    SEQUENCE = 'sequence'
    SEQUENCE_WITH_IMAGES = 'sequence-image'
