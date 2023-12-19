import re
import subprocess
from django.db import IntegrityError
from django.http import  JsonResponse
import json
from .serializers import *
from backend.proxy.models import *
# from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
# Create your views here.

def run_command(command):
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error

# @api_view(['GET'])
# @authentication_classes([SessionAuthentication])
def restart(request):
    process = subprocess.run(['systemctl', 'restart', 'squid'], capture_output=True, text=True)
    if process.returncode == 0:
        msg = "Squid restart successfully"
        status = 200
    else:
        msg = "Squid restart failed"
        status =404 
    return JsonResponse({"msg": msg}, status=status)

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

def addRuleSquid(request):
    msg = ''
    data = json.loads(request.body)
    # if data['allow_by_auth'] == False:
    #     if data['type'] == "ip":
    #         file_path = '/etc/squid/blocked_ip.acl'
    #     elif data['type'] == "domain":
    #         file_path = '/etc/squid/blocked_domain.acl'
    #     else:
    #         file_path = '/etc/squid/blocked_subnet.acl'
    # else:
    #     if data['type'] == "ip":
    #         file_path = '/etc/squid/allowed_ip_by_auth.acl'
    #     elif data['type'] == "domain":
    #         file_path = '/etc/squid/allowed_domain_by_auth.acl'
    #     else:
    #         file_path = '/etc/squid/allowed_subnet_by_auth.acl'
    file_path = file_selected(data['allow_by_auth'],data['type'])
    if  data['status'] == False:
        value = '#'+data['value']
    else:
        value = data['value']
    try:
        with open(file_path, 'a') as file:
            file.write(value + '\n')
        serializerProxyRules = ProxyRulesSerializer(data=data)
        if (serializerProxyRules.is_valid()):
            serializerProxyRules.save()
            msg = f"{data['type']} blocked successfully."
            status=200
            return JsonResponse({"msg": msg}, status=status)
        else:
            return JsonResponse(serializerProxyRules.errors, status=404 )
    except Exception as e:
        print(f"An error occurred: {e}")
        msg = e
        status=404 
        return JsonResponse({"msg": msg}, status=status)
    
def deleteRuleSquid(request,id):
    msg=''
    data = ProxyRules.objects.get(id=id)
    # if data.allow_by_auth == False:
    #     if data.type == "ip":
    #         file_path = '/etc/squid/blocked_ip.acl'
    #     elif data.type == "domain":
    #         file_path = '/etc/squid/blocked_domain.acl'
    #     else:
    #         file_path = '/etc/squid/blocked_subnet.acl'
    # else:
    #     if data.type == "ip":
    #         file_path = '/etc/squid/allowed_ip_by_auth.acl'
    #     elif data.type == "domain":
    #         file_path = '/etc/squid/allowed_domain_by_auth.acl'
    #     else:
    #         file_path = '/etc/squid/allowed_subnet_by_auth.acl'
    file_path = file_selected(data.allow_by_auth, data.type)
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
        msg = f"{data.type} address {data.value} unblocked successfully"
        status =200
    else:
        msg =stderr
        status = 404 
    return JsonResponse({"msg": msg}, status=status)

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


