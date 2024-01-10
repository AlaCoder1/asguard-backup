import math
from django.shortcuts import render
# Create your views here.
import ast
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
from rest_framework import status
from backend.ids_ips.function_BD import *
from backend.ids_ips.function_sys import *
from django.core import serializers
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage
from django.core.serializers import serialize
#################################### SURICATA.YAML CONFIGURATION GENERALE ############################################################
@swagger_auto_schema(
    method='PUT',
    request_body=SuricataFileSerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO update_suricata_configuration  ",
    operation_description="API TO update_suricata_configuration  ",
)  
#Modifier le fichier de configuration du suricata  
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def update_suricata_configuration(request, id):
    if request.method=="PUT":
        try: 
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
            new_copy_mode = data.get("copy_mode", "none")
            if new_copy_mode is True:
                new_copy_mode="ips"
            else:
                new_copy_mode="tap"
            ##interfaces
            interface_ids_input = data.get("interface", [])
            interface_ids = [x["id"] for x in interface_ids_input]
            interface_names=Interface.objects.filter(id__in=interface_ids).values('ifname')
            # Utilisez la fonction get_ip_addresses pour obtenir les adresses IP
            ip_addresses =get_ip_addresses(interface_ids)
            home_net_value_sys = f'[{", ".join(list(set(ip_addresses)))}]'
            home_net_value = f'[{", ".join(ip_addresses)}]'
            ##taritement système
            output,error= execute_cmd("sudo cat " + suricata_yaml_path)
            if output:
                lines = output.split('\n')
                # Appelez d'abord la fonction update_suricata_config pour mettre à jour le système
                aux_update=update_suricata_config(suricata_yaml_path,lines,home_net_value_sys,interface_names[0]['ifname'],status_enabled,str(new_promisc).lower(), new_eve_log, new_syslog, new_mpm_algo, new_profile, new_copy_mode)
                if aux_update is True:
                        # Ensuite, mettez à jour les enregistrements dans la base de données
                        suricata_instance = suricatafile.objects.get(id=id)
                        data_updated={
                            "status_enabled":status_enabled,
                            "promisc" : new_promisc,
                            "eve_log" : new_eve_log,
                            "syslog" : new_syslog,
                            "mpm_algo" : new_mpm_algo,
                            "profile": new_profile,
                            "copy_mode" : new_copy_mode,
                            "interface_ids" : str(interface_ids),
                            "home_net" : home_net_value
                        }
                        suricataSerializer=SuricataFileSerializer(suricata_instance,data=data_updated)
                        if suricataSerializer.is_valid():
                            suricataSerializer.save()
                            msg = "Configuration updated Successfully!!"
                            status=200
                        else:
                            msg= "Failed to save configuration in database !"
                            status=400
                else:
                    msg=aux_update
                    status=400
            else:
                msg="Failed to open config file!"
                status=404
            return JsonResponse({'msg': msg}, status=status) 
        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)}, status=500) 


