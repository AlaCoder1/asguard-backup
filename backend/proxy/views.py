import os
import re
import subprocess
from django.db import IntegrityError
from django.http import  JsonResponse
import json
from .serializers import *
from backend.proxy.models import *
from django.core import serializers
from .function import *
from datetime import datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Schema, TYPE_BOOLEAN, TYPE_INTEGER, TYPE_OBJECT, TYPE_STRING, TYPE_ARRAY
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.authentication import SessionAuthentication
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
# Create your views here.

# Constants
CONSTANT_SQUID = _('Squid')
CONSTANT_PATTERN = _('Pattern')
CONSTANT_LINES = _("Lines")
CONSTANT_INTERFACE = _("interface")
CONSTANT_ADDRESS = _("Address")
CONSTANT_FILE = _("File")
CONSTANT_PATH = _("Path")
CONSTANT_PORT = _("Port")
CONSTANT_CORRECT_PATH = _("Please provide the correct")
CONSTANT_CRON_JOB = _("Cron job")
CONSTANT_USER = _("User")
CONSTANT_STATUS = _("Status")
CONSTANT_RULE = _("Rule")


# Success messages
SUCCESS_MESSAGES_UNBLOCKED= _("is Unblocked")
SUCCESS_MESSAGES_BLOCKED = _("is blocked")
SUCCESS_MESSAGES_INCOMMENTED= _("are Uncommented")
SUCCESS_MESSAGES_COMMENTED = _("are Commented")
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
SUCCESS_MESSAGES_STARTING = _("is started")
SUCCESS_MESSAGES_RESTARTING = _("is restarted")
SUCCESS_MESSAGES_STOPING = _("is stoped")
SUCCESS_MESSAGES_CHANGE_STATUS = _("is changed")
# Error messages
ERROR_MESSAGES_STARTING = _("System error in starting")
ERROR_MESSAGES_RESTARTING = _("System error in restarting")
ERROR_MESSAGES_STOPING = _("System error in stoping")
ERROR_MESSAGES_OCCURRED = _("Error Occurred")
ERROR_MESSAGES_NOTFOUND_INPATH = _("Not Found in")
ERROR_MESSAGES_SAVING_INSTANCE = _("Error in saving instance")
ERROR_MESSAGES_SAVING_USER = _("Error in adding user")
ERROR_MESSAGES_INEXISTANT = _("does not exist")


########################################
################ proxy ################
########################################




def run_command(command):
    """
    Executes a shell command and captures its output and error messages.

    Args:
        command (str): The shell command to execute.

    Returns:
        tuple: A tuple containing:
            - output (str): The standard output of the command.
            - error (str): The standard error of the command.
    """
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error


@swagger_auto_schema(
    method='POST',
    operation_summary="Restart Squid Service and Update Server Status",
    operation_description=(
        "This API endpoint restarts the Squid service on the server and updates the server's "
        "status in the database. If the restart is successful, the server status is marked as inactive."
    ),
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Success message indicating that the Squid service was restarted successfully.",
                    example="Squid service restarted successfully."
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message indicating that the Squid service failed to restart.",
                    example="Error restarting Squid service."
                ),
            }
        ),
    },
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def restart(request):
    """
    Restarts the Squid service and updates the server status in the database.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing a success or error message.
                      - HTTP 200 if the restart is successful.
                      - HTTP 400 if the restart fails.
    
    Side Effects:
        - Executes the 'sudo systemctl restart squid' command.
        - Updates the `ServerSatus` model to mark the server as inactive if the restart succeeds.
    """
    process = subprocess.run(['sudo','systemctl', 'restart', 'squid'], capture_output=True, text=True)
    if process.returncode == 0:
        server_satus = ServerSatus.objects.get(id=1)
        server_satus.status_server = False
        server_satus.save()
        msg = f"{CONSTANT_SQUID} {SUCCESS_MESSAGES_RESTARTING}"
        status = 200
    else:
        msg = f"{ERROR_MESSAGES_RESTARTING} {CONSTANT_SQUID}"
        status =400 
    return JsonResponse({"msg": msg}, status=status)

