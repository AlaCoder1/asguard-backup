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


# Constants
CONSTANT_CONFIGURATION = _("Configuration")
CONSTANT_RULE = _("Rule")
CONSTANT_PAGE = _("Page")
CONSTANT_SURICATA_FILE = _("Suricata File")
CONSTANT_ALERT = _("Alert")
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
    request_body=SuricataFileSerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO update_suricata_configuration  ",
    operation_description="API TO update_suricata_configuration  ",
)  
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def update_suricata_configuration(request, id):
    """API to update config suricata"""
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
        # interface_names=Interface.objects.filter(id__in=interface_ids).values('ifname')
        # Utilisez la fonction get_ip_addresses pour obtenir les adresses IP
        ip_addresses =get_ip_addresses(interface_ids)
        home_net_value_sys = f'[{",".join(list(set(ip_addresses)))}]'
        home_net_value = f'[{",".join(ip_addresses)}]'
        ##traitement système
        yaml_class = ruamel.yaml.YAML()
        data_input=read_from_yaml(suricata_yaml_path_in,yaml_class)
        # print(data_input)
        data_af_packet=transform_data_af(interface_ids_input)
        data_output=update_suricata_config(data_input,home_net_value_sys,new_promisc, new_eve_log,new_syslog, new_mpm_algo,new_profile,data_af_packet,new_mode_inline)
        save_in_yaml(suricata_yaml_path,data_output,yaml_class) 
        aux_update_system=update_config(status_enabled)
        if aux_update_system:
        # Ensuite, mettez à jour les enregistrements dans la base de données
            suricata_instance = suricatafile.objects.get(id=id)
            data_updated={
            "status_enabled":status_enabled,
            "promisc" : new_promisc,
            "eve_log" : new_eve_log,
            "syslog" : new_syslog,
            "mpm_algo" : new_mpm_algo,
            "profile": new_profile,
            "mode_inline" : new_mode_inline,
            # "interface_ids" : str(interface_ids),
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
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def activer_suricata_update(request, id):
    """Add default suricata rules in database"""
    if request.method=="POST":
        cmd="sudo suricata-update"
        _,error=execute_cmd(cmd)
        if error.strip()=="":
            rules_sys = get_suricata_default_rules()
            if rules_sys is not None:
                rules_list=[l['rule'] for l in RuleIdsIpsSerializer(ids_ips_rule.objects.all() , many=True).data]
                rules_add = [log for log in rules_sys if log not in rules_list]
                rules_delete = [log for log in rules_list if log not in rules_sys] 
                if len(rules_add)!=0:
                    add_rule_database(rules_add,id)
                if len(rules_delete)!=0:
                    delete_rule_database(rules_delete)
                return JsonResponse({"message": f"{CONSTANT_RULE} {SUCCESS_MESSAGES_UPDATING}"},status=200)
            
        return JsonResponse({"message": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_RULE}"},status=400)
# def activer_suricata_update(request, id):
# @api_view(['POST'])
# @authentication_classes([SessionAuthentication])
# def activer_suricata_update(request, id):
#     """Add default suricata rules in database"""
#     if request.method=="POST":
#         cmd="sudo suricata-update"
#         _,error=execute_cmd(cmd)
#         if error.strip()=="":
#             ids_ips_rule.objects.all().delete() 
#             rules_sys = get_suricata_default_rules()
            
#             if rules_sys is not None:
#                 rules_add=prepare_rule_attribut(rules_sys)
#                 rule_objects = []
#                 for rule in rules_add:
#                     rule['suricatafile'] = int(id)
#                     serializer_rules = RuleIdsIpsSerializer(data=rule)
#                     if serializer_rules.is_valid():
#                         rule_objects.append(ids_ips_rule(**serializer_rules.validated_data))
#                         # serializer_rules.save()
#                     else:
#                         continue
#                 ids_ips_rule.objects.bulk_create(rule_objects)
              
#             return JsonResponse({"message": f"{CONSTANT_RULE} {SUCCESS_MESSAGES_UPDATING}"},status=200)
#         else:
#             return JsonResponse({"message": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_RULE}"},status=400)
# # def activer_suricata_update(request, id):
#     """Add default suricata rules in database"""
#     if request.method=="POST":
#         cmd="sudo suricata-update"
#         _,error=execute_cmd(cmd)
#         if error.strip()=="":
#             print("hello error in database")
#             rules_db = ids_ips_rule.objects.all()  # Retrieve all alerts from the database
#             rules_sys = get_suricata_default_rules()
#             rules_add=[]
#             rules_delete=[]
#             rules_list=[]
#             serializer = RuleIdsIpsSerializer(rules_db, many=True)
#             rules_list=serializer.data
#             rules_list=[l['sid'] for l in rules_list]
#             rules_sys_list=[l['sid'] for l in prepare_rule_attribut(rules_sys)]
#             print({"rules_delete":rules_delete,"rules_add":rules_sys})

#             if len(list(set(rules_list)-set(rules_sys_list))) != 0:
#                 rules_add = [log for log in rules_sys if log not in rules_list]
#                 rules_delete = [log for log in rules_list if log not in rules_sys]   
#                 if len(rules_add) != 0:
#                     rules_add = prepare_rule_attribut(rules_add)
#                     # Browse the retrieved logs and add them to the database
#                     for rule in rules_add:
#                         rule['suricatafile'] = int(id)
#                         if not ids_ips_rule.objects.filter(sid=rule['sid']).exists():
#                             serializer_rules = RuleIdsIpsSerializer(data=rule)
#                             if serializer_rules.is_valid():
#                                 serializer_rules.save()
#                             else:
#                                 return JsonResponse({"message": str(serializer_rules.errors)},status=400)
                  
#                 if len(rules_delete)!=0:
#                     # rules_delete=prepare_rule_attribut(rules_delete)
#                     for l in rules_delete:
#                         if ids_ips_rule.objects.filter(sid=l).exists():
#                             rule = ids_ips_rule.objects.get(sid=l)
#                             rule.delete()
#                         else:
#                             return JsonResponse({"message": f"{CONSTANT_RULE} {ERROR_MESSAGES_INEXISTANT}"},status=400)
#             return JsonResponse({"message": f"{CONSTANT_RULE} {SUCCESS_MESSAGES_UPDATING}"},status=200)
#         else:
#             print("hello error in system==>",error)
#             return JsonResponse({"message": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_RULE}"},status=400)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_rules_from_database(request, num):
    """Get rules from database"""
    if request.method == "GET":
        rules_from_db = ids_ips_rule.objects.all().order_by('id')

        # Paginate rules
        paginator = Paginator(rules_from_db, 10)
        try:
            rules_page = paginator.page(num)
        except EmptyPage:
            return JsonResponse({"error": f"{CONSTANT_PAGE} {ERROR_MESSAGES_INEXISTANT}"}, status=404)

        # Serialize the rules of the current page
        rule_suricata = serialize("json", rules_page, use_natural_primary_keys=True)
        res = json.loads(rule_suricata)

        rules_list = []
        for i in range(len(res)):
            fields = res[i]['fields']
            fields['id'] = res[i]['pk']
            rules_list.append(fields)
        nbpage=len(rules_from_db)/10
        # Return the list of rules in JSON format
        return JsonResponse({"rules": rules_list, "nombrePageRules": math.ceil(nbpage)}, status=200)


## fonction pour sauvegarder une règle (ajout ou mise à jour )
@swagger_auto_schema(
    method='POST',
    request_body=RuleSerializerForSwagger(many=True),
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO save rule suricata (add/update)",
    operation_description="API TO save rule suricata (add/update) ",
)
#//Ajouter une régle //   
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def save_rules_suricata(request, id):
    # Initialisation d'une chaîne vide pour stocker les messages de réponse
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
                        message = f"{CONSTANT_RULE} {SUCCESS_MESSAGES_UPDATING}"
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
        # Retourne une réponse JSON avec le message de statut
    return Response({"message": list_msg})
# @api_view(['POST'])
# @authentication_classes([SessionAuthentication])
# def save_rules_suricata(request, id):
#     # Initialisation d'une chaîne vide pour stocker les messages de réponse
#     message = ""
#     file_path = '/var/lib/suricata/rules/suricata.rules'
#     list_msg=[]
#     if request.method == 'POST':
#         # Analyse des données JSON de la requête POST
#         data_list = request.data
#         for data in data_list:
#             # Récupération des données de la règle
#             action=None if data.get('action', None) == "" else data.get('action', None)
#             protocol=None if data.get('protocol', None) == "" else data.get('protocol', None)
#             source_ip=None if data.get('source_ip', None) == "" else data.get('source_ip', None)
#             direction=None if data.get('direction', None) == "" else data.get('direction', None)
#             destination_ip=None if data.get('destination_ip', None) == "" else data.get('destination_ip', None)
#             msg=None if data.get('msg', None) == "" else data.get('msg', None)
#             rev=None if data.get('rev', None) == "" else data.get('rev', None)
#             sid=None if data.get('sid', None) == "" else data.get('sid', None)
#             activate_rule=None if data.get('activate_rule', None) == "" else data.get('activate_rule', None)
#             # Recherche du fichier SuricataFile par ID
#             try:
#                 suricatafile_obj = suricatafile.objects.get(id=id)
#             except suricatafile.DoesNotExist:
#                 return Response({"message": f"{CONSTANT_SURICATA_FILE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
#             contenu = {
#                     "action": action,
#                     "protocol": protocol,
#                     "source_ip": source_ip,
#                     "direction": direction,
#                     "destination_ip": destination_ip,
#                     "msg": msg,
#                     "rev": rev,
#                     "sid": sid,
#                     "activate_rule": activate_rule,
                    
#                  }
#             # Ajout de "#" selon la valeur de activate_rule
#             if activate_rule:
#                 must_be_comment = False
#             else:
#                 must_be_comment = True  # Ajouter "#" à la règle si activate_rule est False
#             # Mise à jour de l'ID du fichier SuricataFile dans les données de la règle
#             id_rule=None if data.get('id', None) == "" else data.get('id', None)
#             # Appel de la fonction pour ajouter la règle dans le système Suricata
#             if id_rule is None:
#                 data["default_rule"]=False
#                 if ids_ips_rule.objects.filter(sid=sid).exists():
#                     message = f"{CONSTANT_RULE} {ERROR_MESSAGES_EXISTANT}"
#                     status=400
#                 else:
#                     output, rule,error = add_rule_remote(must_be_comment, contenu,file_path)
#                     data['suricatafile'] = suricatafile_obj.id
#                     data['rule']=rule
#                     if error=="":
#                         rules_serializer = RuleIdsIpsSerializer(data=data)
#                         if rules_serializer.is_valid():
#                             rules_serializer.save()
#                             message = f"{CONSTANT_RULE} {SUCCESS_MESSAGES_CREATING}"
#                             status=200
#                         else:
#                             message = rules_serializer.errors
#                             status=400
                        
#             else:
#                 line_to_update = get_line_by_sid( sid)
#                 if line_to_update is not None:
#                     must_be_comment = not activate_rule  
                    
#                     # Ajouter la nouvelle règle dans le système distant en spécifiant si elle doit être activée ou désactivée
#                     output, rule,error = update_rule_remote(must_be_comment,contenu,line_to_update,file_path)
#                     # Vérification des erreurs lors de l'ajout de la nouvelle règle
#                     if error == '':
#                         # Mettre à jour la règle dans la base de données locale
#                         ids_ips_rule_from_db = ids_ips_rule.objects.get(sid=sid)
#                         ids_ips_rule_from_db.action = action
#                         ids_ips_rule_from_db.protocol = protocol
#                         ids_ips_rule_from_db.source_ip = source_ip
#                         ids_ips_rule_from_db.direction = direction
#                         ids_ips_rule_from_db.destination_ip = destination_ip
#                         ids_ips_rule_from_db.msg = msg
#                         ids_ips_rule_from_db.rev = rev
#                         ids_ips_rule_from_db.activate_rule = activate_rule
#                         ids_ips_rule_from_db.rule=rule
#                         ids_ips_rule_from_db.save()
#                         message = f"{CONSTANT_RULE} {SUCCESS_MESSAGES_UPDATING}"
#                         status=200
#                     else:
#                         message = error
#                         status=400
#                 else:
#                     message = f"{CONSTANT_RULE} {ERROR_MESSAGES_INEXISTANT}"
#                     status=400
#             list_msg.append({"message":message,"status":status,"sid":sid})
#         # Retourne une réponse JSON avec le message de statut
#     return Response({"message": list_msg})


@swagger_auto_schema(
    method='DELETE',
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO DELETE rule suricata with sid",
    operation_description="API TO DELETE rule suricata with sid",
)
#//supprimer une régle//
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_rule(request, sid):
    if request.method == 'DELETE':
        try:
     # Vérification de l'existence de la règle avec le SID donné
            if ids_ips_rule.objects.filter(sid=sid).exists():
     # Récupération de la règle depuis la base de données
                rule = ids_ips_rule.objects.get(sid=sid)
                if rule.default_rule==False:
                    # Chemin du fichier à rechercher
                    file_path_to_search = "/var/lib/suricata/rules/suricata.rules"  # Replace with the actual path
                    sid_to_search = str(sid)  # Convert the rule's sid to string
                    # Obtention de la ligne à supprimer en utilisant la fonction get_line_by_sid
                    l = get_line_by_sid(sid_to_search)
                    if l is not None:
            # Suppression de la ligne dans le fichier distant en utilisant la fonction delete_line_in_remote_file
                        if delete_line_in_remote_file(file_path_to_search, l.rstrip()):
            # Suppression de la règle de la base de données
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
                
       # Retourne une réponse JSON avec le message de statut
            return JsonResponse({"message": message},status=status)
        except Exception as e:
            return JsonResponse({"error": str(e)},status=400)
        

####################################  ALERTS  ####################################

#Ajouter les alertes dans la BD//
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def add_alerts_to_database(request,id):
    if request.method=="POST":
        logs = read_suricata_log()
        alerts = Alert.objects.all()  # Get alerts from database
        logs_add=[]
        logs_delete=[]
        if len(alerts)==0:
            logs_add=prepare_alert_attribut(logs)
        else:
            alert_list=[]
            serializer = AlertSerializer(alerts, many=True)
            alert_list=serializer.data
            alert_list=[l['alert'] for l in alert_list]
            logs_add = [log for log in logs if log not in alert_list]
            logs_add=prepare_alert_attribut(logs_add)
            logs_delete = [log for log in alert_list if log not in logs]   
            
        if len(logs_add) != 0:
            # Looping throw the retrieved logs and add them to the database
            for log in logs_add:
                suricatafile_obj = suricatafile.objects.get(pk=id)  
                log['suricatafile']=int(suricatafile_obj.id)
                if not Alert.objects.filter(alert=log['alert']).exists():
                    serializer_alert = AlertSerializer(data=log)
                    if serializer_alert.is_valid():
                        serializer_alert.save()
                    else:
                        return str(serializer_alert.errors)
               
        elif len(logs_delete)!=0:
            for l in logs_delete:
                if Alert.objects.filter(alert=l).exists():
                    alert = Alert.objects.get(alert=l)
                    alert.delete()
                else:
                    return JsonResponse({"message": f"{CONSTANT_ALERT} {ERROR_MESSAGES_INEXISTANT}"},status=400)
        return JsonResponse({"message": f"{CONSTANT_ALERT} {SUCCESS_MESSAGES_UPDATING}"},status=200) 

    
#Afficher les alertes de la BD avec la pagination//
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_alerts_from_database(request,num):
    if request.method == "GET":
        # Récupérer toutes les règles de la base de données
        alerts_from_db = Alert.objects.all().order_by('id')

        # Paginer les règles
        paginator = Paginator(alerts_from_db, 10)
        try:
           alerts_page = paginator.page(num)
        except EmptyPage:
            return JsonResponse({"error": f"{CONSTANT_PAGE} {ERROR_MESSAGES_INEXISTANT}"}, status=404)

        # Sérialiser les règles de la page actuelle
        rule_suricata = serialize("json", alerts_page, use_natural_primary_keys=True)
        res = json.loads(rule_suricata)

        alerts_list = []
        for i in range(len(res)):
            fields = res[i]['fields']
            fields['id'] = res[i]['pk']
            alerts_list.append(fields)
        nbpage=math.ceil(len(alerts_from_db)/10)
        # Renvoyer la liste des règles au format JSON
        return JsonResponse({"alerts": alerts_list, "nombrePageAlerts": nbpage}, status=200)
