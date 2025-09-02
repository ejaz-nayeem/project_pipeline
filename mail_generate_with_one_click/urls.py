# email_solution/urls.py
from django.urls import path
from .views import GenerateEmailView # <-- Import the new view

urlpatterns = [
    #path('webhook/', MailgunWebhookView.as_view(), name='mailgun-webhook'),
    path('generate-mail/', GenerateEmailView.as_view(), name='generate-email'), # <-- Add this line
]