# pylint: disable=import-error, line-too-long, relative-beyond-top-level
"""
Quizer backend
"""
import random
import traceback
import logging
import json
from datetime import datetime, timedelta
from jwt import DecodeError
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect, reverse
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views import View
from . import mongo
from . import utils
from .decorators import unauthenticated_user, allowed_users, post_method
from .models import Test, Subject
from .forms import SubjectForm, TestForm

logger = logging.getLogger('quizer.main.views')


@unauthenticated_user
def available_tests(request):
    """
    Page to which user is redirected after successful authorization
    For lecturer - displays list of tests that can be run
    For student - displays list of running tests
    """
    storage = mongo.TestsResultsStorage.connect(db=mongo.get_conn())
    running_tests = storage.get_running_tests()
    running_tests_ids = [test['test_id'] for test in running_tests]
    if request.user.groups.filter(name='lecturer'):
        tests = Test.objects.all()
        not_running_tests = [t for t in tests if t.id not in running_tests_ids]
        context = {
            'title': 'Тесты | Quizer',
            'subjects': list(Subject.objects.all()),
            'tests': json.dumps([t.to_dict() for t in not_running_tests]),
        }
        return render(request, 'main/lecturer/availableTests.html', context)
    if len(running_tests_ids) == 0:
        context = {
            'title': 'Тесты | Quizer',
            'message_title': 'Доступные тесты отсутствуют',
            'message': 'Ни один из тестов пока не запущен.',
        }
        return render(request, 'main/student/info.html', context)
    context = {
        'title': 'Тесты | Quizer',
        'tests': [
            {
                'launched_lecturer': User.objects.get(id=test['launched_lecturer_id']),
                **Test.objects.get(id=test['test_id']).to_dict()
            }
            for test in running_tests
        ],
    }
    return render(request, 'main/student/availableTests.html', context)


def login_page(request):
    """
    Authorize user and redirect him to available_tests page
    """
    logout(request)
    logger.error("login view - call utils.get_auth_data")
    try:
        username, group = utils.get_auth_data(request)
    except DecodeError:
        return HttpResponse('JWT decode error: %s' % traceback.format_exc().replace('File', '<br><br>File'))
    logger.error("login view - get username(%s) and group(%s)" % (username, group))
    user = authenticate(
        username=username,
        password='')
    if user is None:
        group2id = {
            'dev': 1,
            'admin': 1,
            'teacher': 1,
            'student': 2
        }
        if group in ['student', 'teacher']:
            user = User(
                username=username,
                password='')
        elif group in ['dev', 'admin']:
            user = User.objects.create_superuser(username=username,
                                                 email='',
                                                 password='')
        else:
            return HttpResponse('Incorrect group.')
        user.save()
        user.groups.add(group2id[group])
    login(request, user)
    mongo.set_conn(
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT'],
        db_name=settings.DATABASES['default']['NAME'])
    return redirect(reverse('main:available_tests'))


class SubjectsView(View):
    """Configuring study subject view"""
    template = 'main/admin/subjects.html'
    title = 'Учебные предметы | Quizer'
    context = {}

    @method_decorator(unauthenticated_user, allowed_users(allowed_roles=['admin']))
    def get(self, request):
        """Displays page with all subjects"""
        self.context = {
            **self.context,
            'title': self.title,
            'form': SubjectForm(),
            'subjects': [
                (subject, Test.objects.filter(subject__id=subject.id).count())
                for subject in Subject.objects.all()
            ]
        }
        return render(request, self.template, self.context)

    @method_decorator(unauthenticated_user, allowed_users(allowed_roles=['admin']))
    def post(self, request):
        """Configuring subjects"""
        form = SubjectForm(request.POST)
        if 'add' in request.POST:
            self.add_subject(form)
        elif 'edit' in request.POST:
            self.edit_subject(request)
        elif 'delete' in request.POST:
            self.delete_subject(request)
        elif 'load' in request.POST:
            self.load_subject(request, form)
        else:
            self.context = {}
        return self.get(request)

    def add_subject(self, form: SubjectForm) -> None:
        """Adding new study subject"""
        if form.is_valid():
            subject = Subject(
                name=form.cleaned_data.get('name'),
                description=form.cleaned_data.get('description'))
            subject.save()
            self.context = {
                'modal_title': 'Новый предмет',
                'modal_message': "Предмет '%s' успешно добавлен." % subject.name
            }
        else:
            self.context = {
                'modal_title': 'Ошибка',
                'modal_message': 'Форма добавления некорректно заполнена.'
            }

    def load_subject(self, request, form: SubjectForm):
        """Loading new subject with tests"""
        if form.is_valid():
            self.context = {
                'modal_title': 'Новый предмет',
                'modal_message': utils.add_subject_with_tests(request, form)
            }
        else:
            self.context = {
                'modal_title': 'Ошибка',
                'modal_message': 'Форма загрузки некорректно заполнена.'
            }

    def edit_subject(self, request):
        """Editing study subject"""
        name = request.POST['name']
        subject_id = int(request.POST['subject_id'])
        Subject.objects.filter(id=subject_id).update(**dict(
            name=name,
            description=request.POST['description']))
        self.context = {
            'modal_title': 'Предмет отредактирован',
            'modal_message': f"Предмет '{name}' успешно изменен."
        }

    def delete_subject(self, request):
        """Deleting study subjects with all tests and questions"""
        subject_id = int(request.POST['subject_id'])
        subject = Subject.objects.get(id=subject_id)
        subject_name = subject.name
        tests = Test.objects.filter(subject__id=subject.id)
        tests_count = tests.count()
        deleted_questions_count = 0
        for test in tests:
            storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
            deleted_questions_count += storage.delete_many(test_id=test.id)
        subject.delete()
        result = "Учебный предмет '%s', %d тестов к нему, а также все " + \
                 "вопросы к тестам в количестве %d были успешно удалены."
        self.context = {
            'modal_title': 'Предмет удален',
            'modal_message': result % (subject_name, tests_count, deleted_questions_count)
        }


