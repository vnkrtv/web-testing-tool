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


class TestAddingAndEditingTest(MainTest):
    def test_student_has_no_access(self):
        client = Client()
        client.login(
            username=self.student.username,
            password='top_secret'
        )
        response = client.post(reverse('main:add_test'), {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You are not permitted to see this page.')

    def test_adding_new_test(self):
        client = Client()
        client.login(
            username=self.lecturer.username,
            password='top_secret'
        )
        response = client.post(reverse('main:add_test'), {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Новый тест')

        self.assertEqual(len(Test.objects.all()), 1)
        response = client.post(reverse('main:add_test_result'), {
            'subject': self.subject.name,
            'test_name': 'Second test',
            'description': 'Description of second test',
            'tasks_num': 3,
            'duration': 45
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        message = 'Тест %s по предмету %s успешно добавлен.' % ('Second test', self.subject.name)
        self.assertContains(response, message)
        self.assertEqual(len(Test.objects.all()), 2)

    def test_editing_test(self):
        client = Client()
        client.login(
            username=self.lecturer.username,
            password='top_secret'
        )
        response = client.post(reverse('main:edit_test'), {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Доступные тесты')


class AddQuestionTest(MainTest):
    def test_student_has_no_access(self):
        client = Client()
        client.login(
            username=self.student.username,
            password='top_secret'
        )
        response = client.post(reverse('main:add_question'), {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You are not permitted to see this page.')

    def test_adding_question(self):
        client = Client()
        client.login(
            username=self.lecturer.username,
            password='top_secret'
        )
        response = client.post(reverse('main:add_question'), {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Новый вопрос')

        old_questions = self.questions_storage.get_many(test_id=self.test.id)
        response = client.post(reverse('main:add_question_result'), {
            'test': self.test.name,
            'question': 'New hard question',
            'tasks_num': 3,
            'multiselect': True,
            'option_1': 'False option',
            'option_2': 'True option!',
            'is_true_2': ['on'],
            'option_3': 'Another true option',
            'is_true_3': ['on']
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'успешно добавлен')
        updated_questions = self.questions_storage.get_many(test_id=self.test.id)
        self.assertEqual(len(updated_questions), len(old_questions) + 1)


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

        response = self.client.post(reverse('main:stop_running_test'), {
            'test_name': self.test.name,
        }, follow=True)
        self.assertContains(response, self.test.name)
        self.assertEqual(0, len(self.tests_results_storage.get_running_tests_ids()))

    def test_get_running_tests_ids_method(self):
        running_tests_ids = self.tests_results_storage.get_running_tests_ids()
        self.assertEqual(running_tests_ids, [self.test.id])

        response = self.client.post(reverse('main:stop_running_test'), {
            'test_name': self.test.name,
        }, follow=True)
        self.assertContains(response, self.test.name)
        self.assertEqual(0, len(self.tests_results_storage.get_running_tests_ids()))

    def test_running_tests_student_page(self):
        self.client.logout()
        self.client.login(
            username=self.student.username,
            password='top_secret'
        )
        response = self.client.post(reverse('main:tests'), {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test.name)

        self.client.logout()
        self.client.login(
            username=self.lecturer.username,
            password='top_secret'
        )
        response = self.client.post(reverse('main:stop_running_test'), {
            'test_name': self.test.name,
        }, follow=True)
        self.assertContains(response, self.test.name)
        self.assertEqual(0, len(self.tests_results_storage.get_running_tests_ids()))

    def test_running_tests_lecturer_page(self):
        response = self.client.post(reverse('main:running_tests'), {}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test.name)

        response = self.client.post(reverse('main:stop_running_test'), {
            'test_name': self.test.name,
        }, follow=True)
        self.assertContains(response, self.test.name)
        self.assertEqual(0, len(self.tests_results_storage.get_running_tests_ids()))


class RunningTestsAnswersStorageTest(TestsResultsStorageTest):
    def test_students_available_tests_page(self):
        client = Client()
        client.login(
            username=self.student.username,
            password='top_secret'
        )
        response = client.post(reverse('main:tests'), {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, len(self.tests_results_storage.get_running_tests_ids()))
        self.assertContains(response, self.test.name)

        self.client.logout()
        self.client.login(
            username=self.lecturer.username,
            password='top_secret'
        )
        response = self.client.post(reverse('main:stop_running_test'), {
            'test_name': self.test.name,
        }, follow=True)
        self.assertContains(response, self.test.name)
        self.assertEqual(0, len(self.tests_results_storage.get_running_tests_ids()))

    def test_student_running_test_page(self):
        client = Client()
        client.login(
            username=self.student.username,
            password='top_secret'
        )
        response = client.post(reverse('main:run_test'), {
            'test_name': self.test.name
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        right_answers = self.running_tests_answers_storage.get(user_id=self.student.id)['right_answers']
        self.assertEqual(len(right_answers), self.test.tasks_num)

        answers = {}
        for question_num in right_answers:
            if len(right_answers[question_num]['right_answers']) == 1:
                answers[question_num] = right_answers[question_num]['right_answers'][0]
            else:
                key = f'{question_num}_{right_answers[question_num]}'
                answers[key] = 'on'

        response = client.post(reverse('main:test_result'), {
            'time': self.test.duration // 2,
            'csrfmiddlewaretoken': 'token',
            **answers

        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Результат')

        right_answers = self.running_tests_answers_storage.get(user_id=self.student.id)
        self.assertEqual(right_answers, None)

        self.client.logout()
        self.client.login(
            username=self.lecturer.username,
            password='top_secret'
        )
        response = self.client.post(reverse('main:stop_running_test'), {
            'test_name': self.test.name,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Результаты тестирования')
        self.assertContains(response, 'Тест: %s' % self.test.name)
        self.assertContains(response, self.student.username)
        self.assertEqual(0, len(self.tests_results_storage.get_running_tests_ids()))