#Aficher le fichier de configuration suricata.yaml//
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_suricata_configuration(request, id):
    if request.method=="GET":
        # Obtenez le champ HOME_NET du système et de la base de données
        home_net_database, interface_ids = get_home_net_de_la_base_de_donnees(id)
        interface_ids = ast.literal_eval(interface_ids)
        address_home_net = home_net_database.strip("[]").split(",")
        # Récupérez les adresses IP à partir de la configuration IP4Config
        ip4config_object = IP4Config.objects.all()
        ip4config_dict = serializers.serialize("json", ip4config_object)
        res = json.loads(ip4config_dict)
        interfaces_ids_ip4config = []
        interfaces_address_ip4config = []
        # Parcourez les enregistrements IP4Config pour obtenir les interfaces et leurs adresses
        for i in range(len(res)):
            interfaces_ids_ip4config.append(res[i]['fields']['interface'])
            interfaces_address_ip4config = get_ip_addresses(interfaces_ids_ip4config)
        # Initialisez des listes pour stocker les valeurs finales
        address_home_net_final = []
        interface_ids_final = []
        # Comparez les interfaces et leurs adresses pour déterminer la configuration finale
        for i in interface_ids:
            if i in interfaces_ids_ip4config:
                if address_home_net[interface_ids.index(i)] == interfaces_address_ip4config[interfaces_ids_ip4config.index(i)]:
                    address = address_home_net[interface_ids.index(i)]
                else:
                    address = interfaces_address_ip4config[interfaces_ids_ip4config.index(i)]
                address_home_net_final.append(address)
                interface_ids_final.append(i)
            else:
                pass
        # Créez une chaîne avec les adresses HOME_NET finales
        home_net_value = ' , '.join(address_home_net_final)
        home_net_value = f'[{home_net_value}]'
        interfaces_ids_value = str(interface_ids_final)
        suricata_yaml_path = "/etc/suricata/suricata.yaml"
        # Exécutez la commande 'sudo cat' pour lire le contenu du fichier
        output, error = execute_cmd("sudo cat " + suricata_yaml_path)
        # Mettez à jour la configuration dans le système
        if output:
            # Lit les lignes du fichier
            lines = output.split('\n')
            updated_lines = []
            for line in lines:
                stripped_line = line.strip()
                if stripped_line.startswith("#"):
                    updated_lines.append(line + '\n')
                    # Conserve les lignes de commentaire telles quelles
                elif "HOME_NET:" in stripped_line:
                    # Met à jour la ligne HOME_NET avec la nouvelle valeur
                    updated_lines.append(f'    HOME_NET: "{home_net_value}"'+'\n')
                else:
                    # Conserve les autres lignes telles quelles
                    updated_lines.append(line + '\n')
                    with open(suricata_yaml_path, 'w') as local_file:
                        for string in updated_lines:
                            local_file.write(string)
        # Mettez à jour la configuration dans la base de données
        suricata_instance = suricatafile.objects.get(id=id)
        suricata_instance.interface_ids = interfaces_ids_value
        suricata_instance.home_net = home_net_value
        suricata_instance.save()
        current_configuration = {
            "promisc": suricata_instance.promisc,
            "eve_log": suricata_instance.eve_log,
            "syslog": suricata_instance.syslog,
            "mpm_algo": suricata_instance.mpm_algo,
            "profile": suricata_instance.profile,
            "copy_mode": suricata_instance.copy_mode,
            "status_enabled":suricata_instance.status_enabled
            }
    return JsonResponse({"configuration": current_configuration, "interface_ids": interface_ids_final, "address_home_net": address_home_net_final})
#################################### FIN SURICATA.YAML CONFIGURATION GENERALE ############################################################

#################################### LES REGLES ############################################################
#Ajouter les régles par défaut dans la BD//
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def activerSuricataUpdate(request, id):
    if request.method=="POST":
        cmd="sudo suricata-update"
        output,error=execute_cmd(cmd)
        if error.strip()=="":
            rules_DB = ids_ips_rule.objects.all()  # Récupérer toutes les alertes de la base de données
            rules_sys = get_suricata_default_rules()
            rules_add=[]
            rules_delete=[]
            rules_list=[]
            serializer = RuleIdsIpsSerializer(rules_DB, many=True)
            rules_list=serializer.data
            rules_list=[l['sid'] for l in rules_list]
            rules_sys_list=[l['sid'] for l in prepare_rule_attribut(rules_sys)]
            if len(list(set(rules_list)-set(rules_sys_list)))!=0:
                rules_add = [log for log in rules_sys if log not in rules_list]
                rules_delete = [log for log in rules_list if log not in rules_sys]   
                if len(rules_add)!=0:
                    rules_add=prepare_rule_attribut(rules_add)
                    # Parcourir les logs récupérés et ajoutez-les à la base de données
                    for rule in rules_add:
                        print("data to add ==>",rule['rule'])
                        rule['suricatafile']=int(id)
                        if not ids_ips_rule.objects.filter(sid=rule['sid']).exists():
                            serializerAlert = RuleIdsIpsSerializer(data=rule)
                            if serializerAlert.is_valid():
                                serializerAlert.save()
                            else:
                                return JsonResponse({"message": str(serializerAlert.errors)},status=400)
                        else:
                            pass
                if len(rules_delete)!=0:
                    rules_delete=prepare_rule_attribut(rules_delete)
                    for l in rules_delete:
                        if ids_ips_rule.objects.filter(sid=l['sid']).exists():
                            rule = ids_ips_rule.objects.get(sid=l['sid'])
                            rule.delete()
                        else:
                            return JsonResponse({"message": "Rule not found!"},status=400)
            return JsonResponse({"message": "Rules updated successfully!"},status=200)
        else:
            return JsonResponse({"message":error},status=400)
            
