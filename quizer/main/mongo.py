# pylint: disable=import-error, too-few-public-methods, global-statement, invalid-name, relative-beyond-top-level
"""
Classes for working with MongoDB and objects stored in it
"""
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import pymongo
from bson import ObjectId
from django.conf import settings
from .models import Test

__db_conn: pymongo.database.Database = None


def set_conn(host: str, port: int, db_name: str) -> None:
    """
    Establish user connection to MongoDB database 'db_name'

    :param host: MongoDB host
    :param port: MongoDB port
    :param db_name: MongoDB database name
    """
    global __db_conn
    __db_conn = pymongo.MongoClient(host, port)[db_name]


def get_conn() -> pymongo.database.Database:
    """
    Get user connection to MongoDB database 'db_name'

    :return: Database - connection to database
    """
    global __db_conn
    if not __db_conn:
        set_conn(
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT'],
            db_name=settings.DATABASES['default']['NAME'])
    return __db_conn


class MongoDB:
    """
    Base class for classes working with MongoDB

    _db:     MongoDB database
    _col:    MongoDB collection
    """

    _db: pymongo.database.Database
    _col: pymongo.collection.Collection

    def set_collection(self, db: pymongo.database.Database, collection_name: str) -> None:
        """
        Get connection to MongoDB database and connect to current collection 'collection_name'

        :param db: MongoDB Database
        :param collection_name: name of database collection
        """
        self._db = db
        self._col = db[collection_name]


class QuestionsStorage(MongoDB):
    """
    Class for working with Questions, stored in MongoDB
    """

    @staticmethod
    def connect(db: pymongo.database.Database):
        """
        Establish connection to database collection 'questions'

        :param db: Database - connection to MongoDB database
        :return: QuestionStorage object
        """
        storage = QuestionsStorage()
        storage.set_collection(
            db=db,
            collection_name='questions')
        return storage

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

    def get_one(self, question_formulation: str, test_id: int) -> list:
        """
        Get question with formulation 'question_formulation' and 'test_id' test_id

        :param question_formulation: <str>
        :param test_id: <int>
        :return: <list>, list of questions
        """
        question = self._col.find_one({
            'formulation': question_formulation,
            'test_id': test_id
        })
        return question

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
        question = self.get_one(
            question_formulation=question_formulation,
            test_id=test_id
        )
        test = Test.objects.get(id=test_id)
        if question['with_images']:
            path = Path(f'{settings.MEDIA_ROOT}/{test.subject.name}/{test.name}/{question["_id"]}')
            shutil.rmtree(path)
        self._col.delete_one({
            'test_id': test_id,
            'formulation': question_formulation
        })

    def delete_many(self, test_id: int) -> int:
        """
        Delete all question for Test(id='test_id')

        :param test_id: <int>
        :return: count od deleted questions
        """
        questions = self.get_many(test_id=test_id)
        test = Test.objects.get(id=test_id)
        for question in questions:
            if question['with_images']:
                p = Path(f'{settings.MEDIA_ROOT}/{test.subject.name}/{test.name}/{question["_id"]}')
                shutil.rmtree(p)
        deleted_questions_count = self._col.delete_many({
            'test_id': test_id,
        }).deleted_count
        return deleted_questions_count


