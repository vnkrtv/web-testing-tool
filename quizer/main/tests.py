# pylint:
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.contrib.auth.models import User, AnonymousUser, Group
from .models import Subject, Test, TestsResultsStorage, RunningTestsAnswersStorage, QuestionsStorage
from .views import login_page, get_tests, index
from .views import run_test_result, add_test, add_test_result, get_running_tests, stop_running_test
from .views import edit_test, edit_test_result, add_question, add_question_result
from .views import get_marks, run_test, test_result
from .config import MONGO_HOST, MONGO_PORT, MONGO_DBNAME


class MainTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.lecturer = User.objects.create_user(
            username='lecturer',
            password='top_secret'
        )
        self.lecturer_group = Group.objects.create(
            id=1,
            name="lecturer"
        )
        self.lecturer.groups.add(1)

        self.student = User.objects.create_user(
            username='user',
            password='top_secret'
        )
        self.student_group = Group.objects.create(
            id=2,
            name="student"
        )
        self.student.groups.add(2)

        self.subject = Subject.objects.create(
            lecturer=self.lecturer,
            name='Subject',
            description='Description of subject'
        )
        self.test = Test.objects.create(
            subject=self.subject,
            author=self.lecturer,
            name='Hard test',
            description='Description of hard test for Subject',
            tasks_num=2,
            duration=60
        )

        self.questions_storage = QuestionsStorage.connect_to_mongodb(
            host=MONGO_HOST,
            port=MONGO_PORT,
            db_name='test_' + MONGO_DBNAME
        )
        self.tests_results_storage = TestsResultsStorage.connect_to_mongodb(
            host=MONGO_HOST,
            port=MONGO_PORT,
            db_name='test_' + MONGO_DBNAME
        )
        self.running_tests_answers_storage = RunningTestsAnswersStorage.connect_to_mongodb(
            host=MONGO_HOST,
            port=MONGO_PORT,
            db_name='test_' + MONGO_DBNAME
        )

        self.questions_storage.add_one(
            question={
                'formulation': 'First question with multiselect',
                'tasks_num': 3,
                'multiselect': True,
                'with_images': False,
                'options': [
                    {
                        'option': 'First true option',
                        'is_true': True
                    },
                    {
                        'option': 'Second false option',
                        'is_true': False
                    },
                    {
                        'option': 'Third true option',
                        'is_true': True
                    }
                ]
            },
            test_id=self.test.id
        )
        self.questions_storage.add_one(
            question={
                'formulation': 'Second question with single answer',
                'tasks_num': 2,
                'multiselect': False,
                'with_images': False,
                'options': [
                    {
                        'option': 'False option',
                        'is_true': False
                    },
                    {
                        'option': 'True option',
                        'is_true': True
                    },
                ]
            },
            test_id=self.test.id
        )


class QuestionsStorageTest(MainTest):
    def test_adding_and_getting_questions(self):
        questions = self.questions_storage.get_many(test_id=self.test.id)
        question = {
            'formulation': 'Test question',
            'tasks_num': 2,
            'multiselect': False,
            'with_images': False,
            'options': [
                {
                    'option': 'First true option',
                    'is_true': True
                },
                {
                    'option': 'Second false option',
                    'is_true': False
                }
            ]
        }
        self.questions_storage.add_one(
            question=question,
            test_id=self.test.id
        )
        updated_questions = self.questions_storage.get_many(test_id=self.test.id)
        self.assertEqual(updated_questions, questions + [question])

    def test_deleting_questions(self):
        questions = self.questions_storage.get_many(test_id=self.test.id)
        self.questions_storage.delete_one(
            question_formulation='First question with multiselect',
            test_id=self.test.id
        )
        updated_questions = self.questions_storage.get_many(test_id=self.test.id)
        self.assertEqual(len(questions) - 1, len(updated_questions))


class AuthorizationTest(MainTest):
    def test_student_auth(self):
        client = Client()
        client.logout()
        response = client.post(reverse('main:index'), {
            'username': self.student.username,
            'password': 'top_secret'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пользователь')

    def test_lecturer_auth(self):
        client = Client()
        client.logout()
        response = client.post(reverse('main:index'), {
            'username': self.lecturer.username,
            'password': 'top_secret'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Преподаватель')

    def test_anonymous_auth(self):
        client = Client()
        client.logout()
        response = client.post(reverse('main:index'), {
            'username': 'anonymous',
            'password': 'anonymous'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Зайти в систему')