class TestsView(View):
    """Configuring tests view"""
    template = 'main/lecturer/tests.html'
    title = 'Тесты | Quizer'
    context = {}

    @method_decorator(unauthenticated_user, allowed_users(allowed_roles=['lecturer']))
    def get(self, request):
        """Displays page with all tests"""
        storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
        tests = [t.to_dict() for t in Test.objects.all()]
        for test in tests:
            test['questions_num'] = len(storage.get_many(test_id=test['id']))
        self.context = {
            **self.context,
            'title': self.title,
            'subjects': list(Subject.objects.all()),
            'tests': json.dumps(tests),
            'form': TestForm()
        }
        return render(request, self.template, self.context)

    @method_decorator(unauthenticated_user, allowed_users(allowed_roles=['lecturer']))
    def post(self, request):
        """Configuring tests"""
        form = TestForm(request.POST)
        if 'add' in request.POST:
            self.add_test(request, form)
        elif 'edit' in request.POST:
            self.edit_test(request)
        elif 'delete' in request.POST:
            self.delete_test(request)
        elif 'load' in request.POST:
            self.load_test(request, form)
        else:
            self.context = {}
        return self.get(request)

    def add_test(self, request, form: TestForm) -> None:
        """Adding new test"""
        if form.is_valid():
            subject = form.cleaned_data['subject']
            test = Test(
                name=form.cleaned_data['test_name'],
                author=request.user,
                subject=subject,
                description=form.cleaned_data['description'],
                tasks_num=form.cleaned_data['tasks_num'],
                duration=form.cleaned_data['duration'])
            test.save()
            self.context = {
                'modal_title': 'Новый тест',
                'modal_message': "Тест '%s' по предмету '%s' успешно добавлен." % (test.name, subject)
            }
        else:
            self.context = {
                'modal_title': 'Ошибка',
                'modal_message': 'Форма добавления некорректно заполнена.'
            }

    def load_test(self, request, form: TestForm):
        """Loading new test from text file"""
        if form.is_valid():
            self.context = {
                'modal_title': 'Новый тест',
                'modal_message': ''
            }
        else:
            self.context = {
                'modal_title': 'Ошибка',
                'modal_message': 'Форма загрузки некорректно заполнена.'
            }

    def edit_test(self, request):
        """Editing test"""
        Test.objects.filter(id=request.POST['test_id']).update(**dict(
            name=request.POST['name'],
            author=request.user,
            description=request.POST['description'],
            tasks_num=request.POST['tasks_num'],
            duration=request.POST['duration']))
        self.context = {
            'modal_title': 'Тест отредактирован',
            'modal_message': "Тест '%s' успешно изменен." % request.POST['name']
        }

    def delete_test(self, request):
        """Deleting test with all questions"""
        test = Test.objects.get(id=request.POST['test_id'])
        storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
        deleted_questions_count = storage.delete_many(test_id=test.id)
        message = "Тест '%s' и %d вопросов к нему были успешно удалены."
        self.context = {
            'modal_title': 'Тест удален',
            'modal_message': message % (test.name, deleted_questions_count)
        }
        Test.delete(test)


