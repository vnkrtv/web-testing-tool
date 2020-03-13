from django.shortcuts import render
from .models import Test, Task
import random


def login(request):
    return render(request, 'main/login.html')


def index(request):
    info = {
        'account': request.POST['account'],
        'group': request.POST['group']
    }
    return render(request, 'main/index.html', info)


def get_tests(request):
    return render(request, 'main/tests.html', {'tests': list(Test.objects.all())})


def get_marks(request):
    return render(request, 'main/marks.html')


def run_test(request):
    test = list(Test.objects.filter(name=request.POST['test_name']))[0]
    print(test)
    tasks = list(Task.objects.filter(test__name=test.name))
    tasks = random.sample(tasks, k=test.tasks_num)
    return render(request, 'main/runTest.html', {'tasks': tasks, 'test_duration': test.duration, 'test_name': test.name})


def test_result(request):
    query_dict = dict(request.POST)
    query_dict.pop('csrfmiddlewaretoken')
    test_name = query_dict.pop('test_name')[0]

    answers_dict = {int(answer.split('_')[0]): int(answer.split('_')[1]) for answer in query_dict}

    # TODO: rewrite dat shit
    tasks_dict = {}
    for task in list(Task.objects.filter(test__name=test_name)):
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

    return render(request, 'main/testResult.html', {'right_answers_count': right_answers_count})
