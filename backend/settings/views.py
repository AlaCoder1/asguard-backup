"""
Django Views for System and Network Configuration Management

This module provides a set of API endpoints to manage general system settings, 
time zones, gateways, network configurations, and system information. 

Features:
---------
- Update system settings (hostname, domain, timezone, DNS servers).
- Retrieve general system settings.
- Retrieve available time zones.
- Retrieve gateway information.
- Retrieve system and network details.
- Create system entries.

Endpoints:
----------
1. `generale_settings(request, id) [PUT]`
   - Updates system settings based on user input.
   - Requires `hostname`, `domain`, `timezone`, and `dns_servers`.

2. `get_generale_settings(request, id) [GET]`
   - Retrieves system settings (hostname, domain, and time zone).

3. `time_zones(request) [GET]`
   - Returns a list of available time zones.

4. `gatways_information(request) [GET]`
   - Fetches details of network gateways.

5. `getSystem(request, id) [GET]`
   - Retrieves system details for a given ID.

6. `getNetwork(request, id) [GET]`
   - Fetches network details for a given ID.

7. `createSystem(request) [POST]`
   - Creates a new system entry.

Dependencies:
-------------
- Django REST framework (`api_view`, `authentication_classes`)
- Django Models: `System`, `Network`, `Gateway`, `Timezone`, `Interface`
- JSON serialization for responses

Constants:
----------
- Success messages (`SUCCESS_MESSAGES_CREATING`, etc.)
- Error messages (`ERROR_MESSAGES_CREATING`, etc.)
- System-related constants (`CONSTANT_SYSTEM`, etc.)

"""
import subprocess
from django.http import JsonResponse
from backend.managementCertificates.models import Certificate
from backend.settings.serializers import SystemSerializer
from backend.gateway.models import Gateway
from backend.settings.utils import add_dns_servers, add_gateway_to_dns_servers, change_domain, change_hostname, execute_all_commandes, get_all_interfaces, get_list_settings, manage_commandes, save_config_db, save_rules_settings, set_time_zone
from backend.settings.models import Network, Settings, System, Timezone
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from backend.network.models import Interface
from backend.waf.models import RulesWaf
from django.utils.translation import gettext_lazy as _
import json

from django.core import serializers
from collections import defaultdict
from drf_yasg.openapi import Schema, TYPE_ARRAY, TYPE_BOOLEAN, TYPE_INTEGER, TYPE_OBJECT, TYPE_STRING
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from django.views.decorators.http import require_http_methods
from decouple import config


# Constants
CONSTANT_SYSTEM = _('System')
CONSTANT_LANGUAGE = _('Language')
CONSTANT_SYSTEM_CONFIG = _('Configuration')
CONSTANT_TIMEZONE_WITH_ID = _('Timezone with id')

# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")

# Error messages
ERROR_MESSAGES_CREATING = _("System error in creating")
ERROR_MESSAGES_INEXISTANT = _("does not exist")
ERROR_MESSAGES_INVALID = _("Invalid")
ERROR_MESSAGES_INVALID_DATA = _("Invalid data")
ERROR_MESSAGES_UPDATING = _("Error in updating settings")
ERROR_MESSAGE_HTTPS=_("If you choose HTTPS, you must select a certificate.")


