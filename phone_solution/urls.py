# phone_solution/urls.py

from django.urls import path
from .views import PurchaseNumberView

urlpatterns = [
    path('purchase-number/', PurchaseNumberView.as_view(), name='purchase-number'),
]