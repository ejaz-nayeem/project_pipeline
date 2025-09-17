# email_solution/urls.py
from django.urls import path
from .views import MailgunWebhookView

urlpatterns = [
    path('webhook/', MailgunWebhookView.as_view(), name='mailgun-webhook'),
]