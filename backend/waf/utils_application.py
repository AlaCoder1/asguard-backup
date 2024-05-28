from backend.waf.constant_variables import PATH_ASGUARD_CONFIG, PATH_MODESC, PATH_RULES_WAF
from backend.waf.models import ApplicationWaf, RulesWaf
from utils.commands_utils import execute_command_without_arguments


def create_application_waf_in_system(app_data):
    """Function to add a WAF Application in system"""
    # Add a directory with application name inside modsec path
    app_directory = f"{PATH_MODESC}{app_data['name']}/"
    app_config = f"{app_directory}{app_data['name']}.conf"
    execute_command_without_arguments(["sudo", "mkdir", "-p", app_directory])
    # Add selected rules configuration for the application
    # Create a list of only selected rules
    list_rule_selected = [rule for rule in app_data["rules"] if rule["rule_policy"]]
    app_config_content = ""
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

    with open(PATH_ASGUARD_CONFIG) as asguard_conf_file:
        asguard_conf_content = asguard_conf_file.read()
    location = """    location /{}/ {{
        proxy_pass {};
        modsecurity on;
        modsecurity_rules_file {};
        }}

}}""".format(app_data['name'], app_data['application_value'], app_config)
    asguard_conf_content = asguard_conf_content[:asguard_conf_content.rfind('}')] + location
    with open(PATH_ASGUARD_CONFIG, 'w') as asguard_conf_file:
        asguard_conf_file.write(asguard_conf_content)
    execute_command_without_arguments(["sudo", "nginx", "-s", "reload"])


def delete_application_waf_in_system(application:ApplicationWaf):
    app_directory = f"{PATH_MODESC}{application.name}/"
    app_config = f"{app_directory}{application.name}.conf"
    execute_command_without_arguments(["sudo", "rm", "-rf", app_directory])
    with open(PATH_ASGUARD_CONFIG) as asguard_conf_file:
        asguard_conf_content = asguard_conf_file.read()
    location = """    location /{}/ {{
        proxy_pass {};
        modsecurity on;
        modsecurity_rules_file {};
        }}

""".format(application.name, application.application_value, app_config)
    asguard_conf_content = asguard_conf_content.replace(location, "")
    with open(PATH_ASGUARD_CONFIG, 'w') as asguard_conf_file:
        asguard_conf_file.write(asguard_conf_content)
    execute_command_without_arguments(["sudo", "nginx", "-s", "reload"])


def update_application_waf_in_system(application:ApplicationWaf, app_data):
    """Function to update a WAF Application in system"""
    delete_application_waf_in_system(application)
    create_application_waf_in_system(app_data)
