# pylint: disable=import-error, invalid-name, too-few-public-methods, relative-beyond-top-level
"""
Main app tests, covered views.py, models.py and mongo.py
"""
import json
from unittest import mock, skip

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group

from rest_framework.test import APIRequestFactory, APIClient, force_authenticate

from main.models import Subject, Test, Question, TestResult, RunningTestsAnswers
from api.serializers import SubjectSerializer, TestSerializer, QuestionSerializer, TestResultSerializer

QUESTIONS_FILE_DATA = """Как создать вопрос?
+ добавив верные ответы
+ которых может быть несколько
- и есть неверные
- обеспечивается случайный порядок вопросов и ответов

Как создать вопрос со множественным выбором, но одним ответом?
* правильный вопрос выделить звездочкой
- а остальные ответы
- всё ещё с минусами

Как создавать вопросы-последовательности?
1 Достаточно просто пронумеровать варианты ответов
2 Их может быть любое число
3 Также поддерживаются вопросы-последовательности с изображениями, но метод их добавления с помощью веб-интерфейса будет реализован позже
"""


class MainTest(TestCase):
    """
    Base class for all tests
    """

    def setUp(self) -> None:
        """
        Add objects to temporary test database:
        - groups 'lecturer' and 'student'
        - 'lecturer' user and 'student' user
        - study subject 'Subject'
        - Subject 'Subject' test 'Hard test'
        - 2 questions for 'Hard test'
        """
        self.lecturer = User.objects.create_user(
            username='lecturer',
            password='')
        Group.objects.create(
            id=1,
            name="lecturer")
        self.lecturer.groups.add(1)

        self.student = User.objects.create_user(
            username='user',
            password='')
        Group.objects.create(
            id=2,
            name="student")
        self.student.groups.add(2)

        self.subject = Subject.objects.create(
            name='Subject',
            description='Description of subject')
        self.another_subject = Subject.objects.create(
            name='Another subject',
            description='Description of another subject')
        self.test = Test.objects.create(
            subject=self.subject,
            author=self.lecturer,
            name='Hard test',
            description='Description of hard test for Subject',
            tasks_num=2,
            duration=60)

        self.question = Question.objects.create(
            formulation='First question with multiselect',
            multiselect=True,
            tasks_num=3,
            type=Question.Type.REGULAR,
            test=Test.objects.get(id=self.test.id),
            options=Question.parse_options([
                {'option': 'First true option', 'is_true': True},
                {'option': 'Second false option', 'is_true': False},
                {'option': 'Third true option', 'is_true': True}
            ])
        )
        self.another_question = Question.objects.create(
            formulation='Second question with single answer',
            multiselect=True,
            tasks_num=2,
            type=Question.Type.REGULAR,
            test=Test.objects.get(id=self.test.id),
            options=Question.parse_options([
                {'option': 'False option', 'is_true': False},
                {'option': 'True option', 'is_true': True}
            ])
        )


