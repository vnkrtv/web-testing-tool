from django.conf.urls import url
from . import views

app_name = 'main'

urlpatterns = [
    url(r'^$', views.login_page, name='login_page'),
    url(r'^home/$', views.index, name='index'),
    url(r'^tests/$', views.get_tests, name='tests'),

    url(r'^add_test/$', views.add_test, name='add_test'),
    url(r'^add_test_result/$', views.add_test_result, name='add_test_result'),
    url(r'^edit_test/$', views.edit_test, name='edit_test'),
    url(r'^edit_test_result/$', views.edit_test_result, name='edit_test_result'),
    url(r'^add_question/$', views.add_question, name='add_question'),
    url(r'^add_question_result/$', views.add_question_result, name='add_question_result'),

    url(r'^marks/$', views.get_marks, name='marks'),
    url(r'^run_test/$', views.run_test, name='run_test'),
    url(r'^test_result/$', views.test_result, name='test_result'),
]