class RunningTestsAnswersStorage(MongoDB):
    """
    Class for working with answers for running tests, stored in MongoDB
    """

    @staticmethod
    def connect(db: pymongo.database.Database):
        """
        Establish connection to database collection 'running_tests_answers'

        :param db: Database - connection to MongoDB database
        :return: RunningTestsAnswersStorage object
        """
        storage = RunningTestsAnswersStorage()
        storage.set_collection(
            db=db,
            collection_name='running_tests_answers')
        return storage

    def add(self, right_answers, test_id: str, user_id: str, test_duration: int) -> None:
        """
        Add right answers for running tests and current user

        :param right_answers: <dict>
            {
                'question_number_1': {
                    'right_answers': ['First true option', 'Second true option' ... <list: str>],
                    'id': str(ObjectId()),
                'question_number_2': {
                    ...
                },
                ...
            }
        :param test_id: <int>
        :param user_id: <int>, user who passes test
        :param test_duration: <int>, test duration in seconds
        """
        self._col.insert_one({
            'right_answers': right_answers,
            'test_duration': test_duration,
            'start_date': datetime.now() + timedelta(hours=3),
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

    def get_left_time(self, user_id: int):
        """
        Get left time for passing running test by current user

        :param user_id: <int>, user who passes test
        :return: <dict>
        """
        right_answers = self._col.find_one({
            'user_id': user_id,
        })
        if not right_answers:
            return None
        delta = datetime.now() - right_answers['start_date']
        return right_answers['test_duration'] - delta.total_seconds()

    def delete(self, user_id: int) -> None:
        """
        Delete user answers for running test

        :param user_id: <int>
        :return: None
        """
        self._col.delete_one({
            'user_id': user_id,
        })

    def cleanup(self, user_id: int) -> list:
        """
        Delete all temporary tests answers for user

        :param user_id: <int>
        """
        docs = list(self._col.find({
            'user_id': user_id,
        }))
        self._col.delete_many({
            'user_id': user_id,
        })
        return list(docs)


class TestsResultsStorage(MongoDB):
    """
    Class for working with tests results, stored in MongoDB
    """

    @staticmethod
    def connect(db: pymongo.database.Database):
        """
        Establish connection to database collection 'tests_results'

        :param db: Database - connection to MongoDB database
        :return: TestsResultsStorage object
        """
        storage = TestsResultsStorage()
        storage.set_collection(
            db=db,
            collection_name='tests_results')
        return storage

    def add_running_test(self, test_id: int, lecturer_id: int, subject_id: int) -> None:
        """
        Create object in collection corresponding to running test

        :param test_id: <int>,
        :param subject_id: <int>,
        :param lecturer_id: <int>, lecturer who ran test
        :return:
        """
        date = datetime.now().timetuple()
        self._col.insert_one({
            'test_id': test_id,
            'subject_id': subject_id,
            'launched_lecturer_id': lecturer_id,
            'is_running': True,
            'results': [],
            'date': datetime.now() + timedelta(hours=3),
            'time': {
                'year': date[0],
                'month': date[1],
                'day': date[2],
                'hour': date[3],
                'minutes': date[4]
            }
        })

    def add_results_to_running_test(self, test_result: dict, test_id: int) -> None:
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
                        'selected_answers': <list: str>,
                        'right_answers': <list: str>
                    },
                    ...
                ]
            }
        :param test_id: <int>
        :return: None
        """
        test_result['date'] = datetime.now()
        self._col.find_one_and_update(
            {'test_id': test_id, 'is_running': True},
            {'$push': {'results': test_result}}
        )

    def get_running_test_results(self, test_id: int, lecturer_id: int) -> dict:
        """
        Get results of running test

        :param test_id: <int>
        :param lecturer_id: <int>, lecturer who ran test
        :return: <dict>, dict with test results and launching info
        """
        test_results = self._col.find_one(
            {'test_id': test_id, 'launched_lecturer_id': lecturer_id, 'is_running': True},
        )
        return test_results if test_results else {}

    def get_running_tests_ids(self) -> list:
        """
        Return list of running tests ids

        :return: <list: int>
        """
        running_tests = self._col.find({'is_running': True})
        return [test['test_id'] for test in running_tests] if running_tests else []

    def get_running_tests(self) -> list:
        """
        Return list of running tests

        :return: <list: dict>
        """
        running_tests = self._col.find({'is_running': True})
        return list(running_tests) if running_tests else []

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
            latest_test_results = max(test_results, key=lambda res: res['date'])
            return latest_test_results['results']
        return []

    def get_tests_results(self, test_id: int, lecturer_id: int) -> list:
        """
        Get results of all tests with test_id ran by lecturer with lecturer_id

        :param test_id: <int>
        :param lecturer_id: <int>, lecturer who ran test
        :return: <list>, list of tests results
        """
        test_results = self._col.find({
            'test_id': test_id,
            'launched_lecturer_id': lecturer_id,
            'is_running': False
        })
        return [{**result, 'id': result['_id']} for result in test_results] if test_results else []

    def get_test_result(self, _id: str) -> dict:
        """
        Get results of all tests with test_id ran by lecturer with lecturer_id

        :param _id: <str>, result id
        :return: <dict>, test results
        """
        test_results = self._col.find_one({
            '_id': ObjectId(_id)
        })
        return test_results if test_results else {}

    def get_all_tests_results(self) -> list:
        """
        Get results of all passed tests

        :return: <list>, list of tests results
        """
        test_results = self._col.find({'is_running': False})
        return [{**result, 'id': result['_id']} for result in test_results] if test_results else []
