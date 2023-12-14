from django.shortcuts import render
from .models import ClamAV
from django.http import JsonResponse
import json
from django.http import JsonResponse
from backend.authentification.views import *
from .serializers import ClamavSerializer
from rest_framework.response import Response
from rest_framework import status
from django.core import serializers
from django.db.models import Q


def getclamavconfigurations(request):
    if request.method=="GET":
        clamd_list = []
        # Get all configurations from database
        clamavconfig_from_db = ClamAV.objects.all()
        clamd = serializers.serialize("json", clamavconfig_from_db)
        res = json.loads(clamd)
        print(res)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            clamd_list.append(res[i]['fields'])

        # Return the list in json form 
    return json.dumps(clamd_list)
    