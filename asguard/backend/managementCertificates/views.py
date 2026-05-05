from datetime import datetime, timedelta
from django.http import JsonResponse
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import SessionAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Schema, TYPE_BOOLEAN, TYPE_INTEGER, TYPE_OBJECT, TYPE_STRING, Parameter, IN_PATH
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from backend.ipsec.models import ServerIPsec
from backend.managementCertificates.certificate import create_certificate_in_system, delete_certificate_in_system, export_certificate_in_system, import_certificate_in_system, revoke_certificates_in_system, unrevoke_certificates_in_system

from backend.managementCertificates.certificate_authority import create_ca_in_system, delete_ca_in_system, export_ca_in_system, export_ca_list_rev_in_system, import_ca_in_system
from backend.managementCertificates.constant_variables import PATH_CA_CRT, PATH_CA_KEY
from backend.managementCertificates.list_certificates import get_list_all_cert_auth, get_list_all_certificates, get_one_cert_auth, get_one_certificate
from backend.managementCertificates.models import Certificate, CertificateAuthority
from backend.managementCertificates.serializers import CertificateAuthoritySerializer, CertificateSerializer
from backend.managementCertificates.utils import check_payload
from backend.waf.models import ApplicationWaf
from utils.errors_utils import CommandExecutionError
from backend.openvpn.models import ClientOpenvpn, ServerOpenvpn

from django.views.decorators.http import require_http_methods
import threading
from backend.backup.notifications import notify_certificate_change
# Constants
CONSTANT_CA = _("Certificate Authority")
CONSTANT_OPENVPN_SERVER = _("openvpn server")
CONSTANT_OPENVPN_CLIENT = _("openvpn client")
CONSTANT_IPSEC = _("IPsec")
CONSTANT_WAF = _("WAF")
CONSTANT_REVOCATION_LIST = _("revocation list")
CONSTANT_CERT = _("Certificate")
CONSTANT_USED_ITEM = _("it's used in")
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
# Error messages
ERROR_MESSAGES_CREATING = _("System error in creating")
ERROR_MESSAGES_DELETING = _("System error in deleting")
ERROR_MESSAGES_EXPORTING = _("System error in exporting")
ERROR_MESSAGES_DELETING_USED_ITEM = _("Unable to delete")
ERROR_MESSAGES_INEXISTANT = _("does not exist")
ERROR_MESSAGES_INVALID_DATA = _("Invalid data")


