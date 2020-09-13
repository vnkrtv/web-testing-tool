import json

from django.contrib.auth.models import User

from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import Subject, Test
from main import mongo
from .serializers import SubjectSerializer, TestSerializer
from .permissions import IsLecturer


class SubjectView(APIView):

    permission_classes = [IsAuthenticated, IsLecturer]

    def get(self, _):
        subjects = Subject.objects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response({
            'subjects': serializer.data
        })

    def post(self, request):
        subject = request.data.get('subject')
        serializer = SubjectSerializer(data=subject)
        if serializer.is_valid(raise_exception=True):
            new_subject = serializer.save()
        return Response({
            'success': "Предмет '%s' успешно добавлен." % new_subject.name
        })

    def put(self, request, pk):
        updated_subject = get_object_or_404(Subject.objects.all(), pk=pk)
        data = request.data.get('subject')
        serializer = SubjectSerializer(instance=updated_subject, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            updated_subject = serializer.save()
        return Response({
            'success': "Предмет '%s' был успешно отредактирован." % updated_subject.name
        })

    def delete(self, _, pk):
        subject = get_object_or_404(Subject.objects.all(), pk=pk)
        subject_name = subject.name
        subject.delete()
        return Response({
            'success': "Предмет '%s' был успешно удален." % subject_name
        }, status=204)


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

