# ip_generate_with_one_click/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import make_request_with_oxylabs

class GenerateIPView(APIView):
    def get(self, request, format=None):
        test_url = 'https://ip.oxylabs.io/json'
        
        response = make_request_with_oxylabs(test_url, country='GB')
        
        if response:
            # --- START DEBUGGING LOGS ---
            print("-----------------------------------------")
            print(f"Proxy Response Status Code: {response.status_code}")
            print("Proxy Response Headers:")
            print(response.headers)
            print("Proxy Response Body (Raw Text):")
            print(response.text)
            print("-----------------------------------------")
            # --- END DEBUGGING LOGS ---

            try:
                ip_data = response.json()
                ip_address = ip_data.get('client_ip') # This will be None if 'ip' key doesn't exist
                return Response({'ip_address': ip_address}, status=status.HTTP_200_OK)
            except Exception as e:
                # This happens if response.text is not valid JSON
                return Response({'error': f'Failed to parse JSON data. Raw response was: {response.text}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'The make_request_with_oxylabs function returned None.'}, status=status.HTTP_502_BAD_GATEWAY)