@swagger_auto_schema('PUT', responses={200: 'Updated', 400: 'Bad Request'}, operation_summary="API TO UPDATE generale settings",
                     request_body=Schema(type=TYPE_OBJECT,  required=['hostname', 'domain', 'timezone', 'dns_servers'],
                                                 properties={'hostname': Schema(type=TYPE_STRING,example="asurad"),
                                                             'domain': Schema(type=TYPE_STRING,example="asurad.com"),
                                                             'timezone': Schema(type=TYPE_STRING,example="Africa/Addis_Ababa"),
                                                             'dns_servers': Schema(type=TYPE_OBJECT,
                                                                                properties={'dns_server': Schema(type=TYPE_STRING,example=config('SERVER_DNS')),
                                                                                            'gateway': Schema(type=TYPE_STRING,example=config('IP_ADDRESS')),
                                                                                            'interface_id': Schema(type=TYPE_INTEGER,example=1),
                                                                                            'metric': Schema(type=TYPE_INTEGER,example=20014)}),
                                                             },example={
            "hostname": "asurad",
            "domain": "asguad.com",
            "timezone": "Africa/Addis_Ababa",
            "dns_servers": [{
                "dns_server": config('SERVER_DNS'),
                "gateway": config('IP_ADDRESS'),
                "interface_id": 3,
                "metric": 20014
            }, {
                "dns_server": config('SERVER_DNS'),
                "gateway": config('IP_ADDRESS'),
                "interface_id": 5,
                "metric": 20014
            }]
        }))
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
def generale_settings(request, id):
    """
    Updates the general system settings including hostname, domain, timezone, and DNS configurations.

    This function handles PUT requests to modify system settings such as:
    - Hostname: Updates the system hostname if valid.
    - Domain: Changes the system domain if it meets the required format.
    - Timezone: Updates the system's timezone based on the provided value.
    - DNS Servers: Adds new DNS servers and associates gateways with them.
    - Network Configuration: Updates or creates a network entry with DNS server settings.

    Parameters:
    ----------
    request : HttpRequest
        The HTTP request object containing the updated system settings.
    id : int
        The ID of the system object to be updated.

    Returns:
    -------
    JsonResponse
        A JSON response containing a success or error message with an appropriate HTTP status code.

    Raises:
    ------
    System.DoesNotExist
        If the system object with the given ID does not exist.
    Timezone.DoesNotExist
        If the provided timezone is not found.
    Gateway.DoesNotExist
        If the specified gateway does not exist.
    Interface.DoesNotExist
        If the specified network interface does not exist.
    """
    msg = ''
    if (request.method == 'PUT'):
        system_object = System.objects.all().first()
        # network = Network.objects.get(id=id)
        
        data = request.data
        if change_hostname(data['hostname']) and '.' in data['domain'] and data['domain'][-1] != '.':
            system_object.hostname = data['hostname']
            change_domain(data['domain'])
            system_object.domaine = data['domain']
            timezone = Timezone.objects.get(name = data['timezone'])
            set_time_zone(timezone.name)
            system_object.time_zone = timezone
            system_object.save()
            # if "dns_servers" in data:
            for i in data['dns_servers']:
                dns_server = i['dns_server']       
                gateway = i['gateway']            
                interface_id = i['interface_id']   
                metric = i['metric']  
                add_dns_servers(dns_server)
                if gateway != "" and interface_id != "":
                    try:
                        gateway = Gateway.objects.get(gwaddress = gateway)
                    except Gateway.DoesNotExist:
                        return JsonResponse({"error": f"Gateway with {gateway} does not exist"}, status=404)
                    except ValueError:
                        return JsonResponse({"error": f"Invalid gateway: {gateway}"}, status=404)
                    try:
                        interface = Interface.objects.get(id=interface_id)
                    except Interface.DoesNotExist:
                        return JsonResponse({"error": f"Interface with ID {interface_id} does not exist"}, status=404)
                    except ValueError:
                        return JsonResponse({"error": f"Invalid interface ID: {interface_id}"}, status=404)
                    resultat,error = add_gateway_to_dns_servers(dns_server,gateway.gwaddress,interface.ifname,metric)
            # network.server_dns = data['dns_servers']
            # network.save()
            # data['dns_servers'][0]['name_interface'] = interface.name_interface
            # For adding if the table is empty
            if not Network.objects.exists():
                Network.objects.create(server_dns=data['dns_servers'])

            # For updating if the table is not empty
            else:
                Network.objects.update_or_create(
                    defaults={'server_dns': data['dns_servers']},
                )
            msg = f"{CONSTANT_SYSTEM} {SUCCESS_MESSAGES_CREATING}"
            status = 200
        else:
            msg = ERROR_MESSAGES_CREATING
            status = 400
    return JsonResponse({"msg": msg}, status=status)


@swagger_auto_schema(
    method='GET',
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                "generale_settings": Schema(
                    type=TYPE_OBJECT,
                    properties={
                        "hostname": Schema(type=TYPE_STRING),
                        "domaine": Schema(type=TYPE_STRING),
                        "time_zone": Schema(
                            type=TYPE_OBJECT,
                            properties={
                                "name": Schema(type=TYPE_STRING),
                                "id": Schema(type=TYPE_INTEGER)
                            }
                        )
                    }
                )
            }
        ),
        400: 'Bad Request',
        404: 'Not Found'
    },
    operation_summary="API to retrieve general settings",
    operation_description="Retrieve general system settings, including hostname, domain, and time zone."
)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def get_generale_settings(request,id):
    """
    Retrieves the general system settings including hostname, domain, and timezone.

    This function handles GET requests to retrieve the system settings for a specific system 
    identified by the provided ID. It returns the system's hostname, domain, and timezone details.

    Parameters:
    ----------
    request : HttpRequest
        The HTTP request object used to retrieve the system settings.
    id : int
        The ID of the system object for which the settings are being retrieved.

    Returns:
    -------
    JsonResponse
        A JSON response containing the general system settings (hostname, domain, and timezone) 
        for the system with the given ID.

    Raises:
    ------
    System.DoesNotExist
        If the system object with the given ID does not exist.
    Timezone.DoesNotExist
        If the timezone associated with the system object cannot be found.
    """
    if (request.method == 'GET'):
        system_object = System.objects.all().first()
        time_zone = Timezone.objects.get(name = system_object.time_zone.name)
        system_dict = {
            "hostname":system_object.hostname,
            "domaine":system_object.domaine,
            "time_zone":{
                "name" :time_zone.name,
                "id":time_zone.pk
            }
        }
        return JsonResponse({"generale_settings":system_dict})


