from openvpn.models import ServerOpenvpn


class CommandExecutionError(Exception):
    """a class error when execution a command line"""
    def __init__(self, command, message="Error executing command"):
        self.command = command
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}: {self.command}"


def find_word_in_line(line, word):
    index = line.find(word)
    if index != -1:
        rest_of_line = line[index + len(word):].strip()
        return rest_of_line
    return ''


def find_word_in_table(table, word):
    for row in table:
        if word in row:
            index = row.index(word)
            rest_of_line = row[index + len(word):]
            return rest_of_line
    return ''


def json_to_str_server(json_object):
    """Function to convert a json object to input of server config file"""
    server_name = json_object["server_name"]
    config_input = f'''port {json_object["local_port"]}
proto {json_object["protocol"]}
dev {json_object["device_mode"]}
topology {json_object["topology"]}

#Certificate Configuration

#ca certificate
ca /etc/openvpn/certificates_{server_name}/ca.crt
#Server Certificate
cert /etc/openvpn/certificates_{server_name}/server.crt

#Server Key and keep this is secret
key /etc/openvpn/certificates_{server_name}/server.key


#See the size a dh key in /etc/openvpn/keys/
dh /etc/openvpn/certificates_{server_name}/dh.pem

#Internal IP will get when already connect
server 10.8.1.0 255.255.255.0

#this line will redirect all traffic through our OpenVPN
push "redirect-gateway def1"
push "route 192.168.0.0 255.255.255.0"

#Provide DNS servers to the client, you can use google DNS
push "dhcp-option DNS 8.8.8.8"
push "dhcp-option DNS 8.8.4.4"

#Enable multiple client to connect with same key
duplicate-cn

cipher {json_object["encryption_algorithm"]}

keepalive 20 60
# comp-lzo {json_object["compression"]}
persist-key
persist-tun
daemon
#float

#openvpn status log
#status /var/log/openvpn/status.log

#enable log
#log-append /var/log/openvpn/openvpn.log

#Log Level
verb {json_object["verbosity_level"]}'''
    return config_input


def json_to_str_client(json_object):
    """Function to convert a json object to input of client config file"""
    server_name = json_object["server_name"]
    client_name = json_object["client_name"]
    config_input = f'''client
remote 10.1.12.254 {json_object["local_port"]}
proto {json_object["protocol"]}
dev {json_object["device_mode"]}
nobind
remote-cert-tls server
cipher {json_object["encryption_algorithm"]}
auth-nocache
script-security 2
persist-key
persist-tun
#auth {json_object["auth_digest_algorithm"]}
#verb {json_object["verbosity_level"]}

ca /etc/openvpn/certificates_{server_name}/ca.crt
cert /etc/openvpn/client/certificates_{client_name}/{client_name}.crt
key /etc/openvpn/client/certificates_{client_name}/{client_name}.key
dh /etc/openvpn/certificates_{server_name}/dh.pem
tls-version-min 1.2
tls-cipher TLS-DHE-RSA-WITH-AES-256-GCM-SHA384:TLS-DHE-RSA-WITH-AES-128-GCM-SHA256:TLS-DHE-RSA-WITH-AES-256-CBC-SHA256:TLS-DHE-RSA-WITH-AES-128-CBC-SHA256'''
    return config_input


#function to update interface tables  
def update_openvpn_table(id,data,ServerOpenvpnSerializer):
    objectConfig=ServerOpenvpn.objects.get(id=id)
    # Set all attributes to None
    for field in objectConfig._meta.fields:
        if field.attname not in ["id"]: 
            setattr(objectConfig, field.attname, None)
    serializerServerOpenvpn= ServerOpenvpnSerializer(objectConfig,data=data)
    if serializerServerOpenvpn.is_valid():
            serializerServerOpenvpn.save()