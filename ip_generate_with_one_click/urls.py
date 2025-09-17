# ip_solution/urls.py
from django.urls import path
from .views import GenerateIPView, PerformRedirectView, GenerateIPAndRedirectView # <-- Import the new view

urlpatterns = [
    
    path('generate-ip/', GenerateIPView.as_view(), name='generate-ip'),
    path('generate-ip-and-get-url/', GenerateIPAndRedirectView.as_view(), name='generate-ip-and-get-url'),
    
  
    path('perform-redirect/', PerformRedirectView.as_view(), name='perform-redirect'),# <-- Add this line
]