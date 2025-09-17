# email_solution/services.py
import re
from ip_solution.services import make_request_with_oxylabs

def process_mailgun_webhook(payload):
    """
    Parses email content from a Mailgun webhook, prints the details, finds a
    verification link, and "clicks" it using our proxy service.
    """
    try:
        # --- START: ADDED LOGGING ---
        # Get the sender, recipient, and subject from the payload
        sender = payload.get('sender', 'N/A')
        recipient = payload.get('recipient', 'N/A')
        subject = payload.get('subject', 'N/A')

        print("\n--- INCOMING EMAIL RECEIVED ---")
        print(f"From:    {sender}")
        print(f"To:      {recipient}")
        print(f"Subject: {subject}")
        print("---------------------------------")
        # --- END: ADDED LOGGING ---

        email_content = payload.get('body-html', payload.get('stripped-text', ''))
        
        # --- ADDED LOGGING FOR THE BODY ---
        print("Raw Email Body:")
        print(email_content)
        print("---------------------------------\n")

        print("Searching for verification link...")

        if not email_content:
            return {'status': 'failed', 'reason': 'Email body was empty.'}

        match = re.search(r'href=["\'](https?://[^\s"\'<>]+)["\']', email_content)

        if not match:
            print("No verification link found in the email.")
            return {'status': 'failed', 'reason': 'No verification link found'}

        verification_url = match.group(1).replace("=\r\n", "").replace("=3D", "=")
        print(f"Found verification URL: {verification_url}")

        print("Attempting to 'click' the link via Oxylabs proxy...")
        response = make_request_with_oxylabs(verification_url, country='GB')

        if response and response.status_code < 400:
            print("Successfully clicked the verification link.")
            return {'status': 'success', 'url_clicked': verification_url}
        else:
            status_code = response.status_code if response else 'N/A'
            print(f"Failed to click link. Status: {status_code}")
            return {'status': 'failed', 'reason': f'Proxy request failed with status {status_code}'}

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {'status': 'error', 'reason': str(e)}