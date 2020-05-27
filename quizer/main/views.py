# pylint: disable=import-error, line-too-long, no-else-return, pointless-string-statement, relative-beyond-top-level
"""
Quizer backend
"""
import random
import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.conf import settings
from bson import ObjectId
from . import mongo
from .decorators import unauthenticated_user, allowed_users, post_method
from .models import Test, Subject


@unauthenticated_user
def get_tests(request):
    """
    Page to which user is redirected after successful authorization
    For lecturer - displays list of tests that can be run
    For student - displays list of running tests
    """
    storage = mongo.TestsResultsStorage.connect(db=mongo.get_conn())
    running_tests_ids = storage.get_running_tests_ids()
    if request.user.groups.filter(name='lecturer'):
        tests = Test.objects.all()
        not_running_tests = [t for t in tests if t.id not in running_tests_ids]
        context = {
            'title': 'Тесты | Quizer',
            'subjects': list(Subject.objects.all()),
            'tests': json.dumps([t.to_dict() for t in not_running_tests]),
        }
        return render(request, 'main/lecturer/tests.html', context)
    if len(running_tests_ids) == 0:
        context = {
            'title': 'Тесты | Quizer',
            'message_title': 'Доступные тесты отсутствуют',
            'message': 'Ни один из тестов пока не запущен.',
        }
        return render(request, 'main/student/info.html', context)
    context = {
        'title': 'Тесты | Quizer',
        'tests': [Test.objects.get(id=_id) for _id in running_tests_ids],
    }
    return render(request, 'main/student/tests.html', context)


def login_page(request):
    """
    In case of successful authorization redirect to get_tests page, else displays login page with error
    """
    logout(request)
    if 'username' not in request.POST or 'password' not in request.POST:
        return render(request, 'main/login.html')
    user = authenticate(
        username=request.POST['username'],
        password=request.POST['password'])
    if user is not None:
        if user.is_active:
            login(request, user)
            mongo.set_conn(
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT'],
                db_name=settings.DATABASES['default']['NAME'])
            return redirect('/tests/')
        else:
            return render(request, 'main/login.html', {'error': 'Ошибка: аккаунт пользователя отключен!'})
    else:
        return render(request, 'main/login.html', {'error': 'Ошибка: неправильное имя пользователя или пароль!'})


@post_method
@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def run_test_result(request):
    """
    Displays page with test run result
    """
    test = Test.objects.get(name=request.POST['test_name'])
    storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
    questions = storage.get_many(test_id=test.id)
    if len(questions) < test.tasks_num:
        context = {
            'title': 'Запуск теста | Quizer',
            'message_title': 'Ошибка',
            'message': 'Тест не запущен, так как вопросов в базе меньше %d.' % test.tasks_num,
        }
        return render(request, 'main/lecturer/info.html', context)
    storage = mongo.TestsResultsStorage.connect(db=mongo.get_conn())
    storage.add_running_test(
        test_id=test.id,
        lecturer_id=request.user.id)
    context = {
        'title': 'Запуск теста | Quizer',
        'message_title': 'Тест запущен',
        'message': "Состояние его прохождения можно отследить во вкладке 'Запущенные тесты'",
    }
    return render(request, 'main/lecturer/info.html', context)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def add_test(request):
    """
    Displays page with an empty form for filling out information about new test
    """
    context = {
        'title': 'Новый тест | Quizer',
        'subjects': list(Subject.objects.all())
    }
    return render(request, 'main/lecturer/addTest.html', context)


