from django.shortcuts import render
from .models import Test, Task

def login(request):
    return render(request, 'main/login.html')


def index(request):
    info = {
        'account': request.POST['account'],
        'group': request.POST['group']
    }
    return render(request, 'main/index.html', info)


def get_tests(request):
    info = {
        'tests': list(Test.objects.all())
    }
    return render(request, 'main/tests.html', info)


def get_marks(request):
    info = {

    }
    return render(request, 'main/marks.html', info)