from django.db import models
from django.conf import settings
from pymongo import MongoClient
from datetime import datetime

DEFAULT_AUTHOR_ID = 1


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


class Test(models.Model):
    subject = models.ForeignKey(
        Subject,
        verbose_name='Предмет',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Составитель',
        on_delete=models.CASCADE,
        default=DEFAULT_AUTHOR_ID
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


class MongoDB(object):

    def __init__(self, host='localhost', port=27017, **kwargs):
        self._client = MongoClient(host, port, **kwargs)

    def add_test(self, test) -> None:
        """
        Add test to db
        :param test: json
            {
                'name': str,
                'author_id': int,
                'description': str,
                'tasks_num': int,
                'duration': int
            }
        :return: None
        """
        db = self._client.data.tests
        if db.find_one({'subject_id': test['subject_id']}):
            db.find_one_and_update(
                {'subject_id': test['subject_id']},
                {'$push': {'tests': test}}
            )
        else:
            db.insert_one({
                'subject_id': test['subject_id'],
                'tests': [test]
            })

    def get_tests(self, subject_id) -> dict:
        db = self._client.data.tests
        return db.find_one({'subject_id': subject_id})['tests']

    def delete_test(self, test_name, subject_id) -> None:
        db = self._client.data.tests
        db.find_one_and_update(
            {'subject_id': subject_id},
            {'$pull': {'tests': {'test_name': test_name}}}
        )

    def add_question(self, question, test_id) -> None:
        """
        Add question to db
        :param question: json
            {
                'formulation': str,
                'tasks_num': int,
                'multiselect': bool,
                'with_images': bool,
                'options': [
                    {
                        'option': str,
                        'is_true': bool
                    },
                    ...
                ]
            }
        :param test_id: int
        :return: None
        """
        db = self._client.data.questions
        if db.find_one({'test_id': test_id}):
            db.find_one_and_update(
                {'test_id': test_id},
                {'$push': {
                    'questions': question
                }})
        else:
            db.insert_one({
                'test_id': test_id,
                'questions': [question]
            })

    def get_questions(self, test_id) -> list:
        """

        :param test_id: int
        :return: list
        """
        db = self._client.data.questions
        test = db.find_one({
                'test_id': test_id
            })
        return test['questions'] if test else []

    def drop_question(self, test_id, question_formulation) -> None:
        db = self._client.data.questions
        db.find_one_and_update(
            {'test_id': test_id},
            {'$pull': {'questions': {'formulation': question_formulation}}}
        )

    def add_running_test(self, user_id, test_id, right_answers):
        db = self._client.data.running_tests
        db.insert_one({
            'test_id': test_id,
            'user_id': user_id,
            'right_answers': right_answers
        })

    def get_running_test(self, user_id):
        db = self._client.data.running_tests
        return db.find_one({
            'user_id': user_id,
        })

    def get_running_tests(self, test_id):
        db = self._client.data.running_tests
        return [test for test in db.find({
            'test_id': test_id,
        })]

    def drop_running_test(self, user_id):
        db = self._client.data.running_tests
        db.delete_one({
            'user_id': user_id,
        })

    def add_test_result(self, ):
        pass



'''
from djongo.models import ArrayField, EmbeddedField
from djongo.models import ListField
from django.contrib.auth.models import User


class LectureUser(AbstractUser):
    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'


class StudentUser(AbstractUser):
    class Meta:
        verbose_name = 'Слушатель'
        verbose_name_plural = 'Слушатели'


class Option(models.Model):
    option = models.CharField('Вариант ответа', max_length=200)
    is_true = models.BooleanField('Верный')

    def __str__(self):
        return self.option

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответа'


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
'''