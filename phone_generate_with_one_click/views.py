# phone_solution/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
#from .services import purchase_phone_number # <-- We will use our existing service
from .services import purchase_phone_number, get_existing_twilio_number
# ... (keep the existing PurchaseNumberView if you want) ...

class GeneratePhoneView(APIView):
    """
    Generates a new phone number by purchasing one from Twilio.
    For now, it purchases a US number to bypass UK regulations.
    """
    def post(self, request, format=None):
        print("GeneratePhoneView: Received request to generate a phone number.")
        
        # Request a GB number as per the requirement
        result = purchase_phone_number(country_code='GB')
        
        if result.get('status') == 'success':
            # On success, just return the phone number
            return Response({'phone_number': result.get('phone_number')}, status=status.HTTP_201_CREATED)
        else:
            # On failure, return the error message from Twilio
            return Response({'error': result.get('message')}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# Add this new class to phone_generate_with_one_click/views.py
#from .services import purchase_phone_number, get_existing_twilio_number # <-- Import the new function

class GetExistingPhoneView(APIView):
    """
    Gets the existing trial phone number from the Twilio account.
    This is a GET request because it doesn't create or change anything.
    """
    def get(self, request, format=None):
        print("GetExistingPhoneView: Received request to fetch existing phone number.")
        result = get_existing_twilio_number()
        
        if result.get('status') == 'success':
            return Response({'phone_number': result.get('phone_number')}, status=status.HTTP_200_OK)
        else:
            return Response({'error': result.get('message')}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)