@swagger_auto_schema(
    method='GET',
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                "timezones": Schema(
                    type=TYPE_ARRAY,
                    items=Schema(
                        type=TYPE_OBJECT,
                        properties={
                            "id": Schema(type=TYPE_INTEGER),
                            "name": Schema(type=TYPE_STRING),
                            "offset": Schema(type=TYPE_STRING)
                        }
                    )
                )
            }
        ),
        400: 'Bad Request'
    },
    operation_summary="API to retrieve time zone information",
    operation_description="Retrieve a list of available time zones with their ID, name, and offset."
)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def time_zones(request):
    """
    Retrieves a list of all available timezones.

    This function handles GET requests to retrieve all timezones from the database. It serializes 
    the timezone data into JSON format, removes unnecessary fields, and returns a cleaned list of timezones.

    Parameters:
    ----------
    request : HttpRequest
        The HTTP request object used to retrieve the list of timezones.

    Returns:
    -------
    JsonResponse
        A JSON response containing the list of timezones with their respective details.

    Example:
    --------
    {
        "timezones": [
            {
                "id": 1,
                "name": "UTC",
                "offset": "+00:00"
            },
            {
                "id": 2,
                "name": "PST",
                "offset": "-08:00"
            }
        ]
    }

    Raises:
    ------
    None
    """
    list_timezones=[]
    if (request.method == 'GET'):
        timezones=Timezone.objects.all()
        timezonesDict = serializers.serialize("json", timezones)
        res = json.loads(timezonesDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_timezones.append(res[i]['fields'])
        return JsonResponse({"timezones": list_timezones})


@swagger_auto_schema(
    method='GET',
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                "gatways_information": Schema(
                    type=TYPE_ARRAY,
                    items=Schema(
                        type=TYPE_OBJECT,
                        properties={
                            "gateway": Schema(
                                type=TYPE_OBJECT,
                                properties={
                                    "id": Schema(type=TYPE_INTEGER),
                                    "address": Schema(type=TYPE_STRING)
                                }
                            ),
                            "info": Schema(
                                type=TYPE_ARRAY,
                                items=Schema(
                                    type=TYPE_OBJECT,
                                    properties={
                                        "interface_id": Schema(type=TYPE_INTEGER),
                                        "metric": Schema(type=TYPE_INTEGER),
                                        "dns_server": Schema(type=TYPE_STRING),
                                        "gateway": Schema(type=TYPE_STRING)
                                    }
                                )
                            )
                        }
                    )
                )
            }
        ),
        400: 'Bad Request'
    },
    operation_summary="API to retrieve gateway information",
    operation_description="Retrieve gateway information along with associated details, including DNS servers, interfaces, and metrics."
)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def gatways_information(request):
    """
    Retrieves information about gateways and their associated details.

    This function handles GET requests to retrieve all gateways' interface information from the database. 
    It serializes the data, processes the information to map it by gateway, and returns a structured JSON response.

    Parameters:
    ----------
    request : HttpRequest
        The HTTP request object used to retrieve gateway information.

    Returns:
    -------
    JsonResponse
        A JSON response containing the gateway information, structured with each gateway's 
        associated details.

    Example:
    --------
    {
        "gatways_information": [
            {
                "gateway": {
                    "id": 1,
                    "address": "192.168.1.1"
                },
                "info": [
                    {
                        "interface_name": "eth0",
                        "metric": 10,
                        "status": "active"
                    },
                    {
                        "interface_name": "eth1",
                        "metric": 20,
                        "status": "inactive"
                    }
                ]
            }
        ]
    }

    Raises:
    ------
    None
    """
    gatways_information=[]
    if (request.method == 'GET'):
        gateway=GatewayInterface.objects.all()
        gatewayDict = serializers.serialize("json", gateway)
        res = json.loads(gatewayDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            gatways_information.append(res[i]['fields'])
        
        output_data = defaultdict(list)
        for item in gatways_information:
            gateway = item["gateway"]
            fetch_gateway = Gateway.objects.get(id = gateway)
            del item["gateway"]
            output_data[gateway].append(item)
        output_data = [
            {
                "gateway": {"id": gateway, "address": fetch_gateway.gwaddress},
                "info": info
            } for gateway, info in output_data.items()
        ]
        return JsonResponse({"gatways_information": output_data})


@swagger_auto_schema(
    method='GET',
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                "id": Schema(type=TYPE_INTEGER),
                "hostname": Schema(type=TYPE_STRING),
                "domain": Schema(type=TYPE_STRING),
                "timezone": Schema(
                    type=TYPE_OBJECT,
                    properties={
                        "name": Schema(type=TYPE_STRING),
                        "id": Schema(type=TYPE_INTEGER)
                    }
                )
            }
        ),
        404: 'Not Found'
    },
    operation_summary="API to retrieve system information",
    operation_description="Retrieve system information by ID."
)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def getSystem(request, id):
    """
    Retrieves system information for a specific ID.

    This function handles GET requests to retrieve system information (System) based on the provided `id`. It fetches the data from the database, formats it by removing unnecessary fields, and returns the system details as a JSON response.

    Parameters:
    ----------
    request : HttpRequest
        The HTTP request object containing the request details.

    id : int
        The unique identifier for the system entry to be retrieved.

    Returns:
    -------
    JsonResponse
        A JSON response containing the system details, excluding unnecessary fields.

    Example:
    --------
    Success response:
    {
        "id": 1,
        "hostname": "system1",
        "domain": "example.com",
        "time_zone": "UTC"
    }

    Raises:
    ------
    KeyError:
        If no system is found for the provided `id`.
    """
    if (request.method == 'GET'):
        system = System.objects.filter(id=id)
        systemDict = serializers.serialize("json", system)
        res = json.loads(systemDict)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields']['id'] = id
        systemJson = res[0]['fields']
        # return a no content response.
        return JsonResponse(systemJson)


