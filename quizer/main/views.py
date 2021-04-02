# pylint: disable=import-error, line-too-long, relative-beyond-top-level
"""Quizer backend"""
import random
import copy
from datetime import datetime, timedelta

import requests
from jwt import DecodeError

from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, reverse
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.conf import settings
from django.views import View

from . import mongo
from . import utils
from .decorators import unauthenticated_user, allowed_users, post_method
from .models import Test, Subject, QuestionType
from .forms import SubjectForm, TestForm


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def manage_questions(request: HttpRequest, test_id: int) -> HttpResponse:
    test = Test.objects.filter(id=test_id).first()
    context = {
        'title': 'Вопросы',
        'test': test
    }
    return render(request, 'main/lecturer/managingQuestions.html', context)


def login_page(request: HttpRequest) -> HttpResponse:
    """Authorize user and redirect him to available_tests page"""
    logout(request)
    try:
        username, group = utils.get_auth_data(request)
    except DecodeError:
        return HttpResponse("JWT decode error: chet polomalos'")

    group2id = {
        'admin': 1,
        'teacher': 1,
        'student': 2
    }


    # костыль на время разработки
    if username == 'ivan_korotaev':
        group = 'admin'
    # костыль на время разработки

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        if group in ['student', 'teacher']:
            user = User(username=username, password='')
        elif group in ['admin']:
            user = User.objects.create_superuser(username=username, email='', password='')
        else:
            return HttpResponse('Incorrect group.')
        user.save()
        user.groups.add(group2id[group])
    id2group = {
        1: 'lecturer',
        2: 'student'
    }
    if group2id[group] == 1:
        if user.groups.filter(name='lecturer'):
            user.groups.remove(1)
        if not user.groups.filter(name='student'):
            user.groups.add(2)
    if not user.groups.filter(name=id2group[group2id[group]]):
        if group2id[group] != 1 and username != 'ivan_korotaev':  # костыль на время разработки
            return HttpResponse("User with username '%s' already exist." % user.username)
        else:
            user.groups.remove(2)
            user.groups.add(group2id[group])

    # костыль на время разработки
    if username == 'ivan_korotaev' and str(requests.get('https://vnkrtv.ru').content).find(
            '502 Bad Gateway') != -1:
        if user.groups.filter(name='lecturer'):
            user.groups.remove(1)
        if not user.groups.filter(name='student'):
            user.groups.add(2)
    else:
        if user.groups.filter(name='student'):
            user.groups.remove(2)
        if not user.groups.filter(name='lecturer'):
            user.groups.add(1)
    # костыль на время разработки

    login(request, user)
    mongo.set_conn(
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT'],
        db_name=settings.DATABASES['default']['NAME'])
    return redirect(reverse('main:available_tests'))


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def lecturer_run_test(request: HttpRequest, test_id: int) -> HttpResponse:
    """Running available test in test mode for lecturer"""
    try:
        test = Test.objects.get(id=test_id)
    except Test.DoesNotExist or ValueError:
        return redirect(reverse('main:available_tests'))

    storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
    test_questions = storage.get_many(test_id=test.id)
    if len(test_questions) < test.tasks_num:
        return redirect(reverse('main:available_tests'))

    test_questions = random.sample(test_questions, k=test.tasks_num)
    for question in test_questions:
        random.shuffle(question['options'])

    right_answers = {}
    for i, question in enumerate(test_questions):
        if question['type'] == QuestionType.SEQUENCE or question['type'] == QuestionType.SEQUENCE_WITH_IMAGES:
            right_options = copy.deepcopy(question['options'])
            right_options.sort(key=lambda option: int(option['num']))
        else:
            right_options = [option for option in question['options'] if option['is_true']]
        right_answers[str(i + 1)] = {
            'right_answers': right_options,
            'id': str(question['_id'])
        }
    storage = mongo.RunningTestsAnswersStorage.connect(db=mongo.get_conn())
    storage.cleanup(user_id=request.user.id)
    storage.add(
        right_answers=right_answers,
        test_id=test.id,
        user_id=request.user.id,
        test_duration=test.duration)

    if len(test_questions) < 25:
        group_size = len(test_questions)
    else:
        group_size = 25
    questions_list = list(zip(*[iter(test_questions)] * group_size))
    questions_list += [test_questions[len(questions_list) * group_size:]]
    questions_list = [(questions_group, len(questions_group) * i) for i, questions_group in enumerate(questions_list)]
    context = {
        'title': 'Тест',
        'questions': test_questions,
        'questions_list': questions_list,
        'test_duration': test.duration,
        'test_name': test.name,
        'right_answers': right_answers,
    }
    return render(request, 'main/lecturer/runTest.html', context)


