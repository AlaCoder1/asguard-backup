from datetime import datetime, timedelta
from django.http import JsonResponse
from django.db.models import Q
from django.db.models.deletion import ProtectedError
import json
from rest_framework.authentication import SessionAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from backend.ipsec.models import ServerIPsec

from backend.managementCertificates.certificate import create_ca_in_system, create_certificate_in_system, delete_ca_in_system, delete_certificate_in_system, export_ca_in_system, export_ca_list_rev_in_system, export_certificate_in_system, import_ca_in_system, import_certificate_in_system, revoke_certificates_in_system, unrevoke_certificates_in_system
from backend.managementCertificates.constant_variables import PATH_CA_CRT, PATH_CA_KEY
from utils.constant_variables import ERROR_MESSAGES_DELETE_USED_CA, ERROR_MESSAGES_DELETE_USED_ITEM, ERROR_MESSAGES_EXPORTING, SUCCESS_MESSAGES_CREATING_ITEM, SUCCESS_MESSAGES_DELETE
from backend.managementCertificates.list_certificates import get_list_all_cert_auth, get_list_all_certificates, get_one_cert_auth, get_one_certificate
from backend.managementCertificates.models import Certificate, CertificateAuthority
from backend.managementCertificates.serializers import CertificateAuthoritySerializer, CertificateSerializer
from utils.constant_variables import ERROR_MESSAGES_CREATING, ERROR_MESSAGES_INEXISTANT
from utils.errors_utils import CommandExecutionError
from backend.openvpn.models import ClientOpenvpn, ServerOpenvpn

# Create your views here.

##################################################
############# Certificates Authority #############
##################################################

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL CERTIFICATES AUTHORITY",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getAllCertAuth(request):
    """Getting all Certificates Authority from database"""
    if (request.method == 'GET'):
        list_ca = get_list_all_cert_auth()
        return JsonResponse(list_ca, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET A CERTIFICATE AUTHORITY",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getCertAuth(request, id):
    """Getting a Certificates Authority by id from database"""
    if (request.method == 'GET'):
        cert = get_one_cert_auth(id)
        return JsonResponse(cert, safe=False)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO CREATE CERTIFICATE AUTHORITY",
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT, required=['name', 'method'],
                                                 properties={'name': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'method': openapi.Schema(
                                                                 type=openapi.TYPE_OBJECT, required=['name_method'],
                                                                 properties={'name_method': openapi.Schema(type=openapi.TYPE_STRING, enum=["create", "import"]),
                                                                             'key_type': openapi.Schema(type=openapi.TYPE_STRING),
                                                                             'key_length': openapi.Schema(type=openapi.TYPE_INTEGER),
                                                                             'digest_algorithm': openapi.Schema(type=openapi.TYPE_STRING, pattern=r'\bsha\d+', description="start with sha like sha123"),
                                                                             'lifetime': openapi.Schema(type=openapi.TYPE_INTEGER),
                                                                             'country_code': openapi.Schema(type=openapi.TYPE_STRING),
                                                                             'state': openapi.Schema(type=openapi.TYPE_STRING),
                                                                             'city': openapi.Schema(type=openapi.TYPE_STRING),
                                                                             'organization': openapi.Schema(type=openapi.TYPE_STRING),
                                                                             'email': openapi.Schema(type=openapi.TYPE_STRING),
                                                                             'common_name': openapi.Schema(type=openapi.TYPE_STRING),
                                                                             'certificate_data': openapi.Schema(type=openapi.TYPE_STRING, description="When name_method is import"),
                                                                             'certificate_key': openapi.Schema(type=openapi.TYPE_STRING, description="When name_method is import"),
                                                                             'serial': openapi.Schema(type=openapi.TYPE_STRING, description="Optional, when name_method is import"),
                                                                             }),
                                                                             }
                                                                             ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def createCertAuth(request):
    """Creating a new Certificates Authority in system and adding it to the database"""
    if request.method == 'POST':
        try:
            data = request.data

            # parse the incoming information
            data = request.data
            name = data.get('name', '')
            method = data.get('method', '')
            if method.get("name_method", "") == 'create':
                
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
                                        #    "DN": "\"org\"",
                                           }
                    # Install the server in system
                    serial = create_ca_in_system(ca_name=name, common_name=common_name, updated_fields_vars=updated_fields_vars)
                    ca_data['serial'] = serial
                    serializer_ca = CertificateAuthoritySerializer(data=ca_data)
                    if serializer_ca.is_valid():
                        # Add the server to the database
                        serializer_ca.save()
                        return JsonResponse({"msg": SUCCESS_MESSAGES_CREATING_ITEM.format('CA', name)}, status=201)
                    
                    else:
                        return JsonResponse({"error": list(serializer_ca.errors.values())[0][0]}, status=400)
                    
                else:
                    return JsonResponse({"error": list(serializer_ca.errors.values())[0][0]}, status=400)
            
            elif method.get("name_method", "") == 'import':

                # Importing an existing CA
                certificate_data = method.get("certificate_data", "")
                certificate_private_key = method.get("certificate_key", "")
                serial = method.get("serial", "")
                ca_data = {"name": name,
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
                        return JsonResponse({"msg": SUCCESS_MESSAGES_CREATING_ITEM.format('CA', name)}, status=201)
                    else:
                        return JsonResponse({"error": list(serializer_ca.errors.values())[0][0]}, status=400)
                else:
                    return JsonResponse({"error": list(serializer_ca.errors.values())[0][0]}, status=400)


        except CommandExecutionError:
            return JsonResponse({"error": ERROR_MESSAGES_CREATING.format('CA')}, status=400)
        except ValueError as error:
            return JsonResponse({"error": error.__str__()}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE CERTIFICATE AUTHORITY",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def deleteCertAuth(request, id):
    """Deleting a Certificates Authority from system and then from database"""
    try:
        if (request.method == 'DELETE'):
            ca = CertificateAuthority.objects.get(id=id)
            
            # Test if there is a certificates authorid by this CA
            list_cert = Certificate.objects.filter(certificate_authority=ca)
            if len(list_cert) == 0:
                # delete from system
                delete_ca_in_system(ca.name)
                # delete from database
                ca.delete()
                return JsonResponse({"msg": f"delete {ca.name} succesfully"})
            else:
                return JsonResponse({"error": ERROR_MESSAGES_DELETE_USED_CA}, status=400)
    except ProtectedError:
        return JsonResponse({"error": ERROR_MESSAGES_DELETE_USED_CA}, status=400)
    except CertificateAuthority.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('CA')}, status=400)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO DOWNLOAD CERTIFICATE AUTHORITY",
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT, required=['type'],
                                                 properties={"type": openapi.Schema(type=openapi.TYPE_STRING, enum=['certificate', 'private_key'])}))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def exportCertAuth(request, id):
    """Exporting a Certificate Authority"""
    if request.method == 'POST':
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
            return JsonResponse({"error": ERROR_MESSAGES_EXPORTING.format("CA")}, status=400)
        except CertificateAuthority.DoesNotExist:
            return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('CA')}, status=400)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DOWNLOAD REVOKACTION LIST OF A CERTIFICATE AUTHORITY",)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def exportCertAuthListRev(request, id):
    """Exporting a Certificate Authority"""
    if request.method == 'POST':
        try:
            ca = CertificateAuthority.objects.get(id=id)
            list_revocation = export_ca_list_rev_in_system(ca.name)
            return JsonResponse({"list_revocation": list_revocation}, status=201)

        except CommandExecutionError:
            return JsonResponse({"error": ERROR_MESSAGES_EXPORTING.format("revokation list")}, status=400)
        except CertificateAuthority.DoesNotExist:
            return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('CA')}, status=400)