##################################################
############# Certificates Authority #############
##################################################

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL CERTIFICATES AUTHORITY",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_cert_auth(request):
    """Getting all Certificates Authority from database"""
    if (request.method == 'GET'):
        list_ca = get_list_all_cert_auth()
        return JsonResponse(list_ca, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO GET A CERTIFICATE AUTHORITY",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_cert_auth(request, id):
    """Getting a Certificates Authority by id from database"""
    if (request.method == 'GET'):
        cert = get_one_cert_auth(id)
        if cert:
            return JsonResponse(cert, safe=False)
        return JsonResponse({"error": f"{CONSTANT_CA} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'POST', responses={200: 'Created', 400: 'Bad Request'}, 
    operation_summary="API TO CREATE CERTIFICATE AUTHORITY",
    request_body=Schema(
        type=TYPE_OBJECT, required=['name', 'method'],
        properties={
            'name': Schema(type=TYPE_STRING, example="ca_create"),
            'method': Schema(type=TYPE_OBJECT, required=['name_method'],
            properties={
                'name_method': Schema(type=TYPE_STRING, enum=["create", "import"]),
                'key_type': Schema(type=TYPE_STRING, example="rsa"),
                'key_length': Schema(type=TYPE_INTEGER, example=2048),
                'digest_algorithm': Schema(type=TYPE_STRING, example="sha256", pattern=r'\bsha\d+', description="start with sha like sha123"),
                'lifetime': Schema(type=TYPE_INTEGER, example=325),
                'country_code': Schema(type=TYPE_STRING, example="\"TN\""),
                'state': Schema(type=TYPE_STRING, example="\"Openvpn\""),
                'city': Schema(type=TYPE_STRING, example="\"Bizerte\""),
                'organization': Schema(type=TYPE_STRING, example="\"Numeryx\""),
                'email': Schema(type=TYPE_STRING, example="\"root@numeryx.fr\""),
                'common_name': Schema(type=TYPE_STRING, example="create-ca"),
                'certificate_data': Schema(type=TYPE_STRING, example="-----BEGIN CERTIFICATE-----\nMIIDwDCCAqigAwIBAgIBADANBgkqhkiG9w0BAQsFADBdMQswCQYDVQQGEwJBRDEL\nMAkGA1UECAwCYWExCzAJBgNVBAcMAmFhMQswCQYDVQQKDAJhYTERMA8GCSqGSIb3\nDQEJARYCYWExFDASBgNVBAMMC2ludGVybmFsLWNhMB4XDTIzMDkyOTE1NTQ1OVoX\nDTI2MDEwMTE1NTQ1OVowXTELMAkGA1UEBhMCQUQxCzAJBgNVBAgMAmFhMQswCQYD\nVQQHDAJhYTELMAkGA1UECgwCYWExETAPBgkqhkiG9w0BCQEWAmFhMRQwEgYDVQQD\nDAtpbnRlcm5hbC1jYTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAK9F\n3mrjuAGr4JFwimHCE9zXA5MSKLIxpclDgKUpIu/JYEGV95jhbU1zRPwLHm2PxWq0\n3S7nGT9IcFuiclfRNUDu0/0OKiSdr25CAq81M1vYK9LwRVAJHDFExL/TeH3R1JlM\nZLyPFGTfYGCZXSc576ku6c+DuSCl6hgSAUYh1OJQ7oLWfmL7i+7LesosKTyV6MZu\ndtNFYuCR2J0TxY5Q/v8MQaUPTxbLCEYCtvB/CX8MvLTKjun3CE78j8B38tU3pfMP\nZHeawsE+LjxbszZywQ48XnKz7kzIA52w+N9NPInFaMlZk9DU5JR7zAbWLi3NzROu\nVFfK+HVjXrg9yvHx38UCAwEAAaOBijCBhzA3BglghkgBhvhCAQ0EKhYoRE1Tc2R3\nYW4gR2VuZXJhdGVkIENlcnRpZmljYXRlIEF1dGhvcml0eTAdBgNVHQ4EFgQUq77W\nkf2+33QVU2XGlYljpBCZZcIwHwYDVR0jBBgwFoAUq77Wkf2+33QVU2XGlYljpBCZ\nZcIwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAeUYo7BSqqEdY39aJ\nA64ObhNOZWI1i6L+xkSvMv0n5Y1/tFXOZN/8UWnNs/3PRhVdBGCNL6ToHgDx0b3/\nb6efERc87LVJ64boOVmfgI0SvkPEj/d6My4zOmFUD+EkLMLlLcqawWud9hizH9fR\ncnhdnOwsZMS7+IRjhiPXNiUTao1znYdYKxVziLPK5ImPE9RWZGerfXveKwTwq8Z/\nyhOUj41QV5WLIZ8xezt3PVYRuI3x6gvr383cO8HGWsoGhwSYY0Af4ZIhL5PkmbCf\ngKpY2ggl+wapth+bbpJ4C0fU8Ht1F/M1z9HUMgrQAm+WfYomrbSvVAbE1xeQiHjU\nrAjzXA==\n-----END CERTIFICATE-----", description="When name_method is import"),
                'certificate_key': Schema(type=TYPE_STRING, example="-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCvRd5q47gBq+CR\ncIphwhPc1wOTEiiyMaXJQ4ClKSLvyWBBlfeY4W1Nc0T8Cx5tj8VqtN0u5xk/SHBb\nonJX0TVA7tP9Diokna9uQgKvNTNb2CvS8EVQCRwxRMS/03h90dSZTGS8jxRk32Bg\nmV0nOe+pLunPg7kgpeoYEgFGIdTiUO6C1n5i+4vuy3rKLCk8lejGbnbTRWLgkdid\nE8WOUP7/DEGlD08WywhGArbwfwl/DLy0yo7p9whO/I/Ad/LVN6XzD2R3msLBPi48\nW7M2csEOPF5ys+5MyAOdsPjfTTyJxWjJWZPQ1OSUe8wG1i4tzc0TrlRXyvh1Y164\nPcrx8d/FAgMBAAECggEAJpFUSOcE9XExwC8odCx1nHG/upwTUmq0VV5CL5Wmt2bz\nhFsQmZZ5K8LCmkeEEY3CXiGgThLSLmetOay8RnClrD0hbpywT1BXawahepZVT894\njTkLt3nZt0mvlZpd+Cm1A2qY/Bjr3up8VaVJpzkLcIn/LweINBPuOA+2Mg19v7K8\nH1NZO/k8tTIID8JBsV/2nlWwPUuKJ5n6S0/KfuOV2kL9PO8zRFj1dARvAAY5Fj0u\ny7Yw7h1JPMYm+sffbeHIqS4OJUsK4Cx/v8mYJgSc/Q/GfloA3E4colWPDlXXCUga\nmFeYc/8Q3q3IjIIgp88GpxG8bw7KdyclQ7JzLW6XvQKBgQDVbZyIj6/VdPKCpUc3\nOY+YRPH1lDC584o/mwJxZHh/1ps+C7wGGNfkRxk9CZ4JO3vP8OwnkRiVBv8uUPQg\nKw+Y02wHiGPpKg3c/2yaIWbvHGPwReNJFccr50FOvbQnYjzcrWWeL70+2NA/qbzm\n6DVXeLUgCSFh0V/1VCBsKOYNDwKBgQDSO+rLbZrEgpF+4nqV9QG8DyiifvlCvlcA\n9T/TCrmmBQLxh2NdYRKDARj2URWiJyiGf5PVmUTazyVPGV4dOhpNOe8Ilsnr3wYj\n5QVA44pWc1mDI0X/1TDc0Thp7K5zBjXqGPeeuSeb1QIaO0mB48VByTFGC4nf0KF3\nk99UYoPt6wKBgQC0FkhFxpBEmehjKpjb1Vr/zfUoFcHDtebKYr599Zvjqq7VfMtL\njbzlZsS6Bxptid6gCBcMD9dhMEUzzKUhW5ROjN8TwBcl0BFgj7oQl+ymCBufyyjM\nK28i8X/etB2GOdNHFZywDHIvzHxzq4K0h+0ygKy8elfLlQLWHAU7nor3KwKBgQC8\nx6Lpsu0T4m8F8hbDyzMYjMAfUkc/gK2dpZv/RRU5mCxxd/Jo6n719ilVHbCAYAtK\n4wp79lpW5UWKRqw1MHRnvkr/em+tByJ7Xu6duvUA9il90VHNDcIHtzOiIi7wCLan\nFG5eL8L6coalyXETWtVJYoGFdV0EBlLHjpgvLRtsqwKBgD0TpsksfShhJ62mlBeJ\nN8gHJJX7NRs3yHdWuZgRUfgCn7pF7zoGwJW6ymO2TUQJkDa78Vv1MhONk7LBeyZ1\nIGuQvos3kTrbHtgmpqqD0/RnF7DhGqY3kjsVQuLjc9EAq8qPSHvtFs1tnw/p/VsC\ng6T46uQDHG5mLBV1/uZiDetw\n-----END PRIVATE KEY-----", description="When name_method is import"),
                'serial': Schema(type=TYPE_STRING, example="5622", description="Optional, when name_method is import"),}),}))
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_cert_auth(request):
    """Creating a new Certificates Authority in system and adding it to the database"""
    try:
        data = request.data
        
        # Check payload validity
        if not check_payload(data):
            return JsonResponse({"error": ERROR_MESSAGES_INVALID_DATA}, status=400)

        # parse the incoming information
        data = request.data
        name = data.get('name', '')
        method = data.get('method', '')
        method_name = method.get("name_method", "")
        if method_name == 'create':
            
            # Creating CA
            lifetime = method.get('lifetime', '')
            valid_from = datetime.now()
            valid_until = valid_from + timedelta(days=lifetime)
            key_type = method.get('key_type', '')
            key_length = method.get('key_length', '')
            digest_algorithm = method.get('digest_algorithm', '')
            country_code = method.get('country_code', '')
            state = method.get('state', '')
            city = method.get('city', '')
            organization = method.get('organization', '')
            email = method.get('email', '')
            common_name = method.get('common_name', '')
            ca_data = {"name": name,
                       "method_name": method_name,
                       "valid_from": valid_from,
                       "valid_until": valid_until,
                       "key_type": key_type,
                       "key_length": key_length,
                       "digest_algorithm": digest_algorithm,
                       "lifetime": lifetime,
                       "country_code": country_code,
                       "state": state,
                       "city": city,
                       "organization": organization,
                       "email": email,
                       "common_name": common_name,
                       }
            serializer_ca = CertificateAuthoritySerializer(data=ca_data)
            if serializer_ca.is_valid():
                updated_fields_vars = {"KEY_SIZE": key_length,
                                       "ALGO": key_type,
                                       "CERT_EXPIRE": lifetime,
                                       "REQ_COUNTRY": country_code,
                                       "REQ_PROVINCE": state,
                                       "REQ_CITY": city,
                                       "REQ_ORG": organization,
                                       "REQ_EMAIL": email,
                                       "DIGEST": digest_algorithm,
                                       "DN": "\"org\"",
                                        }
                # Install the server in system
                serial = create_ca_in_system(ca_name=name, common_name=common_name, updated_fields_vars=updated_fields_vars)
                ca_data['serial'] = serial
                serializer_ca = CertificateAuthoritySerializer(data=ca_data)
                if serializer_ca.is_valid():
                    # Add the server to the database
                    serializer_ca.save()
                    threading.Thread(target=notify_certificate_change, args=("créé", name, "CA"), daemon=True).start()
                    return JsonResponse({"msg": f"{name} {(SUCCESS_MESSAGES_CREATING)}"}, status=201)
            
            return JsonResponse({"error": list(serializer_ca.errors.values())[0][0]}, status=400)
        
        else:
            # Importing an existing CA
            certificate_data = method.get("certificate_data", "")
            certificate_private_key = method.get("certificate_key", "")
            serial = method.get("serial", "")
            ca_data = {"name": name,
                       "method_name": method_name,
                       "serial": serial}
            serializer_ca = CertificateAuthoritySerializer(data=ca_data)
            if serializer_ca.is_valid():
                input_ca = {"certificate_data": certificate_data,
                            "certificate_private_key": certificate_private_key,
                            "serial": serial
                            }
                serial, start_date, end_date, lifetime, distingushed_name = import_ca_in_system(name, input_ca)
                ca_data["valid_from"] = start_date
                ca_data["valid_until"] = end_date
                ca_data["lifetime"] = lifetime
                for dn_item, dn_data in distingushed_name.items():
                    ca_data[dn_item] = dn_data
                serializer_ca = CertificateAuthoritySerializer(data=ca_data)
                if serializer_ca.is_valid():
                    
                    serializer_ca.save()
                    threading.Thread(target=notify_certificate_change, args=("créé", name, "CA import"), daemon=True).start()
                    return JsonResponse({"msg": f"{name} {(SUCCESS_MESSAGES_CREATING)}"}, status=201)
                
            return JsonResponse({"error": list(serializer_ca.errors.values())[0][0]}, status=400)

    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_CA}"}, status=400)
    except ValueError as error:
        return JsonResponse({"error": error.__str__()}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO DELETE CERTIFICATE AUTHORITY",)
@api_view(['Delete'])
@require_http_methods(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_cert_auth(_, id):
    """Deleting a Certificates Authority from system and then from database"""
    try:
        ca = CertificateAuthority.objects.get(id=id)
        
        # Test if there is a certificates authorid by this CA
        list_cert = Certificate.objects.filter(certificate_authority=ca)
        if len(list_cert) == 0:
            # delete from system
            delete_ca_in_system(ca.name)
            # delete from database
            deleted_name = ca.name
            ca.delete()
            threading.Thread(target=notify_certificate_change, args=("supprimé", deleted_name, "CA"), daemon=True).start()
            return JsonResponse({"msg": f"{deleted_name} {(SUCCESS_MESSAGES_DELETING)}"}, status=200)
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING_USED_ITEM} {CONSTANT_CA}, {CONSTANT_USED_ITEM} {CONSTANT_CERT}"}, status=400)
    
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_CA}"}, status=400)
    except ProtectedError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING_USED_ITEM} {CONSTANT_CA}, {CONSTANT_USED_ITEM} {CONSTANT_CERT}"}, status=400)
    except CertificateAuthority.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CA} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'POST', responses={200: 'Created', 400: 'Bad Request'}, 
    operation_summary="API TO DOWNLOAD CERTIFICATE AUTHORITY",
    manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
    request_body=Schema(type=TYPE_OBJECT, required=['type'],
    properties={"type": Schema(type=TYPE_STRING, enum=['certificate', 'private_key'])}))
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def export_cert_auth(request, id):
    """Exporting a Certificate Authority"""
    try:
        ca = CertificateAuthority.objects.get(id=id)
        data = request.data
        download_type = data.get('type', '')
        if download_type == 'certificate':
            ca_value = export_ca_in_system(PATH_CA_CRT.format(ca.name))
        else:
            ca_value = export_ca_in_system(PATH_CA_KEY.format(ca.name))
        return JsonResponse({"cert": ca_value}, status=201)

    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_EXPORTING} {CONSTANT_CA}"}, status=400)
    except CertificateAuthority.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CA} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO DOWNLOAD REVOKACTION LIST OF A CERTIFICATE AUTHORITY",)
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def export_cert_auth_list_rev(_, id):
    """Exporting a Certificate Authority"""
    try:
        ca = CertificateAuthority.objects.get(id=id)
        list_revocation = export_ca_list_rev_in_system(ca.name)
        return JsonResponse({"list_revocation": list_revocation}, status=201)

    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_EXPORTING} {CONSTANT_REVOCATION_LIST}"}, status=400)
    except CertificateAuthority.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CA} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


