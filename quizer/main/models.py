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


class MongoObjectStorage(object):
    """
    Class for working with objects, stored in MongoDB

    _client: MongoClient() object
    _db: MongoDB database
    _col: MongoDB collection
    """

    _client = None
    _db = None
    _col = None

    @staticmethod
    def get_connection(host, port, db_name, collection_name):
        """
        Establish connection to mongodb database 'db_name', collection 'questions'

        :param host: MongoDB host
        :param port: MongoDB port
        :param db_name: database name
        :param collection_name: collection name
        :return: MongoObjectStorage object
        """
        obj = MongoObjectStorage()
        obj._client = MongoClient(host, port)
        obj._db = obj._client[db_name]
        obj._col = obj._db[collection_name]
        return obj


class QuestionStorage(MongoObjectStorage):
    """
    Class for working with Questions, stored in MongoDB
    """

    @staticmethod
    def connect_to_mongodb(host, port, db_name):
        """
        Establish connection to mongodb database 'db_name', collection 'questions'

        :param host: MongoDB host
        :param port: MongoDB port
        :param db_name: MongoDB name
        :return: QuestionStorage object
        """
        obj = MongoObjectStorage.get_connection(
            host=host,
            port=port,
            db_name=db_name,
            collection_name='questions'
        )
        return obj

    def add_one(self, question, test_id: int) -> None:
        """
        Add question to MongoDB

        :param question: dict
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
        question['test_id'] = test_id
        self._col.insert_one(question)

    def get_many(self, test_id: int) -> list:
        """
        Get all questions for Test(id='test_id')

        :param test_id: int
        :return: list of questions
        """
        questions = self._col.find({
            'test_id': test_id
        })
        return [question for question in questions] if questions else []

    def delete_one(self, question_formulation: str) -> None:
        """
        Delete question with formulation 'question_formulation'

        :param question_formulation: str
        :return: None
        """
        self._col.delete_one({'formulation': question_formulation})


class RunningTestAnswersStorage(MongoObjectStorage):
    """
    Class for working with answers for running tests, stored in MongoDB
    """

    @staticmethod
    def connect_to_mongodb(host, port, db_name):
        """
        Establish connection to mongodb database 'db_name', collection 'questions'

        :param host: MongoDB host
        :param port: MongoDB port
        :param db_name: MongoDB name
        :return: RunningTestAnswersStorage object
        """
        obj = MongoObjectStorage.get_connection(
            host=host,
            port=port,
            db_name=db_name,
            collection_name='running_tests_answers'
        )
        return obj

    def add(self, right_answers, test_id: str, user_id: str) -> None:
        """
        Add answers for running tests to MongoDB

        :param right_answers: dict
            {
                'question_number_1': {
                    'right_answers': [1, 2 ... <list: int>],
                    'id': str(ObjectId()),
                'question_number_2': {
                    ...
                },
                ...
            }
        :param test_id: int
        :param user_id: int
        :return:
        """
        self._col.insert_one({
            'right_answers': right_answers,
            'test_id': test_id,
            'user_id': user_id
        })

    def get(self, user_id: int) -> dict:
        """
        Get user answers for running test

        :param user_id: int
        :return: dict
        """
        right_answers = self._col.find_one({
            'user_id': user_id,
        })
        return right_answers

    def delete(self, user_id: int) -> None:
        """
        Delete user answers for running test

        :param user_id: int
        :return: None
        """
        self._col.delete_one({
            'user_id': user_id,
        })

    def add_test_result(self, test_result, test_id):
        db = self._client.data.tests_results
        db.find_one_and_update(
            {'test_id': test_id, 'active': True},
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
