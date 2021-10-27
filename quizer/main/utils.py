# pylint: disable=import-error, line-too-long, pointless-string-statement,
"""
Some utils for views
"""
import json
import math
import os
import pathlib
import re
from datetime import datetime
from operator import itemgetter
from typing import List, Dict, Tuple, Any, Union

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import transaction
from django.http import HttpRequest
from django.utils import timezone
from django.conf import settings

from .models import Test, Subject, Question, UserResult


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
            "bos": "Безопасность операционных систем",
            "bs": "Безопасность сетей",
            "c": "Языки программирования высокого уровня",
            "java": "Язык программирования Java",
            "sharp": "Язык программирования C#",
            "python": "Язык программирования python",
            "timp": "Технологии и методы программирования",
            "timp3": "Технологии и методы программирования, 3 семестр",
            "timp4": "Технологии и методы программирования, 4 семестр",
            "finish": "Выходной контроль",
            "parallel": "Параллельные вычисления",
        }.get(short_name, short_name)

    @staticmethod
    def get_questions_count(short_name: str) -> int:
        return {
            "bos": 10,
            "bs": 30,
            "c": 10,
            "java": 10,
            "sharp": 50,
            "python": 10,
            "timp": 10,
            "timp3": 8,
            "timp4": 10,
            "finish": 50,
            "parallel": 10,
        }.get(short_name, 10)

    @staticmethod
    def get_test_duration(short_name: str) -> int:
        return {
            "bos": 200,
            "bs": 900,
            "c": 200,
            "java": 200,
            "sharp": 3600,
            "python": 300,
            "timp": 600,
            "timp3": 480,
            "timp4": 300,
            "finish": 3600,
            "parallel": 200,
        }.get(short_name, 200)


def create_user(form_data: Dict[str, Any]) -> User:
    username = form_data["username"]
    password = form_data["password"]

    with transaction.atomic():
        user = User.objects.create_user(username=username)
        user.set_password(password)
        user.groups.add(2)
        user.save()

        profile = user.profile

        if re.match(r"^[\d]+_[\d]{4}$", form_data["group"]):
            # Student
            group, admission_year = [int(_) for _ in form_data["group"].split("_")]
        else:
            group, admission_year = int(form_data["group"]), 0

        profile.group = group
        profile.admission_year = admission_year

        profile.save(update_fields=["group", "admission_year"])

    return user


def get_group_results(subject_id: str, group: str, course: str) -> str:
    """
    Getting string with group testing results

    :param subject_id: id of current subject
    :param group: group number
    :param course: group course
    :return: string with results in CSV format
    """
    now = datetime.now()
    add_course = 1 if now.month >= 9 else 0

    tests = Test.objects.filter(subject__id=subject_id)
    tests_list = [
        [test.name, int((re.findall(r"\d", test.name) + ["0"])[0])] for test in tests
    ]
    tests_list.sort(key=itemgetter(1))
    test_position = {test[0]: 2 + pos for pos, test in enumerate(tests_list)}

    results_str = "Fullname,Номер по списку,"
    for test in tests_list[:-1]:
        results_str += f"{test[0]},"
    results_str += f"{tests_list[-1][0]}\n"

    results = UserResult.objects.filter(
        user__profile__group=group,
        user__profile__admission_year=now.year - int(course) + add_course,
        right_answers_count__gt=0,
        testing_result__subject__id=subject_id,
    )
    results_dict = {
        res["user_id"]: [
            str(res["user__profile__name"]),
            str(res["user__profile__number"]),
        ]
        + ["-"] * len(tests)
        for res in results.values(
            "user_id", "user__profile__number", "user__profile__name"
        )
    }
    for user_id in results_dict:
        user_results = results.filter(user__id=user_id)
        for res in user_results:
            test = res.testing_result.test
            if test in tests:
                test_pos = test_position[test.name]
                results_dict[res.user.id][
                    test_pos
                ] = f"{res.right_answers_count}/{res.tasks_num}"

    results_list = list(results_dict.values())
    results_list.sort(key=lambda res: int(res[1]))
    for row in results_list:
        results_str += ",".join(row) + "\n"
    return results_str


