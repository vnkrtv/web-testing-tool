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
        self._db = self._client.data.quizer

    def add_test(self, test) -> None:
        '''
        Add test to db
        :param test: json
            {
                'name': text_field,
                'author_id': int,
                'subject_id': int,
                'description': text_field,
                'tasks_num': int,
                'duration': int
            }
        :return: None
        '''
        date = datetime.now().timetuple()
        test['date'] = {
            'year': date[0],
            'month': date[1],
            'day': date[2],
            'hour': date[3],
            'minutes': date[4]
        }
        if self._db.find_one({'subject_id': test['subject_id']}):
            self._db.find_one_and_update(
                {'subject_id': test['subject_id']},
                {'$push': {'tests': test}}
            )
        else:
            self._db.insert_one({
                'subject_id': test['subject_id'],
                'tests': [test]
            })

    def get_test(self, test_name, subject_id) -> dict:
        return self._db.find_one({'subject_id': subject_id})['tests']

    def delete_test(self, test_name, subject_id) -> None:
        self._db.find_one_and_update(
            {'subject_id': subject_id},
            {'$pull': {'tests': {'test_name': test_name}}}
        )

    def check_domain(self, domain) -> bool:
        """

        :param domain: vk user domain
        :return: True if user exist in db, False else
        """
        if self._db.find_one({'domain': domain}):
            return True
        return False

    def get_fullname(self, domain) -> str:
        """

        :param domain: vk user domain
        :return: str '${first_name} ${last_name}'
        """
        if self.check_domain(domain):
            info = list(self._db.find_one({'domain': domain})['dates'][-1].values())[0]['main_info']
            return info['first_name'] + ' ' + info['last_name']
        else:
            return ''

    def load_user_info(self, id=0, domain='', date='') -> dict:
        """

        :param id: vk user id (if input)
        :param domain: vk user domain (if input)
        :param date: vk user information collected this date (if not input - latest info)
        :return: dict with vk user information
        """
        if id != 0:
            if date:
                info = {}
                for inf in self._db.find_one({'user_id': id})['dates']:
                    for d in inf:
                        if d == date:
                            info = inf[date]
                return info
            else:
                info = self._db.find_one({'user_id': id})
                return list(info['dates'][-1].values())[0]

        elif domain != '':
            if date:
                info = {}
                for inf in self._db.find_one({'domain': domain})['dates']:
                    for d in inf:
                        if d == date:
                            info = inf[date]
                return info
            else:
                info = self._db.find_one({'domain': domain})
                return list(info['dates'][-1].values())[0]

    def get_user_info_dates(self, id=0, domain='') -> list:
        """

        :param id: vk user id
        :param domain: vk user domain
        :return: list of dates when vk user information was collected
        """
        if id != 0:
            dates = [date for date in list(self._db.find_one({'user_id': id})['dates'])]
            return [list(date.keys())[0] for date in dates]
        elif domain != '':
            dates = [date for date in list(self._db.find_one({'domain': domain})['dates'])]
            return [list(date.keys())[0] for date in dates]


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