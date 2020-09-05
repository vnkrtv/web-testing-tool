# pylint: skip-file
from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    url(r'^$', views.login_page, name='login_page'),
    url(r'^available_tests/$', views.AvailableTestsView.as_view(), name='available_tests'),
    url(r'^subjects/$', views.SubjectsView.as_view(), name='subjects'),
    url(r'^tests/$', views.TestsView.as_view(), name='tests'),

    url(r'^tests_results/$', views.tests_results, name='tests_results'),
    path('test_results/<test_result_id>', views.show_test_results, name='show_test_results'),
    url(r'^running_tests/$', views.get_running_tests, name='running_tests'),
    url(r'^stop_running_test/$', views.stop_running_test, name='stop_running_test'),
    url(r'^delete_questions_result/$', views.delete_questions_result, name='delete_questions_result'),

    url(r'^run_test/$', views.run_test, name='run_test'),
    url(r'^get_left_time/$', views.get_left_time, name='get_left_time'),
    url(r'^test_result/$', views.test_result, name='test_result')
]