@swagger_auto_schema(
    method='GET',
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                "id": Schema(type=TYPE_INTEGER),
                "name": Schema(type=TYPE_STRING),
                "subnet": Schema(type=TYPE_STRING),
                "gateway": Schema(type=TYPE_STRING),
                "dns_servers": Schema(type=TYPE_ARRAY, items=Schema(type=TYPE_STRING))
            }
        ),
        404: 'Not Found'
    },
    operation_summary="API to retrieve network information",
    operation_description="Retrieve network information by ID."
)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def getNetwork(request, id):
    """
    Retrieves the network information for a specific ID.

    This function handles GET requests to retrieve network information (Network) based on the provided `id`. It fetches the data from the database, formats it by removing unnecessary fields, and returns the information as a JSON response.

    Parameters:
    ----------
    request : HttpRequest
        The HTTP request object containing the request details.

    id : int
        The unique identifier for the network entry to be retrieved.

    Returns:
    -------
    JsonResponse
        A JSON response containing the network details, excluding unnecessary fields.

    Example:
    --------
    Success response:
    {
        "id": 1,
        "name": "Network A",
        "status": "active",
        "ip_range": "192.168.1.0/24"
    }

    Raises:
    ------
    KeyError:
        If no network is found for the provided `id`.
    """
    if (request.method == 'GET'):
        network = Network.objects.filter(id=id)
        networkDict = serializers.serialize("json", network)
        res = json.loads(networkDict)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields']['id'] = id
        networkJson = res[0]['fields']
        # return a no content response.
        return JsonResponse(networkJson)


