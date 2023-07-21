import json
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from django.core import serializers
from .models import IPsecServer

# Create your views here.

@api_view(['GET'])
@permission_classes([])
def getAllIPsec(request):
    list_ipsec = []
    if (request.method == 'GET'):
        ipsec = IPsecServer.objects.all()
        ipsecDict = serializers.serialize("json", ipsec)
        res = json.loads(ipsecDict)
        for i in range(len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_ipsec.append(res[i]['fields'])
        # return list_openvpn
        return JsonResponse(list_ipsec, safe=False)