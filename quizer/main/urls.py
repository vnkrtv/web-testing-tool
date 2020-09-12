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
    path('questions/<int:test_id>', views.questions, name='questions'),
    url(r'^tests_results/$', views.tests_results, name='tests_results'),
    path('tests_results/<str:test_result_id>', views.show_test_results, name='show_test_results'),
    url(r'^running_tests/$', views.get_running_tests, name='running_tests'),
    url(r'^testing_results/$', views.stop_running_test, name='stop_running_test'),
    url(r'^test_result/$', views.PassedTestView.as_view(), name='test_result'),
    url(r'^get_left_time/$', views.get_left_time, name='get_left_time')
]
