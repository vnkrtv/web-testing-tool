from django.urls import path

from .views import SubjectView, TestView, QuestionView, TestsResultView

app_name = 'api'

urlpatterns = [
    path('subjects/', SubjectView.as_view(), name='get_subjects'),
    path('subjects/<int:pk>', SubjectView.as_view()),
    path('tests/<str:state>', TestView.as_view(), name='get_tests'),
    path('tests/<int:pk>', TestView.as_view()),
    path('test/<int:test_id>/questions', QuestionView.as_view(), name='get_questions'),
    path('tests_results/', TestsResultView.as_view(), name='get_tests_results'),
]
