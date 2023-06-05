from django.http import JsonResponse

from managementUsers.remoteFunctions import decrypt
from .models import *
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
import json
from managementUsers.models import *
from managementUsers.functions import *
from django.core import serializers
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from authentification.authentication import JWTAuthentication
# Create your views here.


@api_view(['GET'])
@permission_classes([AllowAny])
def getAllServers(request):
    list_servers = []
    if (request.method == 'GET'):
        servers = Server.objects.all()
        serverDict = serializers.serialize("json", servers)
        res = json.loads(serverDict)
        print(res)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            type = Type.objects.get(id=res[i]['fields']['type'])
            print(type.type_name)
            res[i]['fields']['id'] = id
            res[i]['fields']['type_name'] = type.type_name
            list_servers.append(res[i]['fields'])
        return JsonResponse(list_servers, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def getServer(request, id):
    if (request.method == 'GET'):
        server = Server.objects.filter(id=id)
        serverDict = serializers.serialize("json", server)
        res = json.loads(serverDict)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        type = Type.objects.get(id=res[0]['fields']['type'])
        res[0]['fields']['id'] = id
        res[0]['fields']['type_name'] = type.type_name
        serverJson = res[0]['fields']
        # return a no content response.
        return JsonResponse(serverJson)


@api_view(['POST'])
@permission_classes([AllowAny])
def createServer(request):
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        user = User.objects.filter(username=data["username"])
        if (len(user) != 0):
            serverDict = serializers.serialize("json", user)
            res = json.loads(serverDict)
            if (decrypt(res[0]['fields']['password']) == data['password']):
                # instanciate with the serializer
                serializerServer = ServerSerializerPost(data=data)
                # check if the sent information is okay
                if (serializerServer.is_valid()):
                    msg = 'server added succesfully'
                    # if okay, save it on the database
                    serializerServer.save()
                    # provide a Json Response with the data that was saved
                    return JsonResponse({"msg": msg}, status=201)

                # provide a Json Response with the necessary error information
                return JsonResponse(serializerServer.errors, status=400)
            else:
                msg = "invalid password"
                return JsonResponse({"msg": msg}, status=201)
        else:
            msg = "invalid " + data['username']
            return JsonResponse({"msg": msg}, status=201)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def deleteServer(request, id):
    msg = ""
    if (request.method == 'DELETE'):
        server = Server.objects.get(id=id)
        server.delete()
        msg = "delete succesfully"
        # return a no content response.
        return JsonResponse({"msg": msg})


@api_view(['PUT'])
@permission_classes([AllowAny])
def modifyServer(request, id):
    msg = ''
    if (request.method == 'PUT'):
        serverById = Server.objects.filter(id=id)
        serverDict = serializers.serialize("json", serverById)
        res = json.loads(serverDict)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields']['id'] = id
        serverJson = res[0]['fields']
        data = json.loads(request.body)
        serverObject = Server.objects.get(id=id)
        server = serverObject.__dict__
        type = Type.objects.get(id=data['type'])
        user = User.objects.filter(username=data["username"])
        if (len(user) != 0):
            serverDict = serializers.serialize("json", user)
            res = json.loads(serverDict)
            if (decrypt(res[0]['fields']['password']) == data['password']):
                serverObject.name_server = data['name_server']
                serverObject.hostname = data['hostname']
                serverObject.transport = data['transport']
                serverObject.protocol_version = data['protocol_version']
                serverObject.scope = data['scope']
                serverObject.domaine_name = data['domaine_name']
                serverObject.type = type
                serverObject.save()
                msg = "update succesfully"
                return JsonResponse({"msg": msg})
            else:
                msg = "invalid password"
                return JsonResponse({"msg": msg}, status=201)
        else:
            msg = "invalid " + data['username']
            return JsonResponse({"msg": msg}, status=201)
