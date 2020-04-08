# pylint: skip-file
from django.conf.urls import url
from . import views

app_name = 'main'

urlpatterns = [
    url(r'^$', views.login_page, name='login_page'),
    url(r'^home/$', views.index, name='index'),
    url(r'^tests/$', views.get_tests, name='tests'),

    url(r'^run_new_test/$', views.run_test_result, name='run_test_result'),
    url(r'^running_tests/$', views.get_running_tests, name='running_tests'),
    url(r'^stop_running_test/$', views.stop_running_test, name='stop_running_test'),
    url(r'^add_test/$', views.add_test, name='add_test'),
    url(r'^add_test_result/$', views.add_test_result, name='add_test_result'),
    url(r'^edit_test/$', views.edit_test, name='edit_test'),
    url(r'^editing_test/$', views.edit_test_redirect, name='edit_test_redirect'),
    url(r'^edit_test_result/$', views.edit_test_result, name='edit_test_result'),
    url(r'^delete_question_result/$', views.delete_question_result, name='delete_question_result'),
    url(r'^delete_test_result/$', views.delete_test_result, name='delete_test_result'),
    url(r'^add_question/$', views.add_question, name='add_question'),
    url(r'^add_question_result/$', views.add_question_result, name='add_question_result'),
    url(r'^load_questions/$', views.load_questions, name='load_questions'),
    url(r'^load_questions_result/$', views.load_questions_result, name='load_questions_result'),

    url(r'^marks/$', views.get_marks, name='marks'),
    url(r'^run_test/$', views.run_test, name='run_test'),
    url(r'^test_result/$', views.test_result, name='test_result')
]
