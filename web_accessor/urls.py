# web_accessor/urls.py
from django.urls import path
from .views import AccessOpenRentView

urlpatterns = [
    path('access-openrent/', AccessOpenRentView.as_view(), name='access-openrent'),
]