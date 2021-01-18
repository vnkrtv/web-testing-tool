# pylint: disable=import-error, line-too-long, pointless-string-statement,
"""
Some utils for views
"""
import json

import jwt
import requests
from bson import ObjectId

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpRequest
from django.conf import settings

from .models import Test, Subject, QuestionType
from .mongo import get_conn, QuestionsStorage


class InvalidFileFormatError(Exception):
    pass


class SubjectParser:
    """
    Some constants for subjects parser
    """

    @staticmethod
    def get_name(short_name: str) -> str:
        return {
            'bos': 'Безопасность операционных систем',
            'bs': 'Безопасность сетей',
            'c': 'Языки программирования высокого уровня',
            'java': 'Язык программирования Java',
            'sharp': 'Язык программирования C#',
            'python': 'Язык программирования python',
            'timp': 'Технологии и методы программирования',
            'timp3': 'Технологии и методы программирования, 3 семестр',
            'timp4': 'Технологии и методы программирования, 4 семестр',
            'finish': 'Выходной контроль',
            'parallel': 'Параллельные вычисления'
        }.get(short_name, short_name)

    @staticmethod
    def get_questions_count(short_name: str) -> int:
        return {
            'bos': 10,
            'bs': 30,
            'c': 10,
            'java': 10,
            'sharp': 50,
            'python': 10,
            'timp': 10,
            'timp3': 8,
            'timp4': 10,
            'finish': 50,
            'parallel': 10
        }.get(short_name, 10)

    @staticmethod
    def get_test_duration(short_name: str) -> int:
        return {
            'bos': 200,
            'bs': 900,
            'c': 200,
            'java': 200,
            'sharp': 3600,
            'python': 300,
            'timp': 600,
            'timp3': 480,
            'timp4': 300,
            'finish': 3600,
            'parallel': 200
        }.get(short_name, 200)


def get_auth_data(request: HttpRequest) -> tuple:
    """
    Get user's username and group using 'user_jqt' cookies

    :param request: <HttpRequest>
    :return: tuple(username: str, group: str)
    """
    user_jwt = request.COOKIES.get('user_jwt', '')
    key_id = jwt.get_unverified_header(user_jwt).get('kid')
    public_key = requests.get(settings.AUTH_URL + key_id).text
    decoded_jwt = jwt.decode(user_jwt, public_key, algorithms='RS256')
    username = decoded_jwt.get('username', '')
    group = decoded_jwt.get('group', '')
    return username, group


def get_question_from_request(request: HttpRequest, test: Test) -> dict:
    """
    Parse request with new question params to question dict

    :param request: <HttpRequest>
    :param test: <Test>
    :return: question
    """
    with_images = request.POST['withImages'] == 'true'
    question = {
        '_id': ObjectId(),
        'formulation': request.POST['formulation'],
        'tasks_num': int(request.POST['tasksNum']),
        'multiselect': request.POST['multiselect'] == 'true',
        'type': QuestionType.WITH_IMAGES if with_images else QuestionType.REGULAR
    }
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
    if not with_images:
        question['options'] = json.loads(request.POST['options'])
    else:
        options = []
        for i, file_name in enumerate(request.FILES):
            path = f'{test.subject.name}/{test.name}/{question["_id"]}/{i}.{file_name.split(".")[-1]}'
            default_storage.save(path, ContentFile(request.FILES[file_name].read()))
            options.append({
                'option': path,
                'is_true': request.POST[file_name] == 'true'
            })
        question['options'] = options
    return question


