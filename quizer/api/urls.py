from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('subjects/', views.SubjectView.as_view(), name='get_subjects'),
    path('subjects/<pk>', views.SubjectView.as_view(), name='edit_subject'),
    path('tests/<str:state>', views.TestView.as_view(), name='get_tests'),
    path('tests/<int:pk>', views.TestView.as_view()),
    path('tests/launch/<pk>', views.LaunchTestView.as_view(), name='launch_test'),
    path('test/<test_id>/questions', views.QuestionView.as_view(), name='get_questions'),
    path('tests_results/<str:state>', views.TestsResultView.as_view(), name='get_tests_results'),
]
