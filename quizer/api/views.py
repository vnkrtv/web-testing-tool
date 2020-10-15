import json

from django.contrib.auth.models import User

from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import Subject, Test
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

    def post(self, request, pk):
        request_dict = dict(request.POST)
        if len(request_dict) == 1:  # DELETE, only csrftoken passed
            subject = get_object_or_404(Subject.objects.all(), pk=pk)
            subject_name = subject.name
            tests = Test.objects.filter(subject__id=subject.id)
            tests_count = tests.count()

            deleted_questions_count = 0
            storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
            for test in tests:
                deleted_questions_count += storage.delete_many(test_id=test.id)
            subject.delete()

            message = "Учебный предмет '%s', %d тестов к нему, а также все " + \
                 "вопросы к тестам в количестве %d были успешно удалены."
            return Response({
                'success': message % (subject_name, tests_count, deleted_questions_count)
            })
        elif pk == 'new':  # POST
            serializer = SubjectSerializer(data=request.data)
            print(serializer)
            if serializer.is_valid(raise_exception=True):
                new_subject = serializer.save()
            return Response({
                'success': "Предмет '%s' успешно добавлен." % new_subject.name
            })
        elif pk == 'load':  # POST
            print(request.POST)
            message = utils.add_subject_with_tests(request)
            return Response({
                'success': message
            })
        else:  # PUT
            updated_subject = get_object_or_404(Subject.objects.all(), pk=pk)
            serializer = SubjectSerializer(instance=updated_subject, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                updated_subject = serializer.save()
            return Response({
                'success': "Предмет '%s' был успешно отредактирован." % updated_subject.name
            })


class TestView(APIView):

    permission_classes = [IsAuthenticated, IsLecturer]

    def get(self, _, state):
        storage = mongo.TestsResultsStorage.connect(db=mongo.get_conn())
        running_tests = storage.get_running_tests()
        if state == 'running':
            tests = []
            for running_test in running_tests:
                test = Test.objects.get(id=running_test['test_id']).to_dict()
                launched_lecturer = User.objects.get(id=running_test['launched_lecturer_id'])
                tests.append({
                    **test,
                    'launched_lecturer': {
                        'id': launched_lecturer.id,
                        'username': launched_lecturer.username
                    }
                })
        elif state == 'not_running':
            running_tests_ids = [test['test_id'] for test in running_tests]
            tests = [t.to_dict() for t in Test.objects.exclude(id__in=running_tests_ids)]
            storage = mongo.QuestionsStorage.connect(db=mongo.get_conn())
            for test in tests:
                test['questions_num'] = len(storage.get_many(test_id=test['id']))
        elif state == 'all':
            tests = Test.objects.all()
            serializer = TestSerializer(tests, many=True)
            tests = serializer.data
        else:
            tests = []
        return Response({
            'tests': tests
        })

    def post(self, request):
        test = request.data.get('test')
        serializer = TestSerializer(data=test)
        if serializer.is_valid(raise_exception=True):
            new_test = serializer.save()
        return Response({
            'success': "Тест '%s' по предмету '%s' успешно добавлен." %
                       (new_test.name, new_test.subject.name)
        })

    def put(self, request, pk):
        updated_test = get_object_or_404(Test.objects.all(), pk=pk)
        data = request.data.get('test')
        serializer = TestSerializer(instance=updated_test, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            updated_test = serializer.save()
        return Response({
            'success': "Тест '%s' по предмету '%s' был успешно отредактирован." %
                       (updated_test.name, updated_test.subject.name)
        })

    def delete(self, _, pk):
        test = get_object_or_404(Subject.objects.all(), pk=pk)
        test_name = test.name
        subject_name = test.subject.name
        test.delete()
        return Response({
            'success': "Тест '%s' по предмету '%s' был успешно удален." %
                       (test_name, subject_name)
        }, status=204)


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