@post_method
@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def run_test_result(request):
    """
    Displays page with test run result
    """
    test = Test.objects.get(id=int(request.POST['test_id']))
    storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
    questions = storage.get_many(test_id=test.id)
    if len(questions) < test.tasks_num:
        context = {
            'title': 'Запуск теста | Quizer',
            'message_title': 'Ошибка',
            'message': 'Тест не запущен, так как вопросов в базе меньше %d.' % test.tasks_num,
            'ref': reverse('main:tests'),
            'ref_message': 'Перейти к тестам',
        }
        return render(request, 'main/lecturer/info.html', context)
    storage = mongo.TestsResultsStorage.connect(db=mongo.get_conn())
    storage.add_running_test(
        test_id=test.id,
        lecturer_id=request.user.id,
        subject_id=test.subject.id)
    context = {
        'title': 'Запуск теста | Quizer',
        'message_title': 'Тест запущен',
        'message': "Состояние его прохождения можно отследить во вкладке 'Запущенные тесты'",
        'ref': reverse('main:running_tests'),
        'ref_message': 'Перейти к запущенным тестам',
    }
    return render(request, 'main/lecturer/info.html', context)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def get_running_tests(request):
    """
    Displays page with running lecturer's tests
    """
    storage = mongo.TestsResultsStorage.connect(db=mongo.get_conn())
    running_tests = storage.get_running_tests()
    tests = []
    for running_test in running_tests:
        if running_test['launched_lecturer_id'] == request.user.id:
            test = Test.objects.get(id=running_test['test_id']).to_dict()
            test_results = storage.get_running_test_results(
                test_id=test['id'],
                lecturer_id=request.user.id)
            results = test_results['results']
            results.sort(key=lambda result: result['date'])
            test['finished_students_results'] = results
            tests.append(test)
    context = {
        'title': 'Запущенные тесты | Quizer',
        'tests': tests
    }
    return render(request, 'main/lecturer/runningTests.html', context)


@post_method
@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def stop_running_test(request):
    """
    Displays page with results of passing stopped test
    """
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
        'title': 'Результаты тестирования | Quizer',
        'test': test,
        'start_date': test_results['date'],
        'questions': json.dumps([result['questions'] for result in results]),
        'end_date': datetime.now() + timedelta(hours=3),
        'results': results,
    }
    return render(request, 'main/lecturer/testingResults.html', context)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def tests_results(request):
    """
    Displays page with all tests results
    """
    storage = mongo.TestsResultsStorage.connect(db=mongo.get_conn())
    results = storage.get_all_tests_results()

    context = {
        'title': 'Результаты тестирований | Quizer',
        'subjects': Subject.objects.all(),
        'lecturers': User.objects.filter(groups__name='lecturer'),
        'tests': Test.objects.all(),
        'results': json.dumps(results)
    }
    return render(request, 'main/lecturer/testsResults.html', context)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def show_test_results(request, test_result_id):
    """
    Displays page with testing results
    """
    storage = mongo.TestsResultsStorage.connect(db=mongo.get_conn())
    test_results = storage.get_test_result(_id=test_result_id)
    test = Test.objects.get(id=test_results['test_id'])
    results = test_results['results']
    results.sort(key=lambda result: result['date'])
    context = {
        'title': 'Результаты тестирования | Quizer',
        'test': test,
        'start_date': test_results['date'],
        'questions': json.dumps([result['questions'] for result in results]),
        'results': results,
    }
    return render(request, 'main/lecturer/testingResults.html', context)


@post_method
@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def edit_test_redirect(request):
    """
    Redirecting 'lecturer' to specific page depending on his choose
    """
    key = [key for key in request.POST if 'test_name_' in key][0]
    test_id = int(key.split('test_name_')[1])
    test = Test.objects.get(id=test_id)
    storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
    questions = [question['formulation'] for question in storage.get_many(test_id=test.id)]
    context = {
        'test': test,
        'questions': questions,
        'title': {
            'edit_test_btn': 'Редактировать тест | Quizer',
            'add_qstn_btn': 'Добавить вопрос | Quizer',
            'load_qstn_btn': 'Загрузить вопросы | Quizer',
            'del_test_btn': 'Удалить тест | Quizer',
            'del_qstn_btn': 'Удалить вопросы | Quizer'
        }[request.POST[key]]
    }
    template = {
        'edit_test_btn': 'editingTestPage',
        'add_qstn_btn': 'addQuestion',
        'load_qstn_btn': 'loadQuestions',
        'del_test_btn': 'deleteTestPage',
        'del_qstn_btn': 'deleteQuestionPage'
    }[request.POST[key]]
    return render(request, f'main/lecturer/{template}.html', context)


