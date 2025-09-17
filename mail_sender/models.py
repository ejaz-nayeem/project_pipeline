from django.db import models
import uuid
from django.conf import settings

class EmailAccount(models.Model):
    address = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.address:
            self.address = f"{uuid.uuid4().hex}@{settings.MAILGUN_DOMAIN}"
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.address
    
class EmailVerification(models.Model):
    # A unique ID to easily find this record via an API
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # The email address the verification was sent to
    recipient_email = models.EmailField()
    
    # The full verification link extracted from the email
    verification_link = models.URLField(max_length=1024)
    
    # Status fields to track our progress
    is_clicked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    clicked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Link for {self.recipient_email} | Clicked: {self.is_clicked}"