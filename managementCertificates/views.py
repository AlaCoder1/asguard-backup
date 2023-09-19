from datetime import datetime, timedelta
from django.http import JsonResponse
import json
from rest_framework.authentication import SessionAuthentication
from django.core import serializers

from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from managementCertificates.certificate import create_ca_in_system, create_certificate_in_system, delete_ca_in_system, delete_certificate_in_system, import_ca_in_system, import_certificate_in_system, read_certificate_value

from managementCertificates.models import Certificate, CertificateAuthority
from managementCertificates.serializers import CertificateAuthoritySerializer, CertificateSerializer
from openvpn.functions import CommandExecutionError

# Create your views here.

############# Certificates Authority #############
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def getAllCertAuth(request):
    """Getting all Certificates Authority from database"""
    list_ca = []
    if (request.method == 'GET'):
        ca = CertificateAuthority.objects.all()
        caDict = serializers.serialize("json",ca)
        res = json.loads(caDict)
        for i in range(len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_ca.append(res[i]['fields'])
        return JsonResponse(list_ca, safe=False)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
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

@api_view(['POST'])
# @authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
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
                                        #    "REQ_CN": common_name
                                           }
                    # Install the server in system
                    create_ca_in_system(ca_name=data["name"], updated_fields_vars=updated_fields_vars)
                    ca_data["certificate_path"] = f'/etc/certificates_{name}/ca.crt\n/etc/certificates_{name}/ca.key'
                    serializer_ca = CertificateAuthoritySerializer(data=ca_data)
                    if serializer_ca.is_valid():

                        # Add the server to the database
                        serializer_ca.save()
                        return JsonResponse({"msg": "CA Configuration is done"}, status=201)
                    else:
                        print(serializer_ca.errors)
                else:
                    print(serializer_ca.errors)
                return JsonResponse({"msg": "Error in CA configuration"}, status=401)
            
            elif method.get("name_method", "") == 'import':

                # Importing an existing CA
                certificate_data = method.get("certificate_data", "")
                certificate_private_key = method.get("certificate_key", "")
                # serial = method.get("serial", "")
                input_ca = {"certificate_data": certificate_data,
                            "certificate_private_key": certificate_private_key,
                            }
                import_ca_in_system(name, input_ca)
                ca_data = {"name": name,
                           "certificate_path": f'/etc/certificates_{name}/ca.crt\n/etc/certificates_{name}/ca.key'}
                serializer_ca = CertificateAuthoritySerializer(data=ca_data)
                if serializer_ca.is_valid():
                    serializer_ca.save()
                    return JsonResponse({"msg": "CA Configuration is done"}, status=201)

        except CommandExecutionError:
            return JsonResponse({"msg": "Error in creating CA"}, status=401)


@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def deleteCertAuth(request, id):
    """Deleting a Certificates Authority from system and then from database"""
    if (request.method == 'DELETE'):
        ca = CertificateAuthority.objects.get(id=id)
        # delete from system
        delete_ca_in_system(ca.name)
        # delete from database
        ca.delete()
        return JsonResponse({"msg": f"delete {ca.name} succesfully"})


############# Certificates #############
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
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
#@permission_classes([IsAuthenticated])
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
# @authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def createCertificate(request):
    """Creating a new Certificates Authority in system and adding it to the database"""
    if request.method == 'POST':
        try:
            # parse the incoming information
            data = request.data
            name = data.get('name', '')
            method = data.get('method', '')
            print('method= ', method)
            certificate_type = data.get('certificate_type', 'True')
            activation = data.get('activation', '')
            if method.get("method_name", "") == 'create':
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
                                            #    "REQ_CN": common_name
                                               }
                        create_certificate_in_system(cert_name=name, ca_name=ca.name, type_cert=certificate_type, 
                                                     updated_fields_vars=updated_fields_vars)

                        # Add the certificate to the database
                        if certificate_type == 'server':
                            cert_data["certificate_path"] = f'''/etc/openvpn/certificates_{name}/server.crt\n/etc/openvpn/certificates_{name}/server.key\n/etc/openvpn/certificates_{name}/dh.pem'''
                        elif certificate_type == 'client':
                            cert_data["certificate_path"] = f'''/etc/openvpn/client/certificates_{name}/{name}.crt\n/etc/openvpn/client/certificates_{name}/{name}.key'''
                        serializer_cert = CertificateSerializer(data=cert_data)

                        if serializer_cert.is_valid():
                            serializer_cert.save()
                            return JsonResponse({"msg": "Certificate Configuration is done"}, status=201)
                else:
                    print('error in creating cert= ', serializer_cert.errors)
                    return JsonResponse({"msg": "Error in Certificate configuration"}, status=401)
            elif method.get("method_name", "") == 'import':
                certificate_data = method.get("certificate_data", "")
                certificate_key = method.get("certificate_key", "")
                input_cert = {"certificate_data": certificate_data,
                            "certificate_private_key": certificate_key,
                            }

                import_certificate_in_system(name, certificate_type, input_cert)
                cert_data = {"name": name,
                             "certificate_type": certificate_type,
                             "activation": activation
                             }
                if certificate_type == 'server':
                    cert_data["certificate_path"] = f'''/etc/openvpn/certificates_{name}/server.crt\n/etc/openvpn/certificates_{name}/server.key'''
                elif certificate_type == 'client':
                    cert_data["certificate_path"] = f'''/etc/openvpn/client/certificates_{name}/{name}.crt\n/etc/openvpn/client/certificates_{name}/{name}.key'''
                serializer_cert = CertificateSerializer(data=cert_data)
                if serializer_cert.is_valid():
                    serializer_cert.save()
                    return JsonResponse({"msg": "Certificate Configuration is done"}, status=201)
                else:
                    print('error in creating cert= ', serializer_cert.errors)
                    return JsonResponse({"msg": "Error in Certificate configuration"}, status=401)

        except CommandExecutionError:
            return JsonResponse({"msg": "Error in creating Certificate"}, status=401)


@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def deleteCertificate(request, id):
    """Deleting a Certificates from system and then from database"""
    if (request.method == 'DELETE'):
        cert = Certificate.objects.get(id=id)
        # delete from system
        delete_certificate_in_system(cert.name, cert.certificate_type)
        # delete from database
        cert.delete()
        return JsonResponse({"msg": f"delete {cert.name} succesfully"})