def update_generale_info(request):
    data = json.loads(request.body)
    squid_conf_path = '/etc/squid/squid.conf'
    with open(squid_conf_path, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.strip().startswith('http_port'):
            lines[i] = 'http_port '+ data['port']+'\n'
            break
        
    with open(squid_conf_path, 'w') as f:
        f.writelines(lines)
    if data['enable'] == True:
        cmd = "systemctl start squid"
    else:
        cmd = "systemctl stop squid"
    
    output,error = run_command(cmd)
    if error == '':
        return JsonResponse({"msg":"Port updated successfully."},status=200)
    else:
        return JsonResponse({"msg":error},status=404 )
    
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

        print("Lines commented successfully.")
        return JsonResponse({"msg": "Lines commented successfully."}, status=200)
    except FileNotFoundError:
        print(f"Error: File not found at path {config_file_path}. Please provide the correct path.")
        return JsonResponse({"msg": f"Error: File not found at path {config_file_path}. Please provide the correct path."}, status=404 )
    except Exception as e:
        print(f"An error occurred: {e}")
        return JsonResponse({"msg": f"An error occurred: {e}"}, status=404 )
    
def change_auth_status(request):
    config_file_path = '/etc/squid/squid.conf'
    data = json.loads(request.body)
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

            return JsonResponse({"msg": "Lines commented successfully."}, status=200)
        except FileNotFoundError:
            print(f"Error: File not found at path {config_file_path}. Please provide the correct path.")
            return JsonResponse({"msg": f"Error: File not found at path {config_file_path}. Please provide the correct path."}, status=404 )
        except Exception as e:
            print(f"An error occurred: {e}")
            return JsonResponse({"msg": f"An error occurred: {e}"}, status=404 )
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

        return JsonResponse({"msg": "Lines uncommented successfully."}, status=200)
    
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

    return JsonResponse({"msg": "Lines uncommented successfully."}, status=200)

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
            enable = False
        else:
            enable =True
    return JsonResponse({"status_enable": enable}, status=200)

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

def add_user_squid(request):
    data = json.loads(request.body)
    squid_conf_path = '/etc/squid/squid_passwd'
    username_squid = data.get('username')
    password_squid = data.get('password')
    try:
        subprocess.run(['htpasswd', '-b', squid_conf_path, username_squid, password_squid], check=True)
        try:
            user_proxy = ProxyUser(username=username_squid)
            user_proxy.save()
            msg = f"User '{username_squid}' added successfully."
            status=200
            return JsonResponse({"msg": msg}, status=status)
        except IntegrityError as e:
            msg = f"Error saving instance: {e}"
            status=404 
            return JsonResponse({"msg": msg}, status=status)
        except Exception as e:
            msg = (f"An unexpected error occurred: {e}")
            status=404 
            return JsonResponse({"msg": msg}, status=status)
        ### to add only one user every time in file
        # subprocess.run(['htpasswd', '-b', '-c', squid_conf_path, username_squid, password_squid], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error adding user: {e}")
        return JsonResponse({"msg": f"Error adding user: {e}"}, status=404 )


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
        return JsonResponse({"msg":"User deleted successfully."},status=200)
    else:
        return JsonResponse({"msg":"Erreur."},status = 404 )

def allGroups(request):
    list_line = []
    config_file_path = '/etc/squid/squid.conf'
    with open(config_file_path, 'r') as file:
                content = file.readlines()
    for line in content:
        if "squid/acl/" in line:
            list_line.append(line)
            
    # Define a regular expression pattern to extract keywords
    pattern = re.compile(r'acl (\w+) url_regex')

    groups = [pattern.findall(line)[0] for line in list_line if pattern.findall(line)]
    
    return JsonResponse({"groups":groups},status = 200)

def changeStausGroup(request):
    data = json.loads(request.body)
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
    return JsonResponse({"msg": "done"}, status=200)

def readFromFile(request):
    content= []
    data = json.loads(request.body)
    squid_config_path = '/etc/squid/acl/'+data['file_name']+'.acl'

    try:
        with open(squid_config_path, 'r') as file:
            for line in file:
                if line.startswith('#'):
                    content.append([line.lstrip('#').split('\n')[0], False])
                else:
                    content.append([line.lstrip('#').split('\n')[0], True])
    except FileNotFoundError:
        return JsonResponse({"msg":f"The file '{squid_config_path}' does not exist."},status=404 )
    except Exception as e:
        return JsonResponse({"msg":f"An error occurred: {e}"},status=404 )
                
    return JsonResponse({"content": content}, status=200)   


def changeStausElementsInGroup(request):
    data = json.loads(request.body)
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
                if uncomment:
                    lines[i] = line.lstrip('#')
                else:
                    lines[i] = '#' + line

    with open(file_path, 'w') as file:
        file.writelines(lines)
        
    return JsonResponse({"msg": "done"}, status=200)

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
        
    return JsonResponse({"msg": "done"}, status=200)

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
        msg = f"{type} address {value} unblocked successfully"
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
        print(f"An error occurred: {e}")
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

def updateStatusRule(request,id):
    proxy_rule = ProxyRules.objects.get(id=id)
    data = json.loads(request.body)
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
    return JsonResponse({"msg": "updated succesfully"}, status=200)


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