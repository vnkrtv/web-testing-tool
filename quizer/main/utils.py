# pylint: disable=import-error, line-too-long, pointless-string-statement,
"""
Some utils for views
"""
import logging
import jwt
import requests
from bson import ObjectId
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpRequest
from django.urls import reverse

from .models import Test, Subject, QuestionType
from .mongo import get_conn, QuestionsStorage


logger = logging.getLogger('quizer.main.utils')


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
    logger.error('get_auth_data - get user_jwt cookie: %s' % user_jwt)
    key_id = jwt.get_unverified_header(user_jwt).get('kid')
    logger.error('get_auth_data - get key_id: %s' % key_id)
    public_key = requests.get(f'http://sms.gitwork.ru/auth/public_key/{key_id}').text
    logger.error('get_auth_data - get public key: %s' % public_key)
    decoded_jwt = jwt.decode(user_jwt, public_key, algorithms='RS256')
    logger.error('get_auth_data - decode JWT: %s' % decoded_jwt)
    username = decoded_jwt.get('username', '')
    group = decoded_jwt.get('group', '')
    return username, group


def parse_question_form(request: HttpRequest, test: Test) -> dict:
    """
    Parse request with new question params to question dict

    :param request: <HttpRequest>
    :param test: <Test>
    :return: question
    """
    question = {
        '_id': ObjectId(),
        'formulation': request.POST['question'],
        'tasks_num': request.POST['tasks_num'],
        'multiselect': 'multiselect' in request.POST,
        'type': QuestionType.WITH_IMAGES if 'with_images' in request.POST else QuestionType.REGULAR,
        'options': []
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
    if question['multiselect']:
        right_options_nums = [key.split('_')[2] for key in request.POST if 'is_true_' in key]
    else:
        right_options_nums = [request.POST['is_true']]
    if question['type'] == QuestionType.WITH_IMAGES:
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
    for question in questions_list:
        buf = question.split('\n')
        if '' in buf:
            buf.remove('')
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
                raise InvalidFileFormatError('invalid file format')
        parsed_questions_list.append({
            'formulation': formulation,
            'tasks_num': len(options),
            'multiselect': multiselect,
            'type': QuestionType.REGULAR,
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


def add_subject_with_tests(request: HttpRequest) -> dict:
    """
    Get information about new subject and test for it from HttpRequest object

    :param request: <HttpRequest>
    :return: response context
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
            logger.error('UnicodeDecodeError - ошибка при обработке файла с вопросами к тесту %s' % test_name)
        except InvalidFileFormatError:
            logger.error('InvalidFileFormatError - ошибка при обработке файла с вопросами к тесту %s' % test_name)
    message = "Предмет '%s', %d тестов и %d вопросов к ним успешно добавлены."
    context = {
        'title': 'Новый предмет | Quizer',
        'message_title': 'Новый предмет',
        'message': message % (subject.name, tests_count, questions_count),
        'ref': reverse('main:configure_subject'),
        'ref_message': 'Перейти к предметам',
    }
    return context
