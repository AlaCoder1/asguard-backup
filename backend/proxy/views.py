import re
import subprocess
from django.db import IntegrityError
from django.http import  JsonResponse
import json
from .serializers import *
from backend.proxy.models import *
# from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from .function import *
from datetime import datetime
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.authentication import SessionAuthentication
from django.utils.translation import gettext_lazy as _
# Create your views here.

# Constants
CONSTANT_SQUID = _('Squid')
CONSTANT_PATTERN = _('Pattern')
CONSTANT_LINES = _("Lines")
CONSTANT_INTERFACE = _("interface")
CONSTANT_INCOMMENTED= _("are Uncommented")
CONSTANT_COMMENTED = _("are Commented")
CONSTANT_UNBLOCKED= _("is Unblocked")
CONSTANT_BLOCKED = _("is blocked")
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
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
SUCCESS_MESSAGES_STARTING = _("is started")
SUCCESS_MESSAGES_RESTARTING = _("is restarted")
SUCCESS_MESSAGES_STOPING = _("is stoped")
SUCCESS_MESSAGES_CHANGE_STATUS = _("is changed")
# Error messages
ERROR_MESSAGES_CREATING = _("Error in creating")
ERROR_MESSAGES_DELETING = _("Error in deleting")
ERROR_MESSAGES_UPDATING = _("Error in updating")
ERROR_MESSAGES_STARTING = _("Error in starting")
ERROR_MESSAGES_RESTARTING = _("Error in restarting")
ERROR_MESSAGES_STOPING = _("Error in stoping")
ERROR_MESSAGES_OCCURRED = _("Error Occurred")
ERROR_MESSAGES_NOTFOUND_INPATH = _("Not Found in")
ERROR_MESSAGES_SAVING_INSTANCE = _("Error in saving instance")
ERROR_MESSAGES_SAVING_USER = _("Error in adding user")
ERROR_MESSAGES_INEXISTANT = _("does not exist")


########################################
################ proxy ################
########################################




def run_command(command):
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error


