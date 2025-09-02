from django.urls import path
from .views import ProxyTestView

urlpatterns = [
    path('test-proxy/', ProxyTestView.as_view(), name='test-proxy'),
]