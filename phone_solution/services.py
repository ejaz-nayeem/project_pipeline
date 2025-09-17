import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

def purchase_phone_number(country_code='GB'):
    """
    Searches for, purchases, and automatically configures a new phone number.
    It reads all necessary credentials and the webhook URL from the .env file.
    """
    # Load all necessary variables from the environment
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    webhook_url = os.environ.get('TWILIO_WEBHOOK_URL')

    # Validate that all required variables are present
    if not all([account_sid, auth_token, webhook_url]):
        return {
            'status': 'error',
            'message': 'Missing required Twilio variables in .env file (ACCOUNT_SID, AUTH_TOKEN, WEBHOOK_URL).'
        }

    try:
        client = Client(account_sid, auth_token)
        print(f"Searching for an available number in {country_code}...")

        # Intelligently select the correct number type based on the country
        if country_code.upper() == 'GB':
            number_list_instance = client.available_phone_numbers('GB').mobile
        elif country_code.upper() == 'US':
            number_list_instance = client.available_phone_numbers('US').local
        else:
            return {'status': 'error', 'message': f'Unsupported country code: {country_code}'}

        # Find one available number
        available_numbers = number_list_instance.list(limit=1)
        if not available_numbers:
            return {'status': 'error', 'message': f'No numbers of the required type are available in {country_code}.'}

        phone_number_to_buy = available_numbers[0].phone_number
        print(f"Found number: {phone_number_to_buy}. Attempting to purchase and configure...")

        # Prepare all parameters for the purchase request in a dictionary
        create_params = {
            'phone_number': phone_number_to_buy,
            'sms_url': webhook_url,      # <-- Automatically configure the webhook for incoming SMS
            'sms_method': 'POST'
        }

        # If we are buying a UK number, we must also add the Bundle SID
        if country_code.upper() == 'GB':
            bundle_sid = os.environ.get('TWILIO_BUNDLE_SID')
            if not bundle_sid:
                return {'status': 'error', 'message': 'TWILIO_BUNDLE_SID is required for UK numbers but is not in the .env file.'}
            create_params['bundle_sid'] = bundle_sid
            print(f"Using Bundle SID: {bundle_sid}")

        # Make the single API call to purchase AND configure the number
        purchased_number = client.incoming_phone_numbers.create(**create_params)

        print(f"Successfully purchased and configured number: {purchased_number.phone_number}")
        return {'status': 'success', 'phone_number': purchased_number.phone_number}

    except TwilioRestException as e:
        # Catch specific Twilio API errors (like authentication, bundle issues, etc.)
        print(f"A Twilio API Error occurred: {e}")
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return {'status': 'error', 'message': str(e)}


def get_existing_twilio_number():
    """
    Fetches the first available phone number already in the Twilio account.
    Useful for testing authentication and connection.
    """
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

    if not account_sid or not auth_token:
        return {'status': 'error', 'message': 'Twilio ACCOUNT_SID and AUTH_TOKEN not found.'}

    try:
        client = Client(account_sid, auth_token)
        print("Fetching existing phone numbers from the account...")
        
        incoming_phone_numbers = client.incoming_phone_numbers.list(limit=1)

        if not incoming_phone_numbers:
            return {'status': 'error', 'message': 'No phone numbers were found in this Twilio account.'}
        
        trial_number = incoming_phone_numbers[0]
        print(f"Successfully found number: {trial_number.phone_number}")
        
        return {
            'status': 'success',
            'phone_number': trial_number.phone_number,
        }
    except Exception as e:
        return {'status': 'error', 'message': 'An unexpected error occurred. Check credentials.'}