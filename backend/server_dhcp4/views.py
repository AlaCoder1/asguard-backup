import json
from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes
# # Create your views here.

# @api_view(['PUT'])
# @authentication_classes([SessionAuthentication])
# def update_server_dhcp(request):
#     """API to get all vlan from database """
#     if (request.method == 'PUT'):
        
#     return JsonResponse({"response": "hello"})  