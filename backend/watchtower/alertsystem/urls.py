# backend/watchtower/alertsystem/urls.py
from django.urls import path
from .views import get_explanation

urlpatterns = [
    path('get_explanation/', get_explanation, name='get_explanation'),
]
