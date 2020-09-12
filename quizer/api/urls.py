from django.urls import path
from .views import SubjectView, TestView

app_name = 'api'

urlpatterns = [
    path('subjects/', SubjectView.as_view()),
    path('subjects/<int:pk>', SubjectView.as_view()),
    path('tests/', TestView.as_view()),
    path('tests/<int:pk>', TestView.as_view())
]
