# phone_solution/services.py

import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

def purchase_uk_phone_number():
    """
    Searches for and purchases one available UK mobile number via the Twilio API.
    
    Returns:
        A dictionary containing purchase details on success, or an error message on failure.
    """
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

    if not account_sid or not auth_token:
        return {'status': 'error', 'message': 'Twilio credentials not found in environment variables.'}

    client = Client(account_sid, auth_token)

    try:
        print("Searching for an available UK mobile number...")
        
        # Search for one available number in Great Britain ('GB') of type 'mobile'
        available_numbers = client.available_phone_numbers('GB').mobile.list(limit=1)

        if not available_numbers:
            print("No UK mobile numbers available at this moment.")
            return {'status': 'error', 'message': 'No UK mobile numbers are currently available.'}

        number_to_buy = available_numbers[0]
        phone_number = number_to_buy.phone_number
        
        print(f"Found number: {phone_number}. Attempting to purchase...")

        # For now, we won't configure the SMS webhook until we build it.
        # This can be updated later.
        purchased_number = client.incoming_phone_numbers.create(
            phone_number=phone_number
        )

        print(f"Successfully purchased number with SID: {purchased_number.sid}")
        
        return {
            'status': 'success',
            'sid': purchased_number.sid,
            'phone_number': purchased_number.phone_number,
            'friendly_name': purchased_number.friendly_name,
        }

    except TwilioRestException as e:
        # Catch specific Twilio errors (e.g., insufficient funds, regulatory issues)
        print(f"Twilio API Error: {e}")
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return {'status': 'error', 'message': 'An unexpected error occurred during purchase.'}