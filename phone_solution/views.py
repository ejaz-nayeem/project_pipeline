from django.shortcuts import render

# Create your views here.
# phone_solution/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import purchase_uk_phone_number

class PurchaseNumberView(APIView):
    """
    An API endpoint to trigger the purchase of a new UK mobile number from Twilio.
    """
    def post(self, request, format=None):
        """
        Handles the POST request to purchase a number.
        We use POST because this action changes state (creates a resource).
        """
        print("PurchaseNumberView: Received request to buy a phone number.")
        result = purchase_uk_phone_number()
        
        if result.get('status') == 'success':
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            # Return a server error if the purchase fails
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)