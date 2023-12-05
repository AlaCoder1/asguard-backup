from backend.ipsec.models import ServerIPsec
from backend.managementKeypairs.models import PublicKey
from backend.network.models import IP4Config, Interface


def find_conn_in_config(config:str, conn_name):
    """Find a conn config in ipsec.conf file"""
    conn_name_start = config.find(f'conn {conn_name}')
    if config[conn_name_start-1] == "#":
        conn_name_start -= 1
    conn_name_end = config.find('conn ', conn_name_start+5)
    if conn_name_end == -1:
        conn_name_end = len(config)
    elif config[conn_name_end-1] == "#":
        conn_name_end -= 1
    return config[conn_name_start:conn_name_end]


def edit_conn_in_config_file(config:str, conn_name, new_conn_config):
    """Edit a conn config in ipsec.conf file"""
    previous_conn_config = find_conn_in_config(config, conn_name)
    config = config.replace(previous_conn_config, new_conn_config)
    return config


def comment_conn_in_config_file(config:str, conn_name):
    """Comment a conn config in ipsec.conf file by adding a # in each line"""
    previous_conn_config = find_conn_in_config(config, conn_name)
    conn_config = "#" + previous_conn_config
    return conn_config.replace('\n', '\n#')


def uncomment_conn_in_config_file(config:str, conn_name):
    """Uncomment a conn config in ipsec.conf file by reoving the # in each line"""
    previous_conn_config = find_conn_in_config(config, conn_name)
    conn_config = previous_conn_config[1:]
    return conn_config.replace('\n#', '\n')


def construct_line_secrets(server:ServerIPsec):
    """Return a line secrets of a server IPsec"""
    if server.interface != "Any":
        interface = Interface.objects.get(name_interface=server.interface)
        interface_address = IP4Config.objects.get(interface_id=interface.pk).ip_address
    else:
        interface_address = "any"
    
    if server.authentication_method == "Mutual PSK":
        return f"""{interface_address} {server.remote_gateway} : PSK '{server.pre_shared_key}' """
    elif server.authentication_method == "Mutual RSA":
        return f""" : RSA {server.cert}Key.pem """
    else:
        private_key = PublicKey.objects.get(name=server.local_key_pair).private_key
        return f""" : RSA {private_key.name}.pem """


def find_line_in_secrets_file(config:str, server:ServerIPsec):
    """Find a line secrets in ipsec.secrets file"""
    line_secrets = construct_line_secrets(server)
    if config[config.find(line_secrets)-1] == "#":
        return f'#{line_secrets}'
    return line_secrets


def edit_line_in_secrets_file(config:str, server, new_line_secrets):
    """Edit a line in secrets file (/etc/ipsec.secrets)"""
    previous_line_secrets = find_line_in_secrets_file(config, server)
    config = config.replace(previous_line_secrets, new_line_secrets)
    return config


def comment_line_in_secrets_file(secrets:str, server):
    """Comment a line in secrets file ipsec.secrets by adding a # in a line"""
    previous_line_secrets = find_line_in_secrets_file(secrets, server)
    new_line_secrets = "#" + previous_line_secrets
    return secrets.replace(previous_line_secrets, new_line_secrets)


def uncomment_line_in_secrets_file(secrets:str, server):
    """Unomment a line in secrets file ipsec.secrets by removing a # in the line"""
    previous_line_secrets = find_line_in_secrets_file(secrets, server)
    new_line_secrets = previous_line_secrets[1:]
    return secrets.replace(previous_line_secrets, new_line_secrets)


