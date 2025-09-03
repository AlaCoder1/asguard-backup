from django.http import JsonResponse
from django.db.models import Q
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes

from backend.ids_ips.views import CONSTANT_RULE, ERROR_MESSAGES_EXISTANT, SUCCESS_MESSAGES_CREATING
from backend.network.models import Interface
from backend.rules.functions import ERROR_MESSAGES_DELETING, SUCCESS_MESSAGES_DELETING, SUCCESS_MESSAGES_UPDATING, add_rule_db, add_rule_remote, calculate_subnet_address, delete_rule_remote, get_handle_rule, init_file_nftables, return_rule, update_rule_db
from backend.rules.models import Rule
from backend.rules.serializers import RuleSerializer
from utils.constant_variables import ERROR_MESSAGES_CREATING, ERROR_MESSAGES_INEXISTANT, ERROR_MESSAGES_UPDATING
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.views.decorators.http import require_http_methods
from decouple import config
@swagger_auto_schema(
    method='post',
    operation_summary="API to delete a rule",
    #   manual_parameters=[
    #     openapi.Parameter(
    #         'id',
    #         openapi.IN_PATH,
    #         description="ID of rule to delete",
    #         type=openapi.TYPE_INTEGER,
    #         required=True
    #     ),
    # ],
     request_body=openapi.Schema(
        type=openapi.TYPE_ARRAY,
       items=openapi.Items(type=openapi.TYPE_INTEGER),
        example=[1, 2, 3, 4]
     ),
    responses={
        200: openapi.Response(
            description=f"{CONSTANT_RULE} {SUCCESS_MESSAGES_DELETING}",
        ),
        400: openapi.Response(
            description=f"{CONSTANT_RULE} {ERROR_MESSAGES_INEXISTANT}",
          
        ),
    }
)

@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
def delete_rule(request):
    """
    API to delete rule from system and database 
    This function to delete a rule from the system and database using id of rule in parameter verify if exist in database and system then delete it .

    Parameters:
    request (HttpRequest): The incoming request object.
    id (int): The unique identifier of the rule to be deleted.

    Returns:
    JsonResponse: A JSON response containing a message indicating the success 
      or failure of the deletion operation.
    """
    if (request.method == 'POST'):
        ids=request.data
        all_response=[]
        for id in ids:
            if (Rule.objects.filter(id=id).exists()):
                rules = Rule.objects.get(id=id)
                rule=rules.rule
                type_rules=rules.type_rule
                interface_object= Interface.objects.get(id=rules.interface_id)
                ifname=interface_object.ifname
                handle=get_handle_rule(ifname,type_rules,rule)
                if handle is not None:
                    return_delete_rule_remote=delete_rule_remote(ifname,type_rules,handle)
                
                rules.delete()
                msg=f"{CONSTANT_RULE} {SUCCESS_MESSAGES_DELETING}"
                status=200
            
            else:
                msg=f"{CONSTANT_RULE} {ERROR_MESSAGES_INEXISTANT}"
                status=400
            all_response.append({"msg":msg,"status":status})
        return JsonResponse({"responses": all_response})
      


@swagger_auto_schema(
    method='POST',
    operation_description="Save multiple rules for a specific interface.",
    manual_parameters=[
        openapi.Parameter(
            'name_interface',
            openapi.IN_PATH,
            description="Name the interface to which you want to add or update a rule.",
            type=openapi.TYPE_STRING,
            required=True
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Rule ID (optional for new rules)',example=1),
                'policy': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='Policy of the rule',
                    enum=["drop", "accept", "reject"],  
                    default="drop"
                    ),
                'saddr': openapi.Schema(type=openapi.TYPE_STRING, description='Source address',example=config('IP_ADDRESS')),
                'daddr': openapi.Schema(type=openapi.TYPE_STRING, description='Destination address',example=config('IP_ADDRESS')),
                'sport': openapi.Schema(type=openapi.TYPE_STRING, description='Source port',example=22),
                'dport': openapi.Schema(type=openapi.TYPE_STRING, description='Destination port',example=22,),
                'protocol': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='Protocol',
                    enum=["all", "tcp", "udp", "icmp", "icmp type echo-request", "icmp type echo-reply"],
                    default="tcp"),
                'type_rule': openapi.Schema(
                    type=openapi.TYPE_STRING, description='Type of the rule',
                    enum=["inbound", "outbound"], 
                    default="inbound"
                    ),
                'rule_description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the rule',example="test rule inbound"),
                'position':openapi.Schema(type=openapi.TYPE_INTEGER, description='Rule position',example=1)
            },
            required=['policy', 'type_rule'], 
           
        )
    ),
      responses={
        200: openapi.Response(
            description="Rules successfully saved.",
            examples={
                "application/json": {
                    "response": [
                        {"id": 1, "msg": "Rule saved successfully", "status": 200},
                        {"id": 2, "msg": "Rule updated successfully", "status": 200}
                    ]
                }
            }
        ),
        400: openapi.Response(
            description="Error in saving rules.",
            examples={
                "application/json": {
                    "response": "Error message"
                }
            }
        ),
    },
    operation_summary="API to Add Firewall Rules"
)



