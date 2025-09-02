from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import make_request_with_oxylabs

class ProxyTestView(APIView):
    def get(self, request, format=None):
        test_url = 'https://ip.oxylabs.io/location'
        response = make_request_with_oxylabs(test_url, country='GB')
        if response:
            return Response({'status': 'success', 'data': response.text}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Request failed via proxy.'}, status=status.HTTP_502_BAD_GATEWAY)