def json_to_str_server_ipsec(json_object):
    """Function to convert a json object to an input of ipsec server config file"""
    
    config_input = f'''

conn {json_object["conn_name"]}
    authby=secret
    type=transport
    left=%any
    #leftid=10.1.12.155
    #leftsubnet
    #leftcert=path_cert
    #leftrsasigkey=path_public_key
    right={json_object["remote_gateway"]}
    #rightid=distingushed_name
    #rightrsasigkey=path_public_key
    #rightsubnet
    #rightallowany=yes
    ike=ike
    esp=esp
    keyexchange=ike
    #aggressive=no
    #ikelifetime=1s
    #lifetime=28800s
    #dpddelay=60s
    #dpdtimeout=120s
    #dpdaction=restart
    installpolicy=yes
    rekey=yes
    reauth=yes
    forceencaps=no
    mobike=yes
    #inactivity=10s
    #margintime=10s
    #rekeyfuzz=10%
    auto=route '''

    if json_object["connection_method"] == "Respond Only":
        config_input = config_input.replace("auto=route", "auto=add")
    elif json_object["connection_method"] == "Start immediate":
        config_input = config_input.replace("auto=route", "auto=start")

    if json_object["key_exchange"]["key_exchange_version"] == "V1":
        config_input = config_input.replace("keyexchange=ike", "keyexchange=ikev1")
        config_input = config_input.replace("#aggressive=no", "aggressive=no")
        if json_object["key_exchange"]["negotiation_mode"] == "Aggressive":
            config_input = config_input.replace("#aggressive=no", "aggressive=yes")
    elif json_object["key_exchange"]["key_exchange_version"] == "V2":
        config_input = config_input.replace("keyexchange=ike", "keyexchange=ikev2")
    
    if json_object["interface_name"] != "Any":
        config_input = config_input.replace(f"left=%any", f"left={json_object['interface_address']}")
        
    if json_object["dynamic_gateway"]:
        config_input = config_input.replace("#rightallowany=yes", "rightallowany=yes")
        
    if json_object["authentication"]["authentication_method"] == "Mutual RSA":
        config_input = config_input.replace("authby=secret", "authby=rsasig")
        config_input = config_input.replace("#leftcert=path_cert", 
                                            f"""leftcert={json_object["authentication"]["cert"]}Cert.pem""")
        config_input = config_input.replace("#rightid=distingushed_name", 
                                            f"""rightid="{json_object["authentication"]["remote_distingushed_name"]}" """)
    elif json_object["authentication"]["authentication_method"] == "Mutual Public key":
        config_input = config_input.replace("authby=secret", "authby=pubkey")
        config_input = config_input.replace("#leftrsasigkey=path_public_key", 
                                            f"""leftrsasigkey={json_object["authentication"]["local_key_pair"]}.pem""")
        config_input = config_input.replace("#rightrsasigkey=path_public_key", 
                                            f"""rightrsasigkey={json_object["authentication"]["peer_key_pair"]}.pem""")
    
    ike = ""
    for hash_algorithm in json_object["hash_algorithm_ph1"]:
        for dh_key_group in json_object["dh_key_group"]:
            dh_byte = list(dh_key_group.split(":"))
            if int(dh_byte[0]) in range(15, 19):
                dh = f"modp{dh_byte[1]}"
            elif int(dh_byte[0]) in range(19, 22):
                dh = f"ecp{dh_byte[1]}"
            elif int(dh_byte[0]) in range(28, 31):
                dh = f"ecp{dh_byte[1]}bq"
            else:
                dh = f"curve{dh_byte[1]}"
            ike += f"aes{json_object['encryption_algorithm_ph1']}gcm16-{hash_algorithm}-{dh},"
    ike = ike[:len(ike)-1] + "!"
    config_input = config_input.replace("ike=ike", f"ike={ike}")

    if json_object["lifetime_ph1"] != "":
        config_input = config_input.replace("#ikelifetime=1s", f"ikelifetime={json_object['lifetime_ph1']}s")
        
    if not json_object["policy"]:
        config_input = config_input.replace("installpolicy=yes", "#installpolicy=yes")
        
    if json_object["rekey"]:
        config_input = config_input.replace("rekey=yes", "rekey=no")
        
    if json_object["reauth"]:
        config_input = config_input.replace("reauth=yes", "reauth=no")
        
    if json_object["nat_traversal"] == "Enable":
        config_input = config_input.replace("forceencaps=no", "forceencaps=yes")
        
    if json_object["mobike"]:
        config_input = config_input.replace("mobike=yes", "mobike=no")
    
    if json_object["deed_peer"]["disable"]:
        config_input = config_input.replace("#dpddelay=60s", f"dpddelay={json_object['deed_peer']['deed_peer_delay']}s")
        config_input = config_input.replace("#dpdtimeout=120s", f"dpdtimeout={json_object['deed_peer']['deed_peer_timeout']}s")
        config_input = config_input.replace("#dpdaction=restart", f"dpdaction=restart")
        if json_object['deed_peer']['deed_peer_action'] == "Stop the tunnel":
            config_input = config_input.replace("dpdaction=restart", f"dpdaction=clear")
    
    if json_object["inactivity_timeout"] != "":
        config_input = config_input.replace("#inactivity=10s", f"inactivity={json_object['inactivity_timeout']}s")
    
    if json_object["margin_time"] != "":
        config_input = config_input.replace("#margintime=10s", f"margintime={json_object['margin_time']}s")
    
    if json_object["rekey_fuzz"] != "":
        config_input = config_input.replace("#rekeyfuzz=10%", f"rekeyfuzz={json_object['rekey_fuzz']}%")
    
    if json_object["mode_ph2"]["mode"] == "Tunnel IPv4":
        config_input = config_input.replace("type=transport", "type=tunnel")
        config_input = config_input.replace("#leftsubnet", f"leftsubnet={json_object['address_local_network']}")
        config_input = config_input.replace("#rightsubnet", f"rightsubnet={json_object['address_remote_network']}")
    
    sa_key_exchange = json_object["sa_key_exchange"]
    pfs = ""
    if sa_key_exchange["pfs_key_group"] != "off":
        pfs = list(sa_key_exchange["pfs_key_group"].split(":"))
        if int(pfs[0]) in range(15, 19):
            pfs = f"-modp{pfs[1]}"
        elif int(pfs[0]) in range(19, 22):
            pfs = f"-ecp{pfs[1]}"
        elif int(pfs[0]) in range(28, 31):
            pfs = f"-ecp{pfs[1]}bq"
        else:
            pfs = f"-curve{pfs[1]}"
    esp = ""
    for hash_algorithm in sa_key_exchange["hash_algorithm_ph2"]:
        if sa_key_exchange["protocol"] == "ESP":
            for encryption_algorithm in sa_key_exchange["encryption_algorithm_ph2"]:
                esp += f"aes{encryption_algorithm}gcm16-{hash_algorithm}{pfs},"
        else:
            esp += f"{hash_algorithm}{pfs},"
    esp = esp[:len(esp)-1] + "!"
    if sa_key_exchange["protocol"] == "ESP":
        config_input = config_input.replace("esp=esp", f"esp={esp}")
    else:
        config_input = config_input.replace("esp=esp", f"ah={esp}")
        config_input = config_input.replace("#installpolicy=yes", "installpolicy=yes")
        config_input = config_input.replace("forceencaps=yes", "forceencaps=no")

    if json_object["lifetime_ph2"] != "":
        config_input = config_input.replace("#lifetime=28800s", f"lifetime={json_object['lifetime_ph2']}s")

    return config_input
