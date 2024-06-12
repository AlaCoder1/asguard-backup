from django.http import JsonResponse
from django.shortcuts import render
from backend.dashboard.functions import get_system_infomations, service_action, update_sevice_DB
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.authentication import SessionAuthentication


# API to set actions service
@api_view(['PUT'])
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
                case "disable":
                    data={
                        "status_enabled":False
                    }
                case "start":
                    data={
                        "status_started":True
                    }
                case "stop":
                    data={
                        "status_started":False
                    }
        aux=service_action(service, action)
        if aux is True:
           if update_sevice_DB(service,data) is True:
               msg=f"You {action} the service successfully!!"
               status=200
           else:
               msg=update_sevice_DB(service,data)
               status=400
        else:
            msg=aux
            status=400
           
        return JsonResponse({"msg:": msg}, status=status)    


def monitoring(request):
    get_system_infomations()
    return render(request, 'basedashboard.html')