def parse_questions(content: str) -> list:
    """
    Parsing string with questions to questions list

    :param content: string with questions
    :return: questions list
    """
    questions_list = content.split('\n\n')
    parsed_questions_list = []
    if '' in questions_list:
        questions_list.remove('')
    numbers = set('0123456789')
    for question in questions_list:
        buf = question.split('\n')
        if '' in buf:
            buf.remove('')
        formulation = buf[0]
        multiselect = False
        sequence = False
        options = []
        for line in buf[1:]:
            if line[0] == '-':
                options.append({
                    'option': line.split('-')[1][1:],
                    'is_true': False
                })
            elif line[0] == '*':
                options.append({
                    'option': line.split('*')[1][1:],
                    'is_true': True
                })
            elif line[0] == '+':
                multiselect = True
                options.append({
                    'option': line.split('+')[1][1:],
                    'is_true': True
                })
            elif line[0] in numbers:
                sequence = True
                num = line.split()[0]
                options.append({
                    'option': line.split(num)[1][1:],
                    'num': int(num),
                    'is_true': True
                })
            else:
                raise InvalidFileFormatError('invalid file format')
        parsed_questions_list.append({
            'formulation': formulation,
            'tasks_num': len(options),
            'multiselect': multiselect,
            'type': QuestionType.SEQUENCE if sequence else QuestionType.REGULAR,
            'options': options
        })
    return parsed_questions_list


def get_questions_list(request: HttpRequest) -> list:
    """
    Parse request with loaded file with questions to questions list

    :param request: <HttpRequest>
    :return: list of questions
    """
    content = request.FILES['file'].read().decode('utf-8')
    return parse_questions(content)


def get_test_result(request: HttpRequest, right_answers: dict, test_duration: int) -> dict:
    """
    Get testing result from HttpRequest object

    :param request: <HttpRequest>
    :param right_answers: dict with right_answers
    :param test_duration: <int>< duration of passed test
    :return: dict with testing result
    """
    response = dict(request.POST)
    response.pop('csrfmiddlewaretoken')
    time = response.get('time', ['0'])[0]

    answers = {}
    for key in response:
        """
            'key' for multiselect: {question_num}_{selected_option}: ['on']
            'key' for single: {question_num}: ['{selected_option}']
        """
        buf = key.split('_')
        if len(buf) == 1:
            if len(response[key]) > 1:
                answers[buf[0]] = response[key]
            else:
                answers[buf[0]] = [response[key][0]]
        else:
            option = '_'.join(buf[1:])
            if buf[0] in answers:
                answers[buf[0]].append(option)
            else:
                answers[buf[0]] = [option]

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
    return {
        'user_id': request.user.id,
        'username': request.user.username,
        'time': test_duration - int(time),
        'tasks_num': len(right_answers),
        'right_answers_count': right_answers_count,
        'questions': questions
    }


def parse_questions_file(file_name: str) -> list:
    """
    Parse file with questions to questions list

    :param file_name: name of file with questions
    :return: list of questions
    """
    with open(file_name, 'r') as f:
        content = f.read()
    return parse_questions(content)


def add_subject_with_tests(request: HttpRequest) -> str:
    """
    Get information about new subject and test for it from HttpRequest object

    :param request: <HttpRequest>
    :return: str with results of loading
    """
    storage = QuestionsStorage.connect(db=get_conn())

    short_name = request.POST['name']
    name = SubjectParser.get_name(short_name)
    subject = Subject(
        name=name,
        description=request.POST['description'])
    subject.save()
    tests_count = 0
    questions_count = 0

    files_names = request.POST['files_names'].split('<separator>')
    for test_name, test_data in zip(files_names, request.FILES.getlist('tests')):
        duration = SubjectParser.get_test_duration(short_name)
        tasks_num = SubjectParser.get_questions_count(short_name)
        test = Test(
            subject=subject,
            name=test_name,
            duration=duration,
            tasks_num=tasks_num)
        test.save()
        tests_count += 1
        try:
            questions_list = parse_questions(test_data.read().decode('utf-8'))
            for question in questions_list:
                storage.add_one(question=question, test_id=test.id)
            questions_count += len(questions_list)
        except UnicodeDecodeError:
            print('UnicodeDecodeError - ошибка при обработке файла с вопросами к тесту %s' % test_name)
        except InvalidFileFormatError:
            print \
                ('InvalidFileFormatError - ошибка при обработке файла с вопросами к тесту %s' % test_name)
    message = "Предмет '%s', %d тестов и %d вопросов к ним успешно добавлены."
    return message % (subject.name, tests_count, questions_count)
