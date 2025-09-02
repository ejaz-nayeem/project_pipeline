# ip_solution/urls.py
from django.urls import path
from .views import GenerateIPView # <-- Import the new view

urlpatterns = [
    
    path('generate-ip/', GenerateIPView.as_view(), name='generate-ip'), # <-- Add this line
]