# phone_generate_with_one_click/models.py
from django.db import models

class ReceivedOTP(models.Model):
    # The number that received the code
    phone_number = models.CharField(max_length=20, db_index=True)
    
    # The 6-digit code
    otp_code = models.CharField(max_length=10)
    
    # Status fields
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP {self.otp_code} for {self.phone_number} | Used: {self.is_used}"