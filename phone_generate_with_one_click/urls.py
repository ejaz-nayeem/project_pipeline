# phone_solution/urls.py
from django.urls import path
from .views import GeneratePhoneView, GetExistingPhoneView # <-- Import the new view

urlpatterns = [
    # The old view can be removed or kept for other purposes
    #path('purchase-number/', PurchaseNumberView.as_view(), name='purchase-number'), 
    path('generate-phone/', GeneratePhoneView.as_view(), name='generate-phone'), # <-- Add this line
    path('get-existing-phone/', GetExistingPhoneView.as_view(), name='get-existing-phone'),
]