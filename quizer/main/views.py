from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users
from .models import Test, MongoDB
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
        'username': request.user.username
    }
    return render(request, 'main/lecturer/addTest.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def edit_test(request):
    info = {
        'username': request.user.username
    }
    return render(request, 'main/lecturer/editTest.html', info)


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
            'error': 'Вопросов по данной теме меньше %d' % test.tasks_num,
            'username': request.user.username
        }
        return render(request, 'main/error.html', info)
    tasks = random.sample(tasks, k=test.tasks_num)

    info = {
        'tasks': tasks, 'test_duration': test.duration,
        'test_name': test.name,
        'username': request.user.username
    }
    return render(request, 'main/runTest.html', info)


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
