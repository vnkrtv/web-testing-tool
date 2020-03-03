from django.conf.urls import url
from . import views

app_name = 'main'

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^home/$', views.index, name='index'),
    url(r'^tests/$', views.get_tests, name='tests'),
    url(r'^marks/$', views.get_marks, name='marks'),
]
