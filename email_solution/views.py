# email_solution/views.py
import os
import hmac
import hashlib
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import process_mailgun_webhook

def verify_mailgun_webhook(signing_key, timestamp, token, signature):
    """Verifies that the incoming webhook request is genuinely from Mailgun."""
    message = f"{timestamp}{token}".encode('utf-8')
    expected_signature = hmac.new(
        key=signing_key.encode('utf-8'),
        msg=message,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)

class MailgunWebhookView(APIView):
    """Receives and processes inbound email webhooks from Mailgun."""
    def post(self, request, format=None):
        print("Mailgun webhook received a POST request.")
        signing_key = os.environ.get('MAILGUN_WEBHOOK_SIGNING_KEY')
        if not signing_key:
            print("ERROR: Mailgun signing key is not configured.")
            return Response({'error': 'Server configuration error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            timestamp = request.POST.get('timestamp')
            token = request.POST.get('token')
            signature = request.POST.get('signature')
            if not all([timestamp, token, signature]):
                raise ValueError("Missing signature components")
            
            if not verify_mailgun_webhook(signing_key, timestamp, token, signature):
                print("SECURITY ALERT: Invalid webhook signature. Request rejected.")
                return Response({'error': 'Invalid signature.'}, status=status.HTTP_403_FORBIDDEN)
            
            print("Webhook signature verified successfully.")
        except (ValueError, KeyError) as e:
            print(f"SECURITY ALERT: Could not parse signature data. Error: {e}")
            return Response({'error': 'Invalid signature data.'}, status=status.HTTP_400_BAD_REQUEST)

        result = process_mailgun_webhook(request.POST)
        
        if result.get('status') in ['success', 'failed']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