@post_method
@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def add_test_result(request):
    """
    Displays page with result of adding new test
    """
    subject = request.POST['subject']
    test = Test(
        name=request.POST['test_name'],
        author=request.user,
        subject=Subject.objects.get(name=subject),
        description=request.POST['description'],
        tasks_num=request.POST['tasks_num'],
        duration=request.POST['duration'])
    test.save()
    context = {
        'title': 'Новый тест | Quizer',
        'message_title': 'Новый тест',
        'message': "Тест '%s' по предмету '%s' успешно добавлен." % (test.name, subject),
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
            results = storage.get_running_test_results(
                test_id=test['id'],
                lecturer_id=request.user.id)
            test['finished_students_num'] = len(results)
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
    test = Test.objects.get(name=request.POST['test_name'])
    storage = mongo.TestsResultsStorage.connect(db=mongo.get_conn())
    results = storage.get_running_test_results(
        test_id=test.id,
        lecturer_id=request.user.id)
    storage.stop_running_test(
        test_id=test.id,
        lecturer_id=request.user.id)
    context = {
        'title': 'Результаты тестирования | Quizer',
        'test': test,
        'results': results,
    }
    return render(request, 'main/lecturer/testingResults.html', context)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def edit_test(request):
    """
    Displays page with all tests
    """
    storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
    tests = [t.to_dict() for t in Test.objects.all()]
    for test in tests:
        test['questions_num'] = len(storage.get_many(test_id=test['id']))

    context = {
        'title': 'Редактировать тест | Quizer',
        'subjects': list(Subject.objects.all()),
        'tests': json.dumps(tests)
    }
    return render(request, 'main/lecturer/editTest.html', context)


@post_method
@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def edit_test_redirect(request):
    """
    Redirecting 'lecturer' to specific page depending on his choose
    """
    key = [key for key in request.POST if 'test_name_' in key][0]
    test_name = key.split('test_name_')[1]
    test = Test.objects.get(name=test_name)
    storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
    questions = [question['formulation'] for question in storage.get_many(test_id=test.id)]
    context = {
        'test': Test.objects.get(name=test_name),
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
def edit_test_result(request):
    """
    Displays page with result of editing test
    """
    test = Test.objects.get(id=request.POST['test_id'])
    new_test = Test(
        id=test.id,
        name=request.POST['test_name'],
        author=request.user,
        subject=test.subject,
        description=request.POST['description'],
        tasks_num=request.POST['tasks_num'],
        duration=request.POST['duration'])
    Test.delete(test)
    new_test.save()
    context = {
        'title': 'Тест отредактирован | Quizer',
        'message_title': 'Редактиктирование теста',
        'message': "Тест '%s' по предмету '%s' успешно изменен." % (new_test.name, new_test.subject),
    }
    return render(request, 'main/lecturer/info.html', context)


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
        'message': "Вопросы к тесту '%s' в количестве %d были успешно удалены." % (test.name, len(request_dict))
    }
    return render(request, 'main/lecturer/info.html', context)


@post_method
@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def delete_test_result(request):
    """
    Displays page with result of deleting test
    """
    test = Test.objects.get(id=request.POST['test_id'])
    if 'del' in request.POST:
        storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
        deleted_questions_count = storage.delete_many(test_id=test.id)
        context = {
            'title': 'Тест удален | Quizer',
            'message_title': 'Результат удаления',
            'message': "Тест '%s' и %d вопросов к нему были успешно удалены." % (test.name, deleted_questions_count)
        }
        Test.delete(test)
        return render(request, 'main/lecturer/info.html', context)
    return redirect('/edit_test')


@post_method
@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def add_question_result(request):
    """
    Displays page with result of adding new question
    """
    test = Test.objects.get(name=request.POST['test'])
    question = {
        '_id': ObjectId(),
        'formulation': request.POST['question'],
        'tasks_num': request.POST['tasks_num'],
        'multiselect': 'multiselect' in request.POST,
        'with_images': 'with_images' in request.POST,
        'options': []
    }
    try:
        """
            request.POST:
            - if not 'with_images':
                - option_{i} = {option} - possible answer
            - if 'multiselect':
                - is_true_{i} = 'on' - if exists in request.POST then option_{i} is true
            - if single answer:
                - is_true = {i} -  option_{i} is true
            request.FILES:
            - if 'with_images':
                - option_{i} - <InMemoryUploadedFile>(image option)
        """
        if question['multiselect']:
            right_options_nums = [key.split('_')[2] for key in request.POST if 'is_true_' in key]
        else:
            right_options_nums = [request.POST['is_true']]
        if question['with_images']:
            options = {
                key.split('_')[1]: request.FILES[key]
                for key in request.FILES if 'option_' in key
            }
            for option_num in options:
                path = f'{test.subject.name}/{test.name}/{question["_id"]}/{option_num}.jpg'
                default_storage.save(path, ContentFile(options[option_num].read()))
                options[option_num] = path
        else:
            options = {
                key.split('_')[1]: request.POST[key]
                for key in request.POST if 'option_' in key
            }
        for option_num in options:
            question['options'].append({
                'option': options[option_num],
                'is_true': option_num in right_options_nums
            })
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
    }
    return render(request, 'main/lecturer/info.html', context)


