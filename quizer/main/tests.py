# pylint: disable=import-error, invalid-name, too-few-public-methods, relative-beyond-top-level
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .models import Subject, Test, TestsResultsStorage, RunningTestsAnswersStorage, QuestionsStorage
from .config import MONGO_HOST, MONGO_PORT, MONGO_DBNAME


class MainTest(TestCase):
    def setUp(self):
        self.lecturer = User.objects.create_user(
            username='lecturer',
            password='top_secret'
        )
        Group.objects.create(
            id=1,
            name="lecturer"
        )
        self.lecturer.groups.add(1)

        self.student = User.objects.create_user(
            username='user',
            password='top_secret'
        )
        Group.objects.create(
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
            db_name=MONGO_DBNAME
        )
        self.running_tests_answers_storage = RunningTestsAnswersStorage.connect_to_mongodb(
            host=MONGO_HOST,
            port=MONGO_PORT,
            db_name=MONGO_DBNAME
        )
        self.tests_results_storage = TestsResultsStorage.connect_to_mongodb(
            host=MONGO_HOST,
            port=MONGO_PORT,
            db_name=MONGO_DBNAME
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
        self.assertContains(response, 'Ошибка: неправильное имя пользователя или пароль!')

    def test_anonymous_redirect(self):
        client = Client()
        client.logout()
        response = client.get(reverse('main:tests'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Зайти в систему')


class AccessRightsTest(MainTest):
    def test_student_access(self):
        client = Client()
        client.login(
            username=self.student.username,
            password='top_secret'
        )
        response = client.post(reverse('main:add_question'), {
            'username': self.student.username,
            'password': 'top_secret'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You are not permitted to see this page.')

    def test_lecturer_access(self):
        client = Client()
        client.login(
            username=self.lecturer.username,
            password='top_secret'
        )
        response = client.post(reverse('main:marks'), {
            'username': self.lecturer.username,
            'password': 'top_secret'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You are not permitted to see this page.')


class TestsResultsStorageTest(MainTest):
    def setUp(self):
        super().setUp()
        self.client = Client()
        self.client.login(
            username=self.lecturer.username,
            password='top_secret'
        )
        self.response = self.client.post(reverse('main:run_test_result'), {
            'test_name': self.test.name,
        }, follow=True)
        self.assertEqual(len(Test.objects.all()), 1)
        self.assertEqual(len(self.tests_results_storage.get_running_tests_ids()), 1)

    def test_running_new_test(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(self.response, 'Тест запущен')

        response = self.client.post(reverse('main:tests'), {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.test.name)

        self.response = self.client.post(reverse('main:stop_running_test'), {
            'test_name': self.test.name,
        }, follow=True)
        self.assertContains(self.response, self.test.name)
        self.assertEqual(0, len(self.tests_results_storage.get_running_tests_ids()))

    def test_get_running_tests_ids_method(self):
        running_tests_ids = self.tests_results_storage.get_running_tests_ids()
        self.assertEqual(running_tests_ids, [self.test.id])

        self.response = self.client.post(reverse('main:stop_running_test'), {
            'test_name': self.test.name,
        }, follow=True)
        self.assertContains(self.response, self.test.name)
        self.assertEqual(0, len(self.tests_results_storage.get_running_tests_ids()))

    def test_running_tests_student_page(self):
        self.client.logout()
        self.client.login(
            username=self.student.username,
            password='top_secret'
        )
        self.response = self.client.post(reverse('main:tests'), {}, follow=True)
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(self.response, self.test.name)

        self.client.logout()
        self.client.login(
            username=self.lecturer.username,
            password='top_secret'
        )
        self.response = self.client.post(reverse('main:stop_running_test'), {
            'test_name': self.test.name,
        }, follow=True)
        self.assertContains(self.response, self.test.name)
        self.assertEqual(0, len(self.tests_results_storage.get_running_tests_ids()))

    def test_running_tests_lecturer_page(self):
        self.response = self.client.post(reverse('main:running_tests'), {}, follow=True)

        self.assertEqual(self.response.status_code, 200)
        self.assertContains(self.response, self.test.name)

        self.response = self.client.post(reverse('main:stop_running_test'), {
            'test_name': self.test.name,
        }, follow=True)
        self.assertContains(self.response, self.test.name)
        self.assertEqual(0, len(self.tests_results_storage.get_running_tests_ids()))
