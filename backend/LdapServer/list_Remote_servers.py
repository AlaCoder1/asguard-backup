from django.shortcuts import render
from .models import ADServer
from django.http import JsonResponse
import json
from backend.authentification.views import *
from .serializers import ADServerSerializer
from rest_framework.response import Response
from rest_framework import status
from django.core import serializers



###################################### Function to display list of Servers ##########################

def get_list_ad_servers():
        """list of Remote servers"""

        servers_list = []
        # Get all Remote servers from database
        list_servers = ADServer.objects.all()
        servers = serializers.serialize("json", list_servers)
        res = json.loads(servers)
        print(res)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            servers_list.append(res[i]['fields'])

        # Return the list in json form 
        return json.dumps(servers_list)

########################################### Function to update the ldap server credentiels ####################################

def update_Ldapserver_DB(data,id):
    servers = ADServer.objects.get(id=id)
    server_serializers = ADServerSerializer(servers,data=data)
    if server_serializers.is_valid():
        server_serializers.save()
        return True
    return server_serializers.errors