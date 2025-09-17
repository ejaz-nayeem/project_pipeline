# web_accessor/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ip_solution.services import make_request_with_oxylabs
from bs4 import BeautifulSoup

class AccessOpenRentView(APIView):
    """
    An API endpoint that accesses the OpenRent website through the
    Oxylabs residential proxy service and reports which IP was used.
    """
    def get(self, request, format=None):
        target_url = 'https://www.openrent.co.uk/'
        ip_checker_url = 'https://ip.oxylabs.io/json' # URL to check our IP
        
        print(f"STEP 1: Attempting to access {target_url} via Oxylabs proxy...")

        # --- First, access the target website ---
        openrent_response = make_request_with_oxylabs(target_url, country='GB')
        
        if not openrent_response:
            print(f"Failed to access {target_url}.")
            return Response({
                'status': 'error',
                'message': 'The request to the target URL via the proxy failed.'
            }, status=status.HTTP_502_BAD_GATEWAY)

        print(f"Successfully accessed {target_url}. Now checking which IP was used...")
        
        # --- Second, if the first request succeeded, check the IP ---
        # We make another request to an IP checker through the same service.
        # This will use a new, but similar, UK residential IP.
        ip_check_response = make_request_with_oxylabs(ip_checker_url, country='GB')
        
        proxy_ip_used = "Could not determine IP address" # Default value
        if ip_check_response:
            try:
                ip_data = ip_check_response.json()
                # The key for the IP address in the response is 'client_ip'
                proxy_ip_used = ip_data.get('client_ip', 'IP key not found in response')
            except Exception:
                proxy_ip_used = "Failed to parse IP checker response"
        
        # --- Finally, parse the data from the first request and build the response ---
        try:
            soup = BeautifulSoup(openrent_response.text, 'html.parser')
            page_title = soup.title.string if soup.title else "No title found"
            
            # --- NEW: Construct the more detailed success response ---
            return Response({
                'status': 'success',
                'message': 'Successfully accessed the website via proxy.',
                'target_url': target_url, # <-- ADDITION 1: The URL link
                'page_title': page_title,
                'proxy_ip_used': proxy_ip_used # <-- ADDITION 2: The IP address
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Failed to parse the HTML content. Error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)