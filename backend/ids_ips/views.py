import math
from django.utils.translation import gettext_lazy as _
from .models import *
from backend.network.serializers import *
from django.http import JsonResponse
from backend.network.models import *
from backend.settings.serializers import *
import json
from django.http import JsonResponse
from backend.authentification.views import *
from .serializers import *
from rest_framework.response import Response
from backend.ids_ips.function_BD import *
from backend.ids_ips.function_sys import *
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage
from django.core.serializers import serialize
import ruamel.yaml
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Constants
CONSTANT_CONFIGURATION = _("Configuration")
CONSTANT_RULE = _("Rule")
CONSTANT_PAGE = _("Page")
CONSTANT_SURICATA_FILE = _("Suricata File")
CONSTANT_ALERT = _("Alert")
CONSTANT_STATUS=_("Rule status")
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
# Error messages
ERROR_MESSAGES_DELETING = _("Error in deleting")
ERROR_MESSAGES_UPDATING = _("Error in updating")
ERROR_MESSAGES_DELETING_USED_ITEM = _("Unable to delete")
ERROR_MESSAGES_EXISTANT = _("already exist")
ERROR_MESSAGES_INEXISTANT = _("does not exist")


#################################### SURICATA.YAML FGENERAL CONFIGURATION ####################################
@swagger_auto_schema(
    method='PUT',
    operation_description="Save system configuration with interface details.",
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="ID of suricata config to update.",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status_enabled': openapi.Schema(
                type=openapi.TYPE_BOOLEAN, 
                description='Indicates if the status is enabled', 
                example=True
            ),
            'promisc': openapi.Schema(
                type=openapi.TYPE_BOOLEAN, 
                description='Indicates if promiscuous mode is enabled', 
                example=False
            ),
            'eve_log': openapi.Schema(
                type=openapi.TYPE_BOOLEAN, 
                description='Indicates if event logging is enabled', 
                example=True
            ),
            'syslog': openapi.Schema(
                type=openapi.TYPE_BOOLEAN, 
                description='Indicates if syslog is enabled', 
                example=True
            ),
            'mpm_algo': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='The algorithm used for memory management', 
                enum=["auto", "ac", "ac-bs", "ac-ks", "hyperscan"],
                example="ac"
            ),
            'profile': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='The profile type', 
                enum=["low", "medium", "high"],
                example="high"
            ),
            'copy_mode': openapi.Schema(
                type=openapi.TYPE_BOOLEAN, 
                description='Indicates if copy mode is enabled', 
                example=True
            ),
            'list_interfaces': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(
                            type=openapi.TYPE_INTEGER, 
                            description='Interface ID', 
                            example=2
                        ),
                        'interface': openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            description='The name of the network interface', 
                            example="enp0s8"
                        ),
                        'threads': openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            description='Thread management', 
                            example=None
                        ),
                        'cluster_id': openapi.Schema(
                            type=openapi.TYPE_INTEGER, 
                            description='Cluster ID associated with the interface', 
                            example=128
                        ),
                        'cluster_type': openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            description='Cluster type for the interface', 
                            enum=["cluster_cpu","cluster_flow","cluster_qm","cluster_ebpf"]
                            
                        ),
                        'defrag': openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            description='Defrag status for the interface', 
                            example="no"
                        ),
                        'use_mmap': openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            description='Indicates if mmap is used for the interface', 
                            enum=['yes','no'],
                            default="no"
                        ),
                        'ring_size': openapi.Schema(
                            type=openapi.TYPE_INTEGER, 
                            description='Ring buffer size for the interface', 
                            example=8555
                        ),
                        'copy_mode': openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            description='Copy mode type for the interface', 
                           enum=["tap","ips"]
                        ),
                        'copy_iface': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(
                                    type=openapi.TYPE_INTEGER, 
                                    description='ID of the copy interface', 
                                    example=1
                                ),
                                'name': openapi.Schema(
                                    type=openapi.TYPE_STRING, 
                                    description='Name of the copy interface', 
                                    example="enp0s17"
                                ),
                            }
                        )
                    }
                )
            )
        },
        required=['status_enabled', 'mpm_algo', 'profile', 'copy_mode', 'list_interfaces',
                  'cluster_id','defrag','ring_size','use_mmap'],
    ),
    responses={
        200: openapi.Response(
            description="System configuration saved successfully",
            examples={
                "application/json": {
                    "response": "Configuration saved successfully"
                }
            }
        ),
        400: openapi.Response(
            description="Bad request",
            examples={
                "application/json": {
                    "response": "Error in saving configuration"
                }
            }
        ),
    },
    operation_summary="API to Save System Configuration"
)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def update_suricata_configuration(request, id):
    """
    API to update suricata configuration with general information in file suricata.yaml.
    Parameters:
        request (HttpRequest): The incoming request object containing the PUT data.
        id (int): The ID of the system configuration to be updated.
    Returns:
        JsonResponse: A JSON response with a message indicating the success or failure of the operation.
        The response includes a status code.
    """
    
    
    if request.method=="PUT":
        # try: 
        suricata_yaml_path_in = "/etc/suricata/suricata.yaml"
        suricata_yaml_path = "/etc/suricata/suricata.yaml"
        
        data = request.data
        ##status suricata
        status_enabled = data.get('status_enabled', None)
        ##promisc
        new_promisc = data.get("promisc", "false")
        new_promisc=str(new_promisc).lower()
        ##eve_log
        new_eve_log = data.get("eve_log", False)
        new_eve_log = "yes" if new_eve_log else "no"
        ##syslog
        new_syslog = data.get("syslog", False)
        new_syslog = "yes" if new_syslog else "no"
        ##mpm_algo
        new_mpm_algo = data.get("mpm_algo", "ac")
        ##detect profile
        new_profile = data.get("profile", "low")
        ##copy_mode
        new_mode_inline = data.get("mode_inline", False)
        new_mode_inline = "yes" if new_mode_inline else "no"
        ##interfaces
        interface_ids_input = data.get("list_interfaces", [])
        interface_ids = [x["id"] for x in interface_ids_input]
        ip_addresses =get_ip_addresses(interface_ids)
        home_net_value_sys = f'[{",".join(list(set(ip_addresses)))}]'
        home_net_value = f'[{",".join(ip_addresses)}]'
        yaml_class = ruamel.yaml.YAML()
        data_input=read_from_yaml(suricata_yaml_path_in,yaml_class)
        data_af_packet=transform_data_af(interface_ids_input)
        data_output=update_suricata_config(data_input,home_net_value_sys,new_promisc, new_eve_log,new_syslog, new_mpm_algo,new_profile,data_af_packet,new_mode_inline)
        save_in_yaml(suricata_yaml_path,data_output,yaml_class) 
        aux_update_system=update_config(status_enabled)
        if aux_update_system:
            suricata_instance = suricatafile.objects.get(id=id)
            data_updated={
            "status_enabled":status_enabled,
            "promisc" : new_promisc,
            "eve_log" : new_eve_log,
            "syslog" : new_syslog,
            "mpm_algo" : new_mpm_algo,
            "profile": new_profile,
            "mode_inline" : new_mode_inline,
            "home_net" : home_net_value
            }
            suricata_serializer=SuricataFileSerializer(suricata_instance,data=data_updated)
            if suricata_serializer.is_valid():
                suricata_serializer.save()
                aux_update=save_suricata_interface(id,interface_ids_input)
                if aux_update:
                    msg = f"{CONSTANT_CONFIGURATION} {SUCCESS_MESSAGES_UPDATING}"
                    status=200
                else:
                    msg= aux_update
                    status=400
            else:
                msg= list(suricata_serializer.errors.values())[0][0]
                status=400
        else:
            msg= f"{ERROR_MESSAGES_UPDATING} {CONSTANT_CONFIGURATION}"
            status=400
        return JsonResponse({'msg': msg}, status=status) 
        

