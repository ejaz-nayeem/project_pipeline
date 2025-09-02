import hmac
import hashlib
import time
import os

# --- INPUTS ---
# This must match the key in your .env file
SIGNING_KEY = "14303712ab3db033162bd59ed56240b6" 

# These values must match what you will put into Postman
TIMESTAMP = str(int(time.time()))
TOKEN = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6" # A random string is fine

# --- CALCULATION ---
message = f"{TIMESTAMP}{TOKEN}".encode('utf-8')
expected_signature = hmac.new(
    key=SIGNING_KEY.encode('utf-8'),
    msg=message,
    digestmod=hashlib.sha256
).hexdigest()

# --- OUTPUT ---
print("--- Use these values in Postman ---")
print(f"timestamp: {TIMESTAMP}")
print(f"token:     {TOKEN}")
print(f"signature: {expected_signature}")
print("-----------------------------------")