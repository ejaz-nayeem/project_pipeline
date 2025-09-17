# mail_sender/views.py
import hmac
import hashlib
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .models import EmailAccount
from .serializers import EmailAccountSerializer

class SendEmailView(APIView):
    def post(self, request):
        recipient_email = request.data.get('recipient_email')
        subject = request.data.get('subject')
        message = request.data.get('message')
        sender_email = request.data.get('sender_email')

        if not all([recipient_email, subject, message, sender_email]):
            return Response(
                {"error": "recipient_email, subject, message, and sender_email are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate sender domain
        if not sender_email.endswith(f"@{settings.MAILGUN_DOMAIN}"):
            return Response(
                {"error": f"Sender email must end with @{settings.MAILGUN_DOMAIN}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Optional: Validate recipient (for sandbox)
        if not recipient_email.endswith(f"@{settings.MAILGUN_DOMAIN}"):
            return Response(
                {"warning": "Recipient should be on your Mailgun domain for best delivery."},
                status=status.HTTP_200_OK
            )  # Proceed, but log if needed

        return self.send_mailgun_email(sender_email, recipient_email, subject, message)

    def send_mailgun_email(self, sender, recipient, subject, text):
        try:
            response = requests.post(
                f"https://api.eu.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages",  
                auth=("api", settings.MAILGUN_API_KEY),
                data={
                    "from": f"Sender Name <{sender}>",
                    "to": [recipient],
                    "subject": subject,
                    "text": text
                }
            )
            # Debug: Log response for troubleshooting
            print(f"Mailgun Response Status: {response.status_code}")
            print(f"Mailgun Response Body: {response.text}")

            response.raise_for_status()
            return Response({"message": "Email sent successfully!"}, status=status.HTTP_200_OK)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return Response(
                    {"error": "Authentication failed (401). Check API key and region."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            return Response(
                {"error": f"HTTP Error: {e.response.status_code} - {e.response.text}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Failed to send email: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateEmailAccount(APIView):
    def post(self, request):
        # Create and save the email account
        # Allow optional address from request, fallback to auto-generated in model
        address = request.data.get('address')
        account = EmailAccount(address=address) if address else EmailAccount()
        account.save()
        serializer = EmailAccountSerializer(account)

        # Check if a catch-all route exists
        if not has_catch_all_route():
            
            # Create catch-all route if missing
            # In GenerateEmailAccount.post() and has_catch_all_route() (if applicable)
            route_data = {
                
                
                "priority": 0,
                "description": "Catch-all webhook route",
                "expression": "catch_all()",
                "action": [f'forward("https://02ec0543cc9c.ngrok-free.app/api/mail-sender/webhook/")']  # New URL
            }
            response = requests.post(
                "https://api.mailgun.net/v3/routes",
                auth=("api", settings.MAILGUN_API_KEY),
                data=route_data
            )
            if response.status_code != 200:
                return Response(
                    {"error": f"Failed to create catch-all: {response.text}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

def has_catch_all_route():
    try:
        response = requests.get(
            "https://api.mailgun.net/v3/routes",
            auth=("api", settings.MAILGUN_API_KEY)
        )
        if response.status_code == 200:
            routes = response.json().get("items", [])
            return any("catch_all()" in route.get("expression", "") for route in routes)
        return False
    except requests.exceptions.RequestException:
        return False


# mail_sender/views.py (or wherever your webhook is)

# In the same file as your webhook (e.g., mail_sender/views.py)

import re
import hmac
import hashlib
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.conf import settings

# --- IMPORTANT: Make sure this import is here ---
# This brings in the function that "clicks" the link via the proxy.
from ip_solution.services import make_request_with_oxylabs


# --- HELPER FUNCTION FOR CLEANLINESS ---
def extract_and_click_link(payload):
    """
    Extracts a verification link from webhook payload (HTML or plain text)
    and then uses the proxy service to "click" it.
    """
    html_body = payload.get('body-html', '')
    plain_body = payload.get('body-plain', '')
    
    verification_url = None

    # 1. First, try to find the link in the HTML body (more reliable)
    if html_body:
        # This regex is great for finding links inside <a href="..."> tags
        match = re.search(r'href=["\'](https?://www\.openrent\.co\.uk/authentication/email[^\s"\'<>]+)["\']', html_body)
        if match:
            verification_url = match.group(1)
            print("Found verification link in HTML body.")

    # 2. If no link was found in the HTML, try the plain text body as a fallback
    if not verification_url and plain_body:
        # This regex looks for the standalone URL in the plain text
        match = re.search(r'\(?\s*(https?://www\.openrent\.co\.uk/authentication/email[^\s\)]+)\s*\)?', plain_body)
        if match:
            verification_url = match.group(1)
            print("Found verification link in plain text body as a fallback.")

    # 3. If no link was found anywhere, report and exit
    if not verification_url:
        print("No verification link found in either HTML or plain text.")
        return

    # 4. Clean the URL and "click" it using our proxy
    # The replace is for characters that get encoded in emails
    verification_url = verification_url.replace("&amp;", "&")
    print(f"Final Verification URL: {verification_url}")

    print("Attempting to 'click' the link via Oxylabs proxy...")
    response = make_request_with_oxylabs(verification_url, country='GB')

    if response and response.status_code < 400:
        print("SUCCESS: Successfully clicked the verification link.")
    else:
        status_code = response.status_code if response else 'N/A'
        print(f"FAILURE: Failed to click the link. Proxy request failed with status {status_code}")


# --- YOUR MAIN WEBHOOK FUNCTION (Now much cleaner) ---
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def webhook(request):
    if request.method == 'POST':
        # --- 1. Signature Verification (Your code is perfect here) ---
        token = request.POST.get('token')
        timestamp = request.POST.get('timestamp')
        signature = request.POST.get('signature')

        if not all([token, timestamp, signature]):
            print("Missing signature components.")
            return HttpResponse('Bad Request: Missing parameters', status=400)

        hmac_digest = hmac.new(
            key=settings.MAILGUN_WEBHOOK_SIGNING_KEY.encode('utf-8'),
            msg=f"{timestamp}{token}".encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(hmac_digest, signature):
            print("Signature verification failed.")
            return HttpResponse('Invalid signature', status=401)
        
        print("Webhook signature verified successfully.")

        # --- 2. Process the Email using our new helper function ---
        # This one function call does all the work now
        extract_and_click_link(request.POST)

        # --- 3. Acknowledge Receipt to Mailgun ---
        # Always return a 200 OK to Mailgun to prevent retries.
        return HttpResponse('OK', status=200)

    return HttpResponse('Method not allowed', status=405)