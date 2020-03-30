from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from .decorators import unauthenticated_user, allowed_users
from .models import Test, Subject, MongoDB
from .config import MONGO_PORT, MONGO_HOST
from pymongo.errors import ServerSelectionTimeoutError
from bson import ObjectId
import random


def login_page(request):
    logout(request)
    return render(request, 'main/login.html')


@unauthenticated_user
def get_tests(request):
    mdb = MongoDB(
        host=MONGO_HOST,
        port=MONGO_PORT
    )
    running_tests_ids = mdb.get_running_tests()
    if request.user.groups.filter(name='lecturer'):
        lectorers_tests = Test.objects.filter(author__username=request.user.username)
        info = {
            'tests': list(filter(lambda test: test.id not in running_tests_ids, lectorers_tests)),
            'username': request.user.username
        }
        return render(request, 'main/lecturer/testsPanel.html', info)
    if request.user.groups.filter(name='student'):
        if len(running_tests_ids) == 0:
            info = {
                'title': 'Доступные тесты отсутствуют',
                'message': 'Ни один из тестов пока не запущен.',
                'username': request.user.username,
            }
            return render(request, 'main/student/info.html', info)
        info = {
            'tests': [Test.objects.get(id=_id) for _id in running_tests_ids],
            'username': request.user.username
        }
        return render(request, 'main/student/tests.html', info)


