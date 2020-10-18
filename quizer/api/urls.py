from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('subjects/', views.SubjectView.as_view(), name='get_subjects'),
    path('subjects/<pk>', views.SubjectView.as_view(), name='edit_subject'),
    path('tests/<str:state>', views.TestView.as_view(), name='tests_api'),
    path('tests/launch/<pk>', views.LaunchTestView.as_view(), name='launch_test'),
    path('test/<test_id>/questions', views.QuestionView.as_view(), name='get_questions'),
    path('test/<test_id>/questions/<str:question_id>', views.QuestionView.as_view(), name='questions_api'),
    path('tests_results/<str:state>', views.TestsResultView.as_view(), name='get_tests_results'),
]
