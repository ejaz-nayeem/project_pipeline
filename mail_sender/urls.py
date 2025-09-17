# email_sender/urls.py

from django.urls import path
#from .views import SendEmailView, MailgunWebhookView, GenerateEmailAccount, webhook, CreateRoute
#from .views import GenerateEmailAccount, webhook, CreateRoute, SendEmailView
from .views import GenerateEmailAccount, webhook, SendEmailView

urlpatterns = [
    path('send-email/', SendEmailView.as_view(), name='send-email'),
    #path('mailgun-webhook/', MailgunWebhookView.as_view(), name='mailgun-webhook'),
    path('generate-account/', GenerateEmailAccount.as_view(), name='generate-account'),
    path('webhook/', webhook, name='webhook'),
    #path('click-link/<uuid:pk>/', ClickVerificationLinkView.as_view(), name='click-verification-link'),
    #path('create-route/', CreateRoute.as_view(), name='create-route'),
]