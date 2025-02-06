from django.shortcuts import render
from backend.double_mask.serializers import DoubleMaskSerializer
from backend.ipsecmonitoring.functions import run_command
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import api_view, authentication_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.authentication import SessionAuthentication
from django.http import JsonResponse

CONSTANT_DOUBLE=_("Double Mask")
SUCCESS_MESSAGES_ACTIVE=_("is active.")
SUCCESS_MESSAGES_DEACTIVE=_("is deactive.")
@swagger_auto_schema(
    method='PUT', 
    operation_summary="API to active double mask.",
    operation_description="This endpoint allows users to active double mask.",
    responses={
        200: f"{CONSTANT_DOUBLE} {SUCCESS_MESSAGES_ACTIVE}",
        400:  _("An error occurred while activating Double Mask.")
    }
)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def activate_double_mask(request):
    """
    API to activate double mask.

    This function handles the PUT request to activate double mask in the database.
    It checks if double mask is installed and returns an error message if it isn't.
    Otherwise, it activates double mask and returns a success message.
    """
    if request.method=="PUT":
        _,error=run_command("cd /home/dbmask/dm && sudo make install")
        if error!="":
            active=True
            double_mask_ser=DoubleMaskSerializer({"active":active})
            if double_mask_ser.is_valid():
                double_mask_ser.save()
                message=f"{CONSTANT_DOUBLE} {SUCCESS_MESSAGES_ACTIVE}"
                status=200
        message=_("An error occurred while activating Double Mask.")
        status=400
        
        
    return JsonResponse({"msg": message},status=status)

@swagger_auto_schema(
    method='PUT', 
    operation_summary="API to deactive double mask.",
    operation_description="This endpoint allows users to deactive double mask.",
    responses={
        200: f"{CONSTANT_DOUBLE} {SUCCESS_MESSAGES_DEACTIVE}",
        400:  _("An error occurred while deactivating Double Mask.")
    }
)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def deactivate_double_mask(request):
    """
    API to deactive double mask.

    This function handles the PUT request to deactivate double mask from the database.
    It checks if double mask is installed and returns an error message if it isn't.
    Otherwise, it deactivates double mask and returns a success message.
    """
    if request.method=="PUT":
        _,error=run_command("cd /home/dbmask/dm && sudo make uninstall")
        if error!="":
            active=False
            double_mask_ser=DoubleMaskSerializer({"active":active})
            if double_mask_ser.is_valid():
                double_mask_ser.save()
                message=f"{CONSTANT_DOUBLE} {SUCCESS_MESSAGES_DEACTIVE}"
                status=200
                
        message=_("An error occurred while deactivating Double Mask.")
        status=400
        
        
    return JsonResponse({"msg": message},status=status)


    