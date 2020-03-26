from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from .decorators import unauthenticated_user, allowed_users
from .models import Test, Subject, MongoDB
from .config import MONGO_PORT, MONGO_HOST
from pymongo.errors import ServerSelectionTimeoutError
import random


def login_page(request):
    logout(request)
    return render(request, 'main/login.html')


@unauthenticated_user
def get_tests(request):
    if request.user.groups.filter(name='lecturer'):
        info = {
            'tests': list(Test.objects.filter(author__username=request.user.username)),
            'username': request.user.username
        }
        return render(request, 'main/lecturer/testsPanel.html', info)
    if request.user.groups.filter(name='student'):
        info = {
            'tests': list(Test.objects.all()),
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
        subject=Subject.objects.get(name=subject).id,
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
    t = Test.objects.get(name='ПЗ1')
    d = mdb.get_questions(
        subject_id=t.subject_id,
        test_id=t.id
    )
    info = {
        'title': 'Успех!',
        'message': d,#'Тест %s по теме %s успешно добавлен' % ('', ''),
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
            true_options = [request.POST['is_true']]

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
            subject_id=test.subject_id,
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
    tasks = list()#Task.objects.filter(test__name=test.name))

    if len(tasks) < test.tasks_num:
        info = {
            'title': 'Ошибка',
            'message': 'Вопросов по данной теме меньше %d' % test.tasks_num,
            'username': request.user.username
        }
        return render(request, 'main/student/info.html', info)
    tasks = random.sample(tasks, k=test.tasks_num)

    info = {
        'tasks': tasks, 'test_duration': test.duration,
        'test_name': test.name,
        'username': request.user.username
    }
    return render(request, 'main/student/runTest.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['student'])
def test_result(request):
    query_dict = dict(request.POST)
    query_dict.pop('csrfmiddlewaretoken')
    test_name = query_dict.pop('test_name')[0]

    answers_dict = {int(answer.split('_')[0]): int(answer.split('_')[1]) for answer in query_dict}

    # TODO: rewrite dat shit
    tasks_dict = {}
    for task in list():#Task.objects.filter(test__name=test_name)):
        if task.options_1.is_true:
            tasks_dict[task.id] = 1
        elif task.options_2.is_true:
            tasks_dict[task.id] = 2
        elif task.options_3.is_true:
            tasks_dict[task.id] = 3
        elif task.options_4.is_true:
            tasks_dict[task.id] = 4

    right_answers_count = 0
    for task_id in answers_dict:
        right_answers_count += 1 if answers_dict[task_id] != tasks_dict[task_id] else 0

    info = {
        'right_answers_count': right_answers_count,
        'username': request.user.username
    }

    return render(request, 'main/testResult.html', info)
