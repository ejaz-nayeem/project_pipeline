# phone_solution/urls.py

from django.urls import path
from .views import PurchaseNumberView, TwilioWebhookView, UseOtpView

urlpatterns = [
    path('purchase-number/', PurchaseNumberView.as_view(), name='purchase-number'),
    path('sms-webhook/', TwilioWebhookView.as_view(), name='sms-webhook'),
    path('use-otp/', UseOtpView.as_view(), name='use-otp'),
]