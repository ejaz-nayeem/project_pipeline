# ip_solution/utils.py

import os # <-- We need os to access environment variables
import requests
from urllib.parse import quote

# Oxylabs proxy connection details are constants
PROXY_HOST = 'pr.oxylabs.io'
PROXY_PORT = '7777'

def make_request_with_oxylabs(url, method='GET', data=None, headers=None, country='GB'):
    """
    Makes a robust HTTP request through the Oxylabs rotating residential proxy network.
    Credentials are loaded directly from environment variables.
    """
    # Load credentials securely from environment variables (from the .env file)
    oxylabs_user_base = os.environ.get('OXYLABS_USER')
    oxylabs_password = os.environ.get('OXYLABS_PASSWORD')

    if not oxylabs_user_base or not oxylabs_password:
        raise ValueError("Oxylabs credentials not found in environment variables. Ensure .env is loaded correctly.")

    username = f"customer-{oxylabs_user_base}-cc-{country.upper()}"
    password_safe = quote(oxylabs_password)
    
    proxy_url = f"http://{username}:{password_safe}@{PROXY_HOST}:{PROXY_PORT}"
    
    proxies = { "http": proxy_url, "https": proxy_url }
    
    if headers is None:
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36' }

    try:
        if method.upper() == 'GET':
            response = requests.get(url, proxies=proxies, headers=headers, timeout=20)
        elif method.upper() == 'POST':
            response = requests.post(url, data=data, proxies=proxies, headers=headers, timeout=20)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"Request Error for {url}: {e}") # Or use proper Django logging
        return None