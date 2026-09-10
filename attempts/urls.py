from django.urls import path
from . import views

app_name = 'attempts'

urlpatterns = [
    path('submit/<slug:slug>/', views.submit_attempt, name='submit'),
    path('<int:pk>/result/', views.attempt_result, name='result'),
    path('history/', views.attempt_history, name='history'),
]