from django.conf.urls import url
from . import views

app_name = 'main'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    #url(r'^settings/$',                     views.change_settings,        name='change_settings'),
]