@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
def save_rules(request,name_interface):
  """
    Function to save multiple rules for a specific interface.
    Parameters:
      request (HttpRequest): The incoming request object containing the rules data.
      name_interface (str): The name of the interface to which the rules will be applied.
    Returns:
      JsonResponse: A JSON response containing a list of responses for each rule, 
        each response includes the rule's ID, a message indicating the success or failure 
        of the operation, and the HTTP status code.
    
  """
  msg=''
  responses=[]
  if (request.method == 'POST'):
    data_list=request.data
    interface_object= Interface.objects.get(name_interface=name_interface)
    ifname=interface_object.ifname
    for index, data in enumerate(data_list):
        id_rule= None if data.get('id', None) == None else data.get('id', None)
        policy = data.get('policy', None)
        saddr = None if data.get('saddr', None) == "ALL" else data.get('saddr', None)
        daddr = None if data.get('daddr', None) =="ALL" else data.get('daddr', None)
        sport = None if data.get('sport', None) == "ALL" else data.get('sport', None)
        dport = None if data.get('dport', None) == "ALL" else data.get('dport', None)
        protocol = None if data.get('protocol', None) == "ALL" else data.get('protocol', None)
        position = index+1
        # print({"position":position})
        type_rule = data.get('type_rule', None)
        rule_description= None if data.get('rule_description', None) == "" else data.get('rule_description', None)
        if id_rule is None:
            msg,status,id_rule=add_rule_db(ifname,policy,saddr,daddr,sport,dport,protocol,type_rule,rule_description,interface_object,position)
        else:
            msg,status=update_rule_db(id_rule,ifname,policy,saddr,daddr,sport,dport,protocol,rule_description,position)
        responses.append({"id":id_rule,"msg":msg,"status":status})
    return JsonResponse({"response": responses},status=status)  
     
     
add_rule_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Rule ID (optional for new rules)',example=1),
                'policy': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='Policy of the rule',
                    enum=["drop", "accept", "reject"],  
                    default="drop"
                    ),
                'saddr': openapi.Schema(type=openapi.TYPE_STRING, description='Source address',example=config('IP_ADDRESS')),
                'daddr': openapi.Schema(type=openapi.TYPE_STRING, description='Destination address',example=config('IP_MASK')),
                'sport': openapi.Schema(type=openapi.TYPE_STRING, description='Source port',example=22),
                'dport': openapi.Schema(type=openapi.TYPE_STRING, description='Destination port',example=22,),
                'protocol': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='Protocol',
                    enum=["all", "tcp", "udp", "icmp", "icmp type echo-request", "icmp type echo-reply"],
                    default="tcp"),
                'type_rule': openapi.Schema(
                    type=openapi.TYPE_STRING, description='Type of the rule',
                    enum=["inbound", "outbound"], 
                    default="inbound"
                    ),
                'rule_description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the rule',example="test rule inbound"),
    },
    required=['policy', 'type_rule']
)   
@swagger_auto_schema(
    method='post',
    operation_summary="API to add rule for a specific interface",
    operation_description="Add rule for a specific interface.",
    manual_parameters=[
        openapi.Parameter(
            'name_interface',
            openapi.IN_PATH,
            description="Name the interface to which you want to add a rule.",
            type=openapi.TYPE_STRING,
            required=True
        ),
    ],
    request_body=add_rule_schema,
 responses={
        200: openapi.Response(description='Rule added successfully'),
        400: openapi.Response(description='Error adding rule'),
    },
    
)


