from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import Subject, Test
from .serializers import SubjectSerializer
from .permissions import LecturerAccessPermission


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
        subject.delete()
        return Response({
            'success': "Предмет '%s' был успешно удален.".format(subject.name)
        }, status=204)