@swagger_auto_schema(
    method='POST',
    request_body=Schema(
        type=TYPE_OBJECT,
        properties={
            'hostname': Schema(type=TYPE_STRING, example="example-host"),
            'domaine': Schema(type=TYPE_STRING, example="example.com"),
            'time_zone': Schema(
                type=TYPE_INTEGER,
                example=1
            ),
            'language': Schema(
                type=TYPE_STRING,
                enum=['en', 'fr'],
                example="en"
            ),
        }
    ),
    responses={
        201: Schema(
            type=TYPE_OBJECT,
            properties={
                "msg": Schema(type=TYPE_STRING)
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                "detail": Schema(type=TYPE_STRING)
            }
        )
    },
    operation_summary="API to create a new system",
    operation_description="Create a new system and store it in the database. A success message is returned upon successful creation."
)
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def create_system(request):
    """
    Creates a new system entry in the database based on incoming data.

    This function handles POST requests to create a new system entry. It parses the incoming request data, validates it using the `SystemSerializer`, and saves it to the database if valid. Upon successful creation, it returns a JSON response with a success message. If the data is invalid, it returns a JSON response with error details.

    Parameters:
    ----------
    request : HttpRequest
        The HTTP request object containing the data for the system to be created.

    Returns:
    -------
    JsonResponse
        A JSON response indicating the success or failure of the system creation.

    Example:
    --------
    Success response:
    {
        "msg": "System created successfully."
    }

    Error response:
    {
        "errors": {
            "field1": ["This field is required."],
            "field2": ["Invalid value."]
        }
    }

    Raises:
    ------
    None
    """
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = request.data
        try:
            time_zone = Timezone.objects.get(id=data['time_zone'])
        except ObjectDoesNotExist:
            return JsonResponse({"error": f"{CONSTANT_TIMEZONE_WITH_ID} {data['time_zone']} {ERROR_MESSAGES_INEXISTANT}"},status=400)
        except ValueError:
            return JsonResponse({"error": f"{ERROR_MESSAGES_INVALID} id: {id}"},status=400)
        if data['language'] not in ['en', 'fr']:
            return JsonResponse({"error": f"{ERROR_MESSAGES_INVALID} language: {data['language']}"},status=400)
        
        # Check if a system already exists
        existing_system = System.objects.first()  # Assuming you only want one system
        
        if existing_system:
            # Update existing system
            serializerSystem = SystemSerializer(existing_system, data=data, partial=True)
            msg = f"{CONSTANT_SYSTEM} {SUCCESS_MESSAGES_UPDATING}"
        else:
            # Create new system
            serializerSystem = SystemSerializer(data=data)
            msg = f"{CONSTANT_SYSTEM} {SUCCESS_MESSAGES_CREATING}"
        
        if serializerSystem.is_valid():
            serializerSystem.save()
            return JsonResponse({"msg": msg}, status=200 if existing_system else 201)
        
        return JsonResponse(serializerSystem.errors, status=400)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET SYSTEM LANGUAGE",)
@api_view(['GET'])
@require_http_methods(['GET'])
# @authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def get_language(request):
    """Getting System language"""
    system = System.objects.all().first()
    return JsonResponse({"language": system.language})


