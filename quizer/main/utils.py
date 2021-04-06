# pylint: disable=import-error, line-too-long, pointless-string-statement,
"""
Some utils for views
"""
import math
from typing import List, Dict, Tuple, Any, Union

import jwt
import requests

from django.http import HttpRequest
from django.conf import settings

from .models import Test, Subject, Question
from .mongo import get_conn, QuestionsStorage


class EmptyOptionsError(Exception):
    """
    Handling exceptions during questions file parsing
    """


class InvalidFileFormatError(Exception):
    """
    Handling exceptions during questions file parsing
    """


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


def get_auth_data(request: HttpRequest) -> Tuple[str, str]:
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


def split_questions(questions: List[Dict[str, Any]]) -> List[Tuple[List[Dict[str, Any]], Union[int, float]]]:
    """
    Split questions list into grouped list of questions lists

    :param questions: questions list
    :return: grouped list of questions
    """
    max_group_size = 25
    group_size = math.ceil(len(questions) / max_group_size)
    optional_group_size = math.ceil(len(questions) / group_size)
    questions_list = []
    for idx, step in enumerate(range(0, len(questions), optional_group_size)):
        questions_group = questions[step: optional_group_size + step]
        questions_list.append((questions_group, idx * optional_group_size))
    return questions_list


def load_questions_list(request: HttpRequest, test_id: int) -> List[Dict[str, Any]]:
    """
    Parse request with loaded file with questions to questions list

    :param request: <HttpRequest>
    :param test_id: id of <Test> instance
    :return: list of questions
    """
    content = request.FILES['file'].read().decode('utf-8')
    questions_list = [question for question in content.replace('\r', '').split('\n\n') if question]
    parsed_questions_list = []
    numbers = set('0123456789')
    cur_line = 0
    for question in questions_list:
        buf = [item for item in question.split('\n') if item]

        formulation = buf[0]
        cur_line += 1

        multiselect = False
        sequence = False
        options = []
        if len(buf[1:]) == 0:
            raise InvalidFileFormatError(f'строка {cur_line} - вопрос без вариантов ответа')
        for line in buf[1:]:
            cur_line += 1  # Line with option

            if len(line) > 1 and line[1] != ' ':
                err_str = f'строка {cur_line} - некорректный формат варианта ответа (пропущен пробел)'
                raise InvalidFileFormatError(err_str)

            option = line[2:]
            if not option:
                err_str = f'строка {cur_line} - некорректный формат варианта ответа (пустой вариант ответа)'
                raise InvalidFileFormatError(err_str)

            if line[0] == '-':
                options.append({
                    'option': option,
                    'is_true': False
                })
            elif line[0] == '*':
                options.append({
                    'option': option,
                    'is_true': True
                })
            elif line[0] == '+':
                multiselect = True
                options.append({
                    'option': option,
                    'is_true': True
                })
            elif line[0] in numbers:
                sequence = True
                num = line.split()[0]
                options.append({
                    'option': option,
                    'num': int(num),
                    'is_true': True
                })
            else:
                err_str = f'строка {cur_line} - некорректный формат варианта ответа (вопроса не определен)'
                raise InvalidFileFormatError(err_str)
        options_set = set([_['option'] for _ in options])
        if len(options) != len(options_set):
            raise InvalidFileFormatError(f'строка {cur_line} - повторяющиеся варианты ответов')
        parsed_questions_list.append({
            'test_id': test_id,
            'formulation': formulation,
            'tasks_num': len(options),
            'multiselect': multiselect,
            'type': Question.Type.SEQUENCE if sequence else Question.Type.REGULAR,
            'options': options
        })
        cur_line += 1  # Empty string between questions
    return parsed_questions_list


def get_test_result(request: HttpRequest, right_answers: dict, test_duration: int) -> Dict[str, Any]:
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


def parse_questions_file(file_name: str) -> List[Dict[str, Any]]:
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
        except UnicodeDecodeError as e:
            print('%s - ошибка при обработке файла с вопросами к тесту %s' % (e, test_name))
        except InvalidFileFormatError as e:
            print('%s - ошибка при обработке файла с вопросами к тесту %s' % (e, test_name))
    message = "Предмет '%s', %d тестов и %d вопросов к ним успешно добавлены."
    return message % (subject.name, tests_count, questions_count)