@post_method
@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def delete_questions_result(request):
    """
    Displays page with result of deleting questions
    """
    request_dict = dict(request.POST)
    request_dict.pop('csrfmiddlewaretoken')
    test = Test.objects.get(id=request_dict.pop('test_id')[0])
    storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
    for question_formulation in request_dict:
        storage.delete_one(
            question_formulation=question_formulation,
            test_id=test.id)
    context = {
        'title': 'Вопросы удалены | Quizer',
        'message_title': 'Результат удаления',
        'message': "Вопросы к тесту '%s' в количестве %d были успешно удалены." % (test.name, len(request_dict)),
        'ref': reverse('main:tests'),
        'ref_message': 'Перейти к тестам',
    }
    return render(request, 'main/lecturer/info.html', context)


@post_method
@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def add_question_result(request):
    """
    Displays page with result of adding new question
    """
    test = Test.objects.get(id=int(request.POST['test_id']))
    try:
        question = utils.parse_question_form(
            request=request,
            test=test)
        mdb = mongo.QuestionsStorage.connect(db=mongo.get_conn())
        mdb.add_one(
            question=question,
            test_id=test.id)
    except KeyError:
        context = {
            'title': 'Ошибка | Quizer',
            'message_title': 'Ошибка',
            'message': 'Форма некорректно заполнена',
        }
        return render(request, 'main/lecturer/info.html', context)
    context = {
        'title': 'Вопрос добавлен | Quizer',
        'message_title': 'Новый вопрос',
        'message': "Вопрос '%s' к тесту '%s' успешно добавлен." % (question['formulation'], test.name),
        'ref': reverse('main:tests'),
        'ref_message': 'Перейти к тестам',
    }
    return render(request, 'main/lecturer/info.html', context)


@post_method
@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def load_questions_result(request):
    """
    Displays result of loading questions from file
    """
    test = Test.objects.get(id=int(request.POST['test_id']))
    try:
        questions_list = utils.get_questions_list(request)
        storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
        for question in questions_list:
            storage.add_one(
                question=question,
                test_id=test.id)
    except utils.InvalidFileFormatError:
        context = {
            'title': 'Ошибка | Quizer',
            'message_title': 'Ошибка',
            'message': 'Файл некорректного формата.',
            'ref': reverse('main:tests'),
            'ref_message': 'Перейти к тестам',
        }
        return render(request, 'main/lecturer/info.html', context)

    context = {
        'title': 'Вопросы загружены | Quizer',
        'message_title': 'Новые вопросы',
        'message': "Вопросы к тесту '%s' в количестве %d успешно добавлены." % (test.name, len(questions_list)),
        'ref': reverse('main:tests'),
        'ref_message': 'Перейти к тестам',
    }
    return render(request, 'main/lecturer/info.html', context)


@post_method
@unauthenticated_user
@allowed_users(allowed_roles=['student'])
def run_test(request):
    """
    Displays page with test for student
    """
    test = Test.objects.get(id=int(request.POST['test_id']))

    storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
    questions = storage.get_many(test_id=test.id)
    questions = random.sample(questions, k=test.tasks_num)
    for question in questions:
        random.shuffle(question['options'])

    right_answers = {}
    for i, question in enumerate(questions):
        right_answers[str(i + 1)] = {
            'right_answers': [option for option in question['options'] if option['is_true']],
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

    context = {
        'title': 'Тест | Quizer',
        'questions': questions,
        'test_duration': test.duration,
        'test_name': test.name,
        'right_answers': right_answers,
    }
    return render(request, 'main/student/runTest.html', context)


def get_left_time(request):
    """
    Updates time that left for passing test
    """
    if request.user.is_authenticated and request.method == 'POST':
        storage = mongo.RunningTestsAnswersStorage.connect(db=mongo.get_conn())
        left_time = storage.get_left_time(user_id=request.user.id)
        if left_time is not None:
            return JsonResponse(left_time, safe=False)
    return JsonResponse({}, safe=False)


@post_method
@unauthenticated_user
@allowed_users(allowed_roles=['student'])
def test_result(request):
    """
    Displays page with results of passing test
    """
    storage = mongo.RunningTestsAnswersStorage.connect(db=mongo.get_conn())
    passed_test_answers = storage.get(user_id=request.user.id)
    if not passed_test_answers:
        return redirect(reverse('main:tests'))
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
    context = {
        'title': 'Результат тестирования | Quizer',
        'tasks_num': result['tasks_num'],
        'right_answers_count': result['right_answers_count']
    }
    return render(request, 'main/student/testResult.html', context)