##################################################
################## Certificates ##################
##################################################

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL CERTIFICATES",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getAllCertificates(request):
    """Getting all Certificates from database"""
    if (request.method == 'GET'):
        list_cert = get_list_all_certificates()
        return JsonResponse(list_cert, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET A CERTIFICATE",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getCertificate(request, id):
    """Getting a Certificate by id from database"""
    if (request.method == 'GET'):
        cert = get_one_certificate(id)
        return JsonResponse(cert, safe=False)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO GET LIST OF ALL CERTIFICATES",
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT, required=['name', 'activation', 'method'],
                                                 properties={'name': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'activation': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                                                             'method': openapi.Schema(
                                                                 type=openapi.TYPE_OBJECT, required=['name_method'],
                                                                 properties={'method_name': openapi.Schema(type=openapi.TYPE_STRING, enum=["create", "import"]),
                                                                             'certificate_type': openapi.Schema(type=openapi.TYPE_STRING, enum=["server", "client"]),
                                                                             'ca': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of a certificate authority"),
                                                                             'key_type': openapi.Schema(type=openapi.TYPE_STRING),
                                                                             'key_length': openapi.Schema(type=openapi.TYPE_INTEGER),
                                                                             'digest_algorithm': openapi.Schema(type=openapi.TYPE_STRING, pattern=r'\bsha\d+', description="start with sha like sha123"),
                                                                             'lifetime': openapi.Schema(type=openapi.TYPE_INTEGER),
                                                                             'private_key_location': openapi.Schema(type=openapi.TYPE_STRING, default="Save on this firewall"),
                                                                             'country_code': openapi.Schema(type=openapi.TYPE_STRING),
                                                                             'state': openapi.Schema(type=openapi.TYPE_STRING),
                                                                             'city': openapi.Schema(type=openapi.TYPE_STRING),
                                                                             'organization': openapi.Schema(type=openapi.TYPE_STRING),
                                                                             'email': openapi.Schema(type=openapi.TYPE_STRING),
                                                                             'common_name': openapi.Schema(type=openapi.TYPE_STRING),
                                                                             'certificate_data': openapi.Schema(type=openapi.TYPE_STRING, description="When name_method is import"),
                                                                             'certificate_key': openapi.Schema(type=openapi.TYPE_STRING, description="When name_method is import"),
                                                                             'serial': openapi.Schema(type=openapi.TYPE_STRING, description="Optional, when name_method is import"),
                                                                             }),
                                                                             }
                                                                             ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def createCertificate(request):
    """Creating a new Certificates in system and adding it to the database"""
    try:
        # parse the incoming information
        data = request.data
        name = data.get('name', '')
        method = data.get('method', '')
        activation = data.get('activation', '')
        if method.get("method_name", "") == 'create':
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
                                                            type_cert=certificate_type, updated_fields_vars=updated_fields_vars)
                    cert_data["serial"] = serial

                    # Add the certificate to the database
                    serializer_cert = CertificateSerializer(data=cert_data)

                    if serializer_cert.is_valid():
                        serializer_cert.save()
                        return JsonResponse({"msg": SUCCESS_MESSAGES_CREATING_ITEM.format('Certificate', name)}, status=201)
            else:
                return JsonResponse({"error": list(serializer_cert.errors.values())[0][0]}, status=400)
        elif method.get("method_name", "") == 'import':
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
                # if serial != cert_data["serial"]:
                #     return JsonResponse({"error": "Serial number input are not correct"}, status=400)

                cert_data["valid_from"] = start_date
                cert_data["valid_until"] = end_date
                cert_data["lifetime"] = lifetime
                cert_data["certificate_type"] = certificate_type
                for dn_item, dn_data in distingushed_name.items():
                    cert_data[dn_item] = dn_data
                serializer_cert = CertificateSerializer(data=cert_data)
                if serializer_cert.is_valid():
                    serializer_cert.save()
                    return JsonResponse({"msg": SUCCESS_MESSAGES_CREATING_ITEM.format('Certificate', name)}, status=201)
                else:
                    return JsonResponse({"error": list(serializer_cert.errors.values())[0][0]}, status=400)
            else:
                return JsonResponse({"error": list(serializer_cert.errors.values())[0][0]}, status=400)

    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_CREATING.format('Certificate')}, status=400)
    except CertificateAuthority.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format("CA")}, status=400)


