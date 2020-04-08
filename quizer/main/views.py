# pylint: disable=import-error, line-too-long, no-else-return, pointless-string-statement, relative-beyond-top-level
"""
Quizer templates rendering functions
"""
import random
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from bson import ObjectId
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
    mdb = QuestionsStorage.connect_to_mongodb(
        host=MONGO_HOST,
        port=MONGO_PORT,
        db_name=MONGO_DBNAME
    )
    tests = []
    for test in list(Test.objects.filter(author__username=request.user.username)):
        tests.append({
            'name': test.name,
            'description': test.description,
            'tasks_num': test.tasks_num,
            'duration': test.duration,
            'questions_num': len(mdb.get_many(test_id=test.id))
        })
    return render(request, 'main/lecturer/editTest.html', {'tests': tests})


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def edit_test_redirect(request):
    """
    Redirecting 'lecturer' to specific page depending on his choose
    """
    test = Test.objects.get(name=request.POST['test_name'])
    mdb = QuestionsStorage.connect_to_mongodb(
        host=MONGO_HOST,
        port=MONGO_PORT,
        db_name=MONGO_DBNAME
    )
    questions = [question['formulation'] for question in mdb.get_many(test_id=test.id)]
    info = {
        'test': Test.objects.get(name=request.POST['test_name']),
        'questions': questions
    }
    template = {
        'edit_test_btn': 'editingTestPage',
        'del_test_btn': 'deleteTestPage',
        'del_qstn_btn': 'deleteQuestionPage'
    }[request.POST["btn"]]
    return render(request, f'main/lecturer/{template}.html', info)


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
        duration=request.POST['duration']
    )
    Test.delete(test)
    new_test.save()
    info = {
        'title': 'Редактиктирование теста',
        'message': "Тест '%s' по предмету '%s' успешно изменен." % (new_test.name, new_test.subject),
    }
    return render(request, 'main/lecturer/info.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def delete_question_result(request):
    """
    Displays page with result of deleting question
    """
    request_dict = dict(request.POST)
    request_dict.pop('csrfmiddlewaretoken')
    test = Test.objects.get(id=request_dict.pop('test_id')[0])
    mdb = QuestionsStorage.connect_to_mongodb(
        host=MONGO_HOST,
        port=MONGO_PORT,
        db_name=MONGO_DBNAME
    )
    for question_formulation in request_dict:
        mdb.delete_one(
            question_formulation=question_formulation,
            test_id=test.id
        )
    info = {
        'title': 'Результат удаления',
        'message': "Вопросы к тесту '%s' в количестве %d были успешно удалены." % (test.name, len(request_dict))
    }
    return render(request, 'main/lecturer/info.html', info)


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def delete_test_result(request):
    """
    Displays page with result of deleting test
    """
    test = Test.objects.get(id=request.POST['test_id'])
    if 'del' in request.POST:
        mdb = QuestionsStorage.connect_to_mongodb(
            host=MONGO_HOST,
            port=MONGO_PORT,
            db_name=MONGO_DBNAME
        )
        deleted_questions_count = mdb.delete_many(test_id=test.id)
        info = {
            'title': 'Результат удаления',
            'message': "Тест '%s' и %d вопросов к нему были успешно удалены." % (test.name, deleted_questions_count)
        }
        Test.delete(test)
        return render(request, 'main/lecturer/info.html', info)
    return redirect('/edit_test')


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def add_question(request):
    """
    Displays page with an empty form for filling out information about new question
    """
    info = {
        'tests': list(Test.objects.filter(author__username=request.user.username))
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
@allowed_users(allowed_roles=['lecturer'])
def load_questions(request):
    """
    Displays page with an empty form for loading questions from file
    """
    tests = Test.objects.filter(author__username=request.user.username)
    return render(request, 'main/lecturer/loadQuestions.html', {'tests': tests})


@unauthenticated_user
@allowed_users(allowed_roles=['lecturer'])
def load_questions_result(request):
    """
    Displays result of loading questions from file
    """
    test = Test.objects.get(name=request.POST['test'])
    mdb = QuestionsStorage.connect_to_mongodb(
        host=MONGO_HOST,
        port=MONGO_PORT,
        db_name=MONGO_DBNAME
    )
    try:
        content = request.FILES['file'].read().decode('utf-8')
        questions_list = content.split('\n\n')
        questions_list.remove('')
        questions_count = 0
        for question in questions_list:
            buf = question.split('\n')
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
            mdb.add_one(
                question={
                    'formulation': formulation,
                    'tasks_num': len(options),
                    'multiselect': multiselect,
                    'with_images': False,
                    'options': options
                },
                test_id=test.id
            )
    except UnicodeDecodeError:
        info = {
            'title': 'Ошибка',
            'message': 'Файл некорректного формата.',
        }
        return render(request, 'main/lecturer/info.html', info)

    info = {
        'title': 'Новые вопросы',
        'message': "Вопросы к тесту '%s' в количестве %d успешно добавлены." % (test.name, questions_count),
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
            'right_answers': [str(i + 1) for i, option in enumerate(question['options']) if option['is_true']],
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
        'questions': questions,
        'test_duration': test.duration,
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
            'right_answers': right_answers[question_num]['right_answers']
        })
        if question_num in answers and right_answers[question_num]['right_answers'] == answers[question_num]:
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
