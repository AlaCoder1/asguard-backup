from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
import json
from django.core import serializers
# Create your views here.

@csrf_exempt
def Settings(request,id):
    # getSystem(request, id)
    # getNetwork(request, id)
    # getServerReseau(request, id)
    # print(getSystem(request, id))
    # print(getNetwork(request, id))
    # print(getServerReseau(request, id))
    return JsonResponse(getSystem(request, id))


@csrf_exempt
def getSystem(request, id):
    if (request.method == 'GET'):
        system = System.objects.filter(id=id)
        systemDict = serializers.serialize("json", system)
        res = json.loads(systemDict)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields']['id'] = id
        systemJson = res[0]['fields']
        # return a no content response.
        return JsonResponse(systemJson)


@csrf_exempt
def getNetwork(request, id):
    if (request.method == 'GET'):
        network = Network.objects.filter(id=id)
        networkDict = serializers.serialize("json", network)
        res = json.loads(networkDict)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields']['id'] = id
        networkJson = res[0]['fields']
        # return a no content response.
        return JsonResponse(networkJson)


@csrf_exempt
def getServerReseau(request, id):
    if (request.method == 'GET'):
        serverReseau = ServerReseau.objects.filter(id=id)
        serverReseauDict = serializers.serialize("json", serverReseau)
        res = json.loads(serverReseauDict)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields']['id'] = id
        serverReseauJson = res[0]['fields']
        # return a no content response.
        return JsonResponse(serverReseauJson)


@csrf_exempt
def createSystem(request):
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        # instanciate with the serializer
        serializerSystem = SystemSerializer(data=data)
        # check if the sent information is okay
        if (serializerSystem.is_valid()):
            msg = 'system added succesfully'
                # if okay, save it on the database
            serializerSystem.save()
                # provide a Json Response with the data that was saved
            return JsonResponse({"msg": msg}, status=201)
            # provide a Json Response with the necessary error information
            return JsonResponse(serializerUser.errors, status=400)
        # provide a Json Response with the necessary error information
        return JsonResponse(SystemSerializer.errors, status=400)


@csrf_exempt
def createNetwork(request):
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        # instanciate with the serializer
        serializerNetwork = NetworkSerializer(data=data)
        # check if the sent information is okay
        if (serializerNetwork.is_valid()):
            msg = 'Network added succesfully'
                # if okay, save it on the database
            serializerNetwork.save()
                # provide a Json Response with the data that was saved
            return JsonResponse({"msg": msg}, status=201)
            # provide a Json Response with the necessary error information
            return JsonResponse(serializerUser.errors, status=400)
        # provide a Json Response with the necessary error information
        return JsonResponse(SystemSerializer.errors, status=400)



@csrf_exempt
def createServerReseau(request):
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        # instanciate with the serializer
        serializerServerReseau = ServerReseauSerializer(data=data)
        # check if the sent information is okay
        if (serializerServerReseau.is_valid()):
            msg = 'ServerReseau added succesfully'
                # if okay, save it on the database
            serializerServerReseau.save()
                # provide a Json Response with the data that was saved
            return JsonResponse({"msg": msg}, status=201)
            # provide a Json Response with the necessary error information
            return JsonResponse(serializerUser.errors, status=400)
        # provide a Json Response with the necessary error information
        return JsonResponse(SystemSerializer.errors, status=400)



