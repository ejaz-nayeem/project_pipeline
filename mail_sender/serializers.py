# mail_sender/serializers.py
from rest_framework import serializers
from .models import EmailAccount

class EmailAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAccount
        fields = ['address', 'created_at']