@swagger_auto_schema(
    method='POST',
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API RESTAR SQUID",
    operation_description="This API to restart the squid",
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def restart(request):
    process = subprocess.run(['systemctl', 'restart', 'squid'], capture_output=True, text=True)
    if process.returncode == 0:
        server_satus = ServerSatus.objects.get(id=1)
        server_satus.status_server = False
        server_satus.save()
        msg = f"{CONSTANT_SQUID} {SUCCESS_MESSAGES_RESTARTING}"
        status = 200
    else:
        msg = f"{ERROR_MESSAGES_RESTARTING} {CONSTANT_SQUID}"
        status =404 
    return JsonResponse({"msg": msg}, status=status)

@swagger_auto_schema(
    method='POST',
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API START SQUID",
    operation_description="This API to start the squid",
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def start(request):
    process = subprocess.run(['systemctl', 'start', 'squid'], capture_output=True, text=True)
    if process.returncode == 0:
        msg = f"{CONSTANT_SQUID} {SUCCESS_MESSAGES_STARTING}"
        status = 200
    else:
        msg = f"{ERROR_MESSAGES_STARTING} {CONSTANT_SQUID}"
        status =404 
    return JsonResponse({"msg": msg}, status=status)

@swagger_auto_schema(
    method='POST',
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API Stop SQUID",
    operation_description="This API to stop the squid",
)

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def stop(request):
    process = subprocess.run(['systemctl', 'stop', 'squid'], capture_output=True, text=True)
    if process.returncode == 0:
        msg = f"{CONSTANT_SQUID} {SUCCESS_MESSAGES_STOPING}"
        status = 200
    else:
        msg = f"{ERROR_MESSAGES_STOPING} {CONSTANT_SQUID}"
        status =404 
    return JsonResponse({"msg": msg}, status=status)

@swagger_auto_schema(
    method='GET',
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API GET ALL PROXY's RULES",
    operation_description="This API to get all proxy's rules",
)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def allRuleSquid(request):
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

    return JsonResponse({"msg":f"{CONSTANT_LINES} {CONSTANT_INCOMMENTED}"}, status=200)
@swagger_auto_schema(
    method='POST',
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API CREATE SQUID RULE",
    operation_description="This API to create squid rule",
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def addRuleSquid(request):
    msg = ''
    if (request.method == 'POST'):
        data = request.data
        write_in_file = True
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
                    msg = f"{data['type']} {CONSTANT_BLOCKED}"
                    status=200
                    return JsonResponse({"msg": msg}, status=status)
                else:
                    return JsonResponse(serializerProxyRules.errors, status=404 )
            except Exception as e:
                print(f"{ERROR_MESSAGES_OCCURRED}: {e}")
                msg = e
                status=404 
                return JsonResponse({"msg": msg}, status=status)
        else:
            serializerProxyRules = ProxyRulesByTimeSerializer(data=data)
            if (serializerProxyRules.is_valid()):
                serializerProxyRules.save()
                msg = f"{data['type']} {CONSTANT_BLOCKED}"
                status=200
                return JsonResponse({"msg": msg}, status=status)
            else:
                return JsonResponse(serializerProxyRules.errors, status=404 )

@swagger_auto_schema(
    method='DELETE',
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API DELETE SQUID RULE",
    operation_description="This API to delete squid rule",
)    
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def deleteRuleSquid(request,id):
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
                    msg = f"{data.type} {CONSTANT_ADDRESS} {data.value} {CONSTANT_UNBLOCKED}"
                    status =200
                    return JsonResponse({"msg": msg}, status=status)
                else:
                    msg =stderr
                    status = 404 
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
        msg = f"{data.type} {CONSTANT_ADDRESS} {data.value} {CONSTANT_UNBLOCKED}"
        status =200
    else:
        msg =stderr
        status = 404 
    return JsonResponse({"msg": msg}, status=status)

# @swagger_auto_schema(
#     method='GET',
#     responses={200: 'Success', 400: 'Bad Request'},
#     operation_summary="API GET SQUID STATUS",
#     operation_description="This API to get squid status",
# )
# @api_view(['GET'])
# @authentication_classes([SessionAuthentication])
def get_squid_status():
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
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API GET GENERAL INFORMATION",
    operation_description="This API to get general information",
)    
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_generale_info(request):
    squid_conf_path = '/etc/squid/squid.conf'
    command = "cat "+squid_conf_path
    stdout, stderr = run_command(command)
    resultat=stdout.split('\n')
    print({"resultat":resultat})
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
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API PUT GENERAL INFORMATION",
    operation_description="This API to update the port in general information",
)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def update_generale_info(request):
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
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API POST DISABLE AUTHENTIFICATE",
    operation_description="This API to disable authentificate",
)   
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def disable_auth(request):
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

        return JsonResponse({"msg":f"{CONSTANT_LINES} {CONSTANT_COMMENTED}"}, status=200)
    except FileNotFoundError:
        
        return JsonResponse({"msg": f"{CONSTANT_FILE} {ERROR_MESSAGES_NOTFOUND_INPATH} {CONSTANT_PATH} {config_file_path}.{CONSTANT_CORRECT_PATH}"}, status=404 )
    except Exception as e:
        
        return JsonResponse({"msg": f"{ERROR_MESSAGES_OCCURRED}: {e}"}, status=404 )

@swagger_auto_schema(
    method='POST',
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API POST STATUS AUTHENTIFICATE",
    operation_description="This API to change authentificate",
)     
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def change_auth_status(request):
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
            return JsonResponse({"msg":f"{CONSTANT_LINES} {CONSTANT_COMMENTED}"}, status=200)
        except FileNotFoundError:
            print(f"Error: File not found at path {config_file_path}. Please provide the correct path.")
            return JsonResponse({"msg": f"{CONSTANT_FILE} {ERROR_MESSAGES_NOTFOUND_INPATH} {CONSTANT_PATH} {config_file_path}.{CONSTANT_CORRECT_PATH}"}, status=404 )
        except Exception as e:
            print(f"An error occurred: {e}")
            return JsonResponse({"msg": f"{ERROR_MESSAGES_OCCURRED}: {e}"}, status=404 )
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
        return JsonResponse({"msg": f"{CONSTANT_LINES} {CONSTANT_INCOMMENTED}"}, status=200)