class AvailableTestsView(View):
    """View for available tests"""
    lecturer_template = 'main/lecturer/availableTests.html'
    student_template = 'main/student/availableTests.html'
    title = 'Доступные тесты'
    context = {}
    decorators = [unauthenticated_user]

    @method_decorator(decorators)
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Page to which user is redirected after successful authorization
        For lecturer - displays list of tests that can be run
        For student - displays list of running tests
        """
        if request.user.groups.filter(name='lecturer'):
            return self.lecturer_available_tests(request)
        return self.student_available_tests(request)

    @method_decorator(decorators)
    def post(self, request: HttpRequest) -> HttpResponse:
        """Configuring running tests"""
        if 'lecturer-passed-test' in request.POST:
            self.lecturer_passed_test_result(request)
        else:
            self.context = {}
        return self.get(request)

    def lecturer_available_tests(self, request: HttpRequest) -> HttpResponse:
        """Tests available for launching by lecturers"""
        self.context = {
            **self.context,
            'title': self.title,
            'subjects': Subject.objects.all()
        }
        return render(request, self.lecturer_template, self.context)

    def student_available_tests(self, request: HttpRequest) -> HttpResponse:
        """Tests available for running by students"""
        self.context = {
            'title': self.title
        }
        return render(request, self.student_template, self.context)

    def lecturer_passed_test_result(self, request: HttpRequest) -> HttpResponse:
        """Test results"""
        storage = mongo.RunningTestsAnswersStorage.connect(db=mongo.get_conn())
        passed_test_answers = storage.get(user_id=request.user.id)

        test_id = passed_test_answers['test_id']
        storage.delete(user_id=request.user.id)

        result = utils.get_test_result(
            request=request,
            right_answers=passed_test_answers['right_answers'],
            test_duration=passed_test_answers['test_duration'])

        storage = mongo.TestsResultsStorage.connect(db=mongo.get_conn())
        storage.add_results_to_running_test(
            test_result=result,
            test_id=test_id)

        self.context = {
            'title': 'Доступные тесты',
            'info': {
                'title': 'Результат',
                'message': 'Число правильных ответов: %d/%d' % (result['right_answers_count'], result['tasks_num'])
            }
        }
        return render(request, self.lecturer_template, self.context)


class SubjectsView(View):
    """Configuring study subject view"""
    template = 'main/admin/subjects.html'
    title = 'Учебные предметы'
    decorators = [unauthenticated_user, allowed_users(allowed_roles=['lecturer'])]

    @method_decorator(decorators)
    def get(self, request: HttpResponse) -> HttpResponse:
        """Displays page with all subjects"""
        context = {
            'title': self.title,
            'form': SubjectForm()
        }
        return render(request, self.template, context)

    @method_decorator(decorators)
    def post(self, request: HttpResponse) -> HttpResponse:
        """Displays page with all subjects"""
        return self.get(request)


class TestsView(View):
    """Configuring tests view"""
    template = 'main/lecturer/tests.html'
    title = 'Тесты'
    context = {}
    decorators = [unauthenticated_user, allowed_users(allowed_roles=['lecturer'])]

    @method_decorator(decorators)
    def get(self, request: HttpRequest) -> HttpResponse:
        """Displays page with all tests"""
        self.context = {
            'title': self.title,
            'subjects': Subject.objects.all(),
            'form': TestForm()
        }
        return render(request, self.template, self.context)

    @method_decorator(decorators)
    def post(self, request: HttpRequest) -> HttpResponse:
        """Configuring tests"""
        return self.get(request)


class PassedTestView(View):
    """View for results of passed tests"""
    template = 'main/student/testingResult.html'
    context = {}
    decorators = [unauthenticated_user, allowed_users(allowed_roles=['student'])]

    @method_decorator(decorators)
    def get(self, _) -> HttpResponse:
        """Redirect user to available tests page"""
        return redirect(reverse('main:available_tests'))

    @method_decorator(decorators)
    def post(self, request: HttpRequest) -> HttpResponse:
        """Displays page with results of passing test"""
        if 'test-passed' in request.POST:
            return self.get_passed_test_results(request)
        return self.get(request)

    def get_passed_test_results(self, request: HttpRequest) -> HttpResponse:
        """Test results"""
        storage = mongo.RunningTestsAnswersStorage.connect(db=mongo.get_conn())
        passed_test_answers = storage.get(user_id=request.user.id)
        if not passed_test_answers:
            return redirect(reverse('main:available_tests'))
        test_id = passed_test_answers['test_id']
        storage.delete(user_id=request.user.id)

        result = utils.get_test_result(
            request=request,
            right_answers=passed_test_answers['right_answers'],
            test_duration=passed_test_answers['test_duration'])

        storage = mongo.TestsResultsStorage.connect(db=mongo.get_conn())
        storage.add_results_to_running_test(
            test_result=result,
            test_id=test_id)

        self.context = {
            'title': 'Результаты тестирования',
            'message_title': 'Результат',
            'message': 'Число правильных ответов: %d/%d' % (result['right_answers_count'], result['tasks_num'])
        }
        return render(request, self.template, self.context)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def get_running_tests(request: HttpRequest) -> HttpResponse:
    """Displays page with running lecturer's tests"""
    context = {
        'title': 'Запущенные тесты',
    }
    return render(request, 'main/lecturer/runningTests.html', context)


