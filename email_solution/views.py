# email_solution/views.py
import os
import hmac
import hashlib
import json # <-- Import the json library
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import process_mailgun_webhook

# (The verify_mailgun_webhook helper function remains the same)
def verify_mailgun_webhook(signing_key, timestamp, token, signature):
    message = f"{timestamp}{token}".encode('utf-8')
    expected_signature = hmac.new(
        key=signing_key.encode('utf-8'),
        msg=message,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)


class MailgunWebhookView(APIView):
    def post(self, request, format=None):
        print("Mailgun webhook received a POST request.")
        
        # --- NEW ROBUST PAYLOAD HANDLING ---
        payload = {}
        if request.POST:
            print("Data found in request.POST (form data).")
            payload = request.POST
        elif request.body:
            print("Data found in request.body. Attempting to parse as JSON.")
            try:
                payload = json.loads(request.body)
            except json.JSONDecodeError:
                print("Could not parse request.body as JSON.")
                return Response({'error': 'Invalid JSON body.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("Webhook received with an empty body. Likely a test/ping request.")
            # We can return 200 OK to satisfy Mailgun's ping test.
            return Response({'status': 'ok', 'message': 'Empty test request received.'}, status=status.HTTP_200_OK)

        # --- SECURITY CHECK ---
        signing_key = os.environ.get('MAILGUN_WEBHOOK_SIGNING_KEY')
        if not signing_key:
            print("ERROR: Mailgun signing key is not configured.")
            return Response({'error': 'Server configuration error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            # Get signature data from the payload dictionary
            timestamp = payload.get('timestamp')
            token = payload.get('token')
            signature = payload.get('signature')

            if not all([timestamp, token, signature]):
                 raise ValueError("Missing signature components in payload")

            if not verify_mailgun_webhook(signing_key, str(timestamp), token, signature):
                print("SECURITY ALERT: Invalid webhook signature. Request rejected.")
                return Response({'error': 'Invalid signature.'}, status=status.HTTP_403_FORBIDDEN)
            
            print("Webhook signature verified successfully.")

        except (ValueError, KeyError) as e:
            print(f"SECURITY ALERT: Could not parse signature data. Error: {e}")
            return Response({'error': 'Invalid signature data.'}, status=status.HTTP_400_BAD_REQUEST)

        # --- PROCESS THE EMAIL (only if security check passes) ---
        result = process_mailgun_webhook(payload)
        
        return Response(result, status=status.HTTP_200_OK)