@swagger_auto_schema('DELETE', request_body=CertificateSerializer, responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE A CERTIFICATE AUTHORITY",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def deleteCertificate(request, id):
    """Deleting a Certificates from system and then from database"""
    if (request.method == 'DELETE'):
        try:
            cert = Certificate.objects.get(id=id)

            # Test if this certificate is used in OpenVPN or IPsec
            list_server_vpn = ServerOpenvpn.objects.filter(cert_name=cert.name)
            list_client_vpn = ClientOpenvpn.objects.filter(cert_name=cert.name)
            list_server_ipsec = ServerIPsec.objects.filter(cert=cert.name)

            if len(list_server_vpn) == 0 and len(list_client_vpn) == 0 and len(list_server_ipsec) == 0: # Not used certififcate
                # delete from system
                delete_certificate_in_system(cert.name, cert.certificate_type)
                # delete from database
                cert.delete()
                return JsonResponse({"msg": SUCCESS_MESSAGES_DELETE.format(cert.name)}, status=201)
            
            elif len(list_server_vpn) > 0:
                return JsonResponse({"error": ERROR_MESSAGES_DELETE_USED_ITEM.format("certificate", "openvpn servers")}, status=400)
            elif len(list_client_vpn) > 0:
                return JsonResponse({"error": ERROR_MESSAGES_DELETE_USED_ITEM.format("certificate", "openvpn clients")}, status=400)
            elif len(list_server_ipsec) > 0:
                return JsonResponse({"error": ERROR_MESSAGES_DELETE_USED_ITEM.format("certificate", "IPsec configuration")}, status=400)
        except Certificate.DoesNotExist:
            return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('Certificate')}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO REVOKE A CERTIFICATE",
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT, required=['reason'],
                                                 properties={"reason": openapi.Schema(type=openapi.TYPE_STRING, enum=["No Status", "Unspecified", "key compromise", "CA compromise", "affiliation changed ", "Supersed", "Cessation of Operation", "Certificate Hold ", "End of Validity Period ", "Technical Issues"])}))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def revokeCertificate(request, id):
    if request.method == 'PUT':
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
                    return JsonResponse({"msg": f"Certificate {cert.name} is revoked and added to the crl file of the ca {ca.name}"})
                else:
                    return JsonResponse({"error": list(cert_serializer.errors.values())[0][0]}, status=400)
            else:
                return JsonResponse({"error": "You can't revoke this imported certificate"}, status=400)
        except Certificate.DoesNotExist:
            return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('Certificate')}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO UNREVOKE A CERTIFICATE",)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def unrevokeCertificate(request, id):
    if request.method == 'PUT':
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
            return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('Certificate')}, status=400)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO DOWNLOAD A CERTIFICATE",
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT, required=['download_type'],
                                                 properties={"download_type": openapi.Schema(type=openapi.TYPE_STRING, enum=["certificate", "private_key", "p12"]),
                                                             "password": openapi.Schema(type=openapi.TYPE_STRING, description="Required when download_type is p12")}))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def exportCert(request, id):
    """Creating a new Certificates Authority in system and adding it to the database"""
    if request.method == 'POST':
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
            return JsonResponse({"error": ERROR_MESSAGES_EXPORTING.format("CA")}, status=400)
        except Certificate.DoesNotExist:
            return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('Certificate')}, status=400)
