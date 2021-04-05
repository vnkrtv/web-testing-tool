import json

from django.contrib.auth.models import User

from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import Subject, Test, Question, TestResult, RunningTestsAnswers
from main import mongo, utils
from .serializers import SubjectSerializer, TestSerializer
from .permissions import IsLecturer


class SubjectView(APIView):
    permission_classes = [IsAuthenticated, IsLecturer]

    def get(self, _):
        subjects = Subject.objects.all()
        serializer = SubjectSerializer(subjects, many=True)
        for subject in serializer.data:
            subject['tests_count'] = Test.objects.filter(subject=subject['id']).count()
        return Response({
            'subjects': serializer.data
        })

    def post(self, request):
        if request.POST.get('load'):
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
    authentication_classes = []
    permission_classes = []

    # permission_classes = [IsAuthenticated]

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

    def get(self, request, pk):
        test = get_object_or_404(Test.objects.all(), pk=pk)
        storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
        questions = storage.get_many(test_id=test.id)
        if len(questions) < test.tasks_num:
            return Response({
                'ok': False,
                'message': "Тест %s не запущен, так как вопросов в базе меньше %d."
                           % (test.name, test.tasks_num)
            })
        else:
            storage = mongo.TestsResultsStorage.connect(db=mongo.get_conn())
            storage.add_running_test(
                test_id=test.id,
                lecturer_id=request.user.id,
                subject_id=test.subject.id)
            message = "Тест '%s' запущен. Состояние его прохождения можно отследить во вкладке 'Запущенные тесты'."
            return Response({
                'ok': True,
                'message': message % test.name
            })


class QuestionView(APIView):
    permission_classes = [IsAuthenticated, IsLecturer]

    def get(self, _, test_id):
        test = get_object_or_404(Test.objects.all(), pk=test_id)
        storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
        test_questions = storage.get_many(test_id=test.id)
        for question in test_questions:
            question['id'] = str(question.pop('_id'))
        return Response({
            'questions': test_questions
        })

    def post(self, request, test_id, question_id):
        test = get_object_or_404(Test.objects.all(), pk=test_id)
        storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())

        request_dict = dict(request.POST)
        if len(request_dict) == 1 and not request.FILES:  # DELETE, only csrftoken passed
            question = storage.get_one(
                question_id=question_id,
                test_id=int(test_id))
            storage.delete_by_id(
                question_id=question_id,
                test_id=int(test_id))
            message = "Вопрос '%s' по тесту '%s' был успешно удален."
            return Response({
                'success': message % (question['formulation'], test.name)
            })
        elif question_id == 'new':  # POST
            try:
                question = utils.get_question_from_request(
                    request=request,
                    test=test)
                storage.add_one(
                    question=question,
                    test_id=test.id)
                message = "Вопрос '%s' к тесту '%s' успешно добавлен."
                response = Response({
                    'success': message % (question['formulation'], test.name)
                })
            except utils.InvalidFileFormatError:
                response = Response({
                    'error': f'Вопрос не был добавлен, так как присутствуют пустые варианты ответов.'
                })
            except Exception as e:
                response = Response({
                    'error': f'Вопрос не был добавлен: {e}.'
                })
            finally:
                return response
        elif question_id == 'load':  # POST
            try:
                questions_list = utils.get_questions_list(request)
                storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
                for question in questions_list:
                    storage.add_one(
                        question=question,
                        test_id=test.id)
                message = "Вопросы к тесту '%s' в количестве %d успешно добавлены."
                response = Response({
                    'success': message % (test.name, len(questions_list))
                })
            except utils.InvalidFileFormatError as e:
                response = Response({
                    'error': f'Вопросы не были загружены: {e}'
                })
            finally:
                return response
        else:  # PUT
            try:
                with_images = json.loads(request_dict['withImages'][0])
                formulation = request_dict['formulation'][0]
                options = json.loads(request_dict['options'][0])

                if '' in [opt['option'] for opt in options]:
                    raise utils.InvalidFileFormatError('empty options are not allowed')
                test = Test.objects.get(id=test_id)

                if with_images:
                    storage.update_formulation(
                        question_id=question_id,
                        formulation=formulation
                    )
                else:
                    storage.update(
                        question_id=question_id,
                        formulation=formulation,
                        options=options
                    )
                message = "Вопрос '%s' по тесту '%s' был успешно отредактирован."
                response = Response({
                    'success': message % (formulation, test.name)
                })
            except utils.InvalidFileFormatError:
                response = Response({
                    'error': f'Вопрос не был отредактирован, так как в вопросе присутствовали пустые варинаты ответов.'
                })
            finally:
                return response


class TestsResultView(APIView):
    permission_classes = [IsAuthenticated, IsLecturer]

    def get(self, _, state):
        storage = mongo.TestsResultsStorage.connect(db=mongo.get_conn())
        if state == 'all':
            results = storage.get_all_tests_results()
        else:
            test_result = storage.get_test_result(_id=state)
            results = [test_result] if test_result else []
        return Response({
            'results': results
        })


class RunningTestView(APIView):
    permission_classes = [IsAuthenticated, IsLecturer]

    def get(self, request):
        date_format = '%H:%M:%S %d.%m.%Y'
        storage = mongo.TestsResultsStorage.connect(db=mongo.get_conn())
        running_tests = storage.get_running_tests()
        tests = []
        for running_test in running_tests:
            if running_test['launched_lecturer_id'] == request.user.id:
                test = Test.objects.get(id=running_test['test_id']).to_dict()
                test_results = storage.get_running_test_results(
                    test_id=test['id'],
                    lecturer_id=request.user.id)
                results = test_results['results']
                results.sort(key=lambda res: res['date'])
                for result in results:
                    result['date'] = result['date'].strftime(date_format)
                test['finished_students_results'] = results
                tests.append(test)
        return Response({
            'tests': tests
        })