def split_questions(
    questions: List[Dict[str, Any]]
) -> List[Tuple[List[Dict[str, Any]], Union[int, float]]]:
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
        questions_group = questions[step : optional_group_size + step]
        questions_list.append((questions_group, idx * optional_group_size))
    return questions_list


def load_questions_list(request: HttpRequest, test_id: int) -> List[Dict[str, Any]]:
    """
    Parse request with loaded file with questions to questions list
    :param test_id: <Test> id
    :param request: <HttpRequest>
    :return: list of questions
    """
    content = request.FILES["file"].read().decode("utf-8")
    return parse_questions(content, test_id)


def parse_questions(content: str, test_id: int) -> List[Dict[str, Any]]:
    """
    Parse request with loaded file with questions to questions list

    :param content: str with questions
    :param test_id: id of <Test> instance
    :return: list of questions
    """
    questions_list = [
        question for question in content.replace("\r", "").split("\n\n") if question
    ]
    parsed_questions_list = []
    numbers = set("0123456789")
    cur_line = 0
    for question in questions_list:
        buf = [item for item in question.split("\n") if item]

        formulation = buf[0]
        cur_line += 1

        multiselect = False
        sequence = False
        options = []
        if len(buf[1:]) == 0:
            raise InvalidFileFormatError(
                f"строка {cur_line} - вопрос без вариантов ответа"
            )
        for line in buf[1:]:
            cur_line += 1  # Line with option

            if len(line) > 1 and line[1] != " ":
                err_str = f"строка {cur_line} - некорректный формат варианта ответа (пропущен пробел)"
                raise InvalidFileFormatError(err_str)

            option = line[2:]
            if not option:
                err_str = f"строка {cur_line} - некорректный формат варианта ответа (пустой вариант ответа)"
                raise InvalidFileFormatError(err_str)

            if line[0] == "-":
                options.append({"option": option, "is_true": False})
            elif line[0] == "*":
                options.append({"option": option, "is_true": True})
            elif line[0] == "+":
                multiselect = True
                options.append({"option": option, "is_true": True})
            elif line[0] in numbers:
                sequence = True
                num = line.split()[0]
                options.append({"option": option, "num": int(num), "is_true": True})
            else:
                err_str = f"строка {cur_line} - некорректный формат варианта ответа (вопроса не определен)"
                raise InvalidFileFormatError(err_str)
        options_set = set([_["option"] for _ in options])
        if len(options) != len(options_set):
            raise InvalidFileFormatError(
                f"строка {cur_line} - повторяющиеся варианты ответов"
            )
        parsed_questions_list.append(
            {
                "test_id": test_id,
                "formulation": formulation,
                "tasks_num": len(options),
                "multiselect": multiselect,
                "type": Question.Type.SEQUENCE if sequence else Question.Type.REGULAR,
                "options": options,
            }
        )
        cur_line += 1  # Empty string between questions
    return parsed_questions_list


def make_database_dump() -> pathlib.Path:
    """
    Make database dump and return path to dump

    :return: path to database dump file
    """
    dump_filename = pathlib.Path(
        f'{settings.DATABASE_DUMP_ROOT}/quizer_{timezone.now().strftime("%d-%m-%y_%H-%M")}.json'
    )
    if not dump_filename.exists():
        os.makedirs(dump_filename.parent, exist_ok=True)

    with open(dump_filename, "w") as dump_file:
        call_command(command_name="dumpdata", format="json", indent=4, stdout=dump_file)

    return dump_filename