##################################################
################## Certificates ##################
##################################################

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL CERTIFICATES",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_certificates(request):
    """Getting all Certificates from database"""
    if (request.method == 'GET'):
        list_cert = get_list_all_certificates()
        return JsonResponse(list_cert, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO GET A CERTIFICATE",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_certificate(request, id):
    """Getting a Certificate by id from database"""
    if (request.method == 'GET'):
        cert = get_one_certificate(id)
        if cert:
            return JsonResponse(cert, safe=False)
        return JsonResponse({"error": f"{CONSTANT_CERT} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'POST', responses={200: 'Created', 400: 'Bad Request'}, 
    operation_summary="API TO GET LIST OF ALL CERTIFICATES",
    request_body=Schema(
        type=TYPE_OBJECT, required=['name', 'activation', 'method'],
        properties={
            'name': Schema(type=TYPE_STRING, example="cert_server"),
            'activation': Schema(type=TYPE_BOOLEAN, default=True),
            'method': Schema(type=TYPE_OBJECT, required=['method_name'],
            properties={
                'method_name': Schema(type=TYPE_STRING, enum=["create", "import"]),
                'certificate_type': Schema(type=TYPE_STRING, enum=["server", "client"]),
                'ca': Schema(type=TYPE_INTEGER, example=1, description="ID of a certificate authority"),
                'key_type': Schema(type=TYPE_STRING, example="rsa"),
                'key_length': Schema(type=TYPE_INTEGER, example=2048),
                'digest_algorithm': Schema(type=TYPE_STRING, example="sha256", pattern=r'\bsha\d+', description="start with sha like sha123"),
                'lifetime': Schema(type=TYPE_INTEGER, example=325),
                'country_code': Schema(type=TYPE_STRING, example="\"TN\""),
                'state': Schema(type=TYPE_STRING, example="\"Openvpn\""),
                'city': Schema(type=TYPE_STRING, example="\"Bizerte\""),
                'organization': Schema(type=TYPE_STRING, example="\"Numeryx\""),
                'email': Schema(type=TYPE_STRING, example="\"root@numeryx.fr\""),
                'common_name': Schema(type=TYPE_STRING, example="create-ca"),
                'certificate_data': Schema(type=TYPE_STRING, example="-----BEGIN CERTIFICATE-----\nMIIDwDCCAqigAwIBAgIBADANBgkqhkiG9w0BAQsFADBdMQswCQYDVQQGEwJBRDEL\nMAkGA1UECAwCYWExCzAJBgNVBAcMAmFhMQswCQYDVQQKDAJhYTERMA8GCSqGSIb3\nDQEJARYCYWExFDASBgNVBAMMC2ludGVybmFsLWNhMB4XDTIzMDkyOTE1NTQ1OVoX\nDTI2MDEwMTE1NTQ1OVowXTELMAkGA1UEBhMCQUQxCzAJBgNVBAgMAmFhMQswCQYD\nVQQHDAJhYTELMAkGA1UECgwCYWExETAPBgkqhkiG9w0BCQEWAmFhMRQwEgYDVQQD\nDAtpbnRlcm5hbC1jYTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAK9F\n3mrjuAGr4JFwimHCE9zXA5MSKLIxpclDgKUpIu/JYEGV95jhbU1zRPwLHm2PxWq0\n3S7nGT9IcFuiclfRNUDu0/0OKiSdr25CAq81M1vYK9LwRVAJHDFExL/TeH3R1JlM\nZLyPFGTfYGCZXSc576ku6c+DuSCl6hgSAUYh1OJQ7oLWfmL7i+7LesosKTyV6MZu\ndtNFYuCR2J0TxY5Q/v8MQaUPTxbLCEYCtvB/CX8MvLTKjun3CE78j8B38tU3pfMP\nZHeawsE+LjxbszZywQ48XnKz7kzIA52w+N9NPInFaMlZk9DU5JR7zAbWLi3NzROu\nVFfK+HVjXrg9yvHx38UCAwEAAaOBijCBhzA3BglghkgBhvhCAQ0EKhYoRE1Tc2R3\nYW4gR2VuZXJhdGVkIENlcnRpZmljYXRlIEF1dGhvcml0eTAdBgNVHQ4EFgQUq77W\nkf2+33QVU2XGlYljpBCZZcIwHwYDVR0jBBgwFoAUq77Wkf2+33QVU2XGlYljpBCZ\nZcIwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAeUYo7BSqqEdY39aJ\nA64ObhNOZWI1i6L+xkSvMv0n5Y1/tFXOZN/8UWnNs/3PRhVdBGCNL6ToHgDx0b3/\nb6efERc87LVJ64boOVmfgI0SvkPEj/d6My4zOmFUD+EkLMLlLcqawWud9hizH9fR\ncnhdnOwsZMS7+IRjhiPXNiUTao1znYdYKxVziLPK5ImPE9RWZGerfXveKwTwq8Z/\nyhOUj41QV5WLIZ8xezt3PVYRuI3x6gvr383cO8HGWsoGhwSYY0Af4ZIhL5PkmbCf\ngKpY2ggl+wapth+bbpJ4C0fU8Ht1F/M1z9HUMgrQAm+WfYomrbSvVAbE1xeQiHjU\nrAjzXA==\n-----END CERTIFICATE-----", description="When name_method is import"),
                'certificate_key': Schema(type=TYPE_STRING, example="-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCvRd5q47gBq+CR\ncIphwhPc1wOTEiiyMaXJQ4ClKSLvyWBBlfeY4W1Nc0T8Cx5tj8VqtN0u5xk/SHBb\nonJX0TVA7tP9Diokna9uQgKvNTNb2CvS8EVQCRwxRMS/03h90dSZTGS8jxRk32Bg\nmV0nOe+pLunPg7kgpeoYEgFGIdTiUO6C1n5i+4vuy3rKLCk8lejGbnbTRWLgkdid\nE8WOUP7/DEGlD08WywhGArbwfwl/DLy0yo7p9whO/I/Ad/LVN6XzD2R3msLBPi48\nW7M2csEOPF5ys+5MyAOdsPjfTTyJxWjJWZPQ1OSUe8wG1i4tzc0TrlRXyvh1Y164\nPcrx8d/FAgMBAAECggEAJpFUSOcE9XExwC8odCx1nHG/upwTUmq0VV5CL5Wmt2bz\nhFsQmZZ5K8LCmkeEEY3CXiGgThLSLmetOay8RnClrD0hbpywT1BXawahepZVT894\njTkLt3nZt0mvlZpd+Cm1A2qY/Bjr3up8VaVJpzkLcIn/LweINBPuOA+2Mg19v7K8\nH1NZO/k8tTIID8JBsV/2nlWwPUuKJ5n6S0/KfuOV2kL9PO8zRFj1dARvAAY5Fj0u\ny7Yw7h1JPMYm+sffbeHIqS4OJUsK4Cx/v8mYJgSc/Q/GfloA3E4colWPDlXXCUga\nmFeYc/8Q3q3IjIIgp88GpxG8bw7KdyclQ7JzLW6XvQKBgQDVbZyIj6/VdPKCpUc3\nOY+YRPH1lDC584o/mwJxZHh/1ps+C7wGGNfkRxk9CZ4JO3vP8OwnkRiVBv8uUPQg\nKw+Y02wHiGPpKg3c/2yaIWbvHGPwReNJFccr50FOvbQnYjzcrWWeL70+2NA/qbzm\n6DVXeLUgCSFh0V/1VCBsKOYNDwKBgQDSO+rLbZrEgpF+4nqV9QG8DyiifvlCvlcA\n9T/TCrmmBQLxh2NdYRKDARj2URWiJyiGf5PVmUTazyVPGV4dOhpNOe8Ilsnr3wYj\n5QVA44pWc1mDI0X/1TDc0Thp7K5zBjXqGPeeuSeb1QIaO0mB48VByTFGC4nf0KF3\nk99UYoPt6wKBgQC0FkhFxpBEmehjKpjb1Vr/zfUoFcHDtebKYr599Zvjqq7VfMtL\njbzlZsS6Bxptid6gCBcMD9dhMEUzzKUhW5ROjN8TwBcl0BFgj7oQl+ymCBufyyjM\nK28i8X/etB2GOdNHFZywDHIvzHxzq4K0h+0ygKy8elfLlQLWHAU7nor3KwKBgQC8\nx6Lpsu0T4m8F8hbDyzMYjMAfUkc/gK2dpZv/RRU5mCxxd/Jo6n719ilVHbCAYAtK\n4wp79lpW5UWKRqw1MHRnvkr/em+tByJ7Xu6duvUA9il90VHNDcIHtzOiIi7wCLan\nFG5eL8L6coalyXETWtVJYoGFdV0EBlLHjpgvLRtsqwKBgD0TpsksfShhJ62mlBeJ\nN8gHJJX7NRs3yHdWuZgRUfgCn7pF7zoGwJW6ymO2TUQJkDa78Vv1MhONk7LBeyZ1\nIGuQvos3kTrbHtgmpqqD0/RnF7DhGqY3kjsVQuLjc9EAq8qPSHvtFs1tnw/p/VsC\ng6T46uQDHG5mLBV1/uZiDetw\n-----END PRIVATE KEY-----", description="When name_method is import"),
                'serial': Schema(type=TYPE_STRING, example="5622", description="Optional, when name_method is import"),}),}))
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_certificate(request):
    """Creating a new Certificates in system and adding it to the database"""
    try:
        # parse the incoming information
        data = request.data
        
        # Check payload validity
        if not check_payload(data):
            return JsonResponse({"error": ERROR_MESSAGES_INVALID_DATA}, status=400)
        
        name = data.get('name', '')
        method = data.get('method', '')
        method_name = method.get("method_name", "")
        activation = data.get('activation', '')
        if method_name == 'create':
            certificate_type = method.get('certificate_type', '')
            lifetime = method.get('lifetime', '')
            valid_from = datetime.now()
            valid_until = valid_from + timedelta(days=lifetime)
            key_type = method.get('key_type', '')
            key_length = method.get('key_length', '')
            digest_algorithm = method.get('digest_algorithm', '')
            private_key_location = method.get('private_key_location', '')
            country_code = method.get('country_code', '')
            state = method.get('state', '')
            city = method.get('city', '')
            organization = method.get('organization', '')
            email = method.get('email', '')
            common_name = method.get('common_name', '')
            ca_id = method.get('ca', '')
            ca = CertificateAuthority.objects.get(pk=ca_id)
            cert_data = {"certificate_authority": ca_id,
                         "name": name,
                         "certificate_type": certificate_type,
                         "activation": activation,
                         "valid_from": valid_from,
                         "valid_until": valid_until,
                         "key_type": key_type,
                         "key_length": key_length,
                         "digest_algorithm": digest_algorithm,
                         "lifetime": lifetime,
                         "private_key_location": private_key_location,
                         "country_code": country_code,
                         "state": state,
                         "city": city,
                         "organization": organization,
                         "email": email,
                         "common_name": common_name,
                         }
            serializer_cert = CertificateSerializer(data=cert_data)
            if serializer_cert.is_valid():
                date_now = datetime.now()
                
                # Verification of certificate authority validation
                if ca.valid_from.replace(tzinfo=None) <= date_now < ca.valid_until.replace(tzinfo=None):
                    # create certificate in system
                    updated_fields_vars = {"KEY_SIZE": key_length,
                                            "ALGO": key_type,
                                            "CERT_EXPIRE": lifetime,
                                            "REQ_COUNTRY": country_code,
                                            "REQ_PROVINCE": state,
                                            "REQ_CITY": city,
                                            "REQ_ORG": organization,
                                            "REQ_EMAIL": email,
                                            "DIGEST": digest_algorithm,
                                            "DN": "\"org\"",
                                            }
                    serial = create_certificate_in_system(cert_name=name, common_name=common_name, ca_name=ca.name, 
                                                          cert_type=certificate_type, updated_fields_vars=updated_fields_vars)
                    cert_data["serial"] = serial

                    # Add the certificate to the database
                    serializer_cert = CertificateSerializer(data=cert_data)

                    if serializer_cert.is_valid():
                        serializer_cert.save()
                        threading.Thread(target=notify_certificate_change, args=("créé", name, "Certificat"), daemon=True).start()
                        return JsonResponse({"msg": f"{name} {(SUCCESS_MESSAGES_CREATING)}"}, status=201)
                else:
                    return JsonResponse({"error": "Authority valide date is expired"}, status=400)
            
            return JsonResponse({"error": list(serializer_cert.errors.values())[0][0]}, status=400)
        elif method_name == 'import':
            certificate_data = method.get("certificate_data", "")
            certificate_key = method.get("certificate_key", "")
            serial = method.get("serial", "")
            certificate_type = 'server'
            cert_data = {"name": name,
                         "activation": activation,
                         "serial": serial
                         }
            serializer_cert = CertificateSerializer(data=cert_data)
            if serializer_cert.is_valid():
                input_cert = {"certificate_data": certificate_data,
                              "certificate_private_key": certificate_key,
                              "serial": serial
                              }
                serial, start_date, end_date, lifetime, distingushed_name, certificate_type = import_certificate_in_system(name, input_cert)

                cert_data["valid_from"] = start_date
                cert_data["valid_until"] = end_date
                cert_data["lifetime"] = lifetime
                cert_data["certificate_type"] = certificate_type
                for dn_item, dn_data in distingushed_name.items():
                    cert_data[dn_item] = dn_data
                serializer_cert = CertificateSerializer(data=cert_data)
                if serializer_cert.is_valid():
                    serializer_cert.save()
                    threading.Thread(target=notify_certificate_change, args=("créé", name, "Certificat import"), daemon=True).start()
                    return JsonResponse({"msg": f"{name} {(SUCCESS_MESSAGES_CREATING)}"}, status=201)
                
            return JsonResponse({"error": list(serializer_cert.errors.values())[0][0]}, status=400)

    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_CERT}"}, status=400)
    except CertificateAuthority.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CA} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'DELETE', request_body=CertificateSerializer, 
    manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO DELETE A CERTIFICATE AUTHORITY",)
