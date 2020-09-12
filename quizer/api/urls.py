from django.urls import path
from .views import SubjectView

app_name = 'api'

urlpatterns = [
    path('subjects/', SubjectView.as_view()),
    path('subjects/<int:pk>', SubjectView.as_view())
]
