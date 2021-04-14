# pylint: disable=import-error, line-too-long, relative-beyond-top-level
"""Quizer backend"""
import json
import os
import random
import copy
import sys
import traceback

import bson
import requests

from jwt import DecodeError

from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, reverse
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views import View
from django.utils import timezone
from django.utils.encoding import smart_str

from . import utils
from .decorators import unauthenticated_user, allowed_users, post_method
from .models import Test, Subject, Question, TestResult, RunningTestsAnswers, TZ_TIMEDELTA
from .forms import SubjectForm, TestForm


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def manage_questions(request: HttpRequest, test_id: int) -> HttpResponse:
    test = Test.objects.filter(id=test_id).first()
    if not test:
        return redirect(reverse('main:available_tests'))
    context = {
        'title': 'Вопросы',
        'test': test
    }
    return render(request, 'main/lecturer/managingQuestions.html', context)


def login_page(request: HttpRequest) -> HttpResponse:
    """Authorize user and redirect him to available_tests page"""
    logout(request)
    try:
        # username, group = utils.get_auth_data(request)
        username, group = 'ivan_korotaev', 'admin'
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
    if not user.groups.filter(name=id2group[group2id[group]]):
        if group2id[group] != 1:
            return HttpResponse("User with username '%s' already exist." % user.username)
        else:
            if user.groups.filter(name='student'):
                user.groups.remove(2)
            user.groups.add(group2id[group])

    # костыль на время разработки
    # if username == 'ivan_korotaev':
    #     if str(requests.get('https://vnkrtv.ru').content).find('502 Bad Gateway') != -1:
    #         if user.groups.filter(name='lecturer'):
    #             user.groups.remove(1)
    #         if not user.groups.filter(name='student'):
    #             user.groups.add(2)
    #     else:
    #         if user.groups.filter(name='student'):
    #             user.groups.remove(2)
    #         if not user.groups.filter(name='lecturer'):
    #             user.groups.add(1)
    # костыль на время разработки

    login(request, user)
    return redirect(reverse('main:available_tests'))


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def lecturer_run_test(request: HttpRequest, test_id: int) -> HttpResponse:
    """Running available test in test mode for lecturer"""
    test = Test.objects.filter(id=test_id).first()
    if not test:
        return redirect(reverse('main:available_tests'))

    test_questions = list(Question.objects.filter(test__id=test_id))
    if len(test_questions) < test.tasks_num:
        return redirect(reverse('main:available_tests'))

    test_questions = random.sample(test_questions, k=test.tasks_num)
    for question in test_questions:
        random.shuffle(question.options)

    right_answers = []
    for i, question in enumerate(test_questions):
        if question.type == Question.Type.SEQUENCE or question.type == Question.Type.SEQUENCE_WITH_IMAGES:
            right_options = copy.deepcopy(question.options)
            right_options.sort(key=lambda option: int(option['num']))
        else:
            right_options = [option for option in question.options if option['is_true']]
        right_answers.append({
            'question_num': i + 1,
            'right_options': right_options,
            'question_id': str(question.object_id)
        })

    RunningTestsAnswers.objects.filter(user__id=request.user.id).delete()
    RunningTestsAnswers.objects.create(
        right_answers=right_answers,
        test=test,
        user=request.user,
        test_duration=test.duration)
    questions_list = utils.split_questions(test_questions)
    context = {
        'title': 'Тест',
        'questions': test_questions,
        'questions_list': questions_list,
        'test_duration': test.duration,
        'test_name': test.name,
        'right_answers': right_answers,
    }
    return render(request, 'main/lecturer/runTest.html', context)


