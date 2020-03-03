from django.shortcuts import render

# Create your views here.


def login(request):
    return render(request, 'main/login.html')


def index(request):
    info = {
        'account': request.POST['account'],
        'group': request.POST['group']
    }
    return render(request, 'main/index.html', info)
