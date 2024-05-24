from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from .models import Server, Type
from .serializers import ServerSerializerPost
import json
from backend.managementUsers.models import User
from django.core import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth.hashers import check_password


# Constants
CONSTANT_USER = _('User')
CONSTANT_SERVER = _('Server')
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
# Error messages
ERROR_MESSAGES_INEXISTANT = _("does not exist")
ERROR_MESSAGES_INVALID_PASSWORD = _("Invalid password")


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_servers(request):
    list_servers = []
    if (request.method == 'GET'):
        servers = Server.objects.all()
        server_dict = serializers.serialize("json", servers)
        res = json.loads(server_dict)
        for i in range(0, len(res)):
            res[i].pop('model')
            server_id = res[i]['pk']
            res[i].pop('pk')
            server_type = Type.objects.get(id=res[i]['fields']['type'])
            res[i]['fields']['id'] = server_id
            res[i]['fields']['type_name'] = server_type.type_name
            list_servers.append(res[i]['fields'])
        return JsonResponse(list_servers, safe=False)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def get_server(request, id):
    if (request.method == 'GET'):
        server = Server.objects.filter(id=id)
        server_dict = serializers.serialize("json", server)
        res = json.loads(server_dict)
        res[0].pop('model')
        server_id = res[0]['pk']
        res[0].pop('pk')
        server_type = Type.objects.get(id=res[0]['fields']['type'])
        res[0]['fields']['id'] = server_id
        res[0]['fields']['type_name'] = server_type.type_name
        server_json = res[0]['fields']
        # return a no content response.
        return JsonResponse(server_json)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
# @permission_classes([IsAuthenticated])
def create_server(request):
    if (request.method == 'POST'):
        
        # parse the incoming information
        data = request.data
        user_search = User.objects.filter(username=data["username"])
        if (len(user_search) != 0):
            user = User.objects.get(username=data["username"])
            server_dict = serializers.serialize("json", user_search)
            res = json.loads(server_dict)
            if check_password(data['password'], user.__dict__['password']):
                # instanciate with the serializer
                serializer_server = ServerSerializerPost(data=data)
                # check if the sent information is okay
                if (serializer_server.is_valid()):
                    # if okay, save it on the database
                    serializer_server.save()
                    # provide a Json Response with the data that was saved
                    return JsonResponse({"msg": f"{CONSTANT_SERVER} {SUCCESS_MESSAGES_CREATING}"}, 
                                        status=201)
                # provide a Json Response with the necessary error information
                return JsonResponse(serializer_server.errors, status=400)
            return JsonResponse({"msg": ERROR_MESSAGES_INVALID_PASSWORD}, status=201)
        return JsonResponse({"msg": f"{CONSTANT_USER} {ERROR_MESSAGES_INEXISTANT}"}, status=201)


@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_server(request, id):
    if (request.method == 'DELETE'):
        server = Server.objects.get(id=id)
        server.delete()
        # return a no content response.
        return JsonResponse({"msg": f"{CONSTANT_SERVER} {SUCCESS_MESSAGES_DELETING}"})


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def modify_server(request, id):
    if (request.method == 'PUT'):
        server_by_id = Server.objects.filter(id=id)
        server_dict = serializers.serialize("json", server_by_id)
        res = json.loads(server_dict)
        res[0].pop('model')
        server_id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields']['id'] = server_id
        server_json = res[0]['fields']
        data = request.data
        server_object = Server.objects.get(id=server_id)
        server = server_object.__dict__
        type = Type.objects.get(id=data['type'])
        user_search = User.objects.filter(username=data["username"])
        if (len(user_search) != 0):
            user = User.objects.get(username=data["username"])
            server_dict = serializers.serialize("json", user_search)
            res = json.loads(server_dict)
            if check_password(data['password'], user.__dict__['password']):
                server_object.name_server = data['name_server']
                server_object.hostname = data['hostname']
                server_object.transport = data['transport']
                server_object.protocol_version = data['protocol_version']
                server_object.scope = data['scope']
                server_object.domaine_name = data['domaine_name']
                server_object.type = type
                server_object.save()
                return JsonResponse({"msg": f"{CONSTANT_SERVER} {SUCCESS_MESSAGES_UPDATING}"})
            return JsonResponse({"msg": ERROR_MESSAGES_INVALID_PASSWORD}, status=201)
        return JsonResponse({"msg": f"{CONSTANT_USER} {ERROR_MESSAGES_INEXISTANT}"}, status=201)
