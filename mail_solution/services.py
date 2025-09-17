# email_solution/services.py
import re

# Import the service from our existing IP solution app
from ip_solution.services import make_request_with_oxylabs

def process_mailgun_webhook(payload):
    """
    Parses the email content from a Mailgun inbound webhook, finds a verification
    link, and "clicks" it using our proxy service.

    Args:
        payload (dict): The request.POST data from Mailgun's webhook.
    
    Returns:
        A dictionary with the result of the operation.
    """
    try:
        # Mailgun provides the email content in several fields.
        # 'body-html' is best for finding links. Fallback to 'stripped-text'.
        email_content = payload.get('body-html', payload.get('stripped-text', ''))
        sender = payload.get('sender', 'unknown')
        recipient = payload.get('recipient', 'unknown')

        print(f"Received email from '{sender}' to '{recipient}'. Searching for link...")

        if not email_content:
            return {'status': 'failed', 'reason': 'Email body was empty.'}

        # Use a robust regex to find the first URL inside an href attribute
        match = re.search(r'href=["\'](https?://[^\s"\'<>]+)["\']', email_content)

        if not match:
            print("No verification link found in the email.")
            return {'status': 'failed', 'reason': 'No verification link found'}

        verification_url = match.group(1)
        # Decode quoted-printable encoding which can appear in HTML emails
        verification_url = verification_url.replace("=\r\n", "").replace("=3D", "=")

        print(f"Found verification URL: {verification_url}")

        # --- THE KEY INTEGRATION STEP ---
        # Use our IP solution to "click" the link through a clean UK IP
        print("Attempting to 'click' the link via Oxylabs proxy...")
        response = make_request_with_oxylabs(verification_url, country='GB')

        if response and response.status_code < 400: # Success is any 2xx or 3xx status
            print("Successfully clicked the verification link.")
            return {'status': 'success', 'url_clicked': verification_url}
        else:
            status_code = response.status_code if response else 'N/A'
            print(f"Failed to click the verification link. Status: {status_code}")
            return {'status': 'failed', 'reason': f'Proxy request failed with status {status_code}'}

    except Exception as e:
        print(f"An unexpected error occurred while processing email: {e}")
        return {'status': 'error', 'reason': str(e)}