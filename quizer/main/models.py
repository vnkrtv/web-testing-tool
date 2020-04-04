# pylint: disable=invalid-name, too-few-public-methods, missing-class-docstring, import-error
"""
Models and classes for working with MongoDB and objects stored in it
"""
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


class MongoDB:
    """
    Class for getting connection to MongoDB

    _client: MongoClient() object
    _db: MongoDB database
    _col: MongoDB collection
    """

    _client = None
    _db = None
    _col = None

    @staticmethod
    def get_connection(host: str, port, db_name: str, collection_name: str) -> tuple:
        """
        Establish connection to mongodb database 'db_name', collection 'questions'

        :param host: MongoDB host
        :param port: MongoDB port
        :param db_name: database name
        :param collection_name: collection name
        :return: tuple of (MongoClient, db, collection)
        """
        client = MongoClient(host, port)
        db = client[db_name]
        col = db[collection_name]
        return client, db, col


class QuestionsStorage(MongoDB):
    """
    Class for working with Questions, stored in MongoDB
    """

    @staticmethod
    def connect_to_mongodb(host: str, port, db_name: str):
        """
        Establish connection to mongodb database 'db_name', collection 'questions'

        :param host: MongoDB host
        :param port: MongoDB port
        :param db_name: MongoDB name
        :return: QuestionStorage object
        """
        obj = QuestionsStorage()
        obj._client, obj._db, obj._col = MongoDB.get_connection(
            host=host,
            port=port,
            db_name=db_name,
            collection_name='questions'
        )
        return obj

    def add_one(self, question, test_id: int) -> None:
        """
        Add question to MongoDB

        :param question: <dict>
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
        :param test_id: <int>
        :return: None
        """
        question['test_id'] = test_id
        self._col.insert_one(question)

    def get_many(self, test_id: int) -> list:
        """
        Get all questions for Test(id='test_id')

        :param test_id: <int>
        :return: <list>, list of questions
        """
        questions = self._col.find({
            'test_id': test_id
        })
        return list(questions) if questions else []

    def delete_one(self, question_formulation: str, test_id: int) -> None:
        """
        Delete question with formulation 'question_formulation' and 'test_id' test_id

        :param question_formulation: <str>
        :param test_id: <int>
        :return: None
        """
        self._col.delete_one({
            'test_id': test_id,
            'formulation': question_formulation
        })


class RunningTestsAnswersStorage(MongoDB):
    """
    Class for working with answers for running tests, stored in MongoDB
    """

    @staticmethod
    def connect_to_mongodb(host, port, db_name):
        """
        Establish connection to mongodb database 'db_name', collection 'running_tests_answers'

        :param host: MongoDB host
        :param port: MongoDB port
        :param db_name: MongoDB name
        :return: RunningTestAnswersStorage object
        """
        obj = RunningTestsAnswersStorage()
        obj._client, obj._db, obj._col = MongoDB.get_connection(
            host=host,
            port=port,
            db_name=db_name,
            collection_name='running_tests_answers'
        )
        return obj

    def add(self, right_answers, test_id: str, user_id: str) -> None:
        """
        Add right answers for running tests and current user

        :param right_answers: <dict>
            {
                'question_number_1': {
                    'right_answers': [1, 2 ... <list: int>],
                    'id': str(ObjectId()),
                'question_number_2': {
                    ...
                },
                ...
            }
        :param test_id: <int>
        :param user_id: <int>, user who passes test
        :return:
        """
        self._col.insert_one({
            'right_answers': right_answers,
            'test_id': test_id,
            'user_id': user_id
        })

    def get(self, user_id: int) -> dict:
        """
        Get right answers for running test and current user

        :param user_id: <int>, user who passes test
        :return: <dict>
        """
        right_answers = self._col.find_one({
            'user_id': user_id,
        })
        return right_answers

    def delete(self, user_id: int) -> None:
        """
        Delete user answers for running test

        :param user_id: <int>
        :return: None
        """
        self._col.delete_one({
            'user_id': user_id,
        })


class TestsResultsStorage(MongoDB):
    """
    Class for working with tests results, stored in MongoDB
    """

    @staticmethod
    def connect_to_mongodb(host, port, db_name):
        """
        Establish connection to mongodb database 'db_name', collection 'tests_results'

        :param host: MongoDB host
        :param port: MongoDB port
        :param db_name: MongoDB name
        :return: TestsResultsStorage object
        """
        obj = TestsResultsStorage()
        obj._client, obj._db, obj._col = MongoDB.get_connection(
            host=host,
            port=port,
            db_name=db_name,
            collection_name='tests_results'
        )
        return obj

    def add_running_test(self, test_id: int, lecturer_id: int):
        """
        Create object in collection corresponding to running test

        :param test_id: <int>
        :param lecturer_id: <int>, lecturer who ran test
        :return:
        """
        date = datetime.now().timetuple()
        self._col.insert_one({
            'test_id': test_id,
            'launched_lecturer_id': lecturer_id,
            'is_running': True,
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

    def add_results_to_running_test(self, test_result, test_id: int) -> None:
        """
        Add passed test result to other results for running test

        :param test_result: <dict>
            {
                'user_id': <int>,
                'username': <str>,
                'time': <int>, time of passing test,
                'tasks_num': <int>, number of questions,
                'right_answers_num': <int>, number of correctly solved questions,
                'questions': [
                    {
                        'id': <str>, str(ObjectId()),
                        'selected_answers': <list: int>,
                        'right_answers': <list: int>
                    },
                    ...
                ]
            }
        :param test_id: <int>
        :return: None
        """
        self._col.find_one_and_update(
            {'test_id': test_id, 'is_running': True},
            {'$push': {'results': test_result}}
        )

    def get_running_test_results(self, test_id: int, lecturer_id: int) -> list:
        """
        Get results of running test

        :param test_id: <int>
        :param lecturer_id: <int>, lecturer who ran test
        :return: <list>, list of results
        """
        test_results = self._col.find_one(
            {'test_id': test_id, 'launched_lecturer_id': lecturer_id, 'is_running': True},
        )
        return test_results['results'] if test_results else []

    def get_running_tests_ids(self) -> list:
        """
        Return list of running tests ids

        :return: <list: int>
        """
        running_tests = self._col.find({'is_running': True})
        return [test['test_id'] for test in running_tests] if running_tests else []

    def stop_running_test(self, test_id: int, lecturer_id: int) -> None:
        """
        Stops running test, setting its 'is_running' field to 'False'

        :param test_id: <int>
        :param lecturer_id: <int>, lecturer who ran test
        :return: None
        """
        self._col.find_one_and_update(
            {'test_id': test_id, 'launched_lecturer_id': lecturer_id, 'is_running': True},
            {'$set': {'is_running': False}}
        )

    def get_latest_test_results(self, test_id: int, lecturer_id: int) -> list:
        """
        Get results of latest test

        :param test_id: <int>
        :param lecturer_id: <int>, lecturer who ran test
        :return: <list>, list of results
        """
        test_results = self._col.find({
            'test_id': test_id,
            'launched_lecturer_id': lecturer_id
        })
        if test_results:
            test_results = list(test_results)
            latest_test_results = max(test_results, key=lambda res: res['timestamp'])
            return latest_test_results['results']
        return []