@swagger_auto_schema(
    method='POST',
    operation_summary="Start Squid Service",
    operation_description=(
        "This API starts the Squid service and returns a success or failure message. "
        "It attempts to execute the 'sudo systemctl start squid' command and reports the result."
    ),
    responses={
        200: "Squid service started successfully.",
        400: "Failed to start the Squid service.",
    },
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def start(request):
    """
    Starts the Squid service and returns a JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing a success or error message.
                      - HTTP 200 if the start command is successful.
                      - HTTP 400 if the start command fails.
    
    Side Effects:
        - Executes the 'sudo systemctl start squid' command.
    """
    process = subprocess.run(['sudo','systemctl', 'start', 'squid'], capture_output=True, text=True)
    if process.returncode == 0:
        msg = f"{CONSTANT_SQUID} {SUCCESS_MESSAGES_STARTING}"
        status = 200
    else:
        msg = f"{ERROR_MESSAGES_STARTING} {CONSTANT_SQUID}"
        status =400
    return JsonResponse({"msg": msg}, status=status)

@swagger_auto_schema(
    method='POST',
    operation_summary="Stop Squid Service",
    operation_description=(
        "This API stops the Squid service and returns a success or failure message. "
        "It attempts to execute the 'sudo systemctl stop squid' command and reports the result."
    ),
    responses={
        200: "Squid service stopped successfully.",
        400: "Failed to stop the Squid service.",
    },
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def stop(request):
    """
    Stops the Squid service and returns a JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing a success or error message.
                      - HTTP 200 if the stop command is successful.
                      - HTTP 400 if the stop command fails.
    
    Side Effects:
        - Executes the 'sudo systemctl stop squid' command.
    """
    process = subprocess.run(['sudo','systemctl', 'stop', 'squid'], capture_output=True, text=True)
    if process.returncode == 0:
        msg = f"{CONSTANT_SQUID} {SUCCESS_MESSAGES_STOPING}"
        status = 200
    else:
        msg = f"{ERROR_MESSAGES_STOPING} {CONSTANT_SQUID}"
        status =400
    return JsonResponse({"msg": msg}, status=status)

@swagger_auto_schema(
    method='GET',
    operation_summary="Retrieve All Proxy Rules",
    operation_description=(
        "This API retrieves all proxy rules stored in the database, formats the data, and returns it "
        "as a JSON response containing a list of proxy rules with relevant fields."
    ),
    responses={
        200: "Successfully retrieved the list of all proxy rules.",
        400: "Failed to retrieve proxy rules.",
    },
)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def allRuleSquid(request):
    """
    Retrieves all proxy rules from the database, formats the data, and returns it as a JSON response.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing a list of proxy rules in the format:
                      {
                          "data": [
                              {
                                  "id": <rule_id>,
                                  <other_fields>
                              },
                              ...
                          ]
                      }
    
    Side Effects:
        - Queries the `ProxyRules` model to fetch all records.
        - Serializes and processes the data before returning it.
    """
    list_proxyRules =[]
    data = ProxyRules.objects.all()
    proxyRulesDict = serializers.serialize("json", data)
    res = json.loads(proxyRulesDict)
    for i in range(0, len(res)):
        res[i].pop('model')
        id = res[i]['pk']
        res[i].pop('pk')
        res[i]['fields']['id'] = id
        list_proxyRules.append(res[i]['fields'])
    return JsonResponse({"data":list_proxyRules})


def add_line_after_pattern(file_path, pattern, new_line):
    """
    Inserts a new line in a file immediately after the first occurrence of a given pattern.

    Args:
        file_path (str): The path to the file where the modification will be made.
        pattern (str): The pattern to search for in the file.
        new_line (str): The line to insert after the first occurrence of the pattern.

    Side Effects:
        - Reads the content of the specified file.
        - Modifies the file by inserting the new line if the pattern is found.
        - Prints an error message if the pattern is not found in the file.

    Notes:
        - The function stops searching after the first occurrence of the pattern.
        - The `new_line` should include a newline character (`\n`) if needed.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    found = False
    for i, line in enumerate(lines):
        if pattern in line:
            found = True
            lines.insert(i + 1, new_line)
            break

    if not found:
        print(f"{CONSTANT_PATTERN} {pattern} {ERROR_MESSAGES_NOTFOUND_INPATH} {CONSTANT_FILE}")

    with open(file_path, 'w') as file:
        file.writelines(lines)


def enable_by_time():
    """
    Enables time-based blocking rules in the Squid configuration by uncommenting a specific line.

    Side Effects:
        - Reads and modifies the Squid configuration file (`/etc/squid/squid.conf`).
        - Removes the `#` character from the line containing `http_access deny blocked_domain_by_time time_block`.
        - Saves the modified configuration back to the file.

    Returns:
        JsonResponse: A JSON response indicating success.
                      - HTTP 200 if the modification is successful.

    Notes:
        - This function assumes that the configuration file is accessible and writable.
        - A Squid service restart may be required for changes to take effect.
    """
    config_file_path = '/etc/squid/squid.conf'
    with open(config_file_path, 'r') as file:
        config_lines = file.readlines()

    # Uncomment the desired lines
    for i, line in enumerate(config_lines):
        if line.strip().startswith('#http_access deny blocked_domain_by_time time_block') :
            config_lines[i] = line.replace('#', '')

    # Write the changes back to the file
    with open(config_file_path, 'w') as file:
        file.writelines(config_lines)

    return JsonResponse({"msg":f"{CONSTANT_LINES} {SUCCESS_MESSAGES_INCOMMENTED}"}, status=200)

@swagger_auto_schema(
    method='POST',
    operation_summary="Add Blocking or Allowing Rule to Squid Configuration",
    operation_description=(
        "This API endpoint adds a blocking or allowing rule to the Squid configuration based on "
        "the provided request data. It determines the appropriate file path based on the rule type (IP, domain, or subnet), "
        "and if time-based restrictions are provided, it applies them in the Squid configuration. "
        "The rule is then saved in the database and the server status is updated."
    ),
    request_body=Schema(
        type=TYPE_OBJECT,
        required=['allow_by_auth', 'type', 'value', 'status'],
        properties={
            'rule_name': Schema(
                type=TYPE_STRING,
                description="The rule name.",
            ),
            'allow_by_auth': Schema(
                type=TYPE_BOOLEAN,
                description="Indicates whether the rule applies to authenticated users.",
                example=True
            ),
            'type': Schema(
                type=TYPE_STRING,
                description="The rule type (e.g., 'ip', 'domain', 'subnet').",
                enum=["ip", "domain", "subnet"],
                example="ip"
            ),
            'value': Schema(
                type=TYPE_STRING,
                description="The IP, domain, or subnet to be blocked or allowed.",
                example="192.168.1.100"
            ),
            'status': Schema(
                type=TYPE_BOOLEAN,
                description="Whether the rule is enabled or disabled.",
                example=True
            ),
            'time_from': Schema(
                type=TYPE_STRING,
                description="Start time for blocking (optional, required for time-based rules).",
                example="08:00"
            ),
            'time_to': Schema(
                type=TYPE_STRING,
                description="End time for blocking (optional, required for time-based rules).",
                example="18:00"
            ),
            'days': Schema(
                type=TYPE_STRING,
                description="Days when the time-based rule applies (optional).",
                example="Monday,Tuesday,Wednesday"
            ),
        },
    ),
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Success message indicating that the rule was successfully added.",
                    example="ip 192.168.1.100 blocked successfully."
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message indicating validation or other issues.",
                    example="Validation error: Invalid IP address format."
                ),
            }
        ),
    },
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def addRuleSquid(request):
    """
    Adds a blocking or allowing rule to Squid configuration based on the provided request data.

    Functionality:
        - Determines the appropriate file path based on rule type (IP, domain, or subnet).
        - If time-based restrictions are provided (`time_from` and `time_to`), updates `squid.conf` to apply time-based access rules.
        - If `allow_by_auth` is `False`, the rule is added to the corresponding blocked list.
        - If `allow_by_auth` is `True`, the rule is added to the allowed list.
        - Saves the rule in the database using the appropriate serializer.
        - Updates the server status when a rule is added.

    Parameters:
        request (HttpRequest): The HTTP request containing rule data (expected to be a POST request with JSON data).

    Request Data:
        - `rule_name` (str): The rule name.
        - `allow_by_auth` (bool): Whether the rule applies to authenticated users.
        - `type` (str): The rule type (`"ip"`, `"domain"`, or `"subnet"`).
        - `value` (str): The IP, domain, or subnet to be blocked/allowed.
        - `status` (bool): Whether the rule is enabled (`True`) or disabled (`False`).
        - `time_from` (str, optional): Start time for blocking (if applicable).
        - `time_to` (str, optional): End time for blocking (if applicable).
        - `days` (str, optional): Days when the time-based rule applies.

    Side Effects:
        - Modifies Squid ACL files (e.g., `/etc/squid/blocked_ip.acl`, `/etc/squid/blocked_domain.acl`).
        - If a time-based rule is added, modifies `/etc/squid/squid.conf`.
        - Saves rule details in the database.

    Returns:
        JsonResponse:
            - HTTP 200 if the rule is successfully added.
            - HTTP 400 if there are validation errors or an exception occurs.

    Notes:
        - The function assumes appropriate permissions to modify Squid configuration files.
        - A restart of Squid may be required for changes to take effect.
    """
    msg = ''
    if (request.method == 'POST'):
        data = request.data
        write_in_file = True
        if data['type'] not in ['ip','domain','subnet']:
            return JsonResponse({"error": 'type must be ip, domain or subnet'}, status=400)
        else:
            if data['allow_by_auth'] == False:
                if data['type'] == "ip":
                    file_path = '/etc/squid/blocked_ip.acl'
                elif data['type'] == "domain":
                    if data['time_from'] != '':
                    # if time_from != '' or time_to !='':
                        squid_path = '/etc/squid/squid.conf'
                        name_rule = 'block_'+data['value']
                        time_block_rule = 'time_'+name_rule
                        line1='acl '+name_rule+' url_regex '+data['value']+'\n'
                        add_line_after_pattern(squid_path,'acl localnet src fe80::/10',line1)
                        line2='acl '+time_block_rule+' time '+data['days']+' '+data['time_from']+'-'+data['time_to']+'\n'
                        # line1='acl '+data['value']+' time '+data['days']+' '+data['time_from']+'-'+data['time_to']+'\n'
                        add_line_after_pattern(squid_path,line1,line2)
                        line3='\nhttp_access deny '+name_rule+' '+time_block_rule+'\n'
                        add_line_after_pattern(squid_path,line2,line3)
                        write_in_file = False
                        # line+='acl time_block time '+data['days']+' '+data['time_from']+'-'+data['time_to']
                        # add_line_after_pattern(file_path,'acl localnet src fe80::/10',line)
                        # enable_by_time()
                    else:
                        file_path = '/etc/squid/blocked_domain.acl'
                else:
                    file_path = '/etc/squid/blocked_subnet.acl'
            else:
                if data['type'] == "ip":
                    file_path = '/etc/squid/allowed_ip_by_auth.acl'
                elif data['type'] == "domain":
                    file_path = '/etc/squid/allowed_domain_by_auth.acl'
                else:
                    file_path = '/etc/squid/allowed_subnet_by_auth.acl'
            # file_path = file_selected(data['allow_by_auth'],data['type'])
            if  data['status'] == False:
                value = '#'+data['value']
            else:
                value = data['value']
            if write_in_file == True:
                try:
                    with open(file_path, 'a') as file:
                        file.write(value + '\n')
                    serializerProxyRules = ProxyRulesSerializer(data=data)
                    if (serializerProxyRules.is_valid()):
                        serializerProxyRules.save()
                        server_satus = ServerSatus.objects.get(id=1)
                        server_satus.status_server = True
                        server_satus.save()
                        msg = f"{data['type']} {SUCCESS_MESSAGES_BLOCKED}"
                        return JsonResponse({"msg": msg}, status=200)
                    else:
                        return JsonResponse(serializerProxyRules.errors, status=400 )
                except Exception as e:
                    return JsonResponse({"error": e}, status=400)
            else:
                serializerProxyRules = ProxyRulesByTimeSerializer(data=data)
                if (serializerProxyRules.is_valid()):
                    serializerProxyRules.save()
                    msg = f"{data['type']} {SUCCESS_MESSAGES_BLOCKED}"
                    return JsonResponse({"msg": msg}, status=200)
                else:
                    return JsonResponse(serializerProxyRules.errors, status=400 )

@swagger_auto_schema(
    method='DELETE',
    operation_summary="Delete a Squid Rule",
    operation_description=(
        "This API deletes a specific Squid rule based on its ID, and updates the relevant configuration files. "
        "If the rule involves a time-based restriction on a domain, it modifies `squid.conf`. Otherwise, it updates "
        "the relevant ACL file (e.g., `blocked_ip.acl`, `blocked_domain.acl`, etc.). After deletion, the server status is updated."
    ),
    responses={
        200: "Squid rule deleted successfully and configuration updated.",
        400: "Failed to delete the Squid rule or update the configuration.",
    },
) 
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def deleteRuleSquid(request,id):
    """
    Supprime une règle Squid en fonction de son ID et met à jour les fichiers de configuration correspondants.

    Cette fonction supprime une règle spécifique de Squid en fonction de son type (`ip`, `domain`, `subnet`) 
    et de son statut (`allow_by_auth`). Elle met à jour les fichiers de règles et, si nécessaire, 
    modifie `squid.conf` pour les domaines avec restrictions de temps.

    Args:
        request (HttpRequest): Requête HTTP envoyée par l'utilisateur.
        id (int): Identifiant de la règle à supprimer.

    Returns:
        JsonResponse: Réponse JSON indiquant le succès ou l'échec de la suppression.
    
    Fonctionnement :
    - Récupère la règle à supprimer depuis la base de données.
    - Détermine le fichier à modifier en fonction du type et du statut de la règle.
    - Si la règle est une restriction temporelle sur un domaine, elle est supprimée de `squid.conf` via `sed`.
    - Sinon, la règle est supprimée du fichier ACL concerné (`blocked_ip.acl`, `blocked_domain.acl`, etc.).
    - Après suppression, met à jour le statut du serveur si nécessaire.
    - Retourne une réponse JSON avec un message de succès ou d'erreur.

    Exceptions possibles :
    - `ProxyRules.DoesNotExist`: Lève une erreur si la règle n'existe pas.
    - Problèmes liés à l'accès ou l'écriture dans les fichiers système.
    """
    msg=''
    data = ProxyRules.objects.get(id=id)
    if data.allow_by_auth == False:
        if data.type == "ip":
            file_path = '/etc/squid/blocked_ip.acl'
        elif data.type == "domain":
            if data.time_from != None:
                squid_path = '/etc/squid/squid.conf'
                command = "sed -i '/"+data.value+"/d' "+squid_path
                stdout, stderr = run_command(command)
                if stderr =="":
                    data.delete()
                    server_satus = ServerSatus.objects.get(id=1)
                    server_satus.status_server = True
                    server_satus.save()
                    msg = f"{data.type} {CONSTANT_ADDRESS} {data.value} {SUCCESS_MESSAGES_UNBLOCKED}"
                    status =200
                    return JsonResponse({"msg": msg}, status=status)
                else:
                    msg =stderr
                    status = 400 
                return JsonResponse({"msg": msg}, status=status)
            else:
                file_path = '/etc/squid/blocked_domain.acl'
        else:
            file_path = '/etc/squid/blocked_subnet.acl'
    else:
        if data.type == "ip":
            file_path = '/etc/squid/allowed_ip_by_auth.acl'
        elif data.type == "domain":
            file_path = '/etc/squid/allowed_domain_by_auth.acl'
        else:
            file_path = '/etc/squid/allowed_subnet_by_auth.acl'
    # file_path = file_selected(data.allow_by_auth, data.type)
    new_content = []
    command = "cat " + file_path
    stdout, stderr = run_command(command)
    resultat = stdout.split('\n')
    resultat = [line.strip() for line in resultat if line.strip()]
    lignes = [ligne for ligne in resultat if ligne.strip() != data.value]
    for line in resultat:
        if line.strip('#') != data.value :
            new_content.append(line)
    text = '\n'.join(new_content)
    command = "echo '" + text + "' > " + file_path  
    stdout, stderr = run_command(command)
    if(stderr == ""):
        data.delete()
        msg = f"{data.type} {CONSTANT_ADDRESS} {data.value} {SUCCESS_MESSAGES_UNBLOCKED}"
        status =200
    else:
        msg =stderr
        status = 400 
    return JsonResponse({"msg": msg}, status=status)

def get_squid_status():
    """
    Récupère le statut actuel du service Squid en utilisant la commande systemctl.

    Cette fonction exécute la commande `systemctl status squid.service` pour obtenir 
    des informations sur l'état du service Squid. Elle extrait ensuite la ligne contenant
    l'état actif du service et retourne le statut sous forme de chaîne de caractères.

    Returns:
        str or None: Le statut du service Squid (par exemple, "active", "inactive").
                      Retourne `None` en cas d'erreur d'exécution de la commande.

    Exceptions possibles:
        subprocess.CalledProcessError: Lève une exception si la commande `systemctl` échoue.
    
    Exemple d'utilisation :
        status = get_squid_status()
        print(status)  # Affiche le statut du service Squid, comme "active" ou "inactive".
    """
    try:
        result = subprocess.run(['systemctl', 'status', 'squid.service'], capture_output=True, text=True, check=True)
        for line in result.stdout.split('\n'):
            if 'Active:' in line:
                status = line.split(':')[1].strip()
                return status
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None

@swagger_auto_schema(
    method='GET',
    operation_summary="Get general Squid service information",
    operation_description=(
        "This API retrieves general information about the Squid service, including the service port and its status. "
        "It reads the Squid configuration file (`/etc/squid/squid.conf`) to extract the configured port, and then checks "
        "if the Squid service is running by using `get_squid_status`."
    ),
    responses={
        200: "Successfully retrieved Squid service information.",
        500: "Failed to retrieve Squid service information.",
    },
) 
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_generale_info(request):
    """
    Récupère les informations générales concernant le service Squid, y compris le port de service et son statut.

    Cette fonction lit le fichier de configuration Squid (`/etc/squid/squid.conf`) pour extraire
    le port sur lequel le service écoute. Elle utilise ensuite la fonction `get_squid_status` 
    pour vérifier si le service Squid est en cours d'exécution et renvoie les informations sous forme de JSON.

    Args:
        request: L'objet de requête HTTP. Non utilisé dans cette fonction, mais nécessaire pour le traitement 
                 de la vue dans Django.

    Returns:
        JsonResponse: Un objet JSON contenant le port sur lequel Squid écoute et le statut du service Squid.
                      Exemple de retour : {"Port": "3128", "status": True} si le service est actif.
    
    Exemple d'utilisation :
        Lorsque la fonction est appelée via une requête HTTP, elle renvoie une réponse JSON contenant :
        - Le port configuré dans Squid (par exemple, "3128").
        - Le statut du service Squid (True si actif, False sinon).
    """
    squid_conf_path = '/etc/squid/squid.conf'
    command = "cat "+squid_conf_path
    stdout, stderr = run_command(command)
    resultat=stdout.split('\n')
    for line in resultat:
        line = line.strip()
        if line.startswith('http_port'):
            parts = line.split()
            if len(parts) >= 2:
                port = parts[1].split(':')[0]
                
    squid_status = get_squid_status()
    if squid_status:
        if 'active' in squid_status:
            return JsonResponse({"Port":port,"status":True})
    else:
        return JsonResponse({"Port":port,"status":False})

@swagger_auto_schema(
    method='PUT',
    operation_summary="Update Squid service port",
    operation_description=(
        "This API updates the Squid service's listening port in the configuration file (`/etc/squid/squid.conf`). "
        "It accepts a POST request with a JSON body containing a 'port' field, which represents the new port number. "
        "The Squid configuration file is updated, and the server status is marked as active."
    ),
    request_body=Schema(
        type=TYPE_OBJECT,
        required=['port'],
        properties={
            'port': Schema(
                type=TYPE_STRING,
                description="The new port for Squid service",
                example="3128"
            ),
        }
    ),
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Success message indicating that the Squid service port was updated.",
                    example="Port 3128 updated successfully."
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message indicating that the 'port' field is missing or invalid.",
                    example="Port is required."
                ),
            }
        ),
        500: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message indicating failure during Squid configuration update or server status update.",
                    example="Failed to update Squid configuration or server status."
                ),
            }
        ),
    }
)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def update_generale_info(request):
    """
    Met à jour le port d'écoute de Squid dans le fichier de configuration (`/etc/squid/squid.conf`).

    Cette fonction prend une requête HTTP contenant un nouveau port pour le service Squid, 
    met à jour le fichier de configuration pour refléter ce changement et enregistre cette 
    modification. Après la mise à jour, elle marque le statut du serveur comme actif dans la base de données.

    Args:
        request (HttpRequest): L'objet de la requête HTTP contenant les données sous forme de JSON. 
                                Le JSON doit inclure un champ 'port' avec le nouveau numéro de port pour Squid.

    Returns:
        JsonResponse: Un objet JSON indiquant que le port a été mis à jour avec succès.
                      Exemple de réponse : {"msg": "Port 3128 updated successfully"}.

    Exemple d'utilisation :
        Lorsqu'une requête POST est envoyée avec un corps JSON contenant le champ 'port', 
        le port d'écoute de Squid est mis à jour dans la configuration et le statut du serveur est marqué comme actif.
    """
    data = request.data
    squid_conf_path = '/etc/squid/squid.conf'
    with open(squid_conf_path, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.strip().startswith('http_port'):
            lines[i] = 'http_port '+ data['port']+'\n'
            break
        
    with open(squid_conf_path, 'w') as f:
        f.writelines(lines)
    server_satus = ServerSatus.objects.get(id=1)
    server_satus.status_server = True
    server_satus.save() 
    return JsonResponse({"msg":f"{CONSTANT_PORT} {SUCCESS_MESSAGES_UPDATING}"},status=200)

@swagger_auto_schema(
    method='POST',
    operation_summary="Disable Authentication for Squid Rules",
    operation_description=(
        "This API endpoint disables authentication for certain rules in the Squid configuration file (`/etc/squid/squid.conf`). "
        "It comments out specific lines in the Squid configuration, effectively disabling authentication for the "
        "defined subnets, IPs, and domains without deleting the configuration. The lines to be commented out are: "
        "- `http_access allow allowed_subnet_by_auth authenticated_users`, "
        "- `http_access allow allowed_ip_by_auth authenticated_users`, "
        "- `http_access allow allowed_domain_by_auth authenticated_users`."
    ),
    request_body=None,  # No specific request body for this endpoint
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Success message indicating that the lines were commented successfully.",
                    example="Lines commented successfully."
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message indicating that the Squid configuration file was not found.",
                    example="File not found at the specified path."
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message indicating that an error occurred during the operation.",
                    example="An error occurred while disabling authentication for Squid rules."
                ),
            }
        ),
    }
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def disable_auth(request):
    """
    Désactive l'authentification pour certaines règles dans le fichier de configuration Squid (`/etc/squid/squid.conf`).

    Cette fonction commente certaines lignes d'accès dans la configuration de Squid pour désactiver l'authentification 
    pour les sous-réseaux, IP et domaines spécifiés. Elle ajoute un caractère '#' au début des lignes pertinentes, 
    les désactivant ainsi sans les supprimer.

    Args:
        request (HttpRequest): L'objet de la requête HTTP. Aucun argument spécifique n'est attendu dans le corps de la requête.

    Returns:
        JsonResponse: Un objet JSON contenant un message de confirmation indiquant que les lignes ont été commentées avec succès.

    Raises:
        FileNotFoundError: Si le fichier de configuration de Squid n'est pas trouvé à l'emplacement spécifié.
        Exception: Si une erreur générale se produit lors de la lecture ou de l'écriture du fichier.

    Exemple d'utilisation :
        Lorsque cette fonction est appelée, elle commente les lignes suivantes dans le fichier `squid.conf` :
            - `http_access allow allowed_subnet_by_auth authenticated_users`
            - `http_access allow allowed_ip_by_auth authenticated_users`
            - `http_access allow allowed_domain_by_auth authenticated_users`

        Cela empêche l'accès basé sur l'authentification pour les sous-réseaux, IP et domaines spécifiés dans ces lignes.
    """
    config_file_path = '/etc/squid/squid.conf'
    lines_to_comment = [
    'http_access allow allowed_subnet_by_auth authenticated_users',
    'http_access allow allowed_ip_by_auth authenticated_users',
    'http_access allow allowed_domain_by_auth authenticated_users',
    ]

    try:
        with open(config_file_path, 'r') as file:
            lines = file.readlines()

        with open(config_file_path, 'w') as file:
            for line in lines:
                if any(line.strip() == comment_line for comment_line in lines_to_comment):
                    file.write('#' + line)  # Comment out the line by adding a '#' at the beginning
                else:
                    file.write(line)

        return JsonResponse({"msg":f"{CONSTANT_LINES} {SUCCESS_MESSAGES_COMMENTED}"}, status=200)
    
    except FileNotFoundError:
        return JsonResponse({"msg": f"{CONSTANT_FILE} {ERROR_MESSAGES_NOTFOUND_INPATH} {CONSTANT_PATH} {config_file_path}.{CONSTANT_CORRECT_PATH}"}, status=400 )
    except Exception as e:
        return JsonResponse({"msg": f"{ERROR_MESSAGES_OCCURRED}: {e}"}, status=400 )

@swagger_auto_schema(
    method='POST',
    operation_summary="Change Authentication Status in Squid Configuration",
    operation_description=(
        "This API endpoint enables or disables authentication in the Squid configuration file (`/etc/squid/squid.conf`) "
        "based on the `status` field in the request. If `status` is `True`, it comments out specific lines to disable "
        "authentication; if `status` is `False`, it removes the comments to reactivate authentication. The following "
        "lines in the Squid configuration are affected: "
        "- `http_access allow allowed_subnet_by_auth authenticated_users`, "
        "- `http_access allow allowed_ip_by_auth authenticated_users`, "
        "- `http_access allow allowed_domain_by_auth authenticated_users`."
    ),
    request_body=Schema(
        type=TYPE_OBJECT,
        required=['status'],
        properties={
            'status': Schema(
                type=TYPE_BOOLEAN,
                description="The desired authentication status. If `True`, authentication is disabled (lines are commented out). "
                            "If `False`, authentication is re-enabled (lines are uncommented).",
                example=True
            ),
        },
    ),
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Success message indicating whether the lines were commented or uncommented successfully.",
                    example="Lines commented successfully."
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message indicating that the Squid configuration file was not found.",
                    example="File not found at the specified path."
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message indicating that an error occurred during the operation.",
                    example="An error occurred while changing the authentication status."
                ),
            }
        ),
    }
)
  
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def change_auth_status(request):
    """
    Change l'état de l'authentification dans le fichier de configuration de Squid (`/etc/squid/squid.conf`).

    Cette fonction active ou désactive l'authentification en fonction du statut passé dans la requête. 
    Si le statut est `True`, elle commente certaines lignes pour désactiver l'authentification, sinon, elle décommente ces lignes pour la réactiver.

    Args:
        request (HttpRequest): L'objet de la requête HTTP, qui doit contenir un champ `status` dans son corps. 
                                Si `status` est `True`, l'authentification est désactivée (lignes commentées), 
                                sinon, l'authentification est réactivée (lignes décommentées).

    Returns:
        JsonResponse: Un objet JSON contenant un message de confirmation indiquant si les lignes ont été commentées ou décommentées avec succès.

    Raises:
        FileNotFoundError: Si le fichier de configuration de Squid n'est pas trouvé à l'emplacement spécifié.
        Exception: Si une erreur générale se produit lors de la lecture ou de l'écriture du fichier.

    Exemple d'utilisation :
        Si le `status` passé est `True`, la fonction commente les lignes suivantes dans le fichier `squid.conf` :
            - `http_access allow allowed_subnet_by_auth authenticated_users`
            - `http_access allow allowed_ip_by_auth authenticated_users`
            - `http_access allow allowed_domain_by_auth authenticated_users`
        Cela désactive l'authentification pour ces règles spécifiques.

        Si `status` est `False`, la fonction réactive l'authentification en décommentant ces lignes.
    """
    config_file_path = '/etc/squid/squid.conf'
    data = request.data
    if data['status'] ==True:
        lines_to_comment = [
        'http_access allow allowed_subnet_by_auth authenticated_users',
        'http_access allow allowed_ip_by_auth authenticated_users',
        'http_access allow allowed_domain_by_auth authenticated_users',
        ]
        try:
            with open(config_file_path, 'r') as file:
                lines = file.readlines()

            with open(config_file_path, 'w') as file:
                for line in lines:
                    if any(line.strip() == comment_line for comment_line in lines_to_comment):
                        file.write('#' + line)  
                    else:
                        file.write(line)
            server_satus = ServerSatus.objects.get(id=1)
            server_satus.status_server = True
            server_satus.save() 
            return JsonResponse({"msg":f"{CONSTANT_LINES} {SUCCESS_MESSAGES_COMMENTED}"}, status=200)
        except FileNotFoundError:
            print(f"Error: File not found at path {config_file_path}. Please provide the correct path.")
            return JsonResponse({"msg": f"{CONSTANT_FILE} {ERROR_MESSAGES_NOTFOUND_INPATH} {CONSTANT_PATH} {config_file_path}.{CONSTANT_CORRECT_PATH}"}, status=400 )
        except Exception as e:
            print(f"An error occurred: {e}")
            return JsonResponse({"msg": f"{ERROR_MESSAGES_OCCURRED}: {e}"}, status=400 )
    else:
        with open(config_file_path, 'r') as file:
            config_lines = file.readlines()

        for i, line in enumerate(config_lines):
            if line.strip().startswith('#http_access allow allowed_subnet_by_auth authenticated_users') or \
            line.strip().startswith('#http_access allow allowed_ip_by_auth authenticated_users') or \
            line.strip().startswith('#http_access allow allowed_domain_by_auth authenticated_users'):
                config_lines[i] = line.replace('#', '')

        with open(config_file_path, 'w') as file:
            file.writelines(config_lines)
        server_satus = ServerSatus.objects.get(id=1)
        server_satus.status = True
        server_satus.save() 
        return JsonResponse({"msg": f"{CONSTANT_LINES} {SUCCESS_MESSAGES_INCOMMENTED}"}, status=200)

@swagger_auto_schema(
    method='POST',
    operation_summary="Enable Authentication in Squid Configuration",
    operation_description=(
        "This API endpoint enables authentication in the Squid configuration file (`/etc/squid/squid.conf`) "
        "by uncommenting specific lines to allow access for authorized subnets, IPs, and domains. The following "
        "lines in the Squid configuration are uncommented to activate authentication: "
        "- `http_access allow allowed_subnet_by_auth authenticated_users`, "
        "- `http_access allow allowed_ip_by_auth authenticated_users`, "
        "- `http_access allow allowed_domain_by_auth authenticated_users`."
    ),
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Success message indicating that the authentication lines were uncommented successfully.",
                    example="Lines uncommented successfully."
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message indicating that the Squid configuration file was not found.",
                    example="File not found at the specified path."
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message indicating that an error occurred during the operation.",
                    example="An error occurred while enabling authentication."
                ),
            }
        ),
    }
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def enable_auth(request):
    """
    Active l'authentification dans le fichier de configuration de Squid (`/etc/squid/squid.conf`).

    Cette fonction décommente les lignes relatives à l'authentification dans le fichier de configuration Squid 
    pour permettre l'accès aux sous-réseaux, IP, et domaines autorisés par l'authentification.

    Args:
        request (HttpRequest): L'objet de la requête HTTP. Cette fonction ne dépend pas du corps de la requête,
                                mais elle effectue les modifications directement dans le fichier de configuration.

    Returns:
        JsonResponse: Un objet JSON contenant un message indiquant que les lignes ont été décommentées avec succès.

    Example:
        La fonction parcourt le fichier `squid.conf` et décommente les lignes suivantes pour activer l'authentification :
            - `http_access allow allowed_subnet_by_auth authenticated_users`
            - `http_access allow allowed_ip_by_auth authenticated_users`
            - `http_access allow allowed_domain_by_auth authenticated_users`
    """
    config_file_path = '/etc/squid/squid.conf'
    with open(config_file_path, 'r') as file:
        config_lines = file.readlines()

    # Uncomment the desired lines
    for i, line in enumerate(config_lines):
        if line.strip().startswith('#http_access allow allowed_subnet_by_auth authenticated_users') or \
        line.strip().startswith('#http_access allow allowed_ip_by_auth authenticated_users') or \
        line.strip().startswith('#http_access allow allowed_domain_by_auth authenticated_users'):
            config_lines[i] = line.replace('#', '')

    # Write the changes back to the file
    with open(config_file_path, 'w') as file:
        file.writelines(config_lines)

    return JsonResponse({"msg":f"{CONSTANT_LINES} {SUCCESS_MESSAGES_INCOMMENTED}"}, status=200)

@swagger_auto_schema(
    method='GET',
    operation_summary="Check if Authentication is Enabled in Squid Configuration",
    operation_description=(
        "This API endpoint checks whether authentication is enabled in the Squid configuration file (`/etc/squid/squid.conf`). "
        "It verifies if the lines associated with authentication are commented in the configuration. If these lines are commented, "
        "authentication is considered disabled; otherwise, it is enabled."
    ),
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                'status_enable': Schema(
                    type=TYPE_BOOLEAN,
                    description="Indicates whether authentication is enabled or disabled in the Squid configuration.",
                    example=True
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message indicating that the Squid configuration file was not found.",
                    example="File not found at the specified path."
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message indicating that an error occurred during the operation.",
                    example="An error occurred while checking the authentication status."
                ),
            }
        ),
    }
)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def status_enable_auth(request):
    """
    Vérifie si l'authentification est activée dans le fichier de configuration de Squid (`/etc/squid/squid.conf`).

    Cette fonction vérifie si les lignes associées à l'authentification sont commentées dans le fichier de configuration 
    Squid. Si ces lignes sont présentes sous forme commentée, cela signifie que l'authentification est désactivée. 
    Sinon, elle est activée.

    Args:
        request (HttpRequest): L'objet de la requête HTTP. La fonction ne dépend pas du corps de la requête,
                                elle effectue uniquement la lecture du fichier de configuration.

    Returns:
        JsonResponse: Un objet JSON contenant un champ `status_enable` qui est `True` si l'authentification est activée 
                      et `False` si elle est désactivée.

    Example:
        La fonction vérifie si les lignes suivantes sont commentées :
            - `#http_access allow allowed_subnet_by_auth authenticated_users`
            - `#http_access allow allowed_ip_by_auth authenticated_users`
            - `#http_access allow allowed_domain_by_auth authenticated_users`
    """
    list_line = []
    config_file_path = '/etc/squid/squid.conf'
    lines_to_check = [
        "#http_access allow allowed_subnet_by_auth authenticated_users\n",
        "#http_access allow allowed_ip_by_auth authenticated_users\n",
        "#http_access allow allowed_domain_by_auth authenticated_users\n"
    ]
    with open(config_file_path, 'r') as file:
            content = file.readlines()
    for line in content:
        if line.strip().startswith('#'):
            list_line.append(line)
    for i in lines_to_check:
        if i in list_line:
            enable = True
        else:
            enable =False
    return JsonResponse({"status_enable": enable}, status=200)

@swagger_auto_schema(
    method='GET',
    operation_summary="Retrieve All Proxy Users",
    operation_description=(
        "This API endpoint retrieves all proxy users from the database and returns them in a JSON response. "
        "It queries the database for all `ProxyUser` objects, serializes them into JSON format, removes unnecessary metadata "
        "such as model information and primary keys, and returns only the relevant user data."
    ),
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                'data': Schema(
                    type=TYPE_ARRAY,
                    items=Schema(
                        type=TYPE_OBJECT,
                        properties={
                            'id': Schema(
                                type=TYPE_INTEGER,
                                description="The unique identifier for the proxy user.",
                                example=1
                            ),
                            'username': Schema(
                                type=TYPE_STRING,
                                description="The username of the proxy user.",
                                example="user1"
                            ),
                            'email': Schema(
                                type=TYPE_STRING,
                                description="The email of the proxy user.",
                                example="user1@example.com"
                            ),
                            # You can add other user fields here as required.
                        }
                    ),
                    description="List of proxy users with their details."
                ),
            }
        ),
        500: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message indicating an internal server error.",
                    example="An error occurred while retrieving proxy users."
                ),
            }
        ),
    }
)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def allProxyUsers(request):
    """
    Récupère tous les utilisateurs du proxy à partir de la base de données et les renvoie sous forme de réponse JSON.

    Cette fonction interroge la base de données pour récupérer tous les objets `ProxyUser`, puis les sérialise en format 
    JSON. Elle supprime ensuite les métadonnées inutiles (comme le modèle et la clé primaire) et renvoie uniquement les 
    données pertinentes des utilisateurs du proxy.

    Args:
        request (HttpRequest): L'objet de la requête HTTP. La fonction utilise cet objet mais n'en tire pas directement 
                                d'informations spécifiques pour le traitement.

    Returns:
        JsonResponse: Une réponse JSON contenant une clé `data` qui est une liste d'objets représentant les utilisateurs 
                      du proxy. Chaque utilisateur est un dictionnaire contenant ses champs, y compris l'identifiant (`id`).

    Example:
        La réponse JSON pourrait ressembler à ceci :
        {
            "data": [
                {
                    "id": 1,
                    "username": "user1",
                    "email": "user1@example.com",
                    ...
                },
                {
                    "id": 2,
                    "username": "user2",
                    "email": "user2@example.com",
                    ...
                }
            ]
        }
    """
    list_proxyUsers =[]
    data = ProxyUser.objects.all()
    proxyUsersDict = serializers.serialize("json", data)
    res = json.loads(proxyUsersDict)
    for i in range(0, len(res)):
        res[i].pop('model')
        id = res[i]['pk']
        res[i].pop('pk')
        res[i]['fields']['id'] = id
        list_proxyUsers.append(res[i]['fields'])
    return JsonResponse({"data":list_proxyUsers})


@swagger_auto_schema(
    method='POST',
    operation_summary="Create a New Cron Job for Password Change Script",
    operation_description=(
        "This API endpoint creates a new cron job to run the Python script `g_pwd.py` at a specified time and frequency. "
        "The cron job will be created based on the parameters provided in the request, which include the time of execution "
        "and the desired execution period (e.g., daily, weekly, or monthly)."
    ),
    request_body=Schema(
        type=TYPE_OBJECT,
        properties={
            'time': Schema(
                type=TYPE_STRING,
                description="The time at which the script should be executed, in the format HH:MM.",
                example="14:30"
            ),
            'period': Schema(
                type=TYPE_STRING,
                description="The frequency of execution for the script. Possible values are:",
                enum=["every days", "MON -> FRI", "every week", "every month"],
                example="every days"
            ),
        },
        required=['time', 'period']
    ),
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="A message indicating the success of the cron job creation.",
                    example="Cron job created successfully."
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message indicating an issue with cron job creation.",
                    example="An error occurred while creating the cron job."
                ),
            }
        ),
    }
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def change_pwd(request):
    """
    Crée un nouveau travail cron pour exécuter un script à des intervalles spécifiés en fonction des paramètres de la requête.

    Cette fonction permet de configurer un travail cron pour exécuter un script Python (`g_pwd.py`) à une heure et une 
    fréquence spécifiques, en fonction des données fournies par la requête. Les périodes supportées incluent : 
    tous les jours, du lundi au vendredi, chaque semaine, ou chaque mois.

    Args:
        request (HttpRequest): L'objet de la requête HTTP contenant les informations nécessaires pour configurer le travail cron.
            - `time`: Heure à laquelle le script doit être exécuté (format "HH:MM").
            - `period`: Période d'exécution du script. Les valeurs possibles sont :
              - "every days"
              - "MON -> FRI"
              - "every week"
              - "every month"

    Returns:
        JsonResponse: Réponse JSON avec un message indiquant si le travail cron a été créé avec succès.
            - Message de succès : Si le travail cron a été créé avec succès.
            - Message d'erreur : Si une erreur survient lors de l'ajout du travail cron.

    Example:
        Si `data['time']` = "14:30" et `data['period']` = "every days", le travail cron configuré sera :
        "30 14 * * * python /home/vagrant/g_pwd.py"

    Raises:
        subprocess.CalledProcessError: Si une erreur survient lors de l'exécution des commandes `crontab`.
    """
    data = request.data
    data_to_convert = datetime.strptime(data['time'], "%H:%M")
    script_path = "/home/vagrant/g_pwd.py"
    if data['period'] == "every days":
        cron_job = f"{data_to_convert.minute} {data_to_convert.hour} * * * python {script_path}" 
    elif data['period'] == "MON -> FRI":
        cron_job = f"{data_to_convert.minute} {data_to_convert.hour} * * 1-5 python {script_path}" 
    elif data['period'] == "every week":
        cron_job = f"{data_to_convert.minute} {data_to_convert.hour} * * 0 python {script_path}" 
    elif data['period'] == "every month":
        month_expression = [ "$(date +\%m -d 'last monday')" != "$(date +\%m)" ]
        cron_job = f"{data_to_convert.minute} {data_to_convert.hour} * * {month_expression} python {script_path}" 

    try:
        # Use subprocess to execute the crontab -l command and capture the current crontab content
        current_crontab = subprocess.check_output(["crontab", "-l"], universal_newlines=True)
        ## reset our cron with a empty str
        current_crontab = ''
        # Add the new cron job to the existing crontab content  
        # new_crontab = f"{current_crontab.strip()}\n{cron_job}\n"
        new_crontab = f"{current_crontab.strip()}{cron_job}\n"

        # Use subprocess to set the new crontab content
        subprocess.run(["echo", new_crontab], stdout=subprocess.PIPE, input=new_crontab, universal_newlines=True)
        subprocess.run(["crontab", "-"], input=new_crontab, universal_newlines=True)

        return JsonResponse({"msg": f"{CONSTANT_CRON_JOB} {SUCCESS_MESSAGES_CREATING}"}, status=200)
    except subprocess.CalledProcessError as e:
        return JsonResponse({"msg": e}, status=400)

@swagger_auto_schema(
    method='POST',
    operation_summary="Add User to Squid Configuration",
    operation_description=(
        "This API endpoint allows the addition of a user to the Squid configuration file by storing their username, "
        "password, and email in the Squid password file (`squid_passwd`) and in the `ProxyUser` database. "
        "It also updates the server status to indicate the success of the operation."
    ),
    request_body=Schema(
        type=TYPE_OBJECT,
        properties={
            'username': Schema(
                type=TYPE_STRING,
                description="The username of the user to be added.",
                example="user1"
            ),
            'password': Schema(
                type=TYPE_STRING,
                description="The password for the user.",
                example="password123"
            ),
            'email': Schema(
                type=TYPE_STRING,
                description="The email address of the user.",
                example="user1@example.com"
            ),
        },
        required=['username', 'password', 'email']
    ),
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="A success message indicating the user was added.",
                    example="User user1 added successfully."
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message if there was an issue adding the user.",
                    example="Error occurred while saving user: {error message}"
                ),
            }
        ),
    }
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def add_user_squid(request):
    """
    Ajoute un utilisateur à la configuration de Squid et enregistre ses informations dans la base de données.

    Cette fonction permet d'ajouter un utilisateur avec un nom d'utilisateur, un mot de passe et un email à un fichier de mot de passe Squid,
    puis de sauvegarder les informations de l'utilisateur dans la base de données `ProxyUser`. Elle met également à jour le statut du serveur
    pour indiquer que l'ajout a été effectué avec succès.

    Args:
        request (HttpRequest): L'objet de la requête HTTP contenant les informations de l'utilisateur à ajouter.
            - `username`: Nom d'utilisateur de l'utilisateur.
            - `password`: Mot de passe de l'utilisateur.
            - `email`: Adresse email de l'utilisateur.

    Returns:
        JsonResponse: Réponse JSON avec un message indiquant si l'ajout de l'utilisateur a réussi ou échoué.
            - Message de succès : Si l'utilisateur a été ajouté avec succès.
            - Message d'erreur : Si une erreur survient lors de l'ajout de l'utilisateur.

    Example:
        Si `data['username'] = "user1"`, `data['password'] = "password123"`, et `data['email'] = "user1@example.com"`,
        un utilisateur est ajouté avec ces informations au fichier `squid_passwd` et à la base de données.

    Raises:
        subprocess.CalledProcessError: Si une erreur survient lors de l'exécution de la commande `htpasswd` pour ajouter l'utilisateur.
        IntegrityError: Si une erreur survient lors de l'enregistrement de l'utilisateur dans la base de données.
        Exception: Si une autre erreur survient lors de l'ajout de l'utilisateur.
    """

    data = request.data
    squid_conf_path = '/etc/squid/squid_passwd'
    username_squid = data.get('username')
    password_squid = data.get('password')
    email_squid = data.get('email')
    try:
        subprocess.run(['htpasswd', '-b', squid_conf_path, username_squid, password_squid], check=True)
        try:
            user_proxy = ProxyUser(username=username_squid,email=email_squid)
            user_proxy.save()
            server_satus = ServerSatus.objects.get(id=1)
            server_satus.status_server = True
            server_satus.save() 
            #send_email_to_user(email_squid,password_squid,username_squid)
            msg = f"{CONSTANT_USER} {username_squid} {SUCCESS_MESSAGES_CREATING}"
            status=200
            return JsonResponse({"msg": msg}, status=status)
        except IntegrityError as e:
            msg = f"{ERROR_MESSAGES_SAVING_INSTANCE}: {e}"
            status=400 
            return JsonResponse({"msg": msg}, status=status)
        except Exception as e:
            msg = (f"{ERROR_MESSAGES_OCCURRED}: {e}")
            status=400 
            return JsonResponse({"msg": msg}, status=status)
        ### to add only one user every time in file
        # subprocess.run(['htpasswd', '-b', '-c', squid_conf_path, username_squid, password_squid], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error adding user: {e}")
        return JsonResponse({"msg": f"{ERROR_MESSAGES_SAVING_USER}: {e}"}, status=400 )

@swagger_auto_schema(
    method='DELETE',
    operation_summary="Delete User from Squid Configuration",
    operation_description=(
        "This API endpoint allows for the deletion of a user from the Squid configuration file (`squid_passwd`) and "
        "removes the user's details from the `ProxyUser` database using their unique ID."
    ),
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="A success message indicating the user was deleted.",
                    example="User user1 deleted successfully."
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message if there was an issue deleting the user.",
                    example="Error occurred while deleting the user."
                ),
            }
        ),
    }
)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_user_squid(request, id):
    """
    Supprime un utilisateur de la configuration de Squid et de la base de données.

    Cette fonction permet de supprimer un utilisateur en utilisant son identifiant (id). Elle retire les informations
    de l'utilisateur du fichier de mot de passe Squid (`squid_passwd`), puis supprime l'utilisateur de la base de données `ProxyUser`.

    Args:
        request (HttpRequest): L'objet de la requête HTTP. L'ID de l'utilisateur à supprimer est passé en tant que paramètre URL.
        id (int): L'identifiant de l'utilisateur à supprimer.

    Returns:
        JsonResponse: Réponse JSON avec un message indiquant si la suppression de l'utilisateur a réussi ou échoué.
            - Message de succès : Si l'utilisateur a été supprimé avec succès du fichier Squid et de la base de données.
            - Message d'erreur : Si une erreur survient lors de la suppression de l'utilisateur.

    Example:
        Si `id = 5`, cette fonction supprimera l'utilisateur avec l'identifiant `5` du fichier `squid_passwd` et de la base de données.

    Raises:
        ProxyUser.DoesNotExist: Si l'utilisateur avec l'ID spécifié n'existe pas dans la base de données.
        Exception: Si une erreur survient lors de l'exécution des commandes ou de la suppression de l'utilisateur.
    """

    user = ProxyUser.objects.get(id=id)
    file_path = '/etc/squid/squid_passwd'
    new_content = []
    command = "cat " + file_path
    stdout, stderr = run_command(command)
    lines = stdout.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    for line in lines:
        fields = line.strip().split(':')
        if fields[0] != user.username:
            new_content.append(line)

    text = '\n'.join(new_content)
    command = "echo '" + text + "' > " + file_path
    stdout, stderr = run_command(command)
    if stderr == '':
        user.delete()
        server_satus = ServerSatus.objects.get(id=1)
        server_satus.status_server = True
        server_satus.save() 
        return JsonResponse({"msg":f"{CONSTANT_USER} {SUCCESS_MESSAGES_DELETING}"},status=200)
    else:
        return JsonResponse({"msg":f"{ERROR_MESSAGES_OCCURRED}"},status = 400 )


def get_line_from_file(file_path, target_line):
    """
    Recherche une ligne spécifique dans un fichier et détermine si elle est commentée ou non.

    Cette fonction lit un fichier ligne par ligne et cherche une occurrence de la ligne cible (`target_line`). 
    Si la ligne est trouvée, elle vérifie si la ligne est commentée (commence par `#`) et retourne un booléen.
    
    Args:
        file_path (str): Le chemin du fichier dans lequel rechercher la ligne.
        target_line (str): La ligne cible à rechercher dans le fichier.

    Returns:
        bool: 
            - `True` si la ligne cible est trouvée et **non commentée**.
            - `False` si la ligne cible est trouvée mais **commentée** (commence par `#`).
            - `None` si la ligne cible n'est pas trouvée dans le fichier.
    
    Example:
        Si le fichier contient une ligne `"http_access allow all"` et vous cherchez `"http_access"`, 
        cette fonction retournera `True` si la ligne n'est pas commentée et `False` si elle l'est.
    
    Raises:
        FileNotFoundError: Si le fichier spécifié n'existe pas ou n'est pas accessible.
    """

    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            if target_line in line:
                if line.strip().startswith("#"):
                    return(False)
                else:
                    return(True)
    return None

@swagger_auto_schema(
    method='GET',
    operation_summary="Get All Squid Groups with Status",
    operation_description=(
        "This API endpoint retrieves all groups defined in the Squid configuration file (`squid.conf`), specifically groups "
        "that are associated with the `url_regex` ACLs. It checks the status of each group, determining whether the line "
        "defining the group is commented or not. The list of groups along with their status is returned in the response."
    ),
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                'groups': Schema(
                    type=TYPE_ARRAY,
                    items=Schema(
                        type=TYPE_OBJECT,
                        properties={
                            'name': Schema(
                                type=TYPE_STRING,
                                description="The name of the group.",
                                example="my_group"
                            ),
                            'status': Schema(
                                type=TYPE_BOOLEAN,
                                description="Indicates whether the group line is commented in the configuration file.",
                                example=False
                            ),
                        }
                    ),
                    description="A list of groups with their names and comment statuses."
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message if there was an issue fetching the groups.",
                    example="File not found."
                ),
            }
        ),
    }
)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def allGroups(request):
    """
    Récupère tous les groupes définis dans le fichier de configuration de Squid et retourne leur statut.

    Cette fonction lit le fichier de configuration de Squid, recherche les définitions de groupes ACL 
    contenant "url_regex", puis vérifie leur statut (commenté ou non) dans le fichier de configuration.

    Elle construit une liste de groupes avec leur nom et leur statut, puis retourne cette liste dans la réponse JSON.

    Args:
        request: Objet de requête HTTP (habituellement fourni par Django dans les vues).

    Returns:
        JsonResponse: Une réponse JSON contenant la liste des groupes et leur statut, où chaque groupe est représenté 
                      par un dictionnaire avec les clés "name" et "status".
                      - "name" est le nom du groupe.
                      - "status" est un booléen indiquant si la ligne correspondant à ce groupe est commentée.

    Example:
        Si le fichier `/etc/squid/squid.conf` contient les lignes suivantes :
            acl my_group url_regex "/path/to/regex"
            http_access deny my_group
        La fonction retournera :
        {
            "groups": [
                {"name": "my_group", "status": False}
            ]
        }

    Raises:
        FileNotFoundError: Si le fichier `/etc/squid/squid.conf` n'existe pas ou n'est pas accessible.
    """

    list_line = []
    list_groups = []
    config_file_path = '/etc/squid/squid.conf'
    with open(config_file_path, 'r') as file:
                content = file.readlines()
    for line in content:
        if "squid/acl/" in line:
            list_line.append(line)
            
    # Define a regular expression pattern to extract keywords
    pattern = re.compile(r'acl (\w+) url_regex')

    groups = [pattern.findall(line)[0] for line in list_line if pattern.findall(line)]
    for i in groups:
        target_line = 'http_access deny '+i
        rslt = get_line_from_file(config_file_path,target_line)
        list_groups.append({"name":i,"status":rslt})
    return JsonResponse({"groups":list_groups},status = 200)
    
@swagger_auto_schema(
    method='POST',
    operation_summary="Change Group Status in Squid Configuration",
    operation_description=(
        "This API endpoint allows modifying the status of a group in the Squid configuration file. "
        "It changes the access control for the specified group from 'deny' to 'allow', or vice versa, based on the provided `status`."
        " After the modification, the Squid configuration file is updated, and the server status is set to indicate that the change has been made."
    ),
    request_body=Schema(
        type=TYPE_OBJECT,
        properties={
            'group': Schema(
                type=TYPE_STRING,
                description="The name of the group whose status needs to be modified.",
                example="my_group"
            ),
            'status': Schema(
                type=TYPE_BOOLEAN,
                description="The new status for the group (True for 'allow', False for 'deny').",
                example=True
            ),
        }
    ),
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Message indicating the successful change of the group's status.",
                    example="Group status changed successfully."
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message if the required fields are missing or invalid.",
                    example="Missing required parameters 'group' or 'status'."
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message if the Squid configuration file cannot be found or accessed.",
                    example="Squid configuration file not found."
                ),
            }
        ),
    }
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def changeStausGroup(request):
    """
    Modifie le statut d'un groupe dans le fichier de configuration Squid.

    Cette fonction permet de modifier la ligne de configuration d'un groupe dans le fichier Squid 
    pour changer son accès de "deny" à "allow" ou vice versa, en fonction de la valeur du paramètre `status`.

    Le fichier de configuration Squid est lu, puis la ligne correspondant au groupe spécifié est mise à jour.
    Après la modification, le fichier est réécrit et le statut du serveur est mis à jour dans la base de données.

    Args:
        request: Objet de requête HTTP contenant les données suivantes :
            - `group` : Le nom du groupe dont le statut doit être modifié.
            - `status` : Le nouveau statut du groupe (True pour "allow", False pour "deny").

    Returns:
        JsonResponse: Une réponse JSON indiquant que le statut du groupe a été modifié avec succès.

    Example:
        Si le fichier `/etc/squid/squid.conf` contient la ligne suivante :
            http_access deny my_group
        Et qu'une requête est envoyée avec `status=True`, la ligne sera modifiée en :
            http_access allow my_group

    Raises:
        FileNotFoundError: Si le fichier `/etc/squid/squid.conf` n'existe pas ou n'est pas accessible.
        KeyError: Si les données de la requête ne contiennent pas les clés `group` ou `status`.
    """

    data = request.data
    group = data['group']
    status = data['status']
    squid_config_path = '/etc/squid/squid.conf'

    with open(squid_config_path, 'r') as file:
        squid_config = file.read()
    if status == True:
        squid_config = squid_config.replace('http_access deny '+group, 'http_access allow '+group)
    else:
        squid_config = squid_config.replace('http_access allow '+group, 'http_access deny '+group)
        
    with open(squid_config_path, 'w') as file:
        file.write(squid_config)
    server_satus = ServerSatus.objects.get(id=1)
    server_satus.status_server = True
    server_satus.save() 
    return JsonResponse({"msg":f"{CONSTANT_STATUS} {SUCCESS_MESSAGES_CHANGE_STATUS}"}, status=200)

@swagger_auto_schema(
    method='POST',
    operation_summary="Read ACL File Content with Status",
    operation_description=(
        "This API endpoint reads the content of a specified Squid ACL file and returns the lines along with their "
        "status (whether they are commented or active). The function checks each line to determine if it is commented (starts with '#') or active. "
        "The response includes the content of the file with each line's status."
    ),
    request_body=Schema(
        type=TYPE_OBJECT,
        properties={
            'file_name': Schema(
                type=TYPE_STRING,
                description="The name of the ACL file like 123found (without the '.acl' extension and we have a project content all .acl files).",
                example="ads" 
            ),
        }
    ),
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                'content': Schema(
                    type=TYPE_ARRAY,
                    description="List of lines in the file with their status. Each line is represented as a list of [line_text, status].",
                    items=Schema(
                        type=TYPE_ARRAY,
                        items=[
                            Schema(type=TYPE_STRING, description="The line of the file"),
                            Schema(type=TYPE_BOOLEAN, description="True if the line is active, False if commented")
                        ]
                    )
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message indicating the file was not found or another error occurred.",
                    example="The specified file does not exist."
                ),
            }
        ),
    }
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def readFromFile(request):
    """
    Lit le contenu d'un fichier de configuration Squid et renvoie les lignes avec leur statut (commentée ou active).

    Cette fonction permet de lire un fichier de configuration Squid spécifique à un fichier ACL (Access Control List) 
    situé dans `/etc/squid/acl/` et de renvoyer son contenu. Chaque ligne du fichier est analysée pour vérifier si elle 
    est commentée (ligne commençant par '#') ou active. Les lignes commentées sont retournées avec un statut `False`,
    et les lignes actives avec un statut `True`.

    Args:
        request: Objet de requête HTTP contenant les données suivantes :
            - `file_name` : Le nom du fichier ACL (sans l'extension `.acl`).

    Returns:
        JsonResponse: Une réponse JSON contenant une liste des lignes du fichier et leur statut :
            - Chaque ligne est une liste contenant le texte de la ligne et un booléen qui indique si elle est active (`True`) ou commentée (`False`).
            - Si le fichier n'existe pas, une erreur est retournée avec un message d'erreur 400.
            - Si une autre exception se produit, un message d'erreur générique est renvoyé.

    Example:
        Si le fichier `/etc/squid/acl/example.acl` contient les lignes suivantes :
            # Allow access
            Deny access
        La réponse JSON sera :
            {
                "content": [
                    ["Allow access", False],
                    ["Deny access", True]
                ]
            }

    Raises:
        FileNotFoundError: Si le fichier spécifié n'existe pas dans le chemin.
        Exception: En cas d'erreur imprévue lors de la lecture du fichier.
    """
    content= []
    data = request.data
    squid_config_path = '/etc/squid/acl/'+data['file_name']+'.acl'

    try:
        with open(squid_config_path, 'r') as file:
            for line in file:
                if line.startswith('#'):
                    content.append([line.lstrip('#').split('\n')[0], False])
                else:
                    content.append([line.lstrip('#').split('\n')[0], True])
    except FileNotFoundError:
        return JsonResponse({"msg":f"{CONSTANT_PATH} {squid_config_path} {ERROR_MESSAGES_INEXISTANT}"},status=400 )
    except Exception as e:
        return JsonResponse({"msg":f"{ERROR_MESSAGES_OCCURRED}{e}"},status=400 )
                
    return JsonResponse({"content": content}, status=200)  



@swagger_auto_schema(
    method='POST',
    operation_summary="Change Status of Elements in Squid ACL File",
    operation_description=(
        "This API endpoint allows you to modify the status (commented or active) of specified elements (URLs) in a Squid ACL file. "
        "The status of each element in the `list_elements` list is updated based on the `uncomment` value, which determines "
        "whether the element should be commented or uncommented. If `uncomment` is False, the element will be uncommented; "
        "if True, it will be commented."
    ),
    request_body = Schema(
    type=TYPE_OBJECT,
    properties={
        'file_name': Schema(
            type=TYPE_STRING,
            description="Le nom du fichier ACL à modifier (sans l'extension '.acl'). "
                        "Ce nom détermine les URLs associées à cette liste.",
            example="ads"
        ),
        'list_elements': Schema(
            type=TYPE_ARRAY,
            description="Une liste d'éléments à mettre à jour dans le fichier ACL spécifié. "
                        "Chaque élément contient une URL cible et un booléen indiquant s'il faut commenter "
                        "ou décommenter la ligne correspondante. Les URLs concernées dépendent du fichier ACL donné en entrée.",
            items=Schema(
                type=TYPE_OBJECT,
                properties={
                    "url": Schema(
                        type=TYPE_STRING,
                        description="L'URL cible à modifier dans le fichier ACL spécifié."
                    ),
                    "comment": Schema(
                        type=TYPE_BOOLEAN,
                        description="True pour commenter l'URL (la désactiver), False pour la décommenter (l'activer)."
                    )
                }
            ),
            example=[
                {"url": "7search.com", "comment": False},
                {"url": "82o9v830.com", "comment": True}
            ]
        ),
    }
),
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Success message indicating that the status of the elements was successfully modified.",
                    example="Status of the elements was changed successfully."
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message indicating that an error occurred during the file read/write operation.",
                    example="An error occurred while modifying the file."
                ),
            }
        ),
    }
)

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def changeStausElementsInGroup(request):
    """
    Modifie le statut (commenté ou actif) des éléments spécifiés dans un fichier ACL Squid.

    Cette fonction permet de mettre à jour le statut des éléments (URLs) dans un fichier ACL de Squid. 
    Chaque élément de la liste `list_elements` contient un URL cible et un statut de commentaire (`True` ou `False`). 
    Si le statut est `False`, l'élément est décommenté, sinon il est commenté.

    Args:
        request: Objet de requête HTTP contenant les données suivantes :
            - `file_name` : Le nom du fichier ACL à modifier (sans l'extension `.acl`).
            - `list_elements` : Une liste de tuples où chaque tuple contient :
                - `target_url` : L'URL cible à modifier.
                - `uncomment` : Booléen qui indique si l'élément doit être commenté (`True`) ou décommenté (`False`).

    Returns:
        JsonResponse: Une réponse JSON indiquant que le statut des éléments a été modifié avec succès.
            Le message retourné est constitué de la constante `CONSTANT_STATUS` et de la constante `SUCCESS_MESSAGES_CHANGE_STATUS`.

    Example:
        Si `list_elements` contient les éléments suivants :
            [
                ("url1.com", False),
                ("url2.com", True)
            ]
        Et le fichier `/etc/squid/acl/example.acl` contient les lignes :
            "# url1.com"
            "url2.com"
        Après exécution, le fichier ACL sera mis à jour pour devenir :
            "url1.com"
            "# url2.com"
        
    Raises:
        Exception: Si une erreur se produit lors de la lecture ou de l'écriture du fichier.
    """

    data = request.data
    list_elements = data['list_elements']
    if data['file_name'] not in ['ads','adult','astrology','audio_video','bitcoin','cryptojacking','dating','ddos','download','drugs','games','jobsearch','social_network','sports','violence']:
        return JsonResponse({"error": "file_name does not exist"}, status=404)
    else:
        file_path = '/etc/squid/acl/'+data['file_name']+'.acl'
        with open(file_path, 'r') as file:
            lines = file.readlines()
            
        for update in list_elements:
            target_url = update["url"]
            comment = update["comment"]
            if target_url+'\n' in list(lines) or '#'+target_url+'\n' in list(lines):
                for i, line in enumerate(lines):
                    if line.lstrip('#').split('\n')[0] == target_url:
                        if comment == True and line.startswith("#") == True:
                            pass
                        elif comment == True and line.startswith("#") == False:
                            lines[i] = '#' + line
                        elif comment == False:
                            lines[i] = line.lstrip('#')
            else:
                return JsonResponse({"error": "target_url does not exist"}, status=404)
        with open(file_path, 'w') as file:
            file.writelines(lines)
        server_satus = ServerSatus.objects.get(id=1)
        server_satus.status_server = True
        server_satus.save() 
        return JsonResponse({"msg": f"{CONSTANT_STATUS} {SUCCESS_MESSAGES_CHANGE_STATUS}"}, status=200)

def changeStausElement(target_url, uncomment, file_path):
    """
    Modifie le statut (commenté ou actif) d'un élément spécifique dans un fichier ACL Squid.

    Cette fonction permet de mettre à jour le statut d'un élément (URL) spécifique dans un fichier ACL de Squid. 
    Si le statut `uncomment` est `True`, l'élément est décommenté (le préfixe `#` est supprimé). 
    Si `uncomment` est `False`, l'élément est commenté (le préfixe `#` est ajouté).

    Args:
        target_url (str): L'URL cible dont le statut doit être modifié dans le fichier ACL.
        uncomment (bool): Indique si l'élément doit être décommenté (`True`) ou commenté (`False`).
        file_path (str): Le chemin d'accès au fichier ACL Squid à modifier.

    Returns:
        JsonResponse: Une réponse JSON contenant un message indiquant que le statut de l'élément a été modifié avec succès.
            Le message retourné est constitué de la constante `CONSTANT_STATUS` et de la constante `SUCCESS_MESSAGES_CHANGE_STATUS`.

    Example:
        Si `target_url` est "url1.com", `uncomment` est `False`, et `file_path` est `/etc/squid/acl/example.acl`, 
        alors l'élément "url1.com" sera commenté dans le fichier.

    Raises:
        Exception: Si une erreur se produit lors de la lecture ou de l'écriture du fichier.
    """

    with open(file_path, 'r') as file:
        lines = file.readlines()
        
    for i, line in enumerate(lines):
        if line.lstrip('#').split('\n')[0] == target_url:
        # if target_url in line:
            if uncomment:
                lines[i] = line.lstrip('#')
            else:
                lines[i] = '#' + line

    with open(file_path, 'w') as file:
        file.writelines(lines)
        
    return JsonResponse({"msg":f"{CONSTANT_STATUS} {SUCCESS_MESSAGES_CHANGE_STATUS}"}, status=200)


def deleteElement(type, value, file_path):
    """
    Supprime un élément spécifique dans un fichier, en fonction du type et de la valeur donnés.

    Cette fonction permet de supprimer une ligne spécifique dans un fichier. La ligne à supprimer est déterminée par la valeur `value`,
    et elle est comparée à chaque ligne du fichier après suppression des caractères `#` de chaque ligne.
    Si la ligne correspond à la valeur spécifiée, elle est supprimée du contenu du fichier.

    Args:
        type (str): Le type de l'élément à supprimer (utilisé pour le message de réponse, par exemple "URL" ou "Group").
        value (str): La valeur de l'élément à supprimer (par exemple, l'URL ou le nom de groupe).
        file_path (str): Le chemin d'accès au fichier à modifier.

    Returns:
        JsonResponse: Une réponse JSON contenant un message indiquant si l'élément a été supprimé avec succès.
            Le message retourné est constitué de la constante `CONSTANT_ADDRESS`, de la valeur de l'élément supprimé et 
            de la constante `SUCCESS_MESSAGES_UNBLOCKED`. En cas d'échec, le message d'erreur retourné est contenu dans `stderr`.

    Example:
        Si `type` est "URL", `value` est "url1.com" et `file_path` est `/etc/squid/acl/example.acl`, 
        la ligne contenant "url1.com" sera supprimée du fichier.

    Raises:
        Exception: Si une erreur se produit lors de la lecture, de la modification ou de l'écriture dans le fichier.
    """

    new_content = []
    command = "cat " + file_path
    stdout, stderr = run_command(command)
    resultat = stdout.split('\n')
    resultat = [line.strip() for line in resultat if line.strip()]
    for line in resultat:
        if line.strip('#') != value :
            new_content.append(line)
    text = '\n'.join(new_content)
    command = "echo '" + text + "' > " + file_path  
    stdout, stderr = run_command(command)
    if(stderr == ""):
        msg = f"{type} {CONSTANT_ADDRESS} {value} {SUCCESS_MESSAGES_UNBLOCKED}"
        status =200
    else:
        msg =stderr
        status = 400 
    return JsonResponse({"msg": msg}, status=status)


def addElement(type, allow_by_auth, status, value):
    """
    Ajoute un élément (IP, domaine, ou sous-réseau) dans un fichier ACL spécifique, en fonction de l'authentification et de l'état (autorisé ou bloqué).

    Cette fonction permet d'ajouter une ligne à un fichier ACL, représentant un élément (IP, domaine ou sous-réseau) 
    qui peut être soit autorisé, soit bloqué. L'élément est ajouté dans le fichier correspondant en fonction des paramètres
    `type` et `allow_by_auth`. Si `status` est False, l'élément est ajouté sous forme commentée (indiquant qu'il est bloqué).

    Args:
        type (str): Le type d'élément à ajouter (par exemple, "ip", "domain", ou "subnet").
        allow_by_auth (bool): Indique si l'élément doit être autorisé par authentification.
        status (bool): Détermine si l'élément est autorisé (True) ou bloqué (False).
        value (str): La valeur de l'élément à ajouter (par exemple, une adresse IP, un domaine, ou un sous-réseau).

    Returns:
        JsonResponse: Une réponse JSON contenant un message de succès ou d'erreur lors de l'ajout de l'élément dans le fichier ACL.
            Si une erreur se produit lors de l'ajout, le message d'erreur est retourné avec le code d'état 400.

    Example:
        Si `type` est "ip", `allow_by_auth` est False, `status` est True et `value` est "192.168.1.1",
        l'adresse "192.168.1.1" sera ajoutée à la liste des adresses IP autorisées dans le fichier correspondant.

    Raises:
        Exception: Si une erreur se produit lors de l'écriture dans le fichier, un message d'erreur est retourné.
    """

    # if allow_by_auth == False:
    #     if type == "ip":
    #         file_path = '/etc/squid/blocked_ip.acl'
    #     elif type == "domain":
    #         file_path = '/etc/squid/blocked_domain.acl'
    #     else:
    #         file_path = '/etc/squid/blocked_subnet.acl'
    # else:
    #     if type == "ip":
    #         file_path = '/etc/squid/allowed_ip_by_auth.acl'
    #     elif type == "domain":
    #         file_path = '/etc/squid/allowed_domain_by_auth.acl'
    #     else:
    #         file_path = '/etc/squid/allowed_subnet_by_auth.acl'
    file_path = file_selected(allow_by_auth, type)
    if  status == False:
        value = '#'+value
    else:
        value = value
    try:
        with open(file_path, 'a') as file:
            file.write(value + '\n')
    except Exception as e:
        print(f"{ERROR_MESSAGES_OCCURRED}: {e}")
        msg = e
        status=400 
        return JsonResponse({"msg": msg}, status=status)
    
# def restart_squid(request):
#     command = "sudo squid -k reconfigure"
#     stdout, stderr = run_command(command)
#     if(stderr == ''):
#         return HttpResponse("Squid restarted successfully.")
#     else:
#         return HttpResponse("erreur.")

@swagger_auto_schema(
    method='PUT',
    operation_summary="Update Proxy Rule Status and Authentication Settings",
    operation_description=(
        "This API endpoint updates the status (allowed or blocked) and authentication state of a proxy rule, "
        "based on the provided rule ID. The function modifies the corresponding ACL file based on the updated status and "
        "authentication parameters. It also updates the proxy rule in the database."
    ),
    request_body=Schema(
        type=TYPE_OBJECT,
        properties={
            'status': Schema(
                type=TYPE_BOOLEAN,
                description="The new status of the rule (True for allowed, False for blocked).",
                example=True
            ),
            'allow_by_auth': Schema(
                type=TYPE_BOOLEAN,
                description="The new authentication state for the rule (True if allowed by authentication, False otherwise).",
                example=False
            ),
        }
    ),
    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Success message indicating that the proxy rule status was successfully updated.",
                    example="Proxy rule status updated successfully."
                ),
            }
        ),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'msg': Schema(
                    type=TYPE_STRING,
                    description="Error message indicating that the rule with the specified ID was not found or an error occurred.",
                    example="Error occurred while updating the rule."
                ),
            }
        ),
    }
)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def updateStatusRule(request, id):
    """
    Met à jour le statut d'une règle proxy dans la base de données et dans les fichiers ACL correspondants.

    Cette fonction prend en charge la mise à jour du statut (autorisé ou bloqué) et de l'état de l'authentification 
    pour une règle proxy spécifique, en fonction de l'ID de la règle. Elle modifie le fichier ACL approprié 
    en fonction des nouveaux paramètres et met à jour la règle dans la base de données.

    Args:
        request (HttpRequest): La requête contenant les nouvelles données pour la règle proxy, incluant les paramètres `status` et `allow_by_auth`.
        id (int): L'ID de la règle proxy à mettre à jour dans la base de données.

    Returns:
        JsonResponse: Une réponse JSON indiquant le succès ou l'échec de la mise à jour du statut de la règle. 
            En cas de succès, un message de confirmation est retourné avec un code d'état 200.
            En cas d'erreur, un message d'erreur est retourné avec un code d'état 400.

    Example:
        Si la règle proxy a un `status` de "True" et un `allow_by_auth` de "False", et que la requête met à jour 
        `status` à "False" et `allow_by_auth` à "True", la fonction mettra à jour la règle dans la base de données 
        et modifiera les fichiers ACL correspondants.

    Raises:
        ProxyRules.DoesNotExist: Si l'ID de la règle proxy n'existe pas dans la base de données.
        Exception: Si une erreur se produit lors de la modification des fichiers ACL ou de la mise à jour de la règle dans la base de données.
    """

    proxy_rule = ProxyRules.objects.get(id=id)
    data = request.data
    # if proxy_rule.allow_by_auth == False:
    #     if proxy_rule.type == "ip":
    #         file_path = '/etc/squid/blocked_ip.acl'
    #     elif proxy_rule.type == "domain":
    #         file_path = '/etc/squid/blocked_domain.acl'
    #     else:
    #         file_path = '/etc/squid/blocked_subnet.acl'
    # else:
    #     if proxy_rule.type == "ip":
    #         file_path = '/etc/squid/allowed_ip_by_auth.acl'
    #     elif proxy_rule.type == "domain":
    #         file_path = '/etc/squid/allowed_domain_by_auth.acl'
    #     else:
    #         file_path = '/etc/squid/allowed_subnet_by_auth.acl'
    file_path = file_selected(proxy_rule.allow_by_auth, proxy_rule.type)
    if proxy_rule.allow_by_auth == data['allow_by_auth']:
        if proxy_rule.status != data['status']:
            changeStausElement(proxy_rule.value,data['status'],file_path)
    else:
        deleteElement(proxy_rule.type,proxy_rule.value,file_path)
        addElement(proxy_rule.type,data['allow_by_auth'],data['status'],proxy_rule.value)
                
    proxy_rule.status = data['status']
    proxy_rule.allow_by_auth = data['allow_by_auth']
    proxy_rule.save()      
    server_satus = ServerSatus.objects.get(id=1)
    server_satus.status_server = True
    server_satus.save() 
    return JsonResponse({"msg": f"{CONSTANT_RULE} {SUCCESS_MESSAGES_UPDATING}"}, status=200)


def file_selected(status, type):
    """
    Sélectionne le chemin du fichier ACL approprié en fonction du statut et du type de règle proxy.

    Cette fonction détermine le fichier ACL à utiliser en fonction des paramètres `status` et `type`. 
    Si le statut est `False`, cela indique que la règle est bloquée, et le fichier approprié pour les adresses IP, domaines ou sous-réseaux bloqués sera retourné. 
    Si le statut est `True`, cela indique que la règle est autorisée, et le fichier approprié pour les adresses IP, domaines ou sous-réseaux autorisés par authentification sera retourné.

    Args:
        status (bool): Le statut de la règle proxy (`True` pour autorisé, `False` pour bloqué).
        type (str): Le type de la règle proxy (peut être "ip", "domain", ou "subnet").

    Returns:
        str: Le chemin du fichier ACL correspondant à la règle proxy spécifiée.

    Example:
        - Si `status` est `False` et `type` est "ip", la fonction retourne '/etc/squid/blocked_ip.acl'.
        - Si `status` est `True` et `type` est "domain", la fonction retourne '/etc/squid/allowed_domain_by_auth.acl'.

    Raises:
        ValueError: Si le paramètre `type` n'est pas l'un des types acceptés ("ip", "domain", "subnet").
    """

    if status == False:
        if type == "ip":
            file_path = '/etc/squid/blocked_ip.acl'
        elif type == "domain":
            file_path = '/etc/squid/blocked_domain.acl'
        else:
            file_path = '/etc/squid/blocked_subnet.acl'
    else:
        if type == "ip":
            file_path = '/etc/squid/allowed_ip_by_auth.acl'
        elif type == "domain":
            file_path = '/etc/squid/allowed_domain_by_auth.acl'
        else:
            file_path = '/etc/squid/allowed_subnet_by_auth.acl'
    return file_path



@swagger_auto_schema(
    method='get',
    operation_summary="Lister les fichiers ACL Squid avec leur contenu et statut",
    operation_description = (
    "Cette API permet de récupérer le contenu de tous les fichiers ACL situés dans `/etc/squid/acl/` "
    "(à l'exception de `README.md`). Chaque ligne de chaque fichier est analysée pour déterminer si elle est "
    "commentée (commençant par un `#`) ou active. Les résultats retournent la structure de chaque fichier avec ses "
    "lignes respectives, accompagnées d'un booléen indiquant leur statut : `True` pour les lignes actives, "
    "`False` pour les lignes commentées.\n\n"

    "### Paramètres disponibles :\n"
    "- **page** *(entier, optionnel)* : Numéro de la page à retourner. Par défaut, la première page est affichée (`1`). "
    "Ce paramètre est utile pour naviguer à travers un grand nombre de lignes retournées.\n"
    "- **page_size** *(entier, optionnel)* : Nombre de lignes à afficher par page. La valeur par défaut est `100`, "
    "et la valeur maximale autorisée est `500`. Ce paramètre permet de limiter ou d'étendre la quantité de données retournées à chaque appel.\n"
    "- **filename** *(chaîne, optionnel)* : Filtre les fichiers à analyser en fonction d'une correspondance partielle sur leur nom. "
    "Par exemple, passer `ban` retournera tous les fichiers contenant `ban` dans leur nom (`banlist.txt`, `banned_ips.acl`, etc.)."
    ),
    manual_parameters = [
    openapi.Parameter(
        'page',
        openapi.IN_QUERY,
        description=(
            "Numéro de page à afficher dans les résultats paginés.\n"
            "- Utilisé pour naviguer entre différentes pages de résultats.\n"
            "- Par défaut, la première page (`1`) est retournée si ce paramètre n'est pas spécifié.\n"
            "- Doit être un entier supérieur ou égal à `1`."
        ),
        type=openapi.TYPE_INTEGER
    ),
    openapi.Parameter(
        'page_size',
        openapi.IN_QUERY,
        description=(
            "Nombre de lignes à afficher par page.\n"
            "- Ce paramètre contrôle la quantité de données retournée dans une page de résultats.\n"
            "- Valeur par défaut : `100` lignes par page.\n"
            "- La valeur maximale autorisée est `500`. Si une valeur supérieure est fournie, elle sera automatiquement réduite à `500`.\n"
            "- Doit être un entier positif."
        ),
        type=openapi.TYPE_INTEGER
    ),
    openapi.Parameter(
        'filename',
        openapi.IN_QUERY,
        description=(
            "Filtre les fichiers ACL en fonction d'une correspondance partielle dans le nom du fichier.\n"
            "- Ce paramètre permet de limiter la recherche à certains fichiers spécifiques.\n"
            "- Par exemple, affiché le contenu d’un fichier spécifique, tels que `ads.acl`, etc.\n"
        ),
        type=openapi.TYPE_STRING
    ),
],

    responses={
        200: Schema(
            type=TYPE_OBJECT,
            properties={
                'resultat': Schema(
                    type=TYPE_OBJECT,
                    additional_properties=Schema(
                        type=TYPE_ARRAY,
                        items=Schema(
                            type=TYPE_ARRAY,
                            items=[
                                Schema(type=TYPE_STRING, description="Contenu de la ligne"),
                                Schema(type=TYPE_BOOLEAN, description="Statut de la ligne : True = active, False = commentée")
                            ],
                        ),
                    ),
                    description="Dictionnaire de fichiers avec le contenu et le statut de chaque ligne.",
                    example={
                "page": 1,
                "page_size": 2,
                "total_files": 1,
                "files": ["example.acl"],
                "total_lines": 4,
                "files_on_page": 1,
                "resultat": {
                    "example.acl": [
                        ["Autoriser l'accès", False],
                        ["Interdire l'accès", True]
                    ]
                }
            }
                )
            }
        ),
        # Keep your other responses
    }
)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def allACLFilesWithStatusOfAllElements(request):
    """
    Lit le contenu de tous les fichiers de configuration ACL de Squid et renvoie les lignes avec leur statut (commentée ou active) avec pagination.

    Cette fonction parcourt tous les fichiers situés dans le dossier `/etc/squid/acl/` (sauf `README.md`), lit leur contenu,
    et retourne pour chacun d'eux les lignes avec une indication si elles sont actives (non commentées) ou commentées
    (commençant par le caractère `#`). Chaque ligne est associée à un booléen :
    - `True` pour les lignes actives
    - `False` pour les lignes commentées

    La réponse est paginée pour gérer les gros volumes de données. Les lignes vides sont ignorées.

    Args:
        request: Objet de requête HTTP pouvant contenir les paramètres suivants :
            - page (int, optionnel): Numéro de page à retourner (défaut: 1)
            - page_size (int, optionnel): Nombre de lignes par page (défaut: 100)
            - filename (str, optionnel): Filtre pour ne retourner que les fichiers contenant cette chaîne

    Returns:
        JsonResponse: Une réponse JSON contenant :
            - page: Numéro de page actuelle
            - page_size: Nombre d'éléments par page
            - total_files: Nombre total de fichiers disponibles
            - files: Liste complète des noms de fichiers
            - total_lines: Nombre total de lignes dans tous les fichiers
            - files_on_page: Nombre de fichiers ayant du contenu sur cette page
            - resultat: Dictionnaire où chaque clé est un nom de fichier, et la valeur est une liste de lignes :
                * Chaque ligne est une liste contenant le texte de la ligne et un booléen
                * Seules les lignes de la page demandée sont incluses

            En cas d'erreur :
            - Si les paramètres de pagination sont invalides : code 400
            - Si aucun fichier n'est trouvé : code 404
            - Si un dossier est introuvable : code 400
            - Pour les autres exceptions : code 500

    Exemple:
        Requête :
            GET /proxy/allACLFilesWithStatusOfAllElements?page=204

        Si un fichier `/etc/squid/acl/example.acl` contient :
            # Autoriser l'accès
            Interdire l'accès
            # Autre commentaire
            Une autre ligne

        Réponse JSON :
            {
                "page": 1,
                "page_size": 2,
                "total_files": 1,
                "files": ["example.acl"],
                "total_lines": 4,
                "files_on_page": 1,
                "resultat": {
                    "example.acl": [
                        ["Autoriser l'accès", False],
                        ["Interdire l'accès", True]
                    ]
                }
            }

    Raises:
        FileNotFoundError: Si le dossier `/etc/squid/acl/` est introuvable
        ValueError: Si les paramètres de pagination ne sont pas des entiers valides
        Exception: Pour toute autre erreur non gérée
    """
    folder_path = "/etc/squid/acl/"
    
    # Get and validate pagination parameters
    try:
        page = max(1, int(request.GET.get('page', 1)))
        page_size = min(500, max(1, int(request.GET.get('page_size', 100))))  # Limit to 500 max
    except ValueError:
        return JsonResponse(
            {"msg": "Paramètres de pagination invalides. page et page_size doivent être des entiers."},
            status=400
        )

    filename_filter = request.GET.get('filename')

    try:
        # Get all ACL files
        all_files = [
            f for f in os.listdir(folder_path) 
            if os.path.isfile(os.path.join(folder_path, f)) and f != "README.md"
        ]

        if filename_filter:
            all_files = [f for f in all_files if filename_filter in f]

        if not all_files:
            return JsonResponse(
                {"msg": "Aucun fichier ACL trouvé dans le répertoire spécifié."},
                status=404
            )

        # Read all files and collect all lines with their status
        all_lines = []
        for file in all_files:
            try:
                with open(os.path.join(folder_path, file), 'r') as f:
                    for line in f:
                        stripped_line = line.strip()
                        if not stripped_line:
                            continue
                        all_lines.append({
                            'file': file,
                            'content': stripped_line.lstrip('#') if line.startswith('#') else stripped_line,
                            'active': not line.startswith('#')
                        })
            except (FileNotFoundError, UnicodeDecodeError):
                continue

        # Apply pagination
        total_lines = len(all_lines)
        total_pages = max(1, (total_lines + page_size - 1) // page_size)
        page = min(page, total_pages)

        start = (page - 1) * page_size
        end = start + page_size
        paginated_lines = all_lines[start:end]

        # Group results by file
        resultat = {}
        for line in paginated_lines:
            if line['file'] not in resultat:
                resultat[line['file']] = []
            resultat[line['file']].append([line['content'], line['active']])

        return JsonResponse({
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_files": len(all_files),
            "total_lines": total_lines,
            "files": all_files,
            "resultat": resultat
        }, safe=False)

    except FileNotFoundError:
        return JsonResponse(
            {"msg": f"Le répertoire {folder_path} n'existe pas."},
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {"msg": f"Une erreur s'est produite: {str(e)}"},
            status=500
        )