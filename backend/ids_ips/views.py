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

#################################### LES REGLES ############################################################
#Ajouter les régles par défaut dans la BD//
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def addDefaultRulesToDatabase(request, id):
    if request.method=="POST":
        rules = get_suricata_default_rules()
        added_rule_ids = []  # Pour stocker les IDs des règles ajoutées avec succès
        # Recherche du fichier SuricataFile par ID
        try:
            suricatafile_obj = suricatafile.objects.get(pk=id)
        except suricatafile.DoesNotExist:
            return Response({"message": "SuricataFile non trouvé"}, status=400)
        # Parcourez les règles récupérées et ajoutez-les à la base de données
        for rule in rules:
            rule = rule.strip()  # Supprimez les espaces inutiles
            action=None
            protocol=None
            sid=None
            src_ip=None
            direction=None
            dest_ip=None
            msg=None
            content=None
            flowbit=None
            rev=None
            if rule.startswith("#") is True:
                active=False
                action=rule.split(" ")[0].strip()+rule.split(" ")[1]
                protocol=rule.split(" ")[2].strip()
            else:
                active=True
                action=rule.split(" ")[0].strip()
                protocol=rule.split(" ")[1].strip()
            if rule.find("sid")!=-1:
                rule_inter=rule[rule.find("sid:"):]
                sid=int(rule_inter[rule_inter.find("sid:")+len("sid:"):rule_inter.find(";")])
            if rule[1:].find("->")!=-1:
                src_ip=rule[rule.find(protocol)+len(protocol):rule.find("->")].strip()
                direction="->"
                dest_ip=rule[rule.find("->")+len("->"):rule.find("(msg")].strip()
            if rule.find("msg:")!=-1:
                msg=rule[rule.find("msg:")+len("msg:"): rule.find('";')].strip()
            if rule.find("content:")!=-1:
                rule_content=rule[rule.find("content:")+len("content:"):].strip()
                content=rule_content[:rule_content.find('";')]
            if rule.find("flowbit:")!=-1:
                flowbit=rule[rule.find("flowbit:")+len("flowbit:"): rule.find(";")].strip()
            if rule.find("rev:")!=-1:
                rev=rule[rule.find("rev:")+len("rev:"): rule.find(";sid")].strip(";")
                if rev.isdigit():
                    rev=int(rev)
                else:
                    rev=None
            action=action if action!="" else None    
            protocol=protocol if protocol!="" else None  
            src_ip=src_ip if src_ip!="" else None    
            direction=direction if direction!="" else None  
            dest_ip=dest_ip if dest_ip!="" else None    
            msg=msg if msg!="" else None  
            content=content if content!="" else None    
            protocol=protocol if protocol!="" else None  
            data = {
                "sid":sid,
                "action":action,
                "protocol":protocol,
                "source_ip":src_ip,
                "direction":direction,
                "destination_ip":dest_ip,
                "msg":msg,
                "content":content,
                "flowbit":flowbit,
                "rev":rev,
                "rule": rule,
                "suricatafile": suricatafile_obj.id,
                "activate_rule":active,
                "default_rule":True
                }
            if ids_ips_rule.objects.filter(sid=sid).exists():
                pass
            else:
                InboundSerializer = RuleIdsIpsSerializer(data=data)
                if InboundSerializer.is_valid():
                    InboundSerializer.save()
                    added_rule_ids.append(data)  # Ajoutez l'ID de la règle ajoutée à la liste
                else:
                    message = InboundSerializer.errors
                    pass
    return JsonResponse({"message": "Les règles par défaut ont été ajoutées.", "added_rule_ids": added_rule_ids})


#//Récupérer les règles de la base de données //
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def getRulesFromDatabase(request):
    if request.method=="GET":
        rules_list = []
        # Récupérer toutes les règles de la base de données
        rules_from_db = ids_ips_rule.objects.all()
        rule_suricata = serializers.serialize("json", rules_from_db)
        res = json.loads(rule_suricata)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            rules_list.append(res[i]['fields'])
    # Renvoyer la liste des règles au format JSON
    return JsonResponse({"rules": rules_list})

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
    file_path = '/var/lib/suricata/rules/suricataTest.rules'
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
            content=None if data.get('content', None) == "" else data.get('content', None)
            flowbit=None if data.get('flowbit', None) == "" else data.get('flowbit', None)
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
                    "content": content,
                    "flowbit": flowbit,
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
                    output, rule,error = add_rule_remote10(must_be_comment, contenu,file_path)
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
                        ids_ips_rule_from_db.content = content
                        ids_ips_rule_from_db.flowbit = flowbit
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
                    file_path_to_search = "/var/lib/suricata/rules/suricataTest.rules"  # Replace with the actual path
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
        
