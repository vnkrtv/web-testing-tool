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
    return render(request, 'main/marks.html', info)


def run_test(request):
    test = Test.objects.filter(name=request.POST['test_name'])
    tasks = Task.objects.filter(test__name=test.name)
    random.choice(tasks, k=test.tasks_num)
    info = {}
    return render(request, 'main/runTest.html', info)
