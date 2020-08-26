# pylint: disable=import-error, line-too-long, pointless-string-statement,
"""
Some utils for views
"""
import os
import logging
import jwt
import requests
from bson import ObjectId
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpRequest
from .models import Test, Subject
from .mongo import get_conn, QuestionsStorage

logger = logging.getLogger('quizer.main.utils')


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
        'with_images': 'with_images' in request.POST,
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
                raise UnicodeDecodeError('invalid file format')
        parsed_questions_list.append({
            'formulation': formulation,
            'tasks_num': len(options),
            'multiselect': multiselect,
            'with_images': False,
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


def parse_tests_folder(folder: str):
    storage = QuestionsStorage.connect(db=get_conn())
    for folder in [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]:

        logger.info('Найдена папка с тестами к предмету %s...' % folder)
        subject = Subject(name=folder)
        subject.save()
        logger.info('Предмет %s добавлен в базу' % folder)

        for test_file in [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]:

            logger.info('Найден файл с тестом %s' % test_file)
            duration = int(input("Длительность теста (в секундах): "))
            tasks_num = int(input("Количество заданий: "))
            test = Test(
                name=test_file,
                duration=duration,
                tasks_num=tasks_num)
            test.save()
            logger.info('Тест %s по предмету %s добавлен в базу' % (test_file, folder))

            try:
                questions_list = parse_questions_file(test_file)
                for question in questions_list:
                    storage.add_one(question=question, test_id=test.id)
                logger.info('%s вопросов к тесту %s по предмету %s добавлены в базу' %
                            (len(questions_list), test_file, folder))
            except UnicodeDecodeError:
                logger.info('Ошибка при обработке файла с вопросами к тесту %s' % test_file)