@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
def add_rule(request,name_interface):
    """
    Function to add rule for a specific interface.
    Parameters:
      request (HttpRequest): The incoming request object containing the rules data.
      name_interface (str): The name of the interface to which the rules will be applied.
    Returns:
      JsonResponse: A JSON response containing a response for each rule, 
         a message indicating the success or failure 
        of the operation, and the HTTP status code.
    
    """
    data =request.data
    interface_object= Interface.objects.get(name_interface=name_interface)
    ifname=interface_object.ifname
    policy = data.get('policy', None)
    saddr = None if data.get('saddr', None) == "" else data.get('saddr', None)
    daddr = None if data.get('daddr', None) == "" else data.get('daddr', None)
    sport = None if data.get('sport', None) == "" else data.get('sport', None)
    dport = None if data.get('dport', None) == "" else data.get('dport', None)
    protocol = None if data.get('protocol', None) == "" else data.get('protocol', None)
    type_rule = data.get('type_rule', None)
    rule_description=data.get('rule_description', None)
    return_init_file_nftables = init_file_nftables(ifname)
    if return_init_file_nftables:
      rule=return_rule(ifname,policy,saddr,daddr,sport,dport,protocol,type_rule)
      if not Rule.objects.filter(
            Q(rule=rule) & (
                (Q(interface_id=interface_object.pk) ) &
                (Q(type_rule=type_rule))
            )
        ).exists():
        return_add_rule=add_rule_remote(rule,ifname,type_rule)
        if return_add_rule:
          data = {
              'policy': policy,
              'saddr':saddr,
              'daddr': daddr,
              'sport': sport,
              'dport': dport,
              'protocol': protocol,
              'type_rule': type_rule,
              'rule_description': rule_description
              }
          data['interface']=interface_object.id
          data={key: value for key, value in data.items() if value is not None}
          saddr_db=calculate_subnet_address(saddr)
          daddr_db=calculate_subnet_address(daddr)
          rule_db=return_rule(ifname,policy,saddr_db,daddr_db,sport,dport,protocol,type_rule)
          data['rule']=rule_db
          data["rule_status"]=True
          data["type_rule"]=type_rule
          rule_serializer = RuleSerializer(data=data)
          if rule_serializer.is_valid():
            rule_serializer.save()
            return JsonResponse({"response": f"{CONSTANT_RULE} {SUCCESS_MESSAGES_CREATING}"}, status=200)
          return JsonResponse({"response": rule_serializer.errors}, status=400)
        return JsonResponse({"response": f"{ERROR_MESSAGES_CREATING} {CONSTANT_RULE}"}, status=400)
      return JsonResponse({"response": f"{CONSTANT_RULE} {ERROR_MESSAGES_EXISTANT}"}, status=400)
    return JsonResponse({"response": f"{ERROR_MESSAGES_CREATING} {CONSTANT_RULE}"}, status=400)


   
@swagger_auto_schema(
  method='put',
    operation_summary="API to update rule for a specific interface.",
  operation_description="Update rule for a specific interface.",
  request_body=add_rule_schema,
    manual_parameters=[
            openapi.Parameter(
                'name_interface',
                openapi.IN_PATH,
                description="Name the interface to which you want to update a rule.",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
responses={
      200: openapi.Response(description='Rule update successfully'),
      400: openapi.Response(description='Error in updating rule'),
  },
)
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
def update_rule(request,name_interface):
    """
    Function to update rule for a specific interface.
    Parameters:
      request (HttpRequest): The incoming request object containing the rules data.
      name_interface (str): The name of the interface to which the rules will be applied.
    Returns:
      JsonResponse: A JSON response containing a response for each rule, 
       , a message indicating the success or failure 
        of the operation, and the HTTP status code.
    
    """
    # parse the incoming information
    data =request.data
    #get object of interface type
    interface_object= Interface.objects.get(name_interface=name_interface)
    #get interface name to execute command systeme
    ifname=interface_object.ifname
    id=data.get('id', None)
    policy = data.get('policy', None)
    saddr = None if data.get('saddr', None) == "" else data.get('saddr', None)
    daddr = None if data.get('daddr', None) == "" else data.get('daddr', None)
    sport = None if data.get('sport', None) == "" else data.get('sport', None)
    dport = None if data.get('dport', None) == "" else data.get('dport', None)
    protocol = None if data.get('protocol', None) == "" else data.get('protocol', None)
    rule_description=data.get('rule_description', None)
    #test if rule exist or not with id 
    if (id is not None and Rule.objects.filter(id=id).exists()):
        rules_object = Rule.objects.get(id=id)
        rule=rules_object.rule
        type_rules=rules_object.type_rule
        #appel la fonction pour retourner rule à ajouter 
        ruleupdate=return_rule(ifname,policy,saddr,daddr,sport,dport,protocol,type_rules)
        handle=get_handle_rule(ifname,type_rules,rule)
        if handle:
            return_delete_rule_remote=delete_rule_remote(ifname,type_rules,handle)
            if return_delete_rule_remote:
                return_add_rule=add_rule_remote(ruleupdate,ifname,type_rules)
                if  return_add_rule:
                    data = {
                    "id":id,
                    'policy': policy,
                    'saddr':saddr,
                    'daddr': daddr,
                    'sport': sport,
                    'dport': dport,
                    'protocol': protocol,
                    'rule_description': rule_description
                    }
                    
                    #appel la fonction pour update rule dans la base de données 
                    # data={key: value for key, value in data.items() if value is not None}
                    data['interface']=rules_object.interface_id
                    saddr_db=calculate_subnet_address(saddr)
                    daddr_db=calculate_subnet_address(daddr)
                    rule_db_update=return_rule(ifname,policy,saddr_db,daddr_db,sport,dport,protocol,type_rules)
                    data['rule']=rule_db_update
                    rule_serializer = RuleSerializer(rules_object,data=data)
                    if rule_serializer.is_valid():
                        rule_serializer.save()
                        return JsonResponse({"response": f"{CONSTANT_RULE} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
                    return JsonResponse({"response": rule_serializer.errors}, status=400)
            return JsonResponse({"response": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_RULE}"}, status=400)
        return JsonResponse({"response": f"{CONSTANT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)

    return JsonResponse({"response": f"{CONSTANT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
    