#//Récupérer les règles de la base de données //
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def getRulesFromDatabase(request, num):
    if request.method == "GET":
        # Récupérer toutes les règles de la base de données
        rules_from_db = ids_ips_rule.objects.all()

        # Paginer les règles
        paginator = Paginator(rules_from_db, 10)
        try:
            rules_page = paginator.page(num)
        except EmptyPage:
            return JsonResponse({"error": "Page not found"}, status=404)

        # Sérialiser les règles de la page actuelle
        rule_suricata = serialize("json", rules_page, use_natural_primary_keys=True)
        res = json.loads(rule_suricata)

        rules_list = []
        for i in range(len(res)):
            fields = res[i]['fields']
            fields['id'] = res[i]['pk']
            rules_list.append(fields)
        nbpage=len(rules_from_db)/10
        # Renvoyer la liste des règles au format JSON
        return JsonResponse({"rules": rules_list,"nombrePageRules":math.ceil(nbpage)},status=200)


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
        # Analyse des données JSON de la requête POST
        data_list = request.data
        for data in data_list:
            # Récupération des données de la règle
            action=None if data.get('action', None) == "" else data.get('action', None)
            protocol=None if data.get('protocol', None) == "" else data.get('protocol', None)
            source_ip=None if data.get('source_ip', None) == "" else data.get('source_ip', None)
            direction=None if data.get('direction', None) == "" else data.get('direction', None)
            destination_ip=None if data.get('destination_ip', None) == "" else data.get('destination_ip', None)
            msg=None if data.get('msg', None) == "" else data.get('msg', None)
            rev=None if data.get('rev', None) == "" else data.get('rev', None)
            sid=None if data.get('sid', None) == "" else data.get('sid', None)
            activate_rule=None if data.get('activate_rule', None) == "" else data.get('activate_rule', None)
            # Recherche du fichier SuricataFile par ID
            try:
                suricatafile_obj = suricatafile.objects.get(id=id)
            except suricatafile.DoesNotExist:
                return Response({"message": "SuricataFile non trouvé"}, status=400)
            contenu = {
                    "action": action,
                    "protocol": protocol,
                    "source_ip": source_ip,
                    "direction": direction,
                    "destination_ip": destination_ip,
                    "msg": msg,
                    "rev": rev,
                    "sid": sid,
                    "activate_rule": activate_rule,
                    
                 }
            # Ajout de "#" selon la valeur de activate_rule
            if activate_rule:
                must_be_comment = False
            else:
                must_be_comment = True  # Ajouter "#" à la règle si activate_rule est False
            # Mise à jour de l'ID du fichier SuricataFile dans les données de la règle
            id_rule=None if data.get('id', None) == "" else data.get('id', None)
            # Appel de la fonction pour ajouter la règle dans le système Suricata
            if id_rule is None:
                data["default_rule"]=False
                if ids_ips_rule.objects.filter(sid=sid).exists():
                    message="Règle existe déjà "
                    status=400
                else:
                    output, rule,error = add_rule_remote(must_be_comment, contenu,file_path)
                    data['suricatafile'] = suricatafile_obj.id
                    data['rule']=rule
                    if error=="":
                        InboundSerializer = RuleIdsIpsSerializer(data=data)
                        if InboundSerializer.is_valid():
                            InboundSerializer.save()
                            message = "Règle ajoutée avec succès " + output
                            status=200
                        else:
                            message = InboundSerializer.errors
                            status=400
                        
            else:
                # Obtenir la ligne à supprimer en utilisant la fonction get_line_by_sid
                line_to_update = get_line_by_sid(file_path, sid)
                # Vérification des erreurs lors de la suppression de la ligne
                if line_to_update is not None:
                    # Ajouter la nouvelle règle dans le système distant en spécifiant si elle doit être activée ou désactivée
                    must_be_comment = not activate_rule  # Ajouter "#" à la règle si activate_rule est False
                    output, rule,error = update_rule_remote(must_be_comment,contenu,line_to_update,file_path)
                    # Vérification des erreurs lors de l'ajout de la nouvelle règle
                    if error == '':
                        # Mettre à jour la règle dans la base de données locale
                        ids_ips_rule_from_db = ids_ips_rule.objects.get(sid=sid)
                        ids_ips_rule_from_db.action = action
                        ids_ips_rule_from_db.protocol = protocol
                        ids_ips_rule_from_db.source_ip = source_ip
                        ids_ips_rule_from_db.direction = direction
                        ids_ips_rule_from_db.destination_ip = destination_ip
                        ids_ips_rule_from_db.msg = msg
                        ids_ips_rule_from_db.rev = rev
                        ids_ips_rule_from_db.activate_rule = activate_rule
                        ids_ips_rule_from_db.save()
                        message = "Mise à jour réussie!!"
                        status=200
                    else:
                        message = error
                        status=400
                else:
                    message="Règle non trouvée!!"
                    status=400
            list_msg.append({"message":message,"status":status,"sid":sid})
        # Retourne une réponse JSON avec le message de statut
    return Response({"message": list_msg})


