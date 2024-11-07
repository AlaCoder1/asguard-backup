
from backend.gateway.models import Gateway
from backend.gateway.serializers import GatewaySerializer
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.core import serializers
import json
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from backend.gateway.functions import add_gateway_db, update_gateway_db
from django.core import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema


# Constants
CONSTANT_GATEWAY = _("Gateway")
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
# Error messages
ERROR_MESSAGES_DELETING = _("Error in deleting")
ERROR_MESSAGES_UPDATING = _("Error in updating")
ERROR_MESSAGES_INEXISTANT = _("does not exist")
ERROR_MESSAGES_EXISTANT = _("already exist")


@api_view(['GET'])
@permission_classes([])
def get_all_gateways(request):
    """API to get all gateways"""
    if (request.method == 'GET'):
        gateways = Gateway.objects.all()
        gateways_dict = serializers.serialize("json", gateways)
        res = json.loads(gateways_dict)
        list_gateways=[]
        for i in range(0, len(res)):
            res[i].pop('model')
            gateway_id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = gateway_id
            list_gateways.append(res[i]['fields'])
    return JsonResponse({"Gateways": list_gateways})


@api_view(['GET'])
@permission_classes([])
def get_all_static_gateways(request):
    """API to get all static gateways"""
    if (request.method == 'GET'):
        gateways= Gateway.objects.filter(staticgw=True)
        gateways_dict = serializers.serialize("json", gateways)
        res = json.loads(gateways_dict)
        list_gateways=[]
        for i in range(0, len(res)):
            res[i].pop('model')
            gateway_id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = gateway_id
            list_gateways.append(res[i]['fields'])
    return JsonResponse({"Gateways": list_gateways})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_gateway_by_id(request, id):
    if request.method == 'GET':
        try:
            gateway = Gateway.objects.get(id=id)
            gateway_data = serializers.serialize("json", [gateway])
            res = json.loads(gateway_data)
            list_gateways=[]
            for i in range(0, len(res)):
                res[i].pop('model')
                gateway_id = res[i]['pk']
                res[i].pop('pk')
                res[i]['fields']['id'] = gateway_id
                list_gateways.append(res[i]['fields'])
            return JsonResponse({"Gateway": list_gateways})
        except Gateway.DoesNotExist:
            return JsonResponse({"error": f"{CONSTANT_GATEWAY} {ERROR_MESSAGES_INEXISTANT}"}, status=404)     


@swagger_auto_schema(
    method='POST',
    request_body=GatewaySerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO ADD GATEWAY",
    operation_description="This API add gateway with their caracteristique in database",
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def add_static_gateway(request):
    """API to add  static gateway"""
    if (request.method == 'POST'):
        data = request.data
        gwaddress = data.get('gwaddress', None)
        data['staticgw']=True
        if Gateway.objects.filter(Q(gwaddress=gwaddress) & Q(staticgw=True)).exists():
            msg = f"{CONSTANT_GATEWAY} {ERROR_MESSAGES_EXISTANT}"
            status=404
        else:
            aux_gateway=add_gateway_db(data)
            if  aux_gateway is True:
                msg = f"{CONSTANT_GATEWAY} {(SUCCESS_MESSAGES_CREATING)}"
                status=200
            else:
                msg =aux_gateway
                status=400
           
        return JsonResponse({"msg": msg},status=status)   


@swagger_auto_schema(
    method='DELETE',
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API DELETE GATEWAY",
    operation_description="This API delete gateway by id ",
)
@api_view(['DELETE'])
@permission_classes([])
def delete_gateway(request,id):
    """API to delete gateway"""
    if (request.method == 'DELETE'):
        msg = f"{ERROR_MESSAGES_DELETING} {CONSTANT_GATEWAY}"
        #tester si rule exist ou non
        if (Gateway.objects.filter(id=id).exists()):
            gateways = Gateway.objects.get(id=id)
            gateways.delete()
            msg = f"{CONSTANT_GATEWAY} {(SUCCESS_MESSAGES_DELETING)}"
    return JsonResponse({"msg": msg})      


@swagger_auto_schema(
    method='PUT',
    request_body=GatewaySerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE GATEWAY",
    operation_description="This API help us to update parametres in gateway added ",
)
@api_view(['PUT'])
@permission_classes([])
def update_gateway(request,id):
    """API to delete gateway"""
    if (request.method == 'PUT'):
        msg = f"{ERROR_MESSAGES_UPDATING} {CONSTANT_GATEWAY}"
        #tester si rule exist ou non
        if (Gateway.objects.filter(id=id).exists()):
            data = JSONParser().parse(request)
            if update_gateway_db(data,id):
                msg = f"{CONSTANT_GATEWAY} {(SUCCESS_MESSAGES_UPDATING)}"
    return JsonResponse({"msg": msg})
