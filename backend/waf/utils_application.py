from backend.managementCertificates.constant_variables import PATH_SERVER_CERT_CRT, PATH_SERVER_CERT_KEY
from backend.waf.constant_variables import PATH_CRS_SETUP, PATH_MAIN_WAF, PATH_MODESC, PATH_NGINX_SITES_AVAILABLE, PATH_NGINX_SITES_ENABLED, PATH_RULES_WAF, PATH_WAF_CONFIG
from backend.waf.models import ApplicationWaf, RulesWaf
from backend.waf.utils import create_reverse_proxy_config
from backend.waf.utils_config import create_waf_config
from utils.commands_utils import append_file_from_system, execute_command_without_arguments, execute_list_commands_without_arguments, read_file_from_system, write_file_from_system


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
    if app_data["application_protocol"] == "https":
        create_reverse_proxy_config(app_config, app_sites_available_config, app_modsecurity_config, 
                                    app_data["application_type"], app_data["application_protocol"], 
                                    app_data["application_value"], app_data["application_port"], 
                                    app_data["certificate_name"])
    else:
        create_reverse_proxy_config(app_config, app_sites_available_config, app_modsecurity_config, 
                                    app_data["application_type"], app_data["application_protocol"], 
                                    app_data["application_value"], app_data["application_port"])
    
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
        write_file_from_system(f"{app_directory}geoip_{app_data['name']}.conf", rule_geoip_block)
    
    rule_geoip_log = f"""SecRule REMOTE_ADDR "@geoLookup" "phase:1,id:{rule_geoip_log_id},log,pass,logdata:'Country: %{{GEO:COUNTRY_CODE}}, Latitude: %{{GEO:LATITUDE}}, Longitude: %{{GEO:LONGITUDE}}'" """
    write_file_from_system(f"{app_directory}geoip_log_{app_data['name']}.conf", rule_geoip_log)
    append_file_from_system(PATH_MAIN_WAF, f"\nInclude {app_directory}geoip_log_{app_data['name']}.conf")
    
    # Add all rules (selected and GEOIP) to the config of the app
    for rule in list_rule_selected:
        rule_waf = RulesWaf.objects.get(id=rule["rule_waf"])
        if rule_waf.created:
            # Add a new rule conf inside application directory
            write_file_from_system(f"{app_directory}{rule_waf.name}.conf", rule_waf.rule_content)
            app_config_content += f"\nInclude {app_directory}{rule_waf.name}.conf"
        else:
            app_config_content += f"\nInclude {PATH_RULES_WAF.format(rule_waf.name)}"
    write_file_from_system(app_config, app_config_content)

    ########## Config of the application ##########
    create_waf_config(app_param_config, app_data["config"])
    
    # # Reload nginx
    execute_command_without_arguments(["sudo", "nginx", "-s", "reload"])


def delete_application_waf_in_system(application_name):
    app_modsecurity_config = f"{PATH_MODESC}{application_name}.conf"
    app_sites_available_config = f"{PATH_NGINX_SITES_AVAILABLE}{application_name}.conf"
    app_sites_enabled_config = f"{PATH_NGINX_SITES_ENABLED}{application_name}.conf"
    app_directory = f"{PATH_MODESC}{application_name}/"
    app_param_config = f"{PATH_MODESC}{application_name}_param.conf"
    list_delete_commands = [["sudo", "rm", "-rf", app_directory],
                            ["sudo", "rm", "-f", app_modsecurity_config],
                            ["sudo", "rm", "-f", app_sites_available_config],
                            ["sudo", "rm", "-f", app_sites_enabled_config],
                            ["sudo", "rm", "-f", app_param_config],]
    execute_list_commands_without_arguments(list_delete_commands)
    main_content = read_file_from_system(PATH_MAIN_WAF)
    main_content = main_content.replace(f"\nInclude {app_directory}geoip_log_{application_name}.conf", "")
    write_file_from_system(PATH_MAIN_WAF, main_content)
    execute_command_without_arguments(["sudo", "nginx", "-s", "reload"])


def update_application_waf_in_system(application:ApplicationWaf, app_data):
    """Function to update a WAF Application in system"""
    delete_application_waf_in_system(application.name)
    create_application_waf_in_system(app_data)
