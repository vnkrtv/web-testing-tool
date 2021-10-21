# pylint: disable=import-error, line-too-long, relative-beyond-top-level
"""Quizer backend"""
import logging
import os
import random
import copy
import pathlib
import bson

import requests
from django.core.management import call_command

from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect, reverse
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views import View
from django.utils import timezone
from django.utils.encoding import smart_str

from . import utils
from .decorators import unauthenticated_user, allowed_users, post_method
from .models import Profile, Test, Subject, Question, TestResult, RunningTestsAnswers, UserResult
from .forms import UserForm, SubjectForm, TestForm


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


class LoginView(View):
    """Login view"""
    template = 'main/login.html'
    title = 'Войти в систему'
    decorators = []

    def get(self, request: HttpRequest) -> HttpResponse:
        logout(request)
        context = {
            'title': self.title,
            'form': UserForm(),
            'register': bool(request.GET.get('register', False))
        }
        return render(request, self.template, context)

    def post(self, request: HttpRequest) -> HttpResponse:
        register = request.POST.get('register', None)
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if register:
                fullname = form.cleaned_data['fullname']
                password2 = form.cleaned_data['password2']

                if len(fullname) == 0:
                    context = {
                        'title': self.title,
                        'form': UserForm(),
                        'error': 'Некорректный username'
                    }
                    return render(request, self.template, context)

                if password != password2:
                    context = {
                        'title': self.title,
                        'form': UserForm(),
                        'error': 'Пароли не совпадают.'
                    }
                    return render(request, self.template, context)

                user = User.objects.create_user(username=username, password=password)
                user.save()
                user.set_password(password)
                user.groups.add(2)
                utils.create_profile(user, fullname)
            else:
                user = authenticate(username=username, password=password)
                if not user:
                    context = {
                        'title': self.title,
                        'form': UserForm(),
                        'error': 'Некорректные данные.'
                    }
                    return render(request, self.template, context)
            login(request, user)
            return redirect(reverse('main:available_tests'))
        context = {
            'title': self.title,
            'form': UserForm(),
            'error': 'Некорректные данные.'
        }
        return render(request, self.template, context)


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
        start_date=timezone.now(),
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
            'title': self.title
        }
        return render(request, self.template, self.context)

    @method_decorator(decorators)
    def post(self, request: HttpRequest) -> HttpResponse:
        """Page with data administration tools"""
        dump_path = utils.save_database_dump(file=request.FILES['dumpfile'])
        call_command('loaddata', dump_path)
        os.remove(dump_path)
        self.context = {
            'info': {
                'title': 'Данные импортированы',
                'message': 'Данные успешно импортированы.'
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
        UserResult.objects.create(
            testing_result=test_results,
            user=result['user'],
            time=result['time'],
            tasks_num=result['tasks_num'],
            right_answers_count=result['right_answers_count'],
            questions=result['questions']
        )
        passed_test_answers.delete()
        self.context = {
            'title': 'Результаты тестирования',
            'message_title': 'Результат',
            'message': 'Число правильных ответов: %d/%d' % (result['right_answers_count'], result['tasks_num'])
        }
        return render(request, self.template, self.context)


class StudentsView(View):
    """Displays page with all students"""
    template = 'main/lecturer/students.html'
    title = 'Тесты'
    context = {}
    decorators = [unauthenticated_user, allowed_users(allowed_roles=['lecturer'])]

    @method_decorator(decorators)
    def get(self, request: HttpRequest) -> HttpResponse:
        """Displays page with all students"""
        self.context = {
            'title': 'Результаты тестирований',
            'subjects': Subject.objects.all(),
            'lecturers': User.objects.filter(groups__name='lecturer')
        }
        return render(request, self.template, self.context)

    @method_decorator(decorators)
    def post(self, request: HttpRequest) -> HttpResponse:
        """Displays page with all students"""
        return self.get(request)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def get_group_results(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        subject_id = request.POST['exportSubject']
        group = request.POST['exportGroup']
        course = request.POST['exportCourse']

        results_str = utils.get_group_results(subject_id, group, course)

        if request.POST.get('csvFileFormat'):
            filepath = pathlib.Path(
                f'results_'
                f'group-{course}{group}_'
                f'subject_id-{subject_id}_'
                f'date-{timezone.now().strftime("%d-%m-%y")}.csv'
            )
            with open(filepath, 'w') as dump_file:
                dump_file.write(results_str)
            with open(filepath, 'r') as dump_file:
                response = HttpResponse(dump_file, content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(filepath.name)
            response['X-Sendfile'] = smart_str(filepath)
            os.remove(filepath)
            return response
        return HttpResponse(results_str.replace('\n', '<br>'))
    return redirect(reverse('main:available_tests'))


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
        is_running=True).first()
    test_results.is_running = False
    test_results.save()

    context = {
        'title': 'Результаты тестирования',
        'test': test,
        'start_date': test_results.date,
        'end_date': timezone.now(),
        'test_results_id': str(test_results.object_id),
        'results': test_results.results.all(),
    }
    return render(request, 'main/lecturer/testingResults.html', context)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def lecturer_current_test_results(request: HttpRequest, test_results_id: str) -> HttpResponse:
    """Displays page with testing results"""
    try:
        _id = bson.ObjectId(test_results_id)
        test_results = TestResult.objects.get(_id=_id)
    except bson.errors.InvalidId or TestResult.DoesNotExist:
        return redirect(reverse('main:available_tests'))
    context = {
        'title': 'Результаты тестирования',
        'test': test_results.test,
        'start_date': test_results.date,
        'test_results_id': test_results_id,
        'results': test_results.results.all(),
    }
    return render(request, 'main/lecturer/testingResults.html', context)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def lecturer_all_tests_results(request: HttpRequest) -> HttpResponse:
    """Displays page with all tests results"""
    context = {
        'title': 'Результаты тестирований',
        'subjects': Subject.objects.all(),
        'lecturers': User.objects.filter(groups__name='lecturer')
    }
    return render(request, 'main/lecturer/testsResults.html', context)


@unauthenticated_user
@allowed_users(allowed_roles=['student'])
def student_run_test(request: HttpRequest) -> HttpResponse:
    """Run test for student"""
    if request.method != 'POST':
        return redirect(reverse('main:available_tests'))

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
        UserResult.objects.create(
            testing_result=test_results,
            user=result['user'],
            time=result['time'],
            tasks_num=result['tasks_num'],
            right_answers_count=result['right_answers_count'],
            questions=result['questions']
        )
    docs.delete()
    RunningTestsAnswers.objects.create(
        start_date=timezone.now(),
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


@unauthenticated_user
def student_tests_results(request: HttpRequest, user_id: int) -> HttpResponse:
    """All students tests results"""
    is_lecturer = request.user.groups.filter(name='lecturer')
    user_query = User.objects.filter(id=user_id)
    if (is_lecturer or request.user.id == user_id) and user_query:
        user = user_query.first()
        context = {
            'title': 'Результаты тестирований ' + user.username,
            'user': user,
            'results': UserResult.objects.filter(user__id=user_id)
        }
        template = f'main/{"lecturer" if is_lecturer else "student"}/userResults.html'
        return render(request, template, context)
    return redirect(reverse('main:available_tests'))


@unauthenticated_user
def game(request: HttpRequest) -> HttpResponse:
    """Rest room"""
    is_lecturer = request.user.groups.filter(name='lecturer')
    template = f'main/{"lecturer" if is_lecturer else "student"}/game.html'
    return render(request, template)


def get_left_time(request: HttpRequest) -> JsonResponse:
    """Return time that left for passing test"""
    if request.user.is_authenticated or request.method != 'POST':
        user_launched_test = RunningTestsAnswers.objects.filter(user__id=request.user.id).first()
        if user_launched_test:
            return JsonResponse({'time_left': user_launched_test.time_left})
    return JsonResponse({})
