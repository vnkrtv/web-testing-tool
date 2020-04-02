# pylint: disable=import-error, line-too-long, missing-module-docstring, no-else-return, pointless-string-statement
import random
from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from .decorators import unauthenticated_user, allowed_users
from .models import Test, Subject, RunningTestsAnswersStorage, TestsResultsStorage, QuestionsStorage
from .config import MONGO_PORT, MONGO_HOST, MONGO_DBNAME


def login_page(request):
    """
    Displays login page
    """
    logout(request)
    return render(request, 'main/login.html')


@unauthenticated_user
def get_tests(request):
    """
    Page to which user is redirected after successful authorization
    For lecturer - displays list of tests that can be run
    For student - displays list of running tests
    """
    mdb = TestsResultsStorage.connect_to_mongodb(
        host=MONGO_HOST,
        port=MONGO_PORT,
        db_name=MONGO_DBNAME
    )
    running_tests_ids = mdb.get_running_tests_ids()
    if request.user.groups.filter(name='lecturer'):
        lecturers_tests = Test.objects.filter(author__username=request.user.username)
        not_running_lecturers_tests = filter(lambda test: test.id not in running_tests_ids, lecturers_tests)
        info = {
            'tests': list(not_running_lecturers_tests),
        }
        return render(request, 'main/lecturer/testsPanel.html', info)
    if len(running_tests_ids) == 0:
        info = {
            'title': 'Доступные тесты отсутствуют',
            'message': 'Ни один из тестов пока не запущен.',
        }
        return render(request, 'main/student/info.html', info)
    info = {
        'tests': [Test.objects.get(id=_id) for _id in running_tests_ids],
    }
    return render(request, 'main/student/tests.html', info)