@swagger_auto_schema(
        method='PUT', 
        responses={200: 'Created', 400: 'Bad Request'}, 
        operation_summary="API TO UPDATE SYSTEM LANGUAGE",
        request_body=Schema(type=TYPE_OBJECT, required=['language'], properties={'language': Schema(type=TYPE_STRING, enum=["en", "fr"])}))
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def change_language(request, id):
    """Update System language"""
    try:
        data = request.data
        system = System.objects.all().first()
        serializer_system = SystemSerializer(system, data=data, partial=True)
        if serializer_system.is_valid():
            # Change language of rule waf description
            if data.get("language", "") == "en":
                for rule in RulesWaf.objects.filter(created=False):
                    rule.description = rule.description_english
                    rule.save()
            elif data.get("language", "") == "fr":
                for rule in RulesWaf.objects.filter(created=False):
                    rule.description = rule.description_french
                    rule.save()
            else:
                return JsonResponse({"error": ERROR_MESSAGES_INVALID_DATA}, status=400)

            serializer_system.save()
            return JsonResponse({"msg":f"{CONSTANT_LANGUAGE} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
        return JsonResponse({"error": list(serializer_system.errors.values())[0][0]}, status=400)
    except System.DoesNotExist:
        return JsonResponse({"error":f"{CONSTANT_SYSTEM_CONFIG} {ERROR_MESSAGES_INEXISTANT}"}, status=400)

interface_item_schema = Schema(
    type=TYPE_OBJECT,
    properties={
        "id": Schema(type=TYPE_INTEGER, description="Interface ID"),
        "address": Schema(type=TYPE_STRING, description="Interface IP address"),
    },
    required=["id", "address"],
)
@swagger_auto_schema(
    method='PUT',
    operation_summary="API TO UPDATE CONFIGURATION",
    responses={200: "Updated", 400: "Bad Request"},
    request_body=Schema(
        type=TYPE_OBJECT,
        required=["tcp_port"],  # tcp_port is required
        properties={
            "enable_ssh": Schema(
                type=TYPE_BOOLEAN,
                default=True,
                description="Enable SSH service (default: True)"
            ),
            "root_login": Schema(
                type=TYPE_BOOLEAN,
                default=True,
                description="Allow root login via SSH (default: True)"
            ),
            "auth_method": Schema(
                type=TYPE_STRING,
                maxLength=800,
                description="Authentication method (max_length=800, blank allowed)"
            ),
            "session_timeout": Schema(
                type=TYPE_INTEGER,
                nullable=True,
                description="Session timeout in seconds (nullable)"
            ),
            "protocol_http": Schema(
                type=TYPE_BOOLEAN,
                default=True,
                description="Enable HTTP protocol (default: True)"
            ),
            "certificat": Schema(
                type=TYPE_INTEGER,
                nullable=True,
                description="Certificate foreign key (nullable, provide certificate ID)"
            ),
            "tcp_port": Schema(
                type=TYPE_INTEGER,
                description="TCP port number (required)"
            ),
            "login_message": Schema(
                type=TYPE_BOOLEAN,
                default=True,
                description="Show login message (default: True)"
            ),
            
           "interface_ssh": Schema(
                type=TYPE_ARRAY,
                items=interface_item_schema,
                default=[{"id": 1, "address": config("IP_ADDRESS")}],
                description="List of interfaces allowed for SSH connections."
            ),

            "interface_web": Schema(
                type=TYPE_ARRAY,
                items=interface_item_schema,
                default=[{"id": 1, "address": config("IP_ADDRESS")}],
                description="List of interfaces allowed for web access."
            ),
        },
        example={  
            "enable_ssh": True,
            "root_login": False,
            "auth_method": "password",
            "session_timeout": 600,
            "protocol_http": False,
            "certificat": 2,
            "tcp_port": 443,
            "login_message": True,
            "interface_ssh":[{"id":1,"address":config("IP_ADDRESS")}],
            "interface_web":[{"id":1,"address":config("IP_ADDRESS")}],
            
        }
    )
)
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_settings(request, id):
    try:
        if Settings.objects.filter(id=id).exists():
            data = request.data
            enable_ssh = data.get("enable_ssh",None)
            root_login = data.get("root_login",None)
            auth_method = data.get("auth_method",None)
            session_timeout = data.get("session_timeout",None)
            protocol_http = data.get("protocol_http",None)
            certificat = data.get("certificat",None)
            tcp_port = data.get("tcp_port",None)
            login_message = data.get("login_message",None)
            interface_ssh = data.get("interface_ssh",[])
            interface_web = data.get("interface_web",[])
            password_length = data.get("password_length", None)
            all_interfaces=get_all_interfaces()
            if not certificat and not protocol_http:
                msg=ERROR_MESSAGE_HTTPS
                status=400 
            else:
                certif=None
                if certificat is not None:
                    certif=Certificate.objects.get(id=certificat).name
                data={
                    "enable_ssh" : enable_ssh,
                    "root_login" : root_login,
                    "auth_method" : auth_method,
                    "session_timeout" : session_timeout,
                    "protocol_http" : protocol_http,
                    "certificat" : certificat,
                    "tcp_port" : tcp_port,
                    "login_message" : login_message,
                    "password_length" : password_length
                    }
                all_commandes,rules_web,rules_ssh=manage_commandes(all_interfaces, interface_ssh, interface_web,root_login,auth_method,enable_ssh,protocol_http,tcp_port,login_message,certif,session_timeout)
                aux_commandes=execute_all_commandes(all_commandes)
                if aux_commandes:
                    msg,status=save_config_db(data,id,interface_web,interface_ssh)
                    save_rules_settings(rules_ssh,rules_web)
                else:
                    msg=ERROR_MESSAGES_UPDATING
                    status=400
        else:
            msg=f"{CONSTANT_SYSTEM_CONFIG} {ERROR_MESSAGES_INEXISTANT}"
            status=404 
        return JsonResponse({"msg":msg},status=status)
    
    except subprocess.CalledProcessError:
        return JsonResponse({"msg": ERROR_MESSAGES_UPDATING}, status=400)
    except Settings.DoesNotExist:
        return JsonResponse({"msg": f"{CONSTANT_SYSTEM_CONFIG} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET SETTINGS",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
def get_settings(request):
    if request.method == 'GET':
        list_settings = get_list_settings()
        return list_settings
