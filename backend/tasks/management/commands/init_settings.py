from backend.managementCertificates.models import Certificate
from backend.managementCertificates.serializers import CertificateSerializer
from backend.settings.utils import create_config_db, execute_all_commandes, get_all_interfaces,manage_commandes, save_rules_settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Your code to add data to the database here
        try:
            enable_ssh=True
            root_login=True
            auth_method="password"
            session_timeout=300
            protocol_http=False
            certificat_id=None
            tcp_port=443
            login_message=True
            interface_ssh=[]
            interface_web=[]
            all_interfaces=get_all_interfaces()
            certificat_data={
                "country":'TN',
                "city":"tunis",
                "state":"tunis",
                "organization":"numeryx",
                "name":"asguard",
                "common_name":"asguard",
                "email":"asguard@numeryx.fr",
                "key_type":"rsa",
                "key_length":4096,
                "digest_algorithm":"sha256",
                "lifetime":3650
                    
            }
            commandes_ssl = [
                    "mkdir -p /etc/nginx/ssl",
                    "cd /etc/nginx/ssl && ("
                    "echo 'TN';" # country
                    "echo 'tunis';" # city
                    "echo 'tunis';" # state
                    "echo 'numeryx';" # organization
                    "echo '';" # 
                    "echo 'asguard';" # name, common_name
                    "echo 'asguard@numeryx.fr'" # email
                    ") | openssl req -newkey rsa:4096 -x509 -sha256 -days 3650 -nodes "
                    "-out /etc/ssl/certs/asguard.crt -keyout /etc/ssl/private/asguard.key"
                ] # rsa:key_type, 4096:key_length, sha256:digest_algorithm, 3650:lifetime
            aux_ssl=execute_all_commandes(commandes_ssl)
            if aux_ssl:
                certificat_serializer=CertificateSerializer(data=certificat_data)
                if certificat_serializer.is_valid():
                    certificat=certificat_serializer.save()
                    certificat_id = certificat.id  
                    certif=certificat.name 
                else:
                    certificat=Certificate.objects.get(name="asguard")
                    certificat_id = certificat.id  
                    certif=certificat.name 
                    print(certificat_serializer.errors)
                data={
                    "enable_ssh":enable_ssh,
                    "root_login":root_login,
                    "auth_method":auth_method,
                    "session_timeout":session_timeout,
                    "protocol_http":protocol_http,
                    "certificat":certificat_id,
                    "tcp_port":tcp_port,
                    "login_message":login_message
                    }
                commandes,rules_web,rules_ssh=manage_commandes(all_interfaces,interface_ssh,interface_web,root_login,auth_method,enable_ssh,protocol_http,tcp_port,login_message,certif,session_timeout)
                
                print({"all_commandes":commandes})
                aux_commandes=execute_all_commandes(commandes)
                if aux_commandes:
                    msg,_=create_config_db(data,interface_web,interface_ssh)
                    save_rules_settings(rules_ssh,rules_web)
                else:
                    msg=aux_commandes
                # status=400
            else:
                return aux_ssl
            return msg
      
     
                            
                
        except IntegrityError as e:
            return "Error: " + str(e)
