import time
from datetime import datetime
from django.db import models
from django.conf import settings
from pymongo import MongoClient


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
        question['test_id'] = test_id
        db.insert_one(question)

    def get_questions(self, test_id) -> list:
        """

        :param test_id: int
        :return: list
        """
        db = self._client.data.questions
        questions = db.find({
            'test_id': test_id
        })
        return [question for question in questions] if questions else []

    def drop_question(self, question_formulation) -> None:
        db = self._client.data.questions
        db.delete_one({'formulation': question_formulation})

    def add_running_test_answers(self, user_id, test_id, right_answers):
        db = self._client.data.running_tests_answers
        db.insert_one({
            'test_id': test_id,
            'user_id': user_id,
            'right_answers': right_answers
        })

    def get_running_test_answers(self, user_id):
        db = self._client.data.running_tests_answers
        return db.find_one({
            'user_id': user_id,
        })

    def drop_running_test_answers(self, user_id):
        db = self._client.data.running_tests_answers
        db.delete_one({
            'user_id': user_id,
        })

    def add_test_result(self, test_result, test_id):
        db = self._client.data.tests_results
        db.find_one_and_update(
            {'test_id': test_id},
            {'$push': {'results': test_result}}
        )

    def get_active_test_results(self, test_id, lectorer_id):
        db = self._client.data.tests_results
        test_results = db.find_one(
            {'test_id': test_id, 'launched_lectorer_id': lectorer_id, 'active': True},
        )
        return test_results['results'] if test_results else []

    def run_test(self, test_id, lectorer_id):
        db = self._client.data.tests_results
        date = datetime.now().timetuple()
        db.insert_one({
            'test_id': test_id,
            'launched_lectorer_id': lectorer_id,
            'active': True,
            'results': [],
            'timestamp': time.time(),
            'time': {
                'year': date[0],
                'month': date[1],
                'day': date[2],
                'hour': date[3],
                'minutes': date[4]
            }
        })

    def get_running_tests(self):
        db = self._client.data.tests_results
        running_tests = db.find({'active': True})
        return [test['test_id'] for test in running_tests] if running_tests else []

    def stop_test(self, test_id, lectorer_id):
        self._client.data.tests_results.find_one_and_update(
            {'test_id': test_id, 'launched_lectorer_id': lectorer_id, 'active': True},
            {'$set': {'active': False}}
        )

    def get_test_results(self, test_id, lectorer_id):
        db = self._client.data.tests_results
        test_results = db.find({
            'test_id': test_id,
            'launched_lectorer_id': lectorer_id
        })
        if test_results:
            test_results = [test_result for test_result in test_results]
            latest_test_results = max(test_results, key=lambda res: res['timestamp'])
            return latest_test_results['results']
        return []