def index(request):
    """
    In case of successful authorization redirect to get_tests page, else displays login page with error
    """
    if request.user.is_authenticated:
        return get_tests(request)
    if 'username' not in request.POST or 'password' not in request.POST:
        return render(request, 'main/login.html', {'error': 'Ошибка: неправильное имя пользователя или пароль!'})
    user = authenticate(
        username=request.POST['username'],
        password=request.POST['password']
    )
    if user is not None:
        if user.is_active:
            login(request, user)
            return get_tests(request)
        else:
            return render(request, 'main/login.html', {'error': 'Ошибка: аккаунт пользователя отключен!'})
    else:
        return render(request, 'main/login.html', {'error': 'Ошибка: неправильное имя пользователя или пароль!'})


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def run_test_result(request):
    """
    Displays page with test run result
    """
    test = Test.objects.get(name=request.POST['test_name'])
    mdb = TestsResultsStorage.connect_to_mongodb(
        host=MONGO_HOST,
        port=MONGO_PORT,
        db_name=MONGO_DBNAME
    )
    mdb.add_running_test(
        test_id=test.id,
        lecturer_id=request.user.id
    )
    info = {
        'title': 'Тест запущен',
        'message': "Состояние его прохождения можно отследить во вкладке 'Запущенные тесты'",
    }
    return render(request, 'main/lecturer/info.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def add_test(request):
    """
    Displays page with an empty form for filling out information about new test
    """
    return render(request, 'main/lecturer/addTest.html', {'subjects': list(Subject.objects.all())})


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
        duration=request.POST['duration']
    )
    test.save()
    info = {
        'title': 'Новый тест',
        'message': 'Тест %s по предмету %s успешно добавлен.' % (test.name, subject),
    }
    return render(request, 'main/lecturer/info.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def get_running_tests(request):
    """
    Displays page with running lecturer's tests
    """
    mdb = TestsResultsStorage.connect_to_mongodb(
        host=MONGO_HOST,
        port=MONGO_PORT,
        db_name=MONGO_DBNAME
    )
    running_tests_ids = mdb.get_running_tests_ids()
    lecturers_tests = Test.objects.filter(author__username=request.user.username)
    running_lecturers_tests = list(filter(lambda item: item.id in running_tests_ids, lecturers_tests))
    tests = []
    for test in running_lecturers_tests:
        results = mdb.get_running_test_results(
            test_id=test.id,
            lecturer_id=request.user.id
        )
        tests.append({
            'name': test.name,
            'description': test.description,
            'tasks_num': test.tasks_num,
            'duration': test.duration,
            'finished_students_num': len(results)
        })
    return render(request, 'main/lecturer/runningTests.html', {'tests': tests})


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def stop_running_test(request):
    """
    Displays page with results of passing stopped test
    """
    test = Test.objects.get(name=request.POST['test_name'])
    mdb = TestsResultsStorage.connect_to_mongodb(
        host=MONGO_HOST,
        port=MONGO_PORT,
        db_name=MONGO_DBNAME
    )
    results = mdb.get_running_test_results(
        test_id=test.id,
        lecturer_id=request.user.id
    )
    mdb.stop_running_test(
        test_id=test.id,
        lecturer_id=request.user.id
    )
    info = {
        'test': test,
        'results': results,
    }
    return render(request, 'main/lecturer/testingResults.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def edit_test(request):
    """
    Displays page with all lecturer's tests
    """
    info = {
        'tests': list(Test.objects.filter(author__username=request.user.username)),
    }
    return render(request, 'main/lecturer/editTest.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def edit_test_result(request):
    """
    Displays page with result of editing test
    """
    info = {
        'title': 'Окно редактирования теста',
        'message': 'Coming soon...',
    }
    return render(request, 'main/lecturer/info.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def add_question(request):
    """
    Displays page with an empty form for filling out information about new question
    """
    info = {
        'tests': list(Test.objects.filter(author__username=request.user.username)),
    }
    return render(request, 'main/lecturer/addQuestion.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def add_question_result(request):
    """
    Displays page with result of adding new question
    """
    test = Test.objects.get(name=request.POST['test'])
    question = {
        'formulation': request.POST['question'],
        'tasks_num': request.POST['tasks_num'],
        'multiselect': 'multiselect' in request.POST,
        'with_images': 'with_images' in request.POST,
        'options': []
    }
    print(request.POST)
    try:
        """
            request.POST:
            - option_{i} - possible answer
            - is_true_{t} - if exists in request.POST then option_{t} is true
        """
        options = {
            request.POST[key]: int(key.split('_')[1])
            for key in request.POST if 'option_' in key
        }
        # images - where store?
        if question['multiselect']:
            true_options = [int(key.split('_')[2]) for key in request.POST if 'is_true_' in key]
        else:
            true_options = [int(request.POST['is_true'])]
        for option_num in options:
            question['options'].append({
                'option': option_num,
                'is_true': options[option_num] in true_options
            })
        mdb = QuestionsStorage.connect_to_mongodb(
            host=MONGO_HOST,
            port=MONGO_PORT,
            db_name=MONGO_DBNAME
        )
        mdb.add_one(
            question=question,
            test_id=test.id
        )
    except KeyError:
        info = {
            'title': 'Ошибка',
            'message': 'Форма некорректно заполнена',
        }
        return render(request, 'main/lecturer/info.html', info)
    info = {
        'title': 'Новый вопрос',
        'message': "Вопрос '%s' к тесту '%s' успешно добавлен." % (question['formulation'], test.name),
    }
    return render(request, 'main/lecturer/info.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['student'])
def get_marks(request):
    """
    Displays page with students marks
    """
    info = {}
    return render(request, 'main/student/marks.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['student'])
def run_test(request):
    """
    Displays page with test for student
    """
    test = Test.objects.get(name=request.POST['test_name'])
    mdb = QuestionsStorage.connect_to_mongodb(
        host=MONGO_HOST,
        port=MONGO_PORT,
        db_name=MONGO_DBNAME
    )
    questions = mdb.get_many(test_id=test.id)
    if len(questions) < test.tasks_num:
        info = {
            'title': 'Ошибка',
            'message': 'Вопросов к данному тесту меньше %d' % test.tasks_num,
        }
        return render(request, 'main/student/info.html', info)
    questions = random.sample(questions, k=test.tasks_num)
    right_answers = {}
    for i, question in enumerate(questions):
        right_answers[str(i + 1)] = {
            'right_answers': [i + 1 for i, option in enumerate(question['options']) if option['is_true']],
            'id': str(question['_id'])
        }
    mdb = RunningTestsAnswersStorage.connect_to_mongodb(
        host=MONGO_HOST,
        port=MONGO_PORT,
        db_name=MONGO_DBNAME
    )
    mdb.add(
        right_answers=right_answers,
        test_id=test.id,
        user_id=request.user.id
    )
    info = {
        'questions': questions, 'test_duration': test.duration,
        'test_name': test.name,
        'right_answers': right_answers,
    }
    return render(request, 'main/student/runTest.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['student'])
def test_result(request):
    """
    Displays page with results of passing test
    """
    mdb = RunningTestsAnswersStorage.connect_to_mongodb(
        host=MONGO_HOST,
        port=MONGO_PORT,
        db_name=MONGO_DBNAME
    )
    passed_test_answers = mdb.get(user_id=request.user.id)
    right_answers = passed_test_answers['right_answers']
    test_id = passed_test_answers['test_id']
    mdb.delete(user_id=request.user.id)

    response = dict(request.POST)
    response.pop('csrfmiddlewaretoken')
    time = response.pop('time')[0]

    answers = {}
    for key in response:
        """
            'key' for multiselect: {question_num}_{selected_option}: True/False
            'key' for single: {question_num}: True/False
        """
        buf = key.split('_')
        if len(buf) == 1:
            answers[buf[0]] = [int(answers[key][0])]
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
            'selected_answers': answers[question_num],
            'right_answers': right_answers[question_num]['right_answers']
        })
        if right_answers[question_num]['right_answers'] == answers[question_num]:
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
    mdb = TestsResultsStorage.connect_to_mongodb(
        host=MONGO_HOST,
        port=MONGO_PORT,
        db_name=MONGO_DBNAME
    )
    mdb.add_results_to_running_test(
        test_result=result,
        test_id=test_id
    )
    return render(request, 'main/student/testResult.html', {'right_answers_count': right_answers_count})
