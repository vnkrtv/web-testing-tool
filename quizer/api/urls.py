from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('users/', views.UserAPI.as_view(), name='users_api'),
    path('subjects/', views.SubjectAPI.as_view(), name='subjects_api'),
    path('subjects/<subject_id>', views.SubjectAPI.as_view(), name='edit_subjects_api'),
    path('tests/', views.TestAPI.as_view(), name='tests_api'),
    path('tests/<test_id>', views.TestAPI.as_view(), name='edit_tests_api'),
    path('tests/launch/<test_id>', views.LaunchTestAPI.as_view(), name='launch_test'),
    path('test/<test_id>/questions', views.QuestionAPI.as_view(), name='questions_api'),
    path('test/<test_id>/questions/<str:question_id>', views.QuestionAPI.as_view(), name='edit_questions_api'),
    path('tests_results/', views.TestsResultAPI.as_view(), name='tests_results_api'),
    path('user_results/', views.UserResultAPI.as_view(), name='user_results_api'),
    path('running_tests/', views.RunningTestAPI.as_view(), name='get_running_tests'),
    path('running_tests/', views.RunningTestAPI.as_view(), name='get_running_tests'),
    path('analysis/questions', views.QuestionAnalysisAPI.as_view(), name='question_analysis_api')
]