@swagger_auto_schema(
    method='PUT',
    request_body=RuleSerializerForSwagger(many=True),
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO update_status_rule suricata ",
    operation_description="API TO update_status_rule suricata ",
)
#Activer/Désactiver une régle//
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def update_status_rule(request, sid):
    file_path = '/var/lib/suricata/rules/suricataTest.rules'
    try:
        # Récupération de la valeur de l'activation de la règle à partir de la requête PUT
        data = request.data
        activate_rule = data.get('activate_rule', None)
        if request.method == 'PUT':
            # Récupérez l'objet depuis la base de données
            old_content = ids_ips_rule.objects.get(sid=sid)
            # Mettez à jour le champ 'activate_rule' de l'objet
            old_content.activate_rule = activate_rule
            # Enregistrez les modifications dans la base de données
            old_content.save()
            contenu = {
                sid: {
                    "action": old_content.action,
                    "protocol": old_content.protocol,
                    "source_ip": old_content.source_ip,
                    "direction": old_content.direction,
                    "destination_ip": old_content.destination_ip,
                    "msg": old_content.msg,
                    "content": old_content.content,
                    "flowbit": old_content.flowbit,
                    "rev": old_content.rev,
                    "sid": sid,
                    "activate_rule": activate_rule}}
            # Obtenir la ligne à supprimer en utilisant la fonction get_line_by_sid
            line_to_delete = get_line_by_sid(file_path, sid)
            error, output = delete_line_in_remote_file(file_path, line_to_delete.rstrip())
            # Déterminer s'il faut ajouter "#" à la règle en fonction de la valeur de activate_rule
            must_be_comment = not activate_rule
            error, output = add_rule_remote10(must_be_comment, contenu)
            if output == '':
                message = "Règle activée avec succès" if activate_rule else "Règle désactivée avec succès"
                status=200
            else:
                message = "Échec de la mise à jour de la règle sur le système distant."
                status=400
        else:
            message = "Le champ 'activate_rule' est requis."
            status=400
        return Response({"message": message},status=status)
    except ids_ips_rule.DoesNotExist:
        return Response({"message": "Règle non trouvée."}, status=404)

#################################### Fin LES REGLES ############################################################

#################################### SURICATA.YAML CONFIGURATION GENERALE ############################################################

#//Lire le fichier de configuration suricata.yaml
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def getSuricataFile(request):
    file = read_suricata_config() 
    return JsonResponse({"file:":file.split('\n')})     
  
