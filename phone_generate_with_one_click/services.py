# phone_generate_with_one_click/services.py

import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

def purchase_phone_number(country_code='GB'):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

    if not account_sid or not auth_token:
        return {'status': 'error', 'message': 'Twilio credentials not found.'}

    try:
        client = Client(account_sid, auth_token)
        print(f"Searching for an available number in {country_code}...")

        if country_code.upper() == 'GB':
            number_list_instance = client.available_phone_numbers('GB').mobile
        elif country_code.upper() == 'US':
            number_list_instance = client.available_phone_numbers('US').local
        else:
            return {'status': 'error', 'message': f'Unsupported country code: {country_code}'}

        available_numbers = number_list_instance.list(limit=1)
        if not available_numbers:
            return {'status': 'error', 'message': f'No numbers available in {country_code}.'}

        phone_number = available_numbers[0].phone_number
        print(f"Found number: {phone_number}. Attempting to purchase...")

        # Prepare the parameters for the create call
        create_params = {'phone_number': phone_number}

        # If buying a GB number, load and add the Bundle SID
        if country_code.upper() == 'GB':
            bundle_sid = os.environ.get('TWILIO_BUNDLE_SID') # <-- It reads the new variable here
            if not bundle_sid:
                return {'status': 'error', 'message': 'TWILIO_BUNDLE_SID is required but not found.'}
            create_params['bundle_sid'] = bundle_sid # <-- It adds the variable to the API call here
            print(f"Using Bundle SID: {bundle_sid}")

        # Make the final call
        purchased_number = client.incoming_phone_numbers.create(**create_params)

        print(f"Successfully purchased number: {purchased_number.phone_number}")
        return {'status': 'success', 'phone_number': purchased_number.phone_number}

    except TwilioRestException as e:
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
    
def get_existing_twilio_number():
    """
    Fetches the first available phone number already in the Twilio account
    using the Account SID and Auth Token.
    """
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

    if not account_sid or not auth_token:
        return {'status': 'error', 'message': 'Twilio ACCOUNT_SID and AUTH_TOKEN not found.'}

    try:
        client = Client(account_sid, auth_token)
        print("Fetching existing phone numbers...")
        incoming_phone_numbers = client.incoming_phone_numbers.list(limit=1)

        if not incoming_phone_numbers:
            return {'status': 'error', 'message': 'No phone numbers found in this account.'}
        
        trial_number = incoming_phone_numbers[0]
        print(f"Successfully found number: {trial_number.phone_number}")
        return {'status': 'success', 'phone_number': trial_number.phone_number}

    except Exception as e:
        return {'status': 'error', 'message': 'An unexpected error occurred. Check credentials.'}