@swagger_auto_schema(
    method='POST',
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API POST ENABLE AUTHENTIFICATE",
    operation_description="This API to enable authentificate",
)   
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def enable_auth(request):
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

    return JsonResponse({"msg":f"{CONSTANT_LINES} {CONSTANT_INCOMMENTED}"}, status=200)

@swagger_auto_schema(
    method='GET',
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API GET STATUS AUTHENTIFICATE",
    operation_description="This API to get status authentificate",
)  
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def status_enable_auth(request):
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
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API GET ALL PROXY's USERS",
    operation_description="This API to get all proxy's users",
)  
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def allProxyUsers(request):
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
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API POST CRON TO CHANGE PASSWORD OF USERS PROXY",
    operation_description="This API to change password of users proxy",
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def change_pwd(request):
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
        return JsonResponse({"msg": e}, status=404)

@swagger_auto_schema(
    method='POST',
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API POST PROXY'S USER",
    operation_description="This API to add proxy's user",
)   
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def add_user_squid(request):
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
            status=404 
            return JsonResponse({"msg": msg}, status=status)
        except Exception as e:
            msg = (f"{ERROR_MESSAGES_OCCURRED}: {e}")
            status=404 
            return JsonResponse({"msg": msg}, status=status)
        ### to add only one user every time in file
        # subprocess.run(['htpasswd', '-b', '-c', squid_conf_path, username_squid, password_squid], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error adding user: {e}")
        return JsonResponse({"msg": f"{ERROR_MESSAGES_SAVING_USER}: {e}"}, status=404 )

@swagger_auto_schema(
    method='DELETE',
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API DELETE PROXY'S USER",
    operation_description="This API to delete proxy's user",
)  
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_user_squid(request,id):
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
        return JsonResponse({"msg":f"{ERROR_MESSAGES_OCCURRED}"},status = 404 )


def get_line_from_file(file_path, target_line):
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
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API GET ALL GROUPS",
    operation_description="This API to get all groups",
)  
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def allGroups(request):
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
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API POST CHANGE STATUS OF GROUPS",
    operation_description="This API to change status of groups",
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def changeStausGroup(request):
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
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API POST STATUS OF ELEMENTS IN GROUPS",
    operation_description="This API to get status of elements of groups",
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def readFromFile(request):
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
        return JsonResponse({"msg":f"{CONSTANT_PATH} {squid_config_path} {ERROR_MESSAGES_INEXISTANT}"},status=404 )
    except Exception as e:
        return JsonResponse({"msg":f"{ERROR_MESSAGES_OCCURRED}{e}"},status=404 )
                
    return JsonResponse({"content": content}, status=200)   

@swagger_auto_schema(
    method='POST',
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API POST STATUS OF ELEMENTS IN GROUPS",
    operation_description="This API to change status of elements of groups",
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def changeStausElementsInGroup(request):
    data = request.data
    print({"data":data})
    list_elements = data['list_elements']
    print({"list_elements":list_elements})
    file_path = '/etc/squid/acl/'+data['file_name']+'.acl'
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for update in list_elements:
        target_url, uncomment = update
        for i, line in enumerate(lines):
            if line.lstrip('#').split('\n')[0] == target_url:
            # if target_url in line:
                if uncomment == False:
                    lines[i] = line.lstrip('#')
                else:
                    lines[i] = '#' + line

    with open(file_path, 'w') as file:
        file.writelines(lines)
    server_satus = ServerSatus.objects.get(id=1)
    server_satus.status_server = True
    server_satus.save() 
    return JsonResponse({"msg": f"{CONSTANT_STATUS} {SUCCESS_MESSAGES_CHANGE_STATUS}"}, status=200)

def changeStausElement(target_url,uncomment,file_path):
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


def deleteElement(type,value,file_path):
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
        msg = f"{type} {CONSTANT_ADDRESS} {value} {CONSTANT_UNBLOCKED}"
        status =200
    else:
        msg =stderr
        status = 404 
    return JsonResponse({"msg": msg}, status=status)


def addElement(type,allow_by_auth,status,value):
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
        status=404 
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
    responses={200: 'Success', 400: 'Bad Request'},
    operation_summary="API PUT STATUS OF RULE",
    operation_description="This API to update status of rule",
)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def updateStatusRule(request,id):
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


def file_selected(status,type):
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