@swagger_auto_schema(
    method='DELETE',
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO DELETE rule suricata with sid",
    operation_description="API TO DELETE rule suricata with sid",
)
#//supprimer une régle//
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def deleteRule(request, sid):
    if request.method == 'DELETE':
        try:
     # Vérification de l'existence de la règle avec le SID donné
            if ids_ips_rule.objects.filter(sid=sid).exists():
     # Récupération de la règle depuis la base de données
                rule = ids_ips_rule.objects.get(sid=sid)
                rule_text = rule.rule
                if rule.default_rule==False:
                    # Chemin du fichier à rechercher
                    file_path_to_search = "/var/lib/suricata/rules/suricata.rules"  # Replace with the actual path
                    sid_to_search = str(sid)  # Convert the rule's sid to string
                    # Obtention de la ligne à supprimer en utilisant la fonction get_line_by_sid
                    l = get_line_by_sid(file_path_to_search, sid_to_search)
                    if l is not None:
            # Suppression de la ligne dans le fichier distant en utilisant la fonction delete_line_in_remote_file
                        if delete_line_in_remote_file(file_path_to_search, l.rstrip()):
            # Suppression de la règle de la base de données
                            rule.delete()
                            message = "Rule deleted successfully!"
                            status=200
                        else:
                            message = "Failed to delete rule from remote file."
                            status=400
                    else:
                            message = "Failed to delete rule from remote file."
                            status=400
                else:
                    message="Vous n'avez pas le droit de supprimer une régle par défaut"
                    status=400
            else:
                message = "Rule not found."
                status=400
                
       # Retourne une réponse JSON avec le message de statut
            return JsonResponse({"message": message},status=status)
        except Exception as e:
            return JsonResponse({"error": str(e)},status=400)
        



#################################### Fin LES REGLES ############################################################



#################################### LES ALERTES  ############################################################

#Ajouter les alertes dans la BD//
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def addalertsToDatabase(request,id):
    if request.method=="POST":
        logs = read_suricata_log()
        alerts = Alert.objects.all()  # Récupérer toutes les alertes de la base de données
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
            
        if len(logs_add)!=0:
            # Parcourir les logs récupérés et ajoutez-les à la base de données
            for log in logs_add:
                # print("data to add ==>",log['alert'])
                suricatafile_obj = suricatafile.objects.get(pk=id)  
                log['suricatafile']=int(suricatafile_obj.id)
                if not Alert.objects.filter(alert=log['alert']).exists():
                    serializerAlert = AlertSerializer(data=log)
                    if serializerAlert.is_valid():
                        serializerAlert.save()
                    else:
                        return str(serializerAlert.errors)
                else:
                    pass
        elif len(logs_delete)!=0:
            for l in logs_delete:
                if Alert.objects.filter(alert=l).exists():
                    alert = Alert.objects.get(alert=l)
                    alert.delete()
                else:
                    return JsonResponse({"message": "Alert not found!!"},status=400)
        return JsonResponse({"message":"Alerts updated successfully!!"},status=200)           

    
#Afficher les alertes de la BD avec la pagination//
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def GetAlertsFromDatabase(request,num):
    if request.method == "GET":
        # Récupérer toutes les règles de la base de données
        alerts_from_db = Alert.objects.all() 

        # Paginer les règles
        paginator = Paginator(alerts_from_db, 10)
        try:
           alerts_page = paginator.page(num)
        except EmptyPage:
            return JsonResponse({"error": "Page not found"}, status=404)

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
        return JsonResponse({"alerts": alerts_list,"nombrePageAlerts":nbpage},status=200)
       
#################################### Fin LES ALERTES  ############################################################