def save_database_dump(file) -> pathlib.Path:
    """
    Save loaded database dump and return path to dump

    :return: path to database dump file
    """
    dump_filename = pathlib.Path(f"{settings.DATABASE_DUMP_ROOT}/{file.name}")
    if not dump_filename.exists():
        os.makedirs(dump_filename.parent, exist_ok=True)
    with open(dump_filename, "w") as dump_file:
        data = json.loads(file.read())
        json.dump(data, dump_file, indent=4)
    return dump_filename


def get_test_result(
    request: HttpRequest, right_answers: List[Dict[str, Any]], test_duration: int
) -> Dict[str, Any]:
    """
    Get testing result from HttpRequest object

    :param request: <HttpRequest>
    :param right_answers: list of dicts with right answers
    :param test_duration: <int>< duration of passed test
    :return: dict with testing result
    """
    response = dict(request.POST)
    time = int(response.get("time", ["0"])[0])

    numbers = set("0123456789")
    answers = {}
    for key in response:
        """
        'key' for multiselect: {question_num}_{selected_option}: ['on']
        'key' for single: {question_num}: ['{selected_option}']
        """
        buf = key.split("_")
        if buf[0] in numbers:
            question_num = int(buf[0])
            if len(buf) == 1:
                if len(response[key]) > 1:
                    answers[question_num] = response[key]
                else:
                    answers[question_num] = [response[key][0]]
            else:
                option = "_".join(buf[1:])
                if question_num in answers:
                    answers[question_num].append(option)
                else:
                    answers[question_num] = [option]

    right_answers_count = 0
    questions = []
    for right_answer in right_answers:
        question_num = right_answer["question_num"]
        questions.append(
            {
                "question_id": right_answer["question_id"],
                "selected_options": answers[question_num]
                if question_num in answers
                else [],
                "right_options": [
                    item["option"] for item in right_answer["right_options"]
                ],
            }
        )
        if question_num in answers:
            if [_["option"] for _ in right_answer["right_options"]] == answers[
                question_num
            ]:
                right_answers_count += 1
                questions[-1]["is_true"] = True
        else:
            questions[-1]["is_true"] = False
    return {
        "user": request.user,
        "time": test_duration - time,
        "tasks_num": len(right_answers),
        "right_answers_count": right_answers_count,
        "questions": questions,
    }


def add_subject_with_tests(request: HttpRequest) -> str:
    """
    Get information about new subject and test for it from HttpRequest object

    :param request: <HttpRequest>
    :return: str with results of loading
    """
    short_name = request.POST["name"]
    name = SubjectParser.get_name(short_name)
    subject = Subject(name=name, description=request.POST["description"])
    subject.save()
    tests_count = 0
    questions_count = 0

    files_names = request.POST["files_names"].split("<separator>")
    for test_name, test_data in zip(files_names, request.FILES.getlist("tests")):
        duration = SubjectParser.get_test_duration(short_name)
        tasks_num = SubjectParser.get_questions_count(short_name)
        test = Test(
            subject=subject, name=test_name, duration=duration, tasks_num=tasks_num
        )
        test.save()
        tests_count += 1
        try:
            questions_list = parse_questions(
                test_data.read().decode("utf-8"), test_id=test.id
            )
            for question in questions_list:
                Question.objects.create(
                    formulation=question.get("formulation"),
                    multiselect=question.get("multiselect"),
                    tasks_num=question.get("tasks_num"),
                    type=question.get("type"),
                    options=Question.parse_options(question.get("options")),
                    test=test,
                )
            questions_count += len(questions_list)
        except UnicodeDecodeError as e:
            print(
                "%s - ошибка при обработке файла с вопросами к тесту %s"
                % (e, test_name)
            )
        except InvalidFileFormatError as e:
            print(
                "%s - ошибка при обработке файла с вопросами к тесту %s"
                % (e, test_name)
            )
    message = "Предмет '%s', %d тестов и %d вопросов к ним успешно добавлены."
    return message % (subject.name, tests_count, questions_count)
