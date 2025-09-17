# email_solution/views.py
import os
import uuid # Used to generate a unique string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# ... (keep existing imports and the MailgunWebhookView) ...

class GenerateEmailView(APIView):
    """
    Generates a new, unique email address using the verified Mailgun domain.
    """
    def get(self, request, format=None):
        mailgun_domain = os.environ.get('MAILGUN_DOMAIN')
        
        if not mailgun_domain:
            return Response({'error': 'MAILGUN_DOMAIN is not configured in .env file.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        # Generate a unique identifier
        unique_id = str(uuid.uuid4().hex)[:12] # Get a 12-character unique string
        
        # Construct the email address
        new_email = f"user-{unique_id}@{mailgun_domain}"
        
        return Response({'email': new_email}, status=status.HTTP_200_OK)