def index(request):
    if request.user.is_authenticated:
        return get_tests(request)
    if 'username' not in request.POST or 'password' not in request.POST:
        return render(request, 'main/login.html', {'error': 'Ошибка: неправильное имя пользователя или пароль!'})
    info = {
        'username': request.POST['username'],
        'password': request.POST['password']
    }
    user = authenticate(username=info['username'], password=info['password'])
    if user is not None:
        if user.is_active:
            login(request, user)
            return get_tests(request)
        else:
            return render(request, 'main/login.html', {'error': 'Ошибка: аккаунт пользователя неактивен!'})
    # Return a 'disabled account' error message
    else:
        return render(request, 'main/login.html', {'error': 'неправильное имя пользователя или пароль!'})


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def run_test_result(request):
    test = Test.objects.get(name=request.POST['test_name'])
    mdb = MongoDB(
        host=MONGO_HOST,
        port=MONGO_PORT
    )
    mdb.run_test(
        test_id=test.id,
        lectorer_id=request.user.id
    )
    info = {
        'title': 'Тест запущен',
        'message': "Состояние его прохождения можно отследить во вкладке 'Запущенные тесты'",
        'username': request.user.username,
    }
    return render(request, 'main/lecturer/info.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def add_test(request):
    info = {
        'subjects': list(Subject.objects.all()),
        'username': request.user.username
    }
    return render(request, 'main/lecturer/addTest.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def add_test_result(request):
    subject = request.POST['subject']
    test = Test(
        name=request.POST['test_name'],
        author=request.user.id,
        subject=Subject.objects.get(name=subject),
        description=request.POST['description'],
        tasks_num=request.POST['tasks_num'],
        duration=request.POST['duration']
    )
    test.save()
    info = {
        'title': 'Новый тест',
        'message': f'Тест {test.name} по предмету {subject} успешно добавлен.',
        'username': request.user.username,
    }
    return render(request, 'main/lecturer/info.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def get_running_tests(request):
    mdb = MongoDB(
        host=MONGO_HOST,
        port=MONGO_PORT
    )
    running_tests_ids = mdb.get_running_tests()
    lectorers_tests = Test.objects.filter(author__username=request.user.username)
    info = {
        'tests': list(filter(lambda test: test.id in running_tests_ids, lectorers_tests)),
        'username': request.user.username
    }
    return render(request, 'main/lecturer/runningTests.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def stop_running_test(request):
    test = Test.objects.get(name=request.POST['test_name'])
    mdb = MongoDB(
        host=MONGO_HOST,
        port=MONGO_PORT
    )
    mdb.stop_test(
        test_id=test.id,
        lectorer_id=request.user.id
    )
    info = {
        'title': 'Тест остановлен',
        'message': 'Тут будет результат прохождения',
        'username': request.user.username,
    }
    return render(request, 'main/lecturer/info.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def edit_test(request):
    info = {
        'tests': list(Test.objects.filter(author__username=request.user.username)),
        'username': request.user.username
    }
    return render(request, 'main/lecturer/editTest.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def edit_test_result(request):
    mdb = MongoDB(
        host=MONGO_HOST,
        port=MONGO_PORT
    )
    question = mdb.get_questions(test_id=1)
    #question.pop('_id')
    import json
    info = {
        'title': 'Окно редактирования теста',
        'message': f"""Пока здесь будет пример вопроса:\n{question}""",
        'username': request.user.username,
    }
    return render(request, 'main/lecturer/info.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def add_question(request):
    info = {
        'tests': list(Test.objects.filter(author__username=request.user.username)),
        'username': request.user.username
    }
    return render(request, 'main/lecturer/addQuestion.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def add_question_result(request):
    test = Test.objects.get(name=request.POST['test'])
    question = {
        'formulation': request.POST['question'],
        'tasks_num': request.POST['tasks_num'],
        'multiselect': True if 'multiselect' in request.POST else False,
        'with_images': True if 'with_images' in request.POST else False,
        'options': []
    }

    try:
        options = {request.POST[key]: int(key.split('_')[1]) for key in request.POST if 'option_' in key}

        # TODO: images - where store?
        if question['multiselect']:
            true_options = [int(key.split('_')[2]) for key in request.POST if 'is_true_' in key]
        else:
            true_options = [int(request.POST['is_true'])]

        for option in options:
            question['options'].append({
                'option': option,
                'is_true': True if options[option] in true_options else False
            })

        mdb = MongoDB(
            host=MONGO_HOST,
            port=MONGO_PORT
        )
        mdb.add_question(
            question=question,
            test_id=test.id
        )
    except KeyError:
        info = {
            'title': 'Ошибка',
            'message': 'Форма некоректно заполнена',
            'username': request.user.username,
        }
        return render(request, 'main/lecturer/info.html', info)
    except ServerSelectionTimeoutError as e:
        info = {
            'title': 'Ошибка',
            'message': 'СУБД MongoDB не подключена: %s' % e,
            'username': request.user.username,
        }
        return render(request, 'main/lecturer/info.html', info)

    info = {
        'title': 'Новый вопрос',
        'message': "Вопрос '%s' к тесту '%s' успешно добавлен." % (question['formulation'], test.name),
        'username': request.user.username,
    }
    return render(request, 'main/lecturer/info.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['student'])
def get_marks(request):
    info = {
        'username': request.user.username
    }
    return render(request, 'main/student/marks.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['student'])
def run_test(request):
    test = list(Test.objects.filter(name=request.POST['test_name']))[0]

    mdb = MongoDB(
        host=MONGO_HOST,
        port=MONGO_PORT
    )
    questions = mdb.get_questions(test_id=test.id)

    if len(questions) < test.tasks_num:
        info = {
            'title': 'Ошибка',
            'message': 'Вопросов по данной теме меньше %d' % test.tasks_num,
            'username': request.user.username
        }
        return render(request, 'main/student/info.html', info)
    questions = random.sample(questions, k=test.tasks_num)

    right_answers = {}
    for i, question in enumerate(questions):
        right_answers[str(i + 1)] = [i + 1 for i, option in enumerate(question['options']) if option['is_true']]
    mdb.add_running_test_answers(
        user_id=request.user.id,
        test_id=test.id,
        right_answers=right_answers
    )
    info = {
        'questions': questions, 'test_duration': test.duration,
        'test_name': test.name,
        'right_answers': right_answers,
        'username': request.user.username
    }
    return render(request, 'main/student/runTest.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['student'])
def test_result(request):
    mdb = MongoDB(
        host=MONGO_HOST,
        port=MONGO_PORT
    )
    right_answers = mdb.get_running_test_answers(user_id=request.user.id)['right_answers']
    mdb.drop_running_test_answers(user_id=request.user.id)

    query_dict = dict(request.POST)
    query_dict.pop('csrfmiddlewaretoken')
    time = query_dict.pop('time')[0]
    print(time)
    answers_dict = {}
    for key in query_dict:
        '''
            'key' for multiselect: {question_num}_{selected_option}: True/False
            'key' for single: {question_num}: True/False
        '''
        buf = key.split('_')
        if len(buf) == 1:
            answers_dict[buf[0]] = [int(query_dict[key][0])]
        else:
            if buf[0] in answers_dict:
                answers_dict[buf[0]].append(buf[1])
            else:
                answers_dict[buf[0]] = [buf[1]]

    right_answers_count = 0
    for question_num in right_answers:
        if right_answers[question_num] == answers_dict[question_num]:
            right_answers_count += 1

    info = {
        'right_answers_count': right_answers_count,
        'username': request.user.username
    }

    return render(request, 'main/student/testResult.html', info)