@api_view(['Delete'])
@require_http_methods(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_certificate(_, id):
    """Deleting a Certificates from system and then from database"""
    try:
        cert = Certificate.objects.get(id=id)

        # Test if this certificate is used in OpenVPN, IPsec or WAF
        list_server_vpn = len(ServerOpenvpn.objects.filter(cert_name=cert))
        list_client_vpn = len(ClientOpenvpn.objects.filter(cert_name=cert))
        list_server_ipsec = len(ServerIPsec.objects.filter(cert=cert.name))
        list_waf = len(ApplicationWaf.objects.filter(certificate_name=cert.name))

        if (list_server_vpn == 0 and list_client_vpn == 0 
            and list_server_ipsec == 0 and list_waf == 0): # Not used certififcate
            # delete from system
            delete_certificate_in_system(cert.name, cert.certificate_type)
            # delete from database
            deleted_cert_name = cert.name
            cert.delete()
            threading.Thread(target=notify_certificate_change, args=("supprimé", deleted_cert_name, "Certificat"), daemon=True).start()
            return JsonResponse({"msg": f"{deleted_cert_name} {(SUCCESS_MESSAGES_DELETING)}"}, status=201)
        elif list_server_vpn > 0:
            return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING_USED_ITEM} {CONSTANT_CERT}, {CONSTANT_USED_ITEM} {CONSTANT_OPENVPN_SERVER}"}, status=400)
        elif list_client_vpn > 0:
            return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING_USED_ITEM} {CONSTANT_CERT}, {CONSTANT_USED_ITEM} {CONSTANT_OPENVPN_CLIENT}"}, status=400)
        elif list_server_ipsec > 0:
            return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING_USED_ITEM} {CONSTANT_CERT}, {CONSTANT_USED_ITEM} {CONSTANT_IPSEC}"}, status=400)
        elif list_waf > 0:
            return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING_USED_ITEM} {CONSTANT_CERT}, {CONSTANT_USED_ITEM} {CONSTANT_WAF}"}, status=400)
    
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_CERT}"}, status=400)
    except Certificate.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CERT} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'PUT', responses={200: 'Created', 400: 'Bad Request'}, 
    operation_summary="API TO REVOKE A CERTIFICATE",
    manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
    request_body=Schema(type=TYPE_OBJECT, required=['reason'],
    properties={"reason": Schema(type=TYPE_STRING, enum=[
        "No Status", "Unspecified", "key compromise", "CA compromise", "affiliation changed ", 
        "Supersed", "Cessation of Operation", "Certificate Hold ", "End of Validity Period ", 
        "Technical Issues"])}))
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def revoke_certificate(request, id):
    try:
        data = request.data
        cert = Certificate.objects.get(id=id)
        cert.reason_revocation = data.get("reason", "")
        cert.activation = False
        ca = cert.certificate_authority

        if ca:
            # Importing all the CA previous revoked certificates and add the new certificate
            list_revoked = Certificate.objects.filter(Q(certificate_authority=ca, activation=False) | Q(id=id))
            
            cert_serializer = CertificateSerializer(cert, data=data)
            if cert_serializer.is_valid():
                # Revoking all the certificates in system and generate a crl file
                revoke_certificates_in_system(ca_name=ca.name, cert=cert, list_revoked_cert=list_revoked)
                cert_serializer.save()
                threading.Thread(target=notify_certificate_change, args=("révoqué", cert.name, "Certificat"), daemon=True).start()
                return JsonResponse({"msg": f"Certificate {cert.name} is revoked and added to the crl file of the ca {ca.name}"})
            
            return JsonResponse({"error": list(cert_serializer.errors.values())[0][0]}, status=400)
        
        else:
            return JsonResponse({"error": "You can't revoke this imported certificate"}, status=400)
    
    except Certificate.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CERT} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO UNREVOKE A CERTIFICATE",)
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def unrevoke_certificate(_, id):
    try:
        cert = Certificate.objects.get(id=id)
        ca = cert.certificate_authority

        # Importing all the CA previous revoked certificates and add the new certificate
        list_revoked = Certificate.objects.filter(~Q(id=cert.id), certificate_authority=ca, activation=False)
        
        # Revoking all the certificates in system and generate a crl file
        unrevoke_certificates_in_system(ca_name=ca.name, cert=cert, list_revoked_cert=list_revoked)
        cert.activation = True
        cert.save()
        return JsonResponse({"msg": f"Certificate {cert.name} is unrevoked and removed from the crl file of the ca {ca.name}"})
    except Certificate.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CERT} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'POST', responses={200: 'Created', 400: 'Bad Request'}, 
    operation_summary="API TO DOWNLOAD A CERTIFICATE",
    manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
    request_body=Schema(type=TYPE_OBJECT, required=['download_type'],
    properties={"download_type": Schema(type=TYPE_STRING, enum=["certificate", "private_key", "p12"]),
                "password": Schema(type=TYPE_STRING, example="password certificate", description="Required when download_type is p12")}))
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def export_cert(request, id):
    """Exporting a Certificate"""
    try:
        cert = Certificate.objects.get(id=id)
        data = request.data
        download_type = data.get('download_type', '')  # Certificate, private key or .p12
        if download_type == 'p12':
            password = data.get('password', '')
            cert_value = export_certificate_in_system(cert_name=cert.name, cert_type=cert.certificate_type, 
                                                        download_type=download_type, password=password)
        else:
            cert_value = export_certificate_in_system(cert_name=cert.name, cert_type=cert.certificate_type,
                                                        download_type=download_type)
        return JsonResponse({"cert": cert_value}, status=201)

    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_EXPORTING} {CONSTANT_CERT}"}, status=400)
    except Certificate.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CERT} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
