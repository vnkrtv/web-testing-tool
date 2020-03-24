from django.conf.urls import url
from . import views

app_name = 'main'

urlpatterns = [
    url(r'^$', views.login_page, name='login_page'),
    url(r'^home/$', views.index, name='index'),
    url(r'^info/$', views.info, name='info'),
    url(r'^tests/$', views.get_tests, name='tests'),

    url(r'^add_test/$', views.add_test, name='add_test'),
    url(r'^edit_test/$', views.edit_test, name='edit_test'),

    url(r'^marks/$', views.get_marks, name='marks'),
    url(r'^run_test/$', views.run_test, name='run_test'),
    url(r'^test_result/$', views.test_result, name='test_result'),
]
