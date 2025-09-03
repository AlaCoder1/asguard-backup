from django.shortcuts import render
from backend.double_mask.constant_variables import PATH_DOUBLE_MASK
from backend.double_mask.models import DoubleMask
from backend.double_mask.serializers import DoubleMaskSerializer
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import api_view, authentication_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.authentication import SessionAuthentication
from django.http import JsonResponse
from .functions import get_compr_ratio, get_nft_ip_addresses, is_address_in_subnet, run_command
from django.views.decorators.http import require_http_methods

CONSTANT_DOUBLE=_("Double Mask")
SUCCESS_MESSAGES_ACTIVE=_("is activated.")
SUCCESS_MESSAGES_DEACTIVE=_("is deactivated.")


@swagger_auto_schema(
    method='PUT',
    operation_summary="API to activate double mask.",
    operation_description="This endpoint allows users to activate the double mask.",
    responses={
        200: f"{CONSTANT_DOUBLE} {SUCCESS_MESSAGES_ACTIVE}",
        400: "An error occurred while activating Double Mask."
    }
)
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
def activate_double_mask(request):
    """
    API to activate double mask.

    This function handles the PUT request to activate double mask in the database.
    It checks if double mask is installed and returns an error message if it isn't.
    Otherwise, it activates double mask and returns a success message.
    """
    if request.method=="PUT":
        out,error=run_command(f"cd {PATH_DOUBLE_MASK} && sudo make install")
        if error.strip()=="":
            active=True
            object_double_mask=DoubleMask.objects.first()
            double_mask_ser=DoubleMaskSerializer(object_double_mask, data={"active":active})
            if double_mask_ser.is_valid():
               
                double_mask_ser.save()
                return JsonResponse({"msg": f"{CONSTANT_DOUBLE} {SUCCESS_MESSAGES_ACTIVE}"}, status=200)
            return JsonResponse({"error": str(next(iter(double_mask_ser.errors.values()))[0]).strip('.')+"!"}, status=400)
        return JsonResponse({"error": _("An error occurred while activating Double Mask.")}, status=400)


@swagger_auto_schema(
    method='PUT', 
    operation_summary="API to deactive double mask.",
    operation_description="This endpoint allows users to deactive double mask.",
    responses={
        200: f"{CONSTANT_DOUBLE} {SUCCESS_MESSAGES_DEACTIVE}",
        400: "An error occurred while deactivating Double Mask."
    }
)
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
def deactivate_double_mask(request):
    """
    API to deactive double mask.

    This function handles the PUT request to deactivate double mask from the database.
    It checks if double mask is installed and returns an error message if it isn't.
    Otherwise, it deactivates double mask and returns a success message.
    """
    if request.method=="PUT":
        out,error=run_command(f"cd {PATH_DOUBLE_MASK} && sudo make uninstall")
        if error.strip()=="":
            print("hello")
            active=False
            object_double_mask=DoubleMask.objects.first()
            double_mask_ser=DoubleMaskSerializer(object_double_mask, data={"active":active})
            if double_mask_ser.is_valid():
                print(double_mask_ser)
                double_mask_ser.save()
                message=f"{CONSTANT_DOUBLE} {SUCCESS_MESSAGES_DEACTIVE}"
                status=200
            else:
                message=str(next(iter(double_mask_ser.errors.values()))[0]).strip('.')+"!"
                status=400  
        else:  
            message=_("An error occurred while deactivating Double Mask.")
            status=400
    return JsonResponse({"msg": message},status=status)


@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
def get_double_mask(request):
    """
    API to get double mask status.

    This function handles the GET request to get the status of double mask.
    It checks if double mask is installed and returns its status.
    
    
    """
    if request.method == 'GET':
        n=0
        n_comp=0
        output,error=run_command('sudo lsmod | grep "ip_filter"')
        if output=="":
            active=False
        else:
            active=True
        ratio,n_comp,n=get_compr_ratio()
        if DoubleMask.objects.all().count()==1:
            double_mask_object=DoubleMask.objects.all().first()
            double_mask_object.active=active
            double_mask_object.ratio=ratio
            double_mask_object.save()
        else:
            double_mask_object=DoubleMask(active=active)
            double_mask_object.save()
    return JsonResponse({"msg": {"active":active,"ratio":ratio,"n_actuel":n_comp,"n_init":n}},status=200)
