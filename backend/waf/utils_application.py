from backend.waf.constant_variables import PATH_CRS_SETUP, PATH_MODESC, PATH_NGINX_SITES_AVAILABLE, PATH_NGINX_SITES_ENABLED, PATH_RULES_WAF, PATH_WAF_CONFIG
from backend.waf.models import ApplicationWaf, RulesWaf
from utils.commands_utils import execute_command_without_arguments, execute_list_commands_without_arguments


def create_application_waf_in_system(app_data):
    """Function to add a WAF Application in system"""
    # Add a modsecurity config file for the app
    app_modsecurity_config = f"{PATH_MODESC}{app_data['name']}.conf"
    app_sites_available_config = f"{PATH_NGINX_SITES_AVAILABLE}{app_data['name']}.conf"
    app_sites_enabled_config = f"{PATH_NGINX_SITES_ENABLED}{app_data['name']}.conf"
    app_directory = f"{PATH_MODESC}{app_data['name']}/"
    app_config = f"{app_directory}{app_data['name']}.conf"
    execute_command_without_arguments(["sudo", "cp", PATH_WAF_CONFIG, app_modsecurity_config])

    config_reverse_proxy = f"""server {{

    listen {app_data["application_port"]};

    modsecurity on;

    modsecurity_rules_file {app_config};

    location / {{

        proxy_pass {app_data["application_value"]}:{app_data["application_port"]};

        proxy_set_header Host $host;

        proxy_set_header X-Real-IP $remote_addr;

        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_set_header X-Forwarded-Proto $scheme;

    }}

}}"""
    with open(app_sites_available_config, 'w') as reverse_proxy_file:
        reverse_proxy_file.write(config_reverse_proxy)
    
    # Put a symbolic link
    execute_command_without_arguments(["sudo", "rm", "-f", app_sites_enabled_config])
    execute_command_without_arguments(["sudo", "ln", "-s", app_sites_available_config, app_sites_enabled_config])
    
    # Add a directory with application name inside modsec path
    execute_command_without_arguments(["sudo", "mkdir", "-p", app_directory])
    
    # Add selected rules configuration for the application
    # Create a list of only selected rules
    list_rule_selected = [rule for rule in app_data["rules"] if rule["rule_policy"]]
    app_config_content = f"""
Include {app_modsecurity_config}
Include {PATH_CRS_SETUP}
Include {app_directory}geoip_{app_data['name']}.conf
"""
    for rule in list_rule_selected:
        rule_waf = RulesWaf.objects.get(id=rule["rule_waf"])
        if rule_waf.created:
            # Add a new rule conf inside application directory
            with open(f"{app_directory}{rule_waf.name}.conf", 'w') as rule_file:
                rule_file.write(rule_waf.rule_content)
            app_config_content += f"Include {app_directory}{rule_waf.name}.conf\n"
        else:
            app_config_content += f"Include {PATH_RULES_WAF.format(rule_waf.name)}\n"
    with open(app_config, 'w') as app_config_file:
        app_config_file.write(app_config_content)
    # Add a GOIP rule
    rule_geoip = f"""
SecRule REMOTE_ADDR "@geoLookup" "phase:1,id:{app_data['rule_geoip_id']},chain,deny,status:403,msg:'Access from blocked countries'"
SecRule GEO:COUNTRY_CODE "@pm {" ".join(app_data['country'])}" """
    with open(f"{app_directory}geoip_{app_data['name']}.conf", 'w') as rule_file:
        rule_file.write(rule_geoip)
    
    # Reload nginx
    execute_command_without_arguments(["sudo", "nginx", "-s", "reload"])


def delete_application_waf_in_system(application:ApplicationWaf):
    app_modsecurity_config = f"{PATH_MODESC}{application.name}.conf"
    app_sites_available_config = f"{PATH_NGINX_SITES_AVAILABLE}{application.name}.conf"
    app_sites_enabled_config = f"{PATH_NGINX_SITES_ENABLED}{application.name}.conf"
    app_directory = f"{PATH_MODESC}{application.name}/"
    list_delete_commands = [["sudo", "rm", "-rf", app_directory],
                            ["sudo", "rm", "-f", app_modsecurity_config],
                            ["sudo", "rm", "-f", app_sites_available_config],
                            ["sudo", "rm", "-f", app_sites_enabled_config],]
    execute_list_commands_without_arguments(list_delete_commands)
    execute_command_without_arguments(["sudo", "nginx", "-s", "reload"])


def update_application_waf_in_system(application:ApplicationWaf, app_data):
    """Function to update a WAF Application in system"""
    delete_application_waf_in_system(application)
    create_application_waf_in_system(app_data)
