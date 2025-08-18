from django.http import JsonResponse
from django.shortcuts import render
from backend.dashboard.functions import get_system_infomations, service_action, update_sevice_DB
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.authentication import SessionAuthentication
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
@swagger_auto_schema(
    method='PUT',
    operation_summary="API to update service action",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'service': openapi.Schema(type=openapi.TYPE_STRING,
                                      enum=['sshd','dhclient@','suricata','squid',
                                            'nftables','NetworkManager','openvpn',
                                            'ipsec','clamv','Asguard-Networking'],default="sshd"),
            'action': openapi.Schema(type=openapi.TYPE_STRING,enum=["enable","disable","start","stop"]),
        },
        required=['service', 'action'],
    ),
    responses={
        200: openapi.Response(
            description='Service action performed successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'msg': openapi.Schema(type=openapi.TYPE_STRING),
                },
                required=['msg'],
            ),
        ),
        400: openapi.Response(
            description='Bad request',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'msg': openapi.Schema(type=openapi.TYPE_STRING),
                },
                required=['msg'],
            ),
        ),
    },
)
# API to set actions service
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
def set_actions_service(request):
    if (request.method == 'PUT'):
        data_in=request.data
        service=data_in.get('service',None)
        action=data_in.get('action',None)
        if action is not None and service is not None:
            match action.lower():
                case "enable":
                    data={
                        "status_enabled":True
                    }
                    msg_suc=_('The service has enabled successfully!')
                    msg_err=_('Failed to enable the service!')
                case "disable":
                    data={
                        "status_enabled":False
                    }
                    msg_suc=_('The service has disabled successfully!')
                    msg_err=_('Failed to disable the service!')
                case "start":
                    data={
                        "status_started":True
                    }
                    msg_suc=_('The service has started successfully!')
                    msg_err=_('Failed to start the service!')
                case "stop":
                    data={
                        "status_started":False
                    }
                    msg_suc=_('The service has stopped successfully!')
                    msg_err=_('Failed to stop the service!')
                case "restart":
                    data={
                        "status_started":True
                    }
                    msg_suc=_('The service has restarted successfully!')
                    msg_err=_('Failed to restart the service!')
        aux=service_action(service, action)
        if aux is True:
           if update_sevice_DB(service,data) is True:
               msg=msg_suc
               status=200
           else:
               msg=update_sevice_DB(service,data)
               status=400
        else:
            msg=msg_err
            status=400
           
        return JsonResponse({"msg": msg}, status=status)    


