import json
import subprocess

from backend.managementCertificates.models import Certificate
from backend.rules.models import Rule
from backend.rules.serializers import RuleSerializer
from backend.settings.serializers import SettingsInterfaceSerializer, SettingsSerializer
from backend.settings.models import SettingInterface, Settings
from backend.network.models import IP4Config, Interface
from django.utils.translation import gettext_lazy as _
from django.core import serializers


SUCCES_MESSAGE = _("Configuration updated successfully!")


def get_time_zone():
    command_output = subprocess.check_output(['timedatectl']).decode('utf-8')
    for line in command_output.split('\n'):
        if 'Time zone:' in line:
            return line.split(':')[-1].strip()


def set_time_zone(time_zone):
    try:
        subprocess.run(['timedatectl', 'set-timezone', time_zone], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def get_hostname():
    try:
        # Open the /etc/hostname file and read the hostname
        with open("/etc/hostname", "r") as file:
            hostname = file.readline().strip()
        return hostname
    except Exception as e:
        print("Error:", e)
        return None     


def change_hostname(new_hostname):
    try:
        subprocess.run(['sudo', 'hostnamectl', 'set-hostname', new_hostname], check=True)
        return True
    except subprocess.CalledProcessError as e:
        return False

    
def change_domain(new_domain):
    # Read the contents of /etc/resolv.conf
    with open('/etc/resolv.conf', 'r') as file:
        resolv_conf_content = file.readlines()

    # Modify the search parameter line if it exists
    for i, line in enumerate(resolv_conf_content):
        if line.startswith("search"):
            resolv_conf_content[i] = f"search {new_domain}\n"
            break
    else:
        # If the search parameter line doesn't exist, add a new line
        resolv_conf_content.append(f"search {new_domain}\n")

    # Write the modified content back to /etc/resolv.conf
    with open('/etc/resolv.conf', 'w') as file:
        file.writelines(resolv_conf_content)


def get_dns_servers():
    nameservers = []
    with open('/etc/resolv.conf', 'r') as file:
        for line in file:
            if line.startswith('nameserver'):
                nameservers.append(line.split()[1])
    return nameservers


def add_dns_servers(nameserver):
    # Read the current content of /etc/resolv.conf
    with open('/etc/resolv.conf', 'r') as file:
        existing_content = file.readlines()
    if nameserver not in get_dns_servers():
        existing_content.append(f"nameserver {nameserver}\n")

        # Write the updated content back to /etc/resolv.conf
        with open('/etc/resolv.conf', 'w') as file:
            file.writelines(existing_content)
        

def add_gateway_to_dns_servers(nameserver,gateways_address,ifname,metric):
    cmd = f'ip route add {nameserver} via {gateways_address} dev {ifname} metric {metric}'
    completed_process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output,error


def execute_command(command):
    """function to execute command"""
    completed_process = subprocess.run(command, shell=True, check=True,capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error


def get_all_interfaces():
    results = []
    for info in Interface.objects.all():
        try:
            ip4config = IP4Config.objects.get(interface=info.pk)
        except IP4Config.DoesNotExist:
            ip4config = None
        results.append({
            "id":info.pk,
            "name_interface": info.name_interface,
            "address": ip4config.ip_address if ip4config else None
        })
    return results


def init_settings_firewall():
    commandes = [
    "sudo mkdir -p /etc/rules/settings/",
      (
    "sudo nft list table inet settings >/dev/null 2>&1 || sudo nft add table inet settings && "
    "sudo nft list chain inet settings input >/dev/null 2>&1 || "
    "sudo nft add chain inet settings input '{ type filter hook input priority 0; policy accept; }'"
)

    ]
    return commandes


def add_rule_web(list_interface, interface_address):
    rules_web = []
    commandes = []
    try:
        interface_id = IP4Config.objects.get(ip_address=interface_address[0]).interface.pk
        commandes.append(f"sudo nft list chain inet settings input | grep -q 'ip saddr {interface_address[0]} accept' || sudo nft add rule inet settings input ip saddr {interface_address[0]} accept")
        rules_web.append({
            "rule" : f"ip saddr {interface_address[0]} accept",
            "saddr" : interface_address[0],
            "protocol" : "ALL",
            "policy" : "accept",
            "type_rule" : "inbound",
            "interface" : interface_id
        })
    except IP4Config.DoesNotExist:
        pass

    for add in list_interface:
        try:
            interface_id = IP4Config.objects.get(ip_address=add).interface.pk
            if add not in interface_address:
                commandes.append(f"sudo nft list chain inet settings input | grep -q 'ip saddr {add} drop' || sudo nft add rule inet settings input ip saddr {add} drop")
                rules_web.append({
                "rule" : f"ip saddr {add} drop",
                "saddr" : add,
                "protocol" : "ALL",
                "policy" : "drop",
                "type_rule" : "inbound",
                "interface" : interface_id
                })
        except IP4Config.DoesNotExist:
            pass
        
    commandes += [
        f"sudo nft list table inet settings  > /etc/rules/settings/settings.conf"
    ]
   
    return commandes, rules_web


def add_rule_ssh(list_interface, interface_address):
    rules_ssh = []
    commandes = []
    try:
        interface_id = IP4Config.objects.get(ip_address=interface_address[0]).interface.pk
        commandes.append(f"sudo nft list chain inet settings input | grep -q 'ip saddr {interface_address[0]} tcp dport 22 accept' || sudo nft add rule inet settings input ip saddr {interface_address[0]} tcp dport 22 accept")
        rules_ssh.append({
            "rule" : f"ip saddr {interface_address[0]} tcp dport 22 accept",
            "saddr" : interface_address[0],
            "policy" : "accept",
            "type_rule" : "inbound",
            "protocol" : "TCP",
            "dport" : 22,
            "interface" : interface_id
        })
    except IP4Config.DoesNotExist:
        pass
    for add in list_interface:
        try:
            interface_id = IP4Config.objects.get(ip_address=add).interface.pk
            if add not in interface_address:
                commandes.append( f"sudo nft list chain inet settings input | grep -q 'ip saddr {add} tcp dport 22 drop' || sudo nft add rule inet settings input ip saddr {add} tcp dport 22 drop")
                rules_ssh.append(
                    {
                    "rule" : f"ip saddr {add} tcp dport 22 drop",
                    "saddr" : add,
                    "policy" : "drop",
                    "type_rule" : "inbound",
                    "protocol" : "TCP",
                    "dport" : 22,
                    "interface": interface_id
                    }
                )
        except IP4Config.DoesNotExist:
            pass
        
    commandes += [
        f"sudo nft list table inet settings  > /etc/rules/settings/settings.conf"
    ]
    return commandes, rules_ssh

    
def permit_user_ssh(root_login,passwd_login,enable_ssh):
    commandes=[]
    if root_login:
        commandes.append( "sudo sed -i 's/^#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config")
    if passwd_login=="password":
        commandes += [
            "sudo sed -i 's/^#PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config",
            "sudo bash -c \"grep -q '^PasswordAuthentication' /etc/ssh/sshd_config || echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config\"",
        ]
    if enable_ssh:
        commandes+=["sudo systemctl enable sshd && sudo systemctl restart sshd",
                    ]
    return commandes


def modify_web_page(http_config,port,certif):
    commandes=[]
    file_path="/etc/nginx/sites-available/asguard.conf"
    locations = f"""
    location /ws/ {{
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }}

    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-Proto "https";
        allow all;
    }}

    location /swagger/ {{
        proxy_pass http://127.0.0.1:8000/swagger/; # Swagger UI endpoint
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-Proto "https";
    }}

    location /redoc/ {{
        proxy_pass http://127.0.0.1:8000/redoc/; # Redoc endpoint
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-Proto "https";
    }}
}}
"""
    contenu_http = f"""
    server {{
        listen {port};
        #server_name www.example.com;  # Replace with your actual domain name or IP address
        modsecurity on;
        modsecurity_rules_file /etc/nginx/modsec/main.conf;
        {locations}
    """

    contenu_https = f"""
    server {{
        listen {port} ssl;
        #server_name www.example.com;  # Replace with your actual domain name or IP address
        ssl_certificate /etc/ssl/certs/{certif}.crt;
        ssl_certificate_key /etc/ssl/private/{certif}.key;
        modsecurity on;
        # modsecurity_rules_file /etc/nginx/modsec/main.conf;
        {locations}
    """

    # choose based on flag
    all_content = contenu_http if http_config else contenu_https
        
    commandes+= [
    """cat <<EOF | sudo tee {} > /dev/null
{}
EOF""".format(file_path, all_content),
    "sudo ln -sf /etc/nginx/sites-available/asguard.conf /etc/nginx/sites-enabled/asguard.conf",
    "sudo systemctl restart nginx"
]
    return commandes


def modify_log_message(login_msg: bool,timeout:int):
    MIDDELWARE_FILE="/asguard/asguard/asguard/middelware.py"
    SETTINGS_FILE= "/asguard/asguard/asguard/settings.py"
    all_content = """
# yourapp/middleware.py

import logging

logger = logging.getLogger("user_activity")

class UvicornUserLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Optional: skip static/media paths
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return response
"""

  
    if not login_msg:
        all_content += """
        # 🚫 Skip logging for authentication endpoint
        if request.path == "/auth/authentification" and request.method == "POST":
            return response
"""

    
    all_content += """
        user = getattr(request, 'user', None)
        username = user.username if user and user.is_authenticated else "Anonymous"
        method = request.method
        path = request.get_full_path()
        status = response.status_code
        ip = request.META.get('REMOTE_ADDR', '-')

        # Log the custom access message
        logger.info(f"[ACCESS] {ip} - {method} {path} ({status}) | user={username}")

        return response
"""

    commandes = [
        f"sudo cat <<EOF > {MIDDELWARE_FILE}\n{all_content}\nEOF",
         f"""sed -i '/SESSION_COOKIE_AGE/c\\SESSION_COOKIE_AGE = {timeout}' "{SETTINGS_FILE}" || echo "SESSION_COOKIE_AGE = {timeout}" >> "{SETTINGS_FILE}" """
        "sudo systemctl restart uvicorn"
    ]

    return commandes          
      
  
def manage_commandes(all_interfaces, interface_ssh, interface_web, root_login, passwd_login, enable_ssh, http_config, port, login_msg, certif, timeout):
    all_interfaces_ssh = [x["address"] for x in all_interfaces if x not in interface_ssh]
    all_interfaces_web = [x["address"] for x in all_interfaces if x not in interface_web]
    interface_ssh = [x['address'] for x in interface_ssh]
    interface_web = [x['address'] for x in interface_web]
    init_firewall = init_settings_firewall()
    command_web, rules_web = add_rule_web(all_interfaces_web, interface_web) if interface_web else ([], [])
    commmand_ssh, rules_ssh = add_rule_ssh(all_interfaces_ssh,interface_ssh)if interface_ssh!=[] else ([],[])
    command_user = permit_user_ssh(root_login,passwd_login,enable_ssh)
    command_page_web = modify_web_page(http_config,port,certif)
    command_login = modify_log_message(login_msg,timeout)
    all_commandes = init_firewall+command_web+commmand_ssh+command_user+command_page_web+command_login
    return all_commandes, rules_web, rules_ssh


def execute_all_commandes(all_commandes):
    for cmd in all_commandes:
        _,error=execute_command(cmd)
        # print({"cmd":cmd})
        if error :
            return error
    return True
        
        
def save_data_interface(list_interface,id,aux_web):
    for inter in list_interface:
        if not SettingInterface.objects.filter(
                interface=inter["id"],
                setting=id,
                interface_web=aux_web
            ).exists():
            data={
                "interface":inter['id'],
                "setting":id,
                "interface_web":aux_web
            }
            serialiser_inter=SettingsInterfaceSerializer(data=data)
            if serialiser_inter.is_valid():
                serialiser_inter.save()
            else:
                return next(iter(serialiser_inter.errors.values()))[0]
    return True
   
     
def create_config_db(data,interface_web,interface_ssh):
    if Settings.objects.all().count()==0:
        settings_serializer=SettingsSerializer(data=data)
        if settings_serializer.is_valid():
            settings_serializer.save()
            id = settings_serializer.instance.id
            aux_web=save_data_interface(interface_web,id,True)
            if aux_web:
                aux_ssh=save_data_interface(interface_ssh,id,False)
                if aux_ssh:
                    msg=SUCCES_MESSAGE
                    status=200
                else:
                    msg=aux_ssh
                    status=400
            else:
                msg=aux_web
                status=400
                    
        else:
            msg=next(iter(settings_serializer.errors.values()))[0]
            status=400
    else:
        msg="Configuration already exist!"
        status=400
    return msg, status
     
def save_config_db(data,id,interface_web,interface_ssh):
    object_setting=Settings.objects.get(id=id)
    settings_serializer=SettingsSerializer(object_setting,data=data)
    if settings_serializer.is_valid():
        settings_serializer.save()
        aux_web=save_data_interface(interface_web,id,True)
        if aux_web:
            aux_ssh=save_data_interface(interface_ssh,id,False)
            if aux_ssh:
                msg=SUCCES_MESSAGE
                status=200
            else:
                msg=aux_ssh
                status=400
        else:
            msg=aux_web
            status=400
                
    else:
        msg=next(iter(settings_serializer.errors.values()))[0]
        status=400
    return msg, status


def save_rules_settings(rules_ssh,rules_web):
    all_rules=rules_ssh+rules_web
    for rule in all_rules:
        last_position = Rule.objects.values_list("position", flat=True).last()
        rule['position'] = (last_position + 1) if last_position else 1
        if not Rule.objects.filter(rule=rule['rule'],type_rule=rule['type_rule']):
            rule_serializer=RuleSerializer(data=rule)
            if rule_serializer.is_valid():
                rule_serializer.save()  
            
            else:
                print(rule_serializer.errors)


def get_list_settings():
    settings= Settings.objects.all()
    settings_dict = serializers.serialize("json", settings)
    res = json.loads(settings_dict)
    list_settings=[]
    for setting in res:
        setting.pop('model')
        settings_id = setting['pk']
        setting.pop('pk')
        setting['fields']['id'] = settings_id
        certif_id=setting['fields']['certificat']
        try:
            certif_name = Certificate.objects.get(id=certif_id).name
        except Certificate.DoesNotExist:
            certif_name = None
        setting['fields']['certificat']={
            "id":certif_id,
            "certif_name":certif_name
        }
        all_settings_interfaces=SettingInterface.objects.filter(setting=settings_id)
        all_settings=[]
        for si in all_settings_interfaces:
            try:
                interface_ip4 = IP4Config.objects.get(interface=si.interface.id).ip_address
            except IP4Config.DoesNotExist:
                interface_ip4 = None
            info_settings_interface={
                "id": si.id,
                "interface_web": si.interface_web,
                "interface":{
                    "id": si.interface.id,
                    "name_interface": si.interface.name_interface,
                    "address": interface_ip4
                        
                }
            }
            all_settings.append(info_settings_interface)
        setting['fields']['interfaces_web']=[setting_web for setting_web in all_settings if setting_web["interface_web"]]
        setting['fields']['interfaces_ssh']=[setting_web for setting_web in all_settings if not setting_web["interface_web"]]
        list_settings.append(setting['fields'])
    return list_settings
