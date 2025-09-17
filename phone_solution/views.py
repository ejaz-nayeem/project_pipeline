from django.shortcuts import render

# Create your views here.
# phone_solution/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import purchase_phone_number
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse
from django.utils.decorators import method_decorator

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
        result = purchase_phone_number()
        
        if result.get('status') == 'success':
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            # Return a server error if the purchase fails
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# In phone_generate_with_one_click/views.py
import re # <-- Make sure to import re
from .models import ReceivedOTP # <-- Import your new model

@method_decorator(csrf_exempt, name='dispatch')
class TwilioWebhookView(APIView):
    """
    Receives incoming SMS, extracts any 6-digit OTP, and saves it.
    """
    def post(self, request, format=None):
        sender_number = request.POST.get('From', 'N/A')
        message_body = request.POST.get('Body', 'N/A')
        your_twilio_number = request.POST.get('To', 'N/A')

        print("\n--- INCOMING SMS RECEIVED ---")
        print(f"From:    {sender_number}")
        print(f"To:      {your_twilio_number}")
        print(f"Message: \"{message_body}\"")
        
        # --- OTP EXTRACTION LOGIC ---
        # This regex finds any sequence of 6 digits in the message
        match = re.search(r'(\d{6})', message_body)
        
        if match:
            otp_code = match.group(1)
            # Save the found OTP to the database
            ReceivedOTP.objects.create(
                phone_number=your_twilio_number,
                otp_code=otp_code
            )
            print(f"SUCCESS: Extracted and saved OTP: {otp_code} for {your_twilio_number}")
        else:
            print("INFO: No 6-digit OTP found in the message.")
        
        print("-----------------------------")

        return HttpResponse('<Response></Response>', content_type='text/xml')
    
# Add this class to the end of phone_generate_with_one_click/views.py

class UseOtpView(APIView):
    """
    Finds the latest unused OTP for a given phone number and simulates submitting it.
    """
    def post(self, request, format=None):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({'error': 'phone_number is required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Find the newest, unused OTP for this specific number
            otp_record = ReceivedOTP.objects.filter(
                phone_number=phone_number,
                is_used=False
            ).latest('created_at')
        except ReceivedOTP.DoesNotExist:
            return Response({'error': f'No unused OTP found for {phone_number}.'}, status=status.HTTP_404_NOT_FOUND)

        otp_code = otp_record.otp_code
        print(f"Found OTP {otp_code} for {phone_number}. Simulating submission...")

        # --- THIS IS WHERE THE NEXT AUTOMATION STEP HAPPENS ---
        # In a real, full pipeline, you would now use this otp_code to:
        # 1. Control a browser with Playwright/Puppeteer to enter the code on the website.
        # 2. Or make a direct API call to OpenRent's verification endpoint.
        print("SIMULATION: Submitting OTP to OpenRent website...")
        
        # Mark the OTP as used so it can't be used again
        otp_record.is_used = True
        otp_record.save()
        
        return Response({
            'status': 'success',
            'message': f'Successfully used OTP {otp_code} for {phone_number}.'
        }, status=status.HTTP_200_OK)