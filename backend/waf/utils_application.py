from backend.managementCertificates.constant_variables import PATH_SERVER_CERT_CRT, PATH_SERVER_CERT_KEY
from backend.waf.constant_variables import PATH_CRS_SETUP, PATH_MAIN_WAF, PATH_MODESC, PATH_NGINX_SITES_AVAILABLE, PATH_NGINX_SITES_ENABLED, PATH_RULES_WAF, PATH_WAF_CONFIG
from backend.waf.models import ApplicationWaf, RulesWaf
from backend.waf.utils_config import create_waf_config
from utils.commands_utils import execute_command_without_arguments, execute_list_commands_without_arguments


def create_application_waf_in_system(app_data):
    """Function to add a WAF Application in system"""
    # Paths of the application
    app_modsecurity_config = f"{PATH_MODESC}{app_data['name']}.conf"
    app_sites_available_config = f"{PATH_NGINX_SITES_AVAILABLE}{app_data['name']}.conf"
    app_sites_enabled_config = f"{PATH_NGINX_SITES_ENABLED}{app_data['name']}.conf"
    app_directory = f"{PATH_MODESC}{app_data['name']}/"
    app_config = f"{app_directory}{app_data['name']}.conf"
    app_param_config = f"{PATH_MODESC}{app_data['name']}_param.conf"

    ########## Configuartion of the application ##########
    # Add a modsecurity config file for the app
    execute_command_without_arguments(["sudo", "cp", PATH_WAF_CONFIG, app_modsecurity_config])

    # Add reverse proxy config for the app 
    modsecurity = f"""
        modsecurity on;
        modsecurity_rules_file {app_config};"""
    location = f"""
        location / {{
            proxy_pass {app_data["application_protocol"]}://{app_data["application_value"]};
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}"""
    
    # Config for HTTP
    if app_data["application_protocol"] == "http": 
        config_reverse_proxy = f"""
server {{
        listen {app_data["application_port"]};

        {modsecurity}

        {location}

}}"""
    # Config for HTTPS
    else:
        # Add SSL settings for the proxy
        location = location.replace("proxy_set_header X-Forwarded-Proto $scheme;", """
            proxy_set_header X-Forwarded-Proto $scheme;

            # SSL settings for the proxy
            proxy_ssl_protocols TLSv1.2 TLSv1.3;
            proxy_ssl_verify off;""")
        config_reverse_proxy = f"""
server {{
    listen 80;
    server_name _l;
 
    # Redirect HTTP to HTTPS
    location / {{
        return 301 https://$host:{app_data["application_port"]}$request_uri;
    }}
}}

server {{
        listen {app_data["application_port"]} ssl;
        server_name _;

        ssl_certificate {PATH_SERVER_CERT_CRT.format(app_data["certificate_name"])};
        ssl_certificate_key {PATH_SERVER_CERT_KEY.format(app_data["certificate_name"])};

        {modsecurity}

        {location}

}}"""
    # changes of config when using domain name
    if app_data['application_type'] != 'ip':
        config_reverse_proxy = config_reverse_proxy.replace("server_name _;", 
                                                            f"server_name {app_data['application_value']};")
        config_reverse_proxy = config_reverse_proxy.replace("server_name _l;", 
                                                            f"server_name {app_data['application_value']};")
    with open(app_sites_available_config, 'w') as reverse_proxy_file:
        reverse_proxy_file.write(config_reverse_proxy)
    
    # Put a symbolic link
    execute_command_without_arguments(["sudo", "rm", "-f", app_sites_enabled_config])
    execute_command_without_arguments(["sudo", "ln", "-s", app_sites_available_config, app_sites_enabled_config])
    
    # Add a directory with application name inside modsec path
    execute_command_without_arguments(["sudo", "mkdir", "-p", app_directory])

    ########## Rules of the application ##########
    # Add selected rules configuration for the application
    # Create a list of only selected rules
    list_rule_selected = [rule for rule in app_data["rules"] if rule["rule_policy"]]
    app_config_content = f"""
Include {app_param_config}
Include {PATH_CRS_SETUP}
Include {app_directory}geoip_log_{app_data['name']}.conf
"""
    rule_geoip_block_id = app_data['rule_geoip_id']
    rule_geoip_log_id = app_data['rule_geoip_id']
    
    # Add a geoip rule block to the config of the app
    if app_data["country"] != []:
        rule_geoip_log_id += 1
        app_config_content += f"""
\nInclude {app_directory}geoip_{app_data['name']}.conf"""
        rule_geoip_block = f"""
SecRule REMOTE_ADDR "@geoLookup" "phase:1,id:{rule_geoip_block_id},chain,deny,status:403,msg:'Access from blocked countries: %{{GEO:COUNTRY_CODE}}',logdata:'Country: %{{GEO:COUNTRY_CODE}}, Latitude: %{{GEO:LATITUDE}}, Longitude: %{{GEO:LONGITUDE}}'"
SecRule GEO:COUNTRY_CODE "@pm {" ".join(app_data['country'])}" """
        with open(f"{app_directory}geoip_{app_data['name']}.conf", 'w') as rule_block_file:
            rule_block_file.write(rule_geoip_block)
    
    rule_geoip_log = f"""SecRule REMOTE_ADDR "@geoLookup" "phase:1,id:{rule_geoip_log_id},log,pass,logdata:'Country: %{{GEO:COUNTRY_CODE}}, Latitude: %{{GEO:LATITUDE}}, Longitude: %{{GEO:LONGITUDE}}'" """
    with open(f"{app_directory}geoip_log_{app_data['name']}.conf", 'w') as rule_log_file:
        rule_log_file.write(rule_geoip_log)
    with open(PATH_MAIN_WAF, 'a') as main_file:
        main_file.write(f"\nInclude {app_directory}geoip_log_{app_data['name']}.conf")
    
    # Add all rules (selected and GEOIP) to the config of the app
    for rule in list_rule_selected:
        rule_waf = RulesWaf.objects.get(id=rule["rule_waf"])
        if rule_waf.created:
            # Add a new rule conf inside application directory
            with open(f"{app_directory}{rule_waf.name}.conf", 'w') as rule_block_file:
                rule_block_file.write(rule_waf.rule_content)
            app_config_content += f"\nInclude {app_directory}{rule_waf.name}.conf"
        else:
            app_config_content += f"\nInclude {PATH_RULES_WAF.format(rule_waf.name)}"
    with open(app_config, 'w') as app_config_file:
        app_config_file.write(app_config_content)

    ########## Config of the application ##########
    create_waf_config(app_param_config, app_data["config"])
    
    # # Reload nginx
    execute_command_without_arguments(["sudo", "nginx", "-s", "reload"])