#################################### RULES ############################################################

@swagger_auto_schema(
    method='POST',
    operation_summary="API TO activate suricata update.",
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="ID of suricata config to update suricata rules.",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    responses={
        200: f"{CONSTANT_RULE} {SUCCESS_MESSAGES_UPDATING}",
        400:f"{ERROR_MESSAGES_UPDATING} {CONSTANT_RULE}"
    }
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def activer_suricata_update(request, id):
    """
    API to update rules in suricata.rules with synchronise system and database .
    Parameters:
        request (HttpRequest): The incoming request object containing the POST data.
        id (int): The ID of the system configuration to be updated.
    Returns:
        JsonResponse: A JSON response with a message indicating the success or failure of the operation.
        The response includes a status code.
    """
    if request.method=="POST":
        # cmd="sudo suricata-update --offline -q"
        # _,error=execute_cmd(cmd)
        # if error.strip()=="":
        rules_sys = get_suricata_default_rules()
        if rules_sys is not None:
            rules_list=[l['rule'] for l in RuleIdsIpsSerializer(ids_ips_rule.objects.all() , many=True).data]
            if (len(list(set(rules_sys)-set(rules_list))))!=0 or (len(list(set(rules_list)-set(rules_sys))))!=0:
                rules_add = [log for log in rules_sys if log not in rules_list]
                rules_delete = [log for log in rules_list if log not in rules_sys] 
                if len(rules_add)!=0:
                    add_rule_database(rules_add,id)
                if len(rules_delete)!=0:
                    delete_rule_database(rules_delete)
            return JsonResponse({"message": f"{CONSTANT_RULE} {SUCCESS_MESSAGES_UPDATING}"},status=200)
            
        return JsonResponse({"message": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_RULE}"},status=400)

@swagger_auto_schema(
    method='GET',
    operation_summary="API to get all rules from the database.",
    manual_parameters=[
        openapi.Parameter(
            'num',
            openapi.IN_PATH,
            description="Number of page of rules suricata.",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    responses={
        404:f"{CONSTANT_PAGE} {ERROR_MESSAGES_INEXISTANT}",
        200: openapi.Response(
            description="List of rule retrieved successfully. Each rule is represented as a dictionary with the following fields:\n"
                        "- \t  `sid`: The signature ID of the alert.\n"
                        "- \t   action`: The action associated with the alert (e.g., 'alert').\n"
                        "- \t   `protocol`: The protocol used (e.g., 'ip').\n"
                        "- \t   `source_ip`: The source IP and port (e.g., 'any any').\n"
                        "- \t   `direction`: The direction of the rule (e.g., '->').\n"
                        "- \t   `destination_ip`: The destination IP and port (e.g., 'any any').\n"
                        "- \t   `msg`: A message describing the alert.\n"
                        "- \t   `rev`: The revision number of the rule.\n"
                        "- \t   `rule`: The full rule string associated with the alert.\n"
                        "- \t   `activate_rule`: A boolean indicating if the rule is active.\n"
                        "- \t   `default_rule`: A boolean indicating if the rule is default.\n"
                        "- \t   `suricatafile`: The ID of the Suricata file associated with the alert.\n"
                        "- \t   `id`: The unique ID of the alert.",
        )
    }
)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_rules_from_database(request, num):
    """
    API to get all RULES per page from the database.
    This function retrieves all RULES per page from the database and returns them as a JSON response.
   
    Parameters:
    request (HttpRequest): The incoming request object containing the GET data.
    num (int): The number of page 

    Returns:
    JsonResponse: A JSON response containing a list of RULES contains informations,
   
    """
    if request.method == "GET":
        rules_from_db = ids_ips_rule.objects.all().order_by('id')

        # Paginate rules
        paginator = Paginator(rules_from_db, 10)
        try:
            rules_page = paginator.page(num)
        except EmptyPage:
            return JsonResponse({"error": f"{CONSTANT_PAGE} {ERROR_MESSAGES_INEXISTANT}"}, status=404)

        rule_suricata = serialize("json", rules_page, use_natural_primary_keys=True)
        res = json.loads(rule_suricata)

        rules_list = []
        for i in range(len(res)):
            fields = res[i]['fields']
            fields['id'] = res[i]['pk']
            rules_list.append(fields)
        nbpage=len(rules_from_db)/10
        return JsonResponse({"rules": rules_list, "nombrePageRules": math.ceil(nbpage)}, status=200)




@swagger_auto_schema(
    method='POST',
    operation_summary="API TO save rule suricata (add/update)",
    operation_description="API TO save rule suricata (add/update) ",
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="ID of suricata config.",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    responses={200:f"{CONSTANT_RULE} {SUCCESS_MESSAGES_UPDATING}", 
               400: 'Bad Request'},
    request_body=openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Rule ID',example=1),
            'activate_rule': openapi.Schema(
                type=openapi.TYPE_BOOLEAN, 
                description='Indicates if the status of rule', 
                example=True
            ),
        }
    )
    )
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def save_rules_suricata(request, id):
    """
    API to update rules status in suricata.rules with synchronise system and database .
    Parameters:
        request (HttpRequest): The incoming request object containing the POST data.
        id (int): The ID of the system configuration to be updated.
    Returns:
        JsonResponse: A JSON response with a message indicating the success or failure of the operation.
        The response includes a status code.
    """
    message = ""
    file_path = '/var/lib/suricata/rules/suricata.rules'
    list_msg=[]
    if request.method == 'POST':
        data_list = request.data
        for data in data_list:
            id_rule=None if data.get('id', None) == "" else data.get('id', None)
            activate_rule=None if data.get('activate_rule', None) == "" else data.get('activate_rule', None)
            sid=ids_ips_rule.objects.get(id=id_rule).sid           
            line_to_update = get_line_by_sid(sid)
            if line_to_update is not None:
                _, rule,error = update_rule_remote(sid,activate_rule,line_to_update,file_path)
                if error == '':
                    contenu = {
                    "activate_rule": activate_rule,
                    "rule":rule,
                    "suricatafile":id,
                        }
                    ids_ips_rule_from_db = ids_ips_rule.objects.get(sid=sid)
                    serializer_rule=RuleIdsIpsSerializer(ids_ips_rule_from_db,data=contenu)
                    if serializer_rule.is_valid():
                        serializer_rule.save()
                        message = f"{CONSTANT_STATUS} {SUCCESS_MESSAGES_UPDATING}"
                        status=200
                    else:
                        message = str(serializer_rule.errors)
                        status=400
                else:
                    message = error
                    status=400
            else:
                message = f"{CONSTANT_RULE} {ERROR_MESSAGES_INEXISTANT}"
                status=400
            list_msg.append({"message":message,"status":status,"sid":sid})
    return Response({"message": list_msg})



@swagger_auto_schema(
    method='delete',
    operation_summary="API to delete a rule",
    manual_parameters=[
        openapi.Parameter(
            'sid',
            openapi.IN_PATH,
            description="SID of the rule to be deleted.",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    responses={
        200: openapi.Response(
            description= f"{CONSTANT_RULE} {SUCCESS_MESSAGES_DELETING}",
        ),
        400: openapi.Response(
            description=f"{ERROR_MESSAGES_DELETING} {CONSTANT_RULE}",
          
        ),
    }
)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_rule(request, sid):
    """
    API to delete rule from system and database 
    This function to delete a rule from the system and database using id of rule in parameter.

    Parameters:
    request (HttpRequest): The incoming request object.
    id (int): The unique identifier of the rule to be deleted.

    Returns:
    JsonResponse: A JSON response containing a message indicating the success 
      or failure of the deletion operation.
    """
    if request.method == 'DELETE':
        try:
            if ids_ips_rule.objects.filter(sid=sid).exists():
                rule = ids_ips_rule.objects.get(sid=sid)
                if rule.default_rule==False:
                    file_path_to_search = "/var/lib/suricata/rules/suricata.rules"  
                    sid_to_search = str(sid)  
                    l = get_line_by_sid(sid_to_search)
                    if l is not None:
                        if delete_line_in_remote_file(file_path_to_search, l.rstrip()):
                            rule.delete()
                            message = f"{CONSTANT_RULE} {SUCCESS_MESSAGES_DELETING}"
                            status=200
                        else:
                            message = f"{ERROR_MESSAGES_DELETING} {CONSTANT_RULE}"
                            status=400
                    else:
                            message = f"{ERROR_MESSAGES_DELETING} {CONSTANT_RULE}"
                            status=400
                else:
                    message = f"{ERROR_MESSAGES_DELETING_USED_ITEM} {CONSTANT_RULE}"
                    status=400
            else:
                message = f"{CONSTANT_RULE} {ERROR_MESSAGES_INEXISTANT}"
                status=400
                
            return JsonResponse({"message": message},status=status)
        except Exception as e:
            return JsonResponse({"error": str(e)},status=400)
        

####################################  ALERTS  ####################################
@swagger_auto_schema(
    method='POST',
    operation_summary="API TO add suricata alerts to database.",
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="ID of suricata config.",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    responses={
        200: f"{CONSTANT_ALERT} {SUCCESS_MESSAGES_UPDATING}",
        400: f"{ERROR_MESSAGES_UPDATING} {CONSTANT_ALERT}"
    }
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def add_alerts_to_database(request,id):
    """
    API to add alerts in database
    This function read from file alert from system and prepare it to be added to database in specific format .
    Parameters:
      request (HttpRequest): The incoming request object containing the rules data.
      id (int): id of suricata config 
    Returns:
      JsonResponse: A JSON response containing a response for each rule, 
         a message indicating the success or failure 
        of the operation, and the HTTP status code.
    
    """
    if request.method=="POST":
        logs = read_suricata_log()
        if logs is not None:
            alert_list=[l['alert'] for l in AlertSerializer( Alert.objects.all(), many=True).data]
            logs_add = [log for log in logs if log not in alert_list]
            logs_add=prepare_alert_attribut(logs_add)
            logs_delete = [log for log in alert_list if log not in logs]   
            if len(list(set(logs)-set(alert_list)))!=0:
                if len(logs_add)!=0:
                    aux_add=add_alert_suricata(logs_add,id)
                    if aux_add is not True:
                        return JsonResponse({"message": aux_add},status=400)
                if len(logs_delete)!=0:
                    delete_alert_suricata(logs_delete)
            return JsonResponse({"message": f"{CONSTANT_ALERT} {SUCCESS_MESSAGES_UPDATING}"},status=200) 
        else:
            return JsonResponse({"message": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_ALERT}"},status=400)
             
@swagger_auto_schema(
    method='GET',
    operation_summary="API to get all alerts from the database.",
      manual_parameters=[
        openapi.Parameter(
            'num',
            openapi.IN_PATH,
            description="Number of page of alerts suricata",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    responses={
        404:f"{CONSTANT_PAGE} {ERROR_MESSAGES_INEXISTANT}",
        200: openapi.Response(
            description="List of alerts retrieved successfully. Each alert is represented as a dictionary with the following fields:\n"
                        "-\t    timestamp: The timestamp of the alert.\n"
                        "- \t   sid: The signature ID of the alert.\n"
                        "- \t   priority: The priority level of the alert.\n"
                        "- \t   protocol: The protocol associated with the alert.\n"
                        "- \t   src_addr: The source IP address.\n"
                        "- \t   src_port: The source port.\n"
                        "- \t   dst_addr: The destination IP address.\n"
                        "- \t   dst_port: The destination port.\n"
                        "- \t   message: A message describing the alert.\n"
                        "- \t   alert: A detailed alert message.\n"
                        "- \t   suricatafile: The ID of the Suricata file associated with the alert.\n"
                        "- \t   id: The unique ID of the alert.",
                        )
    }
)
    
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_alerts_from_database(request,num):
    """
    API to get all ALERTS per page from the database.
    This function retrieves all ALERTS per page from the database and returns them as a JSON response.
   
    Parameters:
    request (HttpRequest): The incoming request object containing the GET data.
    num (int): The number of page 

    Returns:
    JsonResponse: A JSON response containing a list of ALERTS contains informations,
   
    """
    if request.method == "GET":
        alerts_from_db = Alert.objects.all().order_by('-id')

        paginator = Paginator(alerts_from_db, 10)
        try:
           alerts_page = paginator.page(num)
        except EmptyPage:
            return JsonResponse({"error": f"{CONSTANT_PAGE} {ERROR_MESSAGES_INEXISTANT}"}, status=404)

        rule_suricata = serialize("json", alerts_page, use_natural_primary_keys=True)
        res = json.loads(rule_suricata)

        alerts_list = []
        for i in range(len(res)):
            fields = res[i]['fields']
            fields['id'] = res[i]['pk']
            alerts_list.append(fields)
        nbpage=math.ceil(len(alerts_from_db)/10)
        return JsonResponse({"alerts": alerts_list, "nombrePageAlerts": nbpage}, status=200)
