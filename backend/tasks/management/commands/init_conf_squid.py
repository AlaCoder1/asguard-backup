import subprocess
from django.core.management.base import BaseCommand
from backend.proxy.views import run_command

def check_line_in_file(file_path, line_to_check):
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    if line.strip() == line_to_check:
                        return True
            return False
        except FileNotFoundError:
            print("File not found.")
            return False
class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        squid_conf_path = '/etc/squid/squid.conf'
        lines_to_add = [
            '',
            'cache_effective_user squid',
            'cache_effective_group squid',
            'auth_param basic program /usr/lib/squid/basic_ncsa_auth /etc/squid/squid_passwd',
            'acl authenticated_users proxy_auth REQUIRED',
            '',
            '#http_access allow allowed_subnet_by_auth authenticated_users',
            '#http_access allow allowed_ip_by_auth authenticated_users',
            '#http_access allow allowed_domain_by_auth authenticated_users',
            '',
            'http_access deny blocked_subnet',
            'http_access deny blocked_ip',
            'http_access deny blocked_domain',
            '',
            'http_access allow ads',
            'http_access allow adult',
            'http_access allow astrology',
            'http_access allow audio_video',
            'http_access allow bitcoin',
            'http_access allow cryptojacking',
            'http_access allow dating',
            'http_access allow ddos',
            'http_access allow download',
            'http_access allow drugs',
            'http_access allow games',
            'http_access allow jobsearch',
            'http_access allow social_network',
            'http_access allow sports',
            'http_access allow violence',
        ]

        acl_to_add = [
            '',
            'acl blocked_ip dst "/etc/squid/blocked_ip.acl"',
            'acl blocked_domain url_regex "/etc/squid/blocked_domain.acl"',
            'acl blocked_subnet dst "/etc/squid/blocked_subnet.acl"',
            '',
            'acl allowed_ip_by_auth dst "/etc/squid/allowed_ip_by_auth.acl"',
            'acl allowed_domain_by_auth url_regex "/etc/squid/allowed_domain_by_auth.acl"',
            'acl allowed_subnet_by_auth dst "/etc/squid/allowed_subnet_by_auth.acl"',
            '',
            'acl ads url_regex "/etc/squid/acl/ads.acl"',
            'acl adult url_regex "/etc/squid/acl/adult.acl"',
            'acl astrology url_regex "/etc/squid/acl/astrology.acl"',
            'acl audio_video url_regex "/etc/squid/acl/audio_video.acl"',
            'acl bitcoin url_regex "/etc/squid/acl/bitcoin.acl"',
            'acl cryptojacking url_regex "/etc/squid/acl/cryptojacking.acl"',
            'acl dating url_regex "/etc/squid/acl/dating.acl"',
            'acl ddos url_regex "/etc/squid/acl/ddos.acl"',
            'acl download url_regex "/etc/squid/acl/download.acl"',
            'acl drugs url_regex "/etc/squid/acl/drugs.acl"',
            'acl games url_regex "/etc/squid/acl/games.acl"',
            'acl jobsearch url_regex "/etc/squid/acl/jobsearch.acl"',
            'acl social_network url_regex "/etc/squid/acl/social_network.acl"',
            'acl sports url_regex "/etc/squid/acl/sports.acl"',
            'acl violence url_regex "/etc/squid/acl/violence.acl"',
        ]
        line_to_check = 'acl authenticated_users proxy_auth REQUIRED'
        if check_line_in_file(squid_conf_path, line_to_check):
            print("The line exists in the file.")
        else:
            # Read the content of the file
            with open(squid_conf_path, 'r') as file:
                lines = file.readlines()

            # Find the index of the line that starts with 'acl localnet src fe80::/10'
            index = next((i for i, line in enumerate(lines) if line.startswith('acl localnet src fe80::/10')), None)

            if index is not None:
                # Insert the lines after the found line
                lines[index + 1:index + 1] = [line + '\n' for line in acl_to_add]

                # Write the modified content back to the file
                with open(squid_conf_path, 'w') as file:
                    file.writelines(lines)
            else:
                print("Line not found in the file.")

            index_acl = next((i for i, line in enumerate(lines) if line.startswith('# INSERT YOUR OWN RULE(S) HERE TO ALLOW ACCESS FROM YOUR CLIENTS')), None)
            if index_acl is not None:
                # Insert the lines after the found line
                lines[index_acl + 1:index_acl + 1] = [line + '\n' for line in lines_to_add]

                # Write the modified content back to the file
                with open(squid_conf_path, 'w') as file:
                    file.writelines(lines)
            else:
                print("Line not found in the file.")
                
            # Read the content of the file
            with open(squid_conf_path, 'r') as file:
                lines = file.readlines()
            # Find the index of the line that starts with 'http_access deny all'
            index_http_access = next((i for i, line in enumerate(lines) if line.strip() == 'http_access deny all'), None)

            if index_http_access is not None:
                # Replace 'http_access deny all' with 'http_access allow all'
                lines[index_http_access] = 'http_access allow all\n'

                # Write the modified content back to the file
                with open(squid_conf_path, 'w') as file:
                    file.writelines(lines)
            else:
                print("Line not found in the file.")
                