def delete_application_waf_in_system(application:ApplicationWaf):
    app_modsecurity_config = f"{PATH_MODESC}{application.name}.conf"
    app_sites_available_config = f"{PATH_NGINX_SITES_AVAILABLE}{application.name}.conf"
    app_sites_enabled_config = f"{PATH_NGINX_SITES_ENABLED}{application.name}.conf"
    app_directory = f"{PATH_MODESC}{application.name}/"
    app_param_config = f"{PATH_MODESC}{application.name}_param.conf"
    list_delete_commands = [["sudo", "rm", "-rf", app_directory],
                            ["sudo", "rm", "-f", app_modsecurity_config],
                            ["sudo", "rm", "-f", app_sites_available_config],
                            ["sudo", "rm", "-f", app_sites_enabled_config],
                            ["sudo", "rm", "-f", app_param_config],]
    execute_list_commands_without_arguments(list_delete_commands)
    with open(PATH_MAIN_WAF) as main_file:
        main_content = main_file.read()
    main_content = main_content.replace(f"\nInclude {app_directory}geoip_log_{application.name}.conf", "")
    with open(PATH_MAIN_WAF, 'w') as main_file:
        main_file.write(main_content)
    execute_command_without_arguments(["sudo", "nginx", "-s", "reload"])


def update_application_waf_in_system(application:ApplicationWaf, app_data):
    """Function to update a WAF Application in system"""
    delete_application_waf_in_system(application)
    create_application_waf_in_system(app_data)


def restart_nginx_in_system():
    execute_command_without_arguments(["sudo", "systemctl", "restart", "nginx"])
