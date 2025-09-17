# ip_generate_with_one_click/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import make_request_with_oxylabs

from django.shortcuts import redirect 
from django.urls import reverse

class PerformRedirectView(APIView):
    def get(self, request, *args, **kwargs):
        return redirect("https://www.openrent.co.uk/")

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
        
class GenerateIPAndRedirectView(APIView):
    """
    1. Gets a real UK IP address from Oxylabs.
    2. Creates a special URL that, when visited, will redirect to OpenRent.
    3. Returns both the IP and the special URL as JSON.
    """
    def get(self, request, format=None):
        # Step 1: Get the new IP address (same as before)
        ip_test_url = 'https://ip.oxylabs.io/json'
        response = make_request_with_oxylabs(ip_test_url, country='GB')
        
        if not response:
            return Response({'error': 'Failed to get a response from the proxy.'}, status=502)

        try:
            ip_data = response.json()
            generated_ip = ip_data.get('client_ip')
            if not generated_ip:
                return Response({'error': 'Could not extract IP from proxy response.', 'details': ip_data}, status=500)
        except Exception as e:
            return Response({'error': f'Failed to parse proxy response: {e}'}, status=500)

        # Step 2: Create the redirect URL
        # We use Django's 'reverse' to build a full, absolute URL to our new redirect view.
        # This is the "special" URL we will send to the frontend.
        redirect_path = reverse('perform-redirect')
        absolute_redirect_url = request.build_absolute_uri(redirect_path)

        # Step 3: Return both pieces of data
        return Response({
            'generated_ip': generated_ip,
            'redirect_url': absolute_redirect_url
        }, status=status.HTTP_200_OK)