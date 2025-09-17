# email_solution/views.py
import os
import hmac
import hashlib
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import process_mailgun_webhook

# --- SECURITY HELPER FUNCTION ---
def verify_mailgun_webhook(signing_key, timestamp, token, signature):
    """
    Verifies that the incoming webhook request is genuinely from Mailgun.
    """
    # Check if the timestamp is older than a few minutes to prevent replay attacks
    # This is an optional but recommended enhancement
    # ...

    # Concatenate the timestamp and token
    message = f"{timestamp}{token}".encode('utf-8')
    
    # Calculate the expected signature
    expected_signature = hmac.new(
        key=signing_key.encode('utf-8'),
        msg=message,
        digestmod=hashlib.sha256
    ).hexdigest()

    # Securely compare the expected signature with the one from the request
    return hmac.compare_digest(expected_signature, signature)


class MailgunWebhookView(APIView):
    """
    Receives and processes inbound email webhooks from Mailgun with signature verification.
    """
    def post(self, request, format=None):
        print("Mailgun webhook received a POST request.")
        
        # --- SECURITY CHECK ---
        # Load the signing key from our environment
        signing_key = os.environ.get('MAILGUN_WEBHOOK_SIGNING_KEY')
        if not signing_key:
            print("ERROR: Mailgun signing key is not configured.")
            return Response({'error': 'Server configuration error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Mailgun provides signature details in the POST data
        signature_data = request.POST.get('signature', '{}')
        try:
            # signature_data is a JSON string containing timestamp, token, and signature
            # On some versions, it's directly in the payload
            timestamp = request.POST.get('timestamp')
            token = request.POST.get('token')
            signature = request.POST.get('signature')

            if not all([timestamp, token, signature]):
                 raise ValueError("Missing signature components")

            is_valid = verify_mailgun_webhook(signing_key, timestamp, token, signature)
            
            if not is_valid:
                print("SECURITY ALERT: Invalid webhook signature received. Request rejected.")
                return Response({'error': 'Invalid signature.'}, status=status.HTTP_403_FORBIDDEN)
            
            print("Webhook signature verified successfully.")

        except (ValueError, KeyError) as e:
            print(f"SECURITY ALERT: Could not parse signature data. Error: {e}")
            return Response({'error': 'Invalid signature data.'}, status=status.HTTP_400_BAD_REQUEST)

        # --- PROCESS THE EMAIL (only if security check passes) ---
        result = process_mailgun_webhook(request.POST)
        
        if result.get('status') in ['success', 'failed']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)