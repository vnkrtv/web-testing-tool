from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import Subject, Test
from .serializers import SubjectSerializer, TestSerializer
from .permissions import IsLecturer


class SubjectView(APIView):

    permission_classes = [IsAuthenticated, IsAdminUser]

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

    def get(self, _):
        tests = Test.objects.all()
        serializer = TestSerializer(tests, many=True)
        return Response({
            'tests': serializer.data
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