#Modifier la status du suricata (enable/disable)  //  
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def update_suricata_status(request,id):
        try:
            data =request.data
            status_enabled = data.get('status_enabled', None)
            if status_enabled is not None:
                suricatafile_instance = suricatafile.objects.get(id=id)
                if status_enabled is True or status_enabled.lower() == 'true':
                   enable_command = "systemctl enable suricata.service"
                   execute_cmd(enable_command)
                   suricatafile_instance.status_enabled = True
                   suricatafile_instance.save()
                #    print("Suricata a été activé.")
                   return JsonResponse({'message': 'Suricata a été activé.'})
                elif status_enabled is False or status_enabled.lower() == 'false':
                    disable_command = "systemctl disable suricata.service"
                    execute_cmd(disable_command)
                    suricatafile_instance.status_enabled = False
                    suricatafile_instance.save()
                    return JsonResponse({'message': 'Suricata a été désactivé.'},status=200)
                else:
                    return JsonResponse({'message': 'Paramètre "status" invalide.'}, status=400)
            else:
                return JsonResponse({'message': 'Paramètre "status" manquant.'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Erreur de décodage JSON.'}, status=400)

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_suricata_status(request, id):
    try:
        suricatafile_instance = suricatafile.objects.get(id=id)
        # Exécutez une commande pour obtenir l'état de Suricata (activé ou désactivé)
        status_command = "systemctl is-enabled suricata.service"
        output, error = execute_cmd(status_command)
        final = output
        index = final.find('\n')
        if index != -1:
            result = final[:index]
        if result == 'enabled':
            status_enabled = True
            suricatafile_instance.status_enabled = True
            suricatafile_instance.save()
        else:
            status_enabled = False
            suricatafile_instance.status_enabled = False
            suricatafile_instance.save()
        return JsonResponse({'status_enabled': status_enabled})
    except suricatafile.DoesNotExist:
        return JsonResponse({'message': 'SuricataFile non trouvé.'}, status=404)
    except Exception as e:
        return JsonResponse({'message': f'Erreur : {str(e)}'}, status=500)

#Ajouter le fichier de configuration suricata.yaml dans la BD //      
@api_view(['POST'])
@permission_classes([AllowAny])
def addGeneralConfig(request):
    if request.method=="POST":
        file = read_config()
        if file:
            home_net = file.get("HOME_NET")
            promisc = file.get("promisc")
            if promisc is not None:
                promisc = promisc.lower() == "true"
            else:
                promisc = False
            syslog= file.get("syslog-enabled")
            eve_log= file.get("eve-log-enabled")
            mpm_algo = file.get("mpm-algo")
            profile = file.get("profile")
            copy_mode = file.get("copy-mode")
            status_command = "systemctl is-enabled suricata.service"
            output, error = execute_cmd(status_command)
            if output == 'enabled':
                status_enabled = True
            else:
                status_enabled = False
            # print({"HOME_NET": home_net,  "promisc": promisc, "eve_log_enabled": eve_log, "syslog-enabled": syslog, "mpm-algo": mpm_algo, "profile": profile,"copy-mode": copy_mode})
            if not suricatafile.objects.filter(home_net=home_net).exists():
                # Créer une instance du modèle suricatafile
                suricata_config = suricatafile(home_net=home_net, promisc=promisc, eve_log=eve_log, syslog=syslog, mpm_algo=mpm_algo, profile=profile,copy_mode=copy_mode,status_enabled=status_enabled)
                suricata_config.save()
                id_conf=suricata_config.id
            else:
                return JsonResponse({"message": "configuration déjà exist!"},status=400)
                
            return JsonResponse({"message": "Valeurs enregistrées avec succès dans la base de données.","id_conf":id_conf})
        else:
            return JsonResponse({"message": "Erreur lors de la lecture du fichier de configuration."})

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
            suricata_yaml_path = "/etc/suricata/suricataTest.yaml"
            data = request.data
            new_promisc = data.get("promisc", "false")
            new_promisc=str(new_promisc)
            if new_promisc is not None:
                new_promisc = new_promisc.lower() == "true"
            else:
                new_promisc = new_promisc.lower() == "false"
            new_eve_log = data.get("eve_log", False)
            new_eve_log = "yes" if new_eve_log else "no"
            new_syslog = data.get("syslog", False)
            new_syslog = "yes" if new_syslog else "no"
            new_mpm_algo = data.get("mpm_algo", "ac")
            new_profile = data.get("profile", "low")
            new_copy_mode = data.get("copy_mode", "none")
            interface_ids_input = data.get("interface", [])
            interface_ids=[]
            interface_ids = [x["id"] for x in interface_ids_input]
            allowed_profiles = ["medium", "high", "low"]
            allowed_ips = ["none", "tap", "ips"]
            allowed_mpm_algo = ["auto", "ac", "ac-bs", "ac-ks", "hs"]
            allowed_syslog = ["yes", "no"]
            allowed_evelog =["yes", "no"]
            status_enabled = data.get('status_enabled', None)
            if new_profile not in allowed_profiles:
                new_profile = "medium"
                return JsonResponse({"error": "La valeur du profil n'est pas valide. Utilisation de la valeur par défaut."},
                                        status=status.HTTP_400_BAD_REQUEST)
            if new_copy_mode is True:
                new_copy_mode="ips"
            else:
                new_copy_mode="tap"
            if new_mpm_algo not in allowed_mpm_algo:
                new_mpm_algo = "auto"
                return JsonResponse({"msg": "La valeur du mpm algo n'est pas valide. Utilisation de la valeur par défaut."},
                                        status=status.HTTP_400_BAD_REQUEST)
            if new_eve_log not in allowed_evelog:
                allowed_evelog = "yes"
                return JsonResponse({"msg": "La valeur du eve-log n'est pas valide. Utilisation de la valeur par défaut."},
                                        status=status.HTTP_400_BAD_REQUEST)
            if new_syslog not in allowed_syslog:
                allowed_syslog = "no"
                return JsonResponse({"msg": "La valeur du syslog n'est pas valide. Utilisation de la valeur par défaut."},
                                        status=status.HTTP_400_BAD_REQUEST)
            
            # Utilisez la fonction get_ip_addresses pour obtenir les adresses IP
            ip_addresses = get_ip_addresses(interface_ids)
            home_net_value = f'[{", ".join(ip_addresses)}]'
            output,error= execute_cmd("cat " + suricata_yaml_path)
            if output:
                lines = output.split('\n')
                updated_lines = []
                for line in lines:
                    stripped_line = line.strip()
                    if stripped_line.startswith("#"):
                        updated_lines.append(line + '\n')
                    elif "HOME_NET:" in stripped_line:
                        updated_lines.append(f'    HOME_NET: "{home_net_value}"' + '\n')
                    else:
                        updated_lines.append(line + '\n')
                with open(suricata_yaml_path, 'w') as local_file:
                    for string in updated_lines:
                        local_file.write(string)
                # Appelez d'abord la fonction update_suricata_config pour mettre à jour le système
                aux_update=update_suricata_config(status_enabled,str(new_promisc).lower(), new_eve_log, new_syslog, new_mpm_algo, new_profile, new_copy_mode)
                if aux_update is True:
                    # Ensuite, mettez à jour les enregistrements dans la base de données
                    suricata_instance = suricatafile.objects.get(id=id)
                    suricata_instance.status_enabled=status_enabled
                    suricata_instance.promisc = new_promisc
                    suricata_instance.eve_log = new_eve_log
                    suricata_instance.syslog = new_syslog
                    suricata_instance.mpm_algo = new_mpm_algo
                    suricata_instance.profile = new_profile
                    suricata_instance.copy_mode = new_copy_mode
                    suricata_instance.interface_ids = interface_ids
                    suricata_instance.home_net = home_net_value
                    suricata_instance.save()
                    return JsonResponse({'success': True, 'msg': 'Mise à jour du fichier réussie !!!'},status=200)
                else:
                    return JsonResponse({'success': False, 'msg': 'Lecture du fichier échouée.'}, status=500)
            
            else:
                return JsonResponse({'success': False, 'msg': 'Lecture du fichier échouée.'}, status=500)
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
        suricata_yaml_path = "/etc/suricata/suricataTest.yaml"
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

#################################### LES ALERTES  ############################################################

#Ajouter les alertes dans la BD//
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def addalertsToDatabase(request,id):
    if request.method=="POST":
        logs = read_suricata_log()
        if logs:
            added_logs = []  # Pour stocker les logs ajoutés avec succès en base de données
            # Parcourir les logs récupérés et ajoutez-les à la base de données
            for log in logs:
                if  suricatafile.objects.filter(pk=id).exists():
                    suricatafile_obj = suricatafile.objects.get(pk=id)  
                    log['suricatafile']=int(suricatafile_obj.id)
                    serializer = AlertSerializer(data=log)
                    if serializer.is_valid():
                        serializer.save()
                        added_logs.append(serializer.data)
                    else:
                        pass
                else:
                    return JsonResponse({"message": "Le fichier Suricata est non trouvé!"},status=400)
            return JsonResponse({"message": "Les alerts ont été ajoutées avec succès.", "added_logs": added_logs},status=200)
        else:
            return JsonResponse({"message": "Aucun log n'a été trouvé pour ajouter."},status=400)

#Afficher les alertes de la BD//
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def GetAlertsFromDatabase(request):
    if request.method=="GET":
        alert_list=[]
        alerts = alert.objects.all()  # Récupérer toutes les alertes de la base de données
        if alerts:
            serializer = AlertSerializer(alerts, many=True)
            alert_list=serializer.data
        return JsonResponse({"alerts": alert_list})
       
#################################### Fin LES ALERTES  ############################################################