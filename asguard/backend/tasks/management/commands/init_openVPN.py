from backend.openvpn.models import *
from django.core.management.base import BaseCommand
from django.db import IntegrityError
import paramiko
from django.conf import settings

def find_word_in_table(table, word):
    for row in table:
        if word in row:
            index = row.index(word)
            rest_of_line = row[index + len(word):]
            return rest_of_line
    return None 

def sudo(cmd):
    return "sudo "+cmd

class Command(BaseCommand):
    def add_arguments(self, parser):
        # Optional argument
        parser.add_argument('-u', '--name', type=str, help='Define a username name')
        parser.add_argument('-p', '--pw', type=str, help='Define a username password')

    def handle(self, *args, **kwargs):
        # Your code to add data to the database here
        try:
            name = kwargs['name']
            pw = kwargs['pw']
            def connect_ssh():
                ssh = paramiko.SSHClient()
                # automatically add host key when connecting to a new host
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                # connect to SSH server
                ssh.connect(settings.SSH_HOST, username=name,
                            password=pw, port=settings.SSH_PORT)
                return ssh
            server_path = "/etc/openvpn/server.conf"
            ssh = connect_ssh()
            cmd = f"cat {server_path}"
            stdin, stdout, stderr = ssh.exec_command(sudo(cmd))
            if stderr.read().decode('utf-8') == '':
                resultat = stdout.read().decode('utf-8')
                tab = resultat.split('\n')
                port=find_word_in_table(tab,"port")
                proto=find_word_in_table(tab,"proto")
                dev=find_word_in_table(tab,"dev")
                user=find_word_in_table(tab,"user")
                group=find_word_in_table(tab,"group")
                persist_key=find_word_in_table(tab,"persist-key")
                persist_tun=find_word_in_table(tab,"persist-tun")
                keepalive=find_word_in_table(tab,"keepalive")
                topology=find_word_in_table(tab,"topology")
                server=find_word_in_table(tab,"server")
                ifconfig_pool_persist=find_word_in_table(tab,"ifconfig-pool-persist")
                # do it again for dame push in file ^^
                push_ipv4_option1=find_word_in_table(tab,"push")
                push_ipv4_option2=find_word_in_table(tab,"push")
                push_ipv4_option3=find_word_in_table(tab,"push")
                server_ipv6=find_word_in_table(tab,"server-ipv6")
                tun_ipv6=find_word_in_table(tab,"tun-ipv6")
                # do it again for dame push in file ^^
                push_ipv6_option1=find_word_in_table(tab,"push")
                push_ipv6_option2=find_word_in_table(tab,"push")
                push_ipv6_option3=find_word_in_table(tab,"push")
                dh=find_word_in_table(tab,"dh")
                ecdh_curve=find_word_in_table(tab,"ecdh-curve")
                tls_crypt=find_word_in_table(tab,"tls-crypt")
                crl_verify=find_word_in_table(tab,"crl-verify")
                ca=find_word_in_table(tab,"ca")
                cert=find_word_in_table(tab,"cert")
                key=find_word_in_table(tab,"key")
                auth=find_word_in_table(tab,"auth")
                cipher=find_word_in_table(tab,"cipher")
                ncp_ciphers=find_word_in_table(tab,"ncp-ciphers")
                tls_server=find_word_in_table(tab,"tls-server")
                tls_version_min=find_word_in_table(tab,"tls-version-min")
                tls_cipher=find_word_in_table(tab,"tls-cipher")
                client_config_dir=find_word_in_table(tab,"client-config-dir")
                status=find_word_in_table(tab,"status")
                verb=find_word_in_table(tab,"verb")
                ServerOpenvpn.objects.create(port=port,proto=proto,dev=dev,user=user,group=group,persist_key=persist_key,persist_tun=persist_tun,keepalive=keepalive,topology=topology,server=server,ifconfig_pool_persist=ifconfig_pool_persist,push_ipv4_option1=push_ipv4_option1,push_ipv4_option2=push_ipv4_option2,push_ipv4_option3=push_ipv4_option3,server_ipv6=server_ipv6,tun_ipv6=tun_ipv6,push_ipv6_option1=push_ipv6_option1,push_ipv6_option2=push_ipv6_option2,push_ipv6_option3=push_ipv6_option3,dh=dh,ecdh_curve=ecdh_curve,tls_crypt=tls_crypt,crl_verify=crl_verify,ca=ca,cert=cert,key=key,auth=auth,cipher=cipher,ncp_ciphers=ncp_ciphers,tls_server=tls_server,tls_version_min=tls_version_min,tls_cipher=tls_cipher,client_config_dir=client_config_dir,status=status,verb=verb)
                return "ServerOpenvpn added succesffuly"
            else:
                return "erreur: "+stderr.read().decode('utf-8')
        except IntegrityError as e:
            return "Error: " + str(e)