@unauthenticated_user
@allowed_users(allowed_roles=['admin'])
def get_db_dump(request: HttpRequest) -> HttpResponse:
    filepath = utils.make_database_dump()
    with open(filepath, 'r') as dump_file:
        response = HttpResponse(dump_file, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(filepath.name)
    response['X-Sendfile'] = smart_str(filepath)
    os.remove(filepath)
    return response


class AdministrationView(View):
    """View for managing data import/export"""
    template = 'main/admin/administration.html'
    title = 'Данные системы'
    context = {}
    decorators = [unauthenticated_user, allowed_users(allowed_roles=['admin'])]

    @method_decorator(decorators)
    def get(self, request: HttpRequest) -> HttpResponse:
        self.context = {
            **self.context,
            'title': self.title,
            'tests_count': Test.objects.count(),
            'subjects_count': Subject.objects.count(),
            'questions_count': Question.objects.count(),
            'tests_results_count': TestResult.objects.count(),
            'running_tests_answers_count': RunningTestsAnswers.objects.count()
        }
        return render(request, self.template, self.context)

    @method_decorator(decorators)
    def post(self, request: HttpRequest) -> HttpResponse:
        """Page with data administration tools"""
        try:

            file = request.FILES['dumpfile']
            if file.name == 'tests_results.json':
                content = file.read().decode('utf-8')
                dump_obj = json.loads(content)
                for test_result in dump_obj:
                    results = test_result['results'].copy()
                    for user_res in results:
                        for question in user_res['questions']:
                            question['question_id'] = bson.ObjectId(question['question_id'])
                    TestResult.objects.create(
                        _id=bson.ObjectId(test_result['_id']),
                        test=Test.objects.get(id=test_result['test_id']),
                        launched_lecturer=User.objects.get(id=test_result['launched_lecturer_id']),
                        subject=Subject.objects.get(id=test_result['subject_id']),
                        is_running=test_result['is_running'],
                        comment=test_result['comment'],
                        results=results)
                self.context = {
                    'info': {
                        'title': 'Данные экспортированы',
                        'message': 'Успешно экспортировано %d результатов тестирования' % len(dump_obj)
                    }
                }
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.context = {
                'info': {
                    'title': 'Ошибка',
                    'message': repr(f'Error: {e}\n' + '\n'.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
                }
            }
        return self.get(request)


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
        passed_test_answers = RunningTestsAnswers.objects.filter(user__id=request.user.id).first()
        result = utils.get_test_result(
            request=request,
            right_answers=passed_test_answers.right_answers,
            test_duration=passed_test_answers.test_duration)
        passed_test_answers.delete()

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
        passed_test_answers = RunningTestsAnswers.objects.filter(user__id=request.user.id).first()
        if not passed_test_answers:
            return redirect(reverse('main:available_tests'))
        result = utils.get_test_result(
            request=request,
            right_answers=passed_test_answers.right_answers,
            test_duration=passed_test_answers.test_duration)
        test_results = TestResult.objects.get(is_running=True, test__id=passed_test_answers.test.id)
        passed_test_answers.delete()

        test_results.results += result
        test_results.save()

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

    test_results = TestResult.objects.filter(
        test__id=test.id,
        launched_lecturer__id=request.user.id,
        is_running=True)
    test_results.is_running = False
    test_results.save()

    results = test_results.results
    results.sort(key=lambda result: result.date)
    context = {
        'title': 'Результаты тестирования',
        'test': test,
        'start_date': test_results.date,
        'end_date': timezone.now() + TZ_TIMEDELTA,
        'test_results_id': str(test_results.object_id),
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
    try:
        _id = bson.ObjectId(test_results_id)
        test_results = TestResult.objects.get(_id=_id)
    except bson.errors.InvalidId or TestResult.DoesNotExist:
        return redirect(reverse('main:available_tests'))
    results = test_results.results
    results.sort(key=lambda result: result['date'])
    context = {
        'title': 'Результаты тестирования',
        'test': test_results.test,
        'start_date': test_results.date,
        'test_results_id': test_results_id,
        'results': results,
    }
    return render(request, 'main/lecturer/testingResults.html', context)


@unauthenticated_user
@allowed_users(allowed_roles=['student'])
def student_run_test(request: HttpRequest) -> HttpResponse:
    """Run test for student"""
    test_id = int(request.POST['test_id'])
    test = Test.objects.filter(id=test_id).first()
    if not test:
        return redirect(reverse('main:available_tests'))

    test_questions = list(Question.objects.filter(test__id=test_id))
    if len(test_questions) < test.tasks_num:
        return redirect(reverse('main:available_tests'))

    test_questions = random.sample(test_questions, k=test.tasks_num)
    for question in test_questions:
        random.shuffle(question.options)

    right_answers = []
    for i, question in enumerate(test_questions):
        if question.type == Question.Type.SEQUENCE or question.type == Question.Type.SEQUENCE_WITH_IMAGES:
            right_options = copy.deepcopy(question.options)
            right_options.sort(key=lambda option: int(option['num']))
        else:
            right_options = [option for option in question.options if option['is_true']]
        right_answers.append({
            'question_num': i + 1,
            'right_options': right_options,
            'question_id': str(question.object_id)
        })
    docs = RunningTestsAnswers.objects.filter(user__id=request.user.id)
    for test_answers in docs:
        result = utils.get_test_result(
            request=request,
            right_answers=test_answers.right_answers,
            test_duration=test_answers.test_duration)
        test_results = TestResult.objects.get(is_running=True, test__id=test.id)
        test_results.results += result
        test_results.save()
    docs.delete()
    RunningTestsAnswers.objects.create(
        right_answers=right_answers,
        test=test,
        user=request.user,
        test_duration=test.duration)
    questions_list = utils.split_questions(test_questions)
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
        user_launched_test = RunningTestsAnswers.objects.filter(user__id=request.user.id).first()
        if user_launched_test:
            return JsonResponse({'time_left': user_launched_test.time_left})
    return JsonResponse({})