class SubjectAPITest(MainTest):
    """
    Tests for SubjectAPI
    """

    def test_get_for_unauthenticated_user(self):
        """
        Test response code for unauthenticated user
        """
        client = APIClient()
        client.logout()
        response = client.get(reverse('api:subjects_api'))

        self.assertEqual(response.status_code, 401)

    def test_get_for_student(self):
        """
        Test response code for user from student group
        """
        client = APIClient()
        client.login(
            username=self.student.username,
            password=''
        )
        response = client.get(reverse('api:subjects_api'))

        self.assertEqual(response.status_code, 403)

    def test_get(self):
        """
        Test get method for user from lecturer group
        """
        client = APIClient()
        client.login(
            username=self.lecturer.username,
            password=''
        )
        response = client.get(reverse('api:subjects_api'))

        self.assertEqual(response.status_code, 200)
        subjects = json.dumps(SubjectSerializer(Subject.objects.all(), many=True).data)
        response_data = json.dumps(json.loads(response.content)['subjects'])
        self.assertEqual(subjects, response_data)

    def test_post(self):
        """
        Test post method for user from lecturer group
        """
        client = APIClient()
        client.login(
            username=self.lecturer.username,
            password=''
        )
        new_subject_data = {
            'name': 'New subject',
            'description': 'New subject description'
        }
        response = client.post(
            reverse('api:subjects_api'),
            json.dumps(new_subject_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'success')
        new_subject = Subject.objects.filter(name=new_subject_data['name'])
        self.assertEqual(1, len(new_subject))

    def test_put(self):
        """
        Test put method for user from lecturer group
        """
        client = APIClient()
        client.login(
            username=self.lecturer.username,
            password=''
        )

        old_name = self.subject.name
        updated_subject_data = {
            'name': 'Updated subject'
        }
        response = client.put(
            reverse('api:edit_subjects_api', kwargs={"subject_id": self.subject.id}),
            json.dumps(updated_subject_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'success')
        self.assertNotEqual(old_name, Subject.objects.get(id=self.subject.id).name)

    def test_delete(self):
        """
        Test delete method for user from lecturer group
        """
        client = APIClient()
        client.login(
            username=self.lecturer.username,
            password=''
        )

        deleted_subject_id = self.subject.id
        response = client.delete(
            reverse('api:edit_subjects_api', kwargs={"subject_id": self.subject.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'success')
        self.assertEqual(0, len(Subject.objects.filter(id=deleted_subject_id)))


class TestAPITest(MainTest):
    """
    Tests for TestAPI
    """

    def test_get_for_unauthenticated_user(self):
        """
        Test response code for unauthenticated user
        """
        client = APIClient()
        client.logout()
        response = client.get(reverse('api:tests_api'))

        self.assertEqual(response.status_code, 401)

    def test_get_all_student(self):
        """
        Test for get method
        """
        client = APIClient()
        client.login(
            username=self.student.username,
            password=''
        )
        response = client.get(reverse('api:tests_api'))

        self.assertEqual(response.status_code, 200)
        tests = json.dumps(TestSerializer(Test.objects.all(), many=True).data)
        response_data = json.dumps(json.loads(response.content)['tests'])
        self.assertEqual(tests, response_data)

    def test_permissions_for_students(self):
        """
        Test permissions for students on TestAPI
        """
        client = APIClient()
        client.login(
            username=self.student.username,
            password=''
        )

        new_test_data = {
            'name': 'New test',
            'description': 'New test description',
            'tasks_num': '5',
            'duration': '30',
            'subject_id': self.subject.id,
            'author_id': self.lecturer.id
        }
        response = client.post(
            reverse('api:tests_api'),
            json.dumps(new_test_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

        response = client.put(
            reverse('api:edit_tests_api', kwargs={'test_id': self.test.id}),
            json.dumps({'name': 'New name'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

        response = client.delete(reverse('api:edit_tests_api', kwargs={'test_id': self.test.id}))
        self.assertEqual(response.status_code, 403)

    def test_get_all_lecturer(self):
        """
        Test for get method
        """
        client = APIClient()
        client.login(
            username=self.lecturer.username,
            password=''
        )
        response = client.get(reverse('api:tests_api'))

        self.assertEqual(response.status_code, 200)
        tests = json.dumps(TestSerializer(Test.objects.all(), many=True).data)
        response_data = json.dumps(json.loads(response.content)['tests'])
        self.assertEqual(tests, response_data)

    def test_get_running(self):
        """
        Test for get method
        """
        client = APIClient()
        client.login(
            username=self.lecturer.username,
            password=''
        )
        response = client.get(reverse('api:tests_api') + '?state=running')

        self.assertEqual(response.status_code, 200)
        running_tests = json.loads(response.content)['tests']
        self.assertEqual([], running_tests)

    def test_post(self):
        """
        Test post method for user from lecturer group
        """
        client = APIClient()
        client.login(
            username=self.lecturer.username,
            password=''
        )
        new_test_data = {
            'name': 'New test',
            'description': 'New test description',
            'tasks_num': '5',
            'duration': '30',
            'subject_id': self.subject.id,
            'author_id': self.lecturer.id
        }
        response = client.post(
            reverse('api:tests_api'),
            json.dumps(new_test_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'success')
        new_test = Test.objects.filter(name=new_test_data['name'])
        self.assertEqual(1, len(new_test))

    def test_put(self):
        """
        Test put method for user from lecturer group
        """
        client = APIClient()
        client.login(
            username=self.lecturer.username,
            password=''
        )

        old_name = self.test.name
        updated_test_data = {
            'name': 'Updated test',
            'duration': self.test.duration * 2
        }
        response = client.put(
            reverse('api:edit_tests_api', kwargs={"test_id": self.test.id}),
            json.dumps(updated_test_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'success')
        self.assertNotEqual(old_name, Test.objects.get(id=self.test.id).name)

    def test_delete(self):
        """
        Test delete method for user from lecturer group
        """
        client = APIClient()
        client.login(
            username=self.lecturer.username,
            password=''
        )

        deleted_test_id = self.test.id
        response = client.delete(
            reverse('api:edit_tests_api', kwargs={"test_id": self.test.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'success')
        self.assertEqual(0, len(Test.objects.filter(id=deleted_test_id)))


class QuestionAPITest(MainTest):
    """
    Tests for QuestionAPI
    """

    def test_get_for_unauthenticated_user(self):
        """
        Test response code for unauthenticated user
        """
        client = APIClient()
        client.logout()
        response = client.get(reverse('api:questions_api', kwargs={'test_id': self.test.id}))

        self.assertEqual(response.status_code, 401)

    def test_get_student(self):
        """
        Test for get method
        """
        client = APIClient()
        client.login(
            username=self.student.username,
            password=''
        )
        response = client.get(reverse('api:questions_api', kwargs={'test_id': self.test.id}))
        self.assertEqual(response.status_code, 403)

    def test_get_lecturer(self):
        """
        Test for get method
        """
        client = APIClient()
        client.login(
            username=self.lecturer.username,
            password=''
        )
        response = client.get(reverse('api:questions_api', kwargs={'test_id': self.test.id}))

        self.assertEqual(response.status_code, 200)
        questions = json.dumps(QuestionSerializer(Question.objects.filter(test__id=self.test.id), many=True).data)
        response_data = json.dumps(json.loads(response.content)['questions'])
        self.assertEqual(questions, response_data)

    def test_post(self):
        """
        Test post method for user from lecturer group
        """
        client = APIClient()
        client.login(
            username=self.lecturer.username,
            password=''
        )
        old_questions_count = len(Question.objects.filter(test__id=self.test.id))
        new_question = {
            'test_id': self.test.id,
            'formulation': 'New hard question',
            'tasks_num': '3',
            'with_images': 'false',
            'multiselect': 'true',
            'options': [
                {'option': 'False option', 'is_true': 'false'},
                {'option': 'True option!', 'is_true': 'true'},
                {'option': 'Another true option', 'is_true': 'true'}
            ]
        }
        response = client.post(
            reverse('api:questions_api', kwargs={'test_id': self.test.id}),
            json.dumps(new_question),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'success')
        updated_questions = Question.objects.filter(test__id=self.test.id)
        self.assertEqual(len(updated_questions), old_questions_count + 1)

    def test_put(self):
        """
        Test put method for user from lecturer group
        """
        client = APIClient()
        client.login(
            username=self.lecturer.username,
            password=''
        )

        old_formulation = self.question.formulation
        old_options = self.question.options
        updated_question_data = {
            'test_id': self.test.id,
            'formulation': 'New cool question formulation',
            'options': [
                {'option': 'New false option', 'is_true': 'false'},
                {'option': 'New true option!', 'is_true': 'true'},
                {'option': 'Another false option', 'is_true': 'false'}
            ]
        }
        response = client.put(
            reverse('api:edit_questions_api', kwargs={"test_id": self.test.id, "question_id": self.question.object_id}),
            json.dumps(updated_question_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'success')
        self.assertNotEqual(old_formulation, Question.objects.get(_id=self.question._id).formulation)
        self.assertNotEqual(old_options, Question.objects.get(_id=self.question._id).options)

    def test_delete(self):
        """
        Test delete method for user from lecturer group
        """
        client = APIClient()
        client.login(
            username=self.lecturer.username,
            password=''
        )

        deleted_question_id = self.question._id
        response = client.delete(
            reverse('api:edit_questions_api', kwargs={"test_id": self.test.id, "question_id": self.question.object_id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'success')
        self.assertEqual(0, len(Question.objects.filter(_id=deleted_question_id)))


class TestPassingTest(MainTest):
    """
    Tests for tests passing
    """

    def test_launching_test(self):
        """
        Test response code for unauthenticated user
        """
        client = APIClient()
        client.login(
            username=self.lecturer.username,
            password=''
        )

        response = client.get(reverse('api:tests_api') + '?state=running')
        self.assertEqual(response.status_code, 200)
        running_tests = json.loads(response.content)['tests']
        self.assertEqual([], running_tests)

        response = client.get(reverse('api:tests_api') + '?state=not_running')
        self.assertEqual(response.status_code, 200)
        not_running_tests = json.loads(response.content)['tests']
        self.assertEqual(1, len(not_running_tests))

        response = client.put(reverse('api:launch_test', kwargs={'test_id': self.test.id}))
        self.assertEqual(True, json.loads(response.content)['ok'])

        response = client.get(reverse('api:tests_api') + '?state=running')
        self.assertEqual(response.status_code, 200)
        running_tests = json.loads(response.content)['tests']
        self.assertEqual(1, len(running_tests))

        response = client.get(reverse('api:tests_api') + '?state=not_running')
        self.assertEqual(response.status_code, 200)
        not_running_tests = json.loads(response.content)['tests']
        self.assertEqual(0, len(not_running_tests))

    def test_rest_result_api(self):
        """
        Test for TestResultAPI
        """
        client = APIClient()
        client.login(
            username=self.lecturer.username,
            password=''
        )

        test_results = TestResult.objects.all()
        self.assertEqual(len(test_results), 0)

        response = client.put(reverse('api:launch_test', kwargs={'test_id': self.test.id}))
        self.assertEqual(True, json.loads(response.content)['ok'])

        test_results = TestResult.objects.all()
        self.assertEqual(len(test_results), 1)

    def test_passing_test(self):
        """
        Test for TestResultAPI
        """
        lecturer_client = APIClient()
        lecturer_client.login(
            username=self.lecturer.username,
            password=''
        )

        student_client = APIClient()
        student_client.login(
            username=self.student.username,
            password=''
        )

        # Launching test
        test_results = TestResult.objects.all()
        self.assertEqual(len(test_results), 0)

        response = lecturer_client.put(reverse('api:launch_test', kwargs={'test_id': self.test.id}))
        self.assertEqual(True, json.loads(response.content)['ok'])

        test_results = TestResult.objects.all()
        self.assertEqual(len(test_results), 1)
        self.assertEqual(len(test_results.first().results.all()), 0)

        # Running test by student

        self.assertEqual(0, RunningTestsAnswers.objects.all().count())
        student_client.post(
            reverse('main:student_run_test'),
            {'test_id': self.test.id},
            follow=True
        )
        running_tests_answers = RunningTestsAnswers.objects.all()
        self.assertEqual(1, running_tests_answers.count())
        right_answers = running_tests_answers.first().right_answers

        answers = {}
        for right_answer in right_answers:
            question_num = right_answer['question_num']
            if len(right_answer['right_options']) == 1:
                answers[question_num] = right_answer['right_options'][0]['option']
            else:
                key = f'{question_num}_{right_answer["right_options"][0]["option"]}'
                answers[key] = 'on'

        response = student_client.post(reverse('main:test_result'), {
            'test-passed': '',
            'time': self.test.duration // 2,
            'csrfmiddlewaretoken': 'token',
            **answers
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Результат')

        self.assertEqual(0, RunningTestsAnswers.objects.all().count())
        test_results = TestResult.objects.all()
        self.assertEqual(len(test_results), 1)
        self.assertEqual(len(test_results.first().results.all()), 1)


class TestResultAPITest(MainTest):
    """
    Tests for TestResultAPI realization
    """

    def setUp(self) -> None:
        """
        Launch one test for one student
        """
        super().setUp()
        self.lecturer_client = APIClient()
        self.lecturer_client.login(
            username=self.lecturer.username,
            password=''
        )
        response = self.lecturer_client.put(reverse('api:launch_test', kwargs={'test_id': self.test.id}))
        self.assertEqual(True, json.loads(response.content)['ok'])

        self.student_client = APIClient()
        self.student_client.login(
            username=self.student.username,
            password=''
        )
        self.student_client.post(
            reverse('main:student_run_test'),
            {'test_id': self.test.id},
            follow=True
        )
        running_tests_answers = RunningTestsAnswers.objects.all()
        right_answers = running_tests_answers.first().right_answers
        answers = {}
        for right_answer in right_answers:
            question_num = right_answer['question_num']
            if len(right_answer['right_options']) == 1:
                answers[question_num] = right_answer['right_options'][0]['option']
            else:
                key = f'{question_num}_{right_answer["right_options"][0]["option"]}'
                answers[key] = 'on'
        response = self.student_client.post(reverse('main:test_result'), {
            'test-passed': '',
            'time': self.test.duration // 2,
            'csrfmiddlewaretoken': 'token',
            **answers
        }, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_get_test_results(self):
        """
        Test for get test results method
        """
        response = self.lecturer_client.get(reverse('api:tests_results_api'))
        results = json.loads(response.content)['results']
        self.assertEqual(1, len(results[0]['results']))

    def test_get_user_results(self):
        """
        Test for get method
        """
        response = self.student_client.get(reverse('api:user_results_api') + f'?user_id={self.student.id}')
        results = json.loads(response.content)['results']
        self.assertEqual(1, len(results))



#
# class AuthorizationTest(MainTest):
#     """
#     Tests for authorization system in the application
#     """
#
#     @mock.patch('main.utils.get_auth_data')
#     def test_student_auth(self, get_auth_data) -> None:
#         """
#         Test for authorization of user belonging to 'student' group
#         """
#         get_auth_data.return_value = self.student.username, 'student'
#         client = Client()
#         client.logout()
#         response = client.get(reverse('main:login_page'), follow=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'Слушатель')
#
#     @mock.patch('main.utils.get_auth_data')
#     def test_lecturer_auth(self, get_auth_data) -> None:
#         """
#         Test for authorization of user belonging to 'lecturer' group
#         """
#         get_auth_data.return_value = self.lecturer.username, 'teacher'
#         client = Client()
#         client.logout()
#         response = client.get(reverse('main:login_page'), follow=True)
#
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'Преподаватель')
#
#     @mock.patch('main.utils.get_auth_data')
#     def test_anonymous_auth(self, get_auth_data) -> None:
#         """
#         Test for authorization of a user not registered in the system
#         """
#         get_auth_data.return_value = 'anon', 'unknown'
#         client = Client()
#         client.logout()
#         response = client.get(reverse('main:login_page'), follow=True)
#
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'Incorrect group.')
#
#     @mock.patch('main.utils.get_auth_data')
#     def test_anonymous_redirect(self, get_auth_data) -> None:
#         """
#         Test redirecting a logged-out user to the login page when trying to get to the home page
#         """
#         get_auth_data.return_value = '', ''
#         client = Client()
#         client.logout()
#         response = client.get(reverse('main:tests'), follow=True)
#
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'Incorrect group.')
#
#
# class AccessRightsTest(MainTest):
#     """
#     Testing access rights of various user groups
#     """
#
#     def test_student_access(self) -> None:
#         """
#         Testing that user belonging to 'student' group does not
#         have permission to view 'lecturer' pages
#         """
#         client = Client()
#         client.login(
#             username=self.student.username,
#             password=''
#         )
#         response = client.post(reverse('main:tests'), {
#             'username': self.student.username,
#             'password': ''
#         }, follow=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'Слушатель')
#
#
# class LoadingQuestionsTest(MainTest):
#     """
#     Tests loading new questions from file using web interface
#     """
#
#     def test_loading_questions(self) -> None:
#         """
#         Testing adding new questions by loading them from file
#         """
#         client = Client()
#         client.login(
#             username=self.lecturer.username,
#             password=''
#         )
#         old_questions = self.questions_storage.get_many(test_id=self.test.id)
#
#         with open('tmp.txt', 'w') as file:
#             file.write(QUESTIONS_FILE_DATA)
#
#         with open('tmp.txt', 'r+') as file:
#             response = client.post(reverse('main:tests'), {
#                 'load-questions': '',
#                 'test_id': self.test.id,
#                 'file': file
#             }, follow=True)
#
#         os.remove(file.name)
#
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, self.test.name)
#         updated_questions = self.questions_storage.get_many(test_id=self.test.id)
#         self.assertEqual(len(updated_questions), len(old_questions) + 2)
