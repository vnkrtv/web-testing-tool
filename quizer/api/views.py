import sys
import traceback

import bson

from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import Subject, Test, Question, TestResult, RunningTestsAnswers
from main import utils
from .serializers import SubjectSerializer, TestSerializer, QuestionSerializer, TestResultSerializer
from .permissions import IsLecturer


class SubjectView(APIView):
    permission_classes = [IsAuthenticated, IsLecturer]

    def get(self, _):
        serializer = SubjectSerializer(Subject.objects.all(), many=True)
        for subject in serializer.data:
            subject['tests_count'] = Test.objects.filter(subject=subject['id']).count()
        return Response({
            'subjects': serializer.data
        })

    def post(self, request):
        if request.data.get('load'):
            message = utils.add_subject_with_tests(request)
            return Response({
                'success': message
            })
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            new_subject = serializer.save()
        return Response({
            'success': "Предмет '%s' успешно добавлен." % new_subject.name
        })

    def put(self, request, subject_id):
        updated_subject = get_object_or_404(Subject.objects.all(), pk=subject_id)
        serializer = SubjectSerializer(instance=updated_subject, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            updated_subject = serializer.save()
        return Response({
            'success': "Предмет '%s' был успешно отредактирован." % updated_subject.name
        })

    def delete(self, _, subject_id):
        subject = get_object_or_404(Subject.objects.all(), pk=subject_id)
        message = "Учебный предмет '%s', а также все тесты и вопросы, " \
                  "относящиеся к нему, были успешно удалены." % subject.name
        subject.delete()
        return Response({
            'success': message
        })


class TestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        state = request.query_params.get('state', None)
        if state == 'running':
            tests = Test.get_running_tests()
        elif state == 'not_running':
            tests = Test.get_not_running_tests()
        else:
            tests = Test.get_all()
        return Response({
            'tests': tests
        })

    def post(self, request):
        serializer = TestSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            new_test = serializer.save()
        return Response({
            'success': "Тест '%s' по предмету '%s' успешно добавлен." %
                       (new_test.name, new_test.subject.name)
        })

    def put(self, request, test_id):
        updated_test = get_object_or_404(Test.objects.all(), pk=test_id)
        serializer = TestSerializer(instance=updated_test, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            updated_test = serializer.save()
        return Response({
            'success': "Тест '%s' по предмету '%s' был успешно отредактирован." %
                       (updated_test.name, updated_test.subject.name)
        })

    def delete(self, _, test_id):
        test = get_object_or_404(Test.objects.all(), pk=test_id)
        message = "Тест '%s' по предмету '%s', а также все " \
                  "вопросы к нему были успешно удалены." % (test.name, test.subject.name)
        test.delete()
        return Response({
            'success': message
        })


class LaunchTestView(APIView):
    permission_classes = [IsAuthenticated, IsLecturer]

    def put(self, request, test_id):
        test = get_object_or_404(Test.objects.all(), pk=test_id)
        if test.questions.count() < test.tasks_num:
            return Response({
                'ok': False,
                'message': "Тест %s не запущен, так как вопросов в базе меньше %d."
                           % (test.name, test.tasks_num)
            })
        TestResult.objects.create(
            test=test,
            launched_lecturer=request.user,
            subject=test.subject,
            is_running=True,
            comment=request.data.get('comment', ''),
            results=[])
        message = "Тест '%s' запущен. Состояние его прохождения можно отследить во вкладке 'Запущенные тесты'."
        return Response({
            'ok': True,
            'message': message % test.name
        })


class QuestionView(APIView):
    permission_classes = [IsAuthenticated, IsLecturer]

    def get(self, request, test_id):
        questions = Question.objects.filter(test__id=test_id)
        serializer = QuestionSerializer(instance=questions, many=True)
        return Response({
            'questions': serializer.data
        })

    def post(self, request, test_id):
        serializer = QuestionSerializer()
        try:
            if request.POST.get('load'):
                questions = utils.load_questions_list(request, test_id)
                for question in questions:
                    serializer.create(question)
                message = "Вопросы к тесту в количестве %d успешно добавлены." % len(questions)
                return Response({
                    'success': message
                })
            question = serializer.create_from_request(request)
            message = "Вопрос '%s' к тесту '%s' успешно добавлен."
            return Response({
                'success': message % (question.formulation, question.test.name)
            })
        except utils.EmptyOptionsError:
            return Response({
                'error': f'Вопрос не был добавлен, так как присутствуют пустые варианты ответов.'
            })
        except UnicodeDecodeError:
            return Response({
                'error': f'Файл некорректного формата.'
            })
        except utils.InvalidFileFormatError as e:
            return Response({
                'error': f'Вопросы не были загружены: {e}'
            })

    def put(self, request, test_id, question_id):
        try:
            _id = bson.ObjectId(question_id)
        except bson.errors.InvalidId:
            return Response({
                'error': 'Некорректный questions_id'
            })
        question = get_object_or_404(Question.objects.all(), _id=_id)
        serializer = QuestionSerializer(instance=question, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            updated_question = serializer.save()
        message = "Вопрос '%s' по тесту '%s' был успешно отредактирован."
        return Response({
            'success': message % (updated_question.formulation, updated_question.test.name)
        })

    def delete(self, request, test_id, question_id):
        try:
            _id = bson.ObjectId(question_id)
        except bson.errors.InvalidId:
            return Response({
                'error': 'Некорректный questions_id'
            })
        question = get_object_or_404(Question.objects.all(), _id=_id)
        message = "Вопрос '%s' по тесту '%s' был успешно удален." % (question.formulation, question.test.name)
        question.delete()
        return Response({
            'success': message
        })


class TestsResultView(APIView):
    permission_classes = [IsAuthenticated, IsLecturer]

    def get(self, request):
        try:
            test_results_id = request.query_params.get('id', None)
            if test_results_id:
                try:
                    _id = bson.ObjectId(test_results_id)
                except bson.errors.InvalidId:
                    return Response({
                        'error': 'Некорректный test_results_id'
                    })
                serializer = TestResultSerializer(TestResult.objects.filter(_id=_id), many=True)
            else:
                serializer = TestResultSerializer(TestResult.objects.all(), many=True)
            return Response({
                'results': serializer.data
            })
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            return Response({
                'error': 'Error: {e}\n' + '\n'.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            })


class RunningTestView(APIView):
    permission_classes = [IsAuthenticated, IsLecturer]

    def get(self, request):
        running_tests = []
        serializer = TestResultSerializer(TestResult.objects.filter(is_running=True), many=True)
        for test_results in serializer.data:
            if test_results['launched_lecturer_id'] == request.user.id:
                results = test_results['results']
                results.sort(key=lambda res: res.date)
                test = Test.objects.get(id=test_results['test_id'])
                running_tests.append({
                    **test.to_dict(),
                    'finished_students_results': results
                })
        return Response({
            'tests': running_tests
        })
