from datetime import datetime, timedelta
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q
from django.db.models.deletion import ProtectedError
import json
from rest_framework.authentication import SessionAuthentication
from django.core import serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from backend.managementCertificates.certificate import create_ca_in_system, create_certificate_in_system, delete_ca_in_system, delete_certificate_in_system, export_ca_in_system, export_ca_list_rev_in_system, export_certificate_in_system, import_ca_in_system, import_certificate_in_system, revoke_certificates_in_system, unrevoke_certificates_in_system
from backend.managementCertificates.functions import extract_certificate_distingushed_name
from backend.managementCertificates.models import Certificate, CertificateAuthority
from backend.managementCertificates.serializers import CertificateAuthoritySerializer, CertificateSerializer
from backend.openvpn.manage_errors import CommandExecutionError

# Create your views here.

##################################################
############# Certificates Authority #############
##################################################

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getAllCertAuth(request):
    """Getting all Certificates Authority from database"""
    list_ca = []
    if (request.method == 'GET'):
        ca = CertificateAuthority.objects.all()
        caDict = serializers.serialize("json",ca)
        res = json.loads(caDict)
        for i in range(len(res)):
            list_certs_auth_by_ca = len(Certificate.objects.filter(certificate_authority=ca[i].pk))
            list_revoke_ca = Certificate.objects.filter(certificate_authority=ca[i].pk, activation=False)
            list_revokation = []
            for revoke in list_revoke_ca:
                list_revokation.append({"id": revoke.id,
                                        "name": revoke.name,
                                        "reason": revoke.reason_revocation})
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            res[i]['fields']['certificates'] = list_certs_auth_by_ca
            res[i]['fields']['list_revokation'] = list_revokation
            list_ca.append(res[i]['fields'])
        return JsonResponse(list_ca, safe=False)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getCertAuth(request, id):
    """Getting a Certificates Authority by id from database"""
    if (request.method == 'GET'):
        ca = CertificateAuthority.objects.filter(pk=id)
        caDict = serializers.serialize("json", ca)
        res = json.loads(caDict)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields']['id'] = id
        return JsonResponse(res[0]['fields'], safe=False)


