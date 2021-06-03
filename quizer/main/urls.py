# pylint: skip-file
from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    url(r'^$', views.login_page, name='login_page'),
    url(r'^available_tests/$', views.AvailableTestsView.as_view(), name='available_tests'),
    path('run_test/<test_id>', views.lecturer_run_test, name='lecturer_run_test'),
    url(r'^subjects/$', views.SubjectsView.as_view(), name='subjects'),
    url(r'^tests/$', views.TestsView.as_view(), name='tests'),
    path('questions/<test_id>', views.manage_questions, name='questions'),
    url(r'^tests_results/$', views.lecturer_all_tests_results, name='tests_results'),
    path('tests_results/<test_results_id>', views.lecturer_current_test_results, name='show_test_results'),
    path('user_results/<int:user_id>', views.student_tests_results, name='user_results'),
    url(r'^running_tests/$', views.get_running_tests, name='running_tests'),
    url(r'^testing_results/$', views.stop_running_test, name='stop_running_test'),
    url(r'^test_result/$', views.PassedTestView.as_view(), name='test_result'),
    url(r'^test/$', views.student_run_test, name='student_run_test'),
    url(r'^get_left_time/$', views.get_left_time, name='get_left_time'),
    url(r'^administration/$', views.AdministrationView.as_view(), name='administration'),
    url(r'^get_db_dump/$', views.get_db_dump, name='get_db_dump'),
    url(r'^game/$', views.game, name='game')
]