@post_method
@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def load_questions_result(request):
    """
    Displays result of loading questions from file
    """
    test = Test.objects.get(name=request.POST['test'])
    storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
    try:
        content = request.FILES['file'].read().decode('utf-8')
        questions_list = content.split('\n\n')
        if '' in questions_list:
            questions_list.remove('')
        questions_count = 0
        for question in questions_list:
            buf = question.split('\n')
            if '' in buf:
                buf.remove('')
            formulation = buf[0]
            multiselect = False
            options = []
            for line in buf[1:]:
                if '-' in line:
                    options.append({
                        'option': line.split('-')[1][1:],
                        'is_true': False
                    })
                elif '*' in line:
                    options.append({
                        'option': line.split('*')[1][1:],
                        'is_true': True
                    })
                elif '+' in line:
                    multiselect = True
                    options.append({
                        'option': line.split('+')[1][1:],
                        'is_true': True
                    })
                else:
                    raise UnicodeDecodeError
            questions_count += 1
            storage.add_one(
                question={
                    'formulation': formulation,
                    'tasks_num': len(options),
                    'multiselect': multiselect,
                    'with_images': False,
                    'options': options
                },
                test_id=test.id)
    except UnicodeDecodeError:
        context = {
            'title': 'Ошибка | Quizer',
            'message_title': 'Ошибка',
            'message': 'Файл некорректного формата.',
        }
        return render(request, 'main/lecturer/info.html', context)

    context = {
        'title': 'Вопросы загружены | Quizer',
        'message_title': 'Новые вопросы',
        'message': "Вопросы к тесту '%s' в количестве %d успешно добавлены." % (test.name, questions_count),
    }
    return render(request, 'main/lecturer/info.html', context)


@unauthenticated_user
@allowed_users(allowed_roles=['student'])
def get_marks(request):
    """
    Displays page with students marks
    """
    context = {
        'title': 'Оценки | Quizer'
    }
    return render(request, 'main/student/marks.html', context)


@post_method
@unauthenticated_user
@allowed_users(allowed_roles=['student'])
def run_test(request):
    """
    Displays page with test for student
    """
    test = Test.objects.get(name=request.POST['test_name'])
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
    storage.add(
        right_answers=right_answers,
        test_id=test.id,
        user_id=request.user.id)
    context = {
        'title': 'Тест | Quizer',
        'questions': questions,
        'test_duration': test.duration,
        'test_name': test.name,
        'right_answers': right_answers,
    }
    return render(request, 'main/student/runTest.html', context)


@post_method
@unauthenticated_user
@allowed_users(allowed_roles=['student'])
def test_result(request):
    """
    Displays page with results of passing test
    """
    storage = mongo.RunningTestsAnswersStorage.connect(db=mongo.get_conn())
    passed_test_answers = storage.get(user_id=request.user.id)
    right_answers = passed_test_answers['right_answers']
    test_id = passed_test_answers['test_id']
    storage.delete(user_id=request.user.id)

    response = dict(request.POST)
    response.pop('csrfmiddlewaretoken')
    time = response.pop('time')[0]

    answers = {}
    for key in response:
        """
            'key' for multiselect: {question_num}_{selected_option}: ['on']
            'key' for single: {question_num}: ['{selected_option}']
        """
        buf = key.split('_')
        if len(buf) == 1:
            answers[buf[0]] = [response[key][0]]
        else:
            if buf[0] in answers:
                answers[buf[0]].append(buf[1])
            else:
                answers[buf[0]] = [buf[1]]

    right_answers_count = 0
    questions = []
    for question_num in right_answers:
        questions.append({
            'id': right_answers[question_num]['id'],
            'selected_answers': answers[question_num] if question_num in answers else [],
            'right_answers': [item['option'] for item in right_answers[question_num]['right_answers']]
        })
        if question_num in answers:
            if [item['option'] for item in right_answers[question_num]['right_answers']] == answers[question_num]:
                right_answers_count += 1
                questions[-1]['is_true'] = True
            else:
                questions[-1]['is_true'] = False
    result = {
        'user_id': request.user.id,
        'username': request.user.username,
        'time': time,
        'tasks_num': len(right_answers),
        'right_answers_num': right_answers_count,
        'questions': questions
    }
    storage = mongo.TestsResultsStorage.connect(db=mongo.get_conn())
    storage.add_results_to_running_test(
        test_result=result,
        test_id=test_id)
    context = {
        'title': 'Результат тестирования | Quizer',
        'right_answers_count': right_answers_count
    }
    return render(request, 'main/student/testResult.html', context)