# @swagger_auto_schema('POST', request_body=CertificateAuthoritySerializer, responses={200: 'Created', 400: 'Bad Request'}, 
#                      manual_parameters=[openapi.Parameter('method', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Description'),
#         ])
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
                    ca_data["certificate_path"] = f'/etc/certificates_{name}/ca.crt\n/etc/certificates_{name}/ca.key'
                    serializer_ca = CertificateAuthoritySerializer(data=ca_data)
                    if serializer_ca.is_valid():
                        # Add the server to the database
                        serializer_ca.save()
                        return JsonResponse({"msg": f"CA {name} is created"}, status=201)
                    
                    else:
                        print(serializer_ca.errors)
                        return JsonResponse({"msg": "Error in CA configuration"}, status=401)
                    
                else:
                    print(serializer_ca.errors)
                    return JsonResponse({"msg": "Error in CA configuration"}, status=401)
            
            elif method.get("name_method", "") == 'import':

                # Importing an existing CA
                certificate_data = method.get("certificate_data", "")
                certificate_private_key = method.get("certificate_key", "")
                serial = method.get("serial", "")
                ca_data = {"name": name,
                           "certificate_path": f'/etc/certificates_{name}/ca.crt\n/etc/certificates_{name}/ca.key',
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
                        return JsonResponse({"msg": f"CA {name} is created"}, status=201)
                    else:
                        print(serializer_ca.errors)
                        return JsonResponse({"msg": "Error in CA configuration"}, status=401)
                else:
                    print(serializer_ca.errors)
                    return JsonResponse({"msg": "Error in CA configuration"}, status=401)


        except CommandExecutionError:
            return JsonResponse({"msg": "Error in creating CA"}, status=401)
        except ValueError as error:
            return JsonResponse({"msg": error.__str__()})


@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def deleteCertAuth(request, id):
    """Deleting a Certificates Authority from system and then from database"""
    try:
        if (request.method == 'DELETE'):
            ca = CertificateAuthority.objects.get(id=id)
            # delete from system
            delete_ca_in_system(ca.name)
            # delete from database
            ca.delete()
            return JsonResponse({"msg": f"delete {ca.name} succesfully"})
    except ProtectedError:
        return JsonResponse({"msg": "You have to delete Certificates authoried by this CA"}, status=401)
    except CertificateAuthority.DoesNotExist:
        return JsonResponse({"msg": "This CA does not exist"}, status=401)


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
                ca_value = export_ca_in_system(f'/etc/certificates_{ca.name}/ca.crt')
            else:
                ca_value = export_ca_in_system(f'/etc/certificates_{ca.name}/ca.key')
            return JsonResponse({"cert": ca_value}, status=201)

        except CommandExecutionError:
            return JsonResponse({"msg": "Error in exporting CA"}, status=401)
        except CertificateAuthority.DoesNotExist:
            return JsonResponse({"msg": "This CA does not exist"}, status=401)


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
            return JsonResponse({"msg": "Error in exporting list of revocation"}, status=401)
        except CertificateAuthority.DoesNotExist:
            return JsonResponse({"msg": "This CA does not exist"}, status=401)


##################################################
################## Certificates ##################
##################################################
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getAllCertificates(request):
    """Getting all Certificates from database"""
    list_cert = []
    if (request.method == 'GET'):
        cert = Certificate.objects.all()
        certDict = serializers.serialize("json",cert)
        res = json.loads(certDict)
        for i in range(len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_cert.append(res[i]['fields'])
        return JsonResponse(list_cert, safe=False)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getCertificate(request, id):
    """Getting a Certificate by id from database"""
    if (request.method == 'GET'):
        cert = CertificateAuthority.objects.filter(pk=id)
        certDict = serializers.serialize("json", cert)
        res = json.loads(certDict)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields']['id'] = id
        return JsonResponse(res[0]['fields'], safe=False)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def createCertificate(request):
    """Creating a new Certificates in system and adding it to the database"""
    if request.method == 'POST':
        try:
            # parse the incoming information
            data = request.data
            name = data.get('name', '')
            method = data.get('method', '')
            activation = data.get('activation', '')
            if method.get("method_name", "") == 'create':
                certificate_type = method.get('certificate_type', 'True')
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
                        if certificate_type == 'server':
                            cert_data["certificate_path"] = f'''/etc/openvpn/certificates_{name}/server.crt\n/etc/openvpn/certificates_{name}/server.key\n/etc/openvpn/certificates_{name}/dh.pem'''
                        elif certificate_type == 'client':
                            cert_data["certificate_path"] = f'''/etc/openvpn/client/certificates_{name}/{name}.crt\n/etc/openvpn/client/certificates_{name}/{name}.key'''
                        serializer_cert = CertificateSerializer(data=cert_data)

                        if serializer_cert.is_valid():
                            serializer_cert.save()
                            return JsonResponse({"msg": f"Certificate {name} is created"}, status=201)
                else:
                    return JsonResponse({"msg": f"Error in Certificate configuration\n{serializer_cert.errors}"}, status=401)
            elif method.get("method_name", "") == 'import':
                certificate_data = method.get("certificate_data", "")
                certificate_key = method.get("certificate_key", "")
                serial = method.get("serial", "")
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
                    certificate_type = 'server'
                    serial, start_date, end_date, lifetime, distingushed_name = import_certificate_in_system(name, certificate_type, input_cert)
                    
                    if certificate_type == 'server':
                        cert_data["certificate_path"] = f'''/etc/openvpn/certificates_{name}/server.crt\n/etc/openvpn/certificates_{name}/server.key'''
                    elif certificate_type == 'client':
                        cert_data["certificate_path"] = f'''/etc/openvpn/client/certificates_{name}/{name}.crt\n/etc/openvpn/client/certificates_{name}/{name}.key'''
                    cert_data["valid_from"] = start_date
                    cert_data["valid_until"] = end_date
                    cert_data["lifetime"] = lifetime
                    for dn_item, dn_data in distingushed_name.items():
                        cert_data[dn_item] = dn_data
                    serializer_cert = CertificateSerializer(data=cert_data)
                    if serializer_cert.is_valid():
                        serializer_cert.save()
                        return JsonResponse({"msg": "Certificate Configuration is done"}, status=201)
                    else:
                        print('error in creating cert= ', serializer_cert.errors)
                        return JsonResponse({"msg": "Error in Certificate configuration"}, status=401)
                else:
                    print('error in creating cert= ', serializer_cert.errors)
                    return JsonResponse({"msg": "Error in Certificate configuration"}, status=401)

        except CommandExecutionError:
            return JsonResponse({"msg": "Error in creating Certificate"}, status=401)
        except CertificateAuthority.DoesNotExist:
            return JsonResponse({"msg": "CA does not ewxist"}, status=401)
        except ValueError as error:
            return JsonResponse({"msg": error}, status=401)


@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def deleteCertificate(request, id):
    """Deleting a Certificates from system and then from database"""
    if (request.method == 'DELETE'):
        try:
            cert = Certificate.objects.get(id=id)
            # delete from system
            delete_certificate_in_system(cert.name, cert.certificate_type)
            # delete from database
            cert.delete()
            return JsonResponse({"msg": f"delete {cert.name} succesfully"}, status=201)
        except Certificate.DoesNotExist:
            return JsonResponse({"msg": "This Certificate does not exist"}, status=401)


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

            # Importing all the CA previous revoked certificates and add the new certificate
            list_revoked = Certificate.objects.filter(Q(certificate_authority=ca, activation=False) | Q(id=id))
            
            cert_serializer = CertificateSerializer(cert, data=data)
            if cert_serializer.is_valid():
                # Revoking all the certificates in system and generate a crl file
                revoke_certificates_in_system(ca_name=ca.name, cert=cert, list_revoked_cert=list_revoked)
                cert_serializer.save()
                return JsonResponse({"msg": f"Certificate {cert.name} is revoked and added to the crl file of the ca {ca.name}"})
            else:
                print(cert_serializer.errors)
                return JsonResponse({"msg": "Error in Revocation certificate"}, status=401)
        except Certificate.DoesNotExist:
            return JsonResponse({"msg": "This Certificate does not exist"}, status=401)


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
            return JsonResponse({"msg": "This Certificate does not exist"}, status=401)


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
            return JsonResponse({"msg": "Error in exporting CA"}, status=401)
        except Certificate.DoesNotExist:
            return JsonResponse({"msg": "This Certificate does not exist"}, status=401)