@post_method
@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def stop_running_test(request: HttpRequest) -> HttpResponse:
    """Displays page with results of passing stopped test"""
    test = Test.objects.get(id=int(request.POST['test_id']))
    storage = mongo.TestsResultsStorage.connect(db=mongo.get_conn())
    test_results = storage.get_running_test_results(
        test_id=test.id,
        lecturer_id=request.user.id)
    storage.stop_running_test(
        test_id=test.id,
        lecturer_id=request.user.id)
    results = test_results['results']
    results.sort(key=lambda result: result['date'])
    context = {
        'title': 'Результаты тестирования',
        'test': test,
        'start_date': test_results['date'],
        'end_date': datetime.now() + timedelta(hours=3),
        'test_results_id': str(test_results['_id']),
        'results': results,
    }
    return render(request, 'main/lecturer/testingResults.html', context)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def tests_results(request: HttpRequest) -> HttpResponse:
    """Displays page with all tests results"""
    context = {
        'title': 'Результаты тестирований',
        'subjects': Subject.objects.all(),
        'lecturers': User.objects.filter(groups__name='lecturer')
    }
    return render(request, 'main/lecturer/testsResults.html', context)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def show_test_results(request: HttpRequest, test_results_id: str) -> HttpResponse:
    """Displays page with testing results"""
    storage = mongo.TestsResultsStorage.connect(db=mongo.get_conn())
    test_results = storage.get_test_result(_id=test_results_id)
    if not test_results:
        return redirect(reverse('main:available_tests'))
    test = Test.objects.get(id=test_results['test_id'])
    results = test_results['results']
    results.sort(key=lambda result: result['date'])
    context = {
        'title': 'Результаты тестирования',
        'test': test,
        'start_date': test_results['date'],
        'test_results_id': test_results_id,
        'results': results,
    }
    return render(request, 'main/lecturer/testingResults.html', context)


@unauthenticated_user
@allowed_users(allowed_roles=['student'])
def student_run_test(request: HttpRequest) -> HttpResponse:
    """Run test for student"""
    test = Test.objects.get(id=int(request.POST['test_id']))
    storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
    test_questions = storage.get_many(test_id=test.id)
    test_questions = random.sample(test_questions, k=test.tasks_num)

    for question in test_questions:
        random.shuffle(question['options'], random.random)

    right_answers = {}
    for i, question in enumerate(test_questions):
        if question['type'] == QuestionType.SEQUENCE or question['type'] == QuestionType.SEQUENCE_WITH_IMAGES:
            right_options = copy.deepcopy(question['options'])
            right_options.sort(key=lambda option: int(option['num']))
        else:
            right_options = [option for option in question['options'] if option['is_true']]
        right_answers[str(i + 1)] = {
            'right_answers': right_options,
            'id': str(question['_id'])
        }
    storage = mongo.RunningTestsAnswersStorage.connect(db=mongo.get_conn())
    docs = storage.cleanup(user_id=request.user.id)
    storage.add(
        right_answers=right_answers,
        test_id=test.id,
        user_id=request.user.id,
        test_duration=test.duration)
    for test_answers in docs:
        result = utils.get_test_result(
            request=request,
            right_answers=test_answers['right_answers'],
            test_duration=test_answers['test_duration'])
        storage = mongo.TestsResultsStorage.connect(db=mongo.get_conn())
        storage.add_results_to_running_test(
            test_result=result,
            test_id=test.id)

    if len(test_questions) < 25:
        group_size = len(test_questions)
    else:
        group_size = 25
    questions_list = list(zip(*[iter(test_questions)] * group_size))
    questions_list += [test_questions[len(questions_list) * group_size:]]
    questions_list = [(questions_group, len(questions_group) * i) for i, questions_group in enumerate(questions_list)]

    context = {
        'title': 'Тест',
        'questions': test_questions,
        'questions_list': questions_list,
        'test_duration': test.duration,
        'test_name': test.name,
        'right_answers': right_answers,
    }
    return render(request, 'main/student/runTest.html', context)


def get_left_time(request: HttpRequest) -> JsonResponse:
    """Return time that left for passing test"""
    if request.user.is_authenticated or request.method != 'POST':
        storage = mongo.RunningTestsAnswersStorage.connect(db=mongo.get_conn())
        time_left = storage.get_left_time(user_id=request.user.id)
        if time_left is not None:
            return JsonResponse({'time_left': time_left})
    return JsonResponse({})
