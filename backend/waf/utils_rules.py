"""This file is for changes on system"""


from backend.waf.constant_variables import PATH_MAIN_WAF, PATH_RULES_WAF
from backend.waf.models import RulesWaf
from backend.waf.utils import convert_waf_rule_payload
from utils.commands_utils import execute_command_without_arguments


def create_rule_waf_in_system(rule_data):
    """Function to add a WAF Rule in system"""
    # Create the rule
    rule_waf = create_rule(rule_data)
    # Add the rule in custom_rules file
    with open(PATH_RULES_WAF.format("custom_rules"), 'a') as custom_rule_file:
        custom_rule_file.write(f"\n{rule_waf}")
    # Add a commented line in RESPONSE-999 file for removing this new rule if the rule will be desactivated
    with open(PATH_RULES_WAF.format("RESPONSE-999-EXCLUSION-RULES-AFTER-CRS"), 'a') as rule999_file:
        rule999_file.write(f"\n#SecRuleRemoveById {rule_data['rule_id']}")
    execute_command_without_arguments(["sudo", "nginx", "-s", "reload"])
    return rule_waf


def delete_rule_waf_in_system(rule:RulesWaf):
    """Function to delete a WAF Rule in system"""
    # Remove the rule from custom rule file by replacing the rule content with an empty string
    update_content_in_rules_file(PATH_RULES_WAF.format("custom_rules"), rule.rule_content, "")
    
    # Remove the SecRuleRemoveById line of the rule from main.conf
    if rule.rule_status:
        update_content_in_rules_file(PATH_RULES_WAF.format("RESPONSE-999-EXCLUSION-RULES-AFTER-CRS"), 
                                    f"\n#SecRuleRemoveById {rule.rule_id}", "")
    else:
        update_content_in_rules_file(PATH_RULES_WAF.format("RESPONSE-999-EXCLUSION-RULES-AFTER-CRS"), 
                                    f"\nSecRuleRemoveById {rule.rule_id}", "")


def update_rule_waf_in_system(previous_rule_content, rule_data):
    """Function to update a WAF Rule in system"""
    # Create the new rule
    rule_waf = create_rule(rule_data)
    # Update the rule in custom_rules file
    update_content_in_rules_file(PATH_RULES_WAF.format("custom_rules"), previous_rule_content, f"\n{rule_waf}")
    # Add a commented line in RESPONSE-999 file for removing this new rule if the rule will be desactivated
    with open(PATH_RULES_WAF.format("RESPONSE-999-EXCLUSION-RULES-AFTER-CRS"), 'a') as rule999_file:
        rule999_file.write(f"\n#SecRuleRemoveById {rule_data['rule_id']}")
    execute_command_without_arguments(["sudo", "nginx", "-s", "reload"])
    return rule_waf


def start_rule_in_system(rule:RulesWaf):
    """Function to start a rule in system"""
    if rule.created:
        update_content_in_rules_file(PATH_RULES_WAF.format('RESPONSE-999-EXCLUSION-RULES-AFTER-CRS'),
                                     f"SecRuleRemoveById {rule.rule_id}",
                                     f"#SecRuleRemoveById {rule.rule_id}")
    else:
        update_content_in_rules_file(PATH_MAIN_WAF, 
                                     f"#Include {PATH_RULES_WAF.format(rule.name)}",
                                     f"\nInclude {PATH_RULES_WAF.format(rule.name)}")
    execute_command_without_arguments(["sudo", "nginx", "-s", "reload"])


def stop_rule_in_system(rule:RulesWaf):
    """Function to stop a rule in system"""
    if rule.created:
        update_content_in_rules_file(PATH_RULES_WAF.format('RESPONSE-999-EXCLUSION-RULES-AFTER-CRS'),
                                     f"#SecRuleRemoveById {rule.rule_id}",
                                     f"SecRuleRemoveById {rule.rule_id}")
    else:
        update_content_in_rules_file(PATH_MAIN_WAF, 
                                     f"Include {PATH_RULES_WAF.format(rule.name)}",
                                     f"\n#Include {PATH_RULES_WAF.format(rule.name)}")
    execute_command_without_arguments(["sudo", "nginx", "-s", "reload"])


def update_content_in_rules_file(file_path, previous_content, new_content):
    """Function to update a content in rules file"""
    # Get the custom rules file content
    with open(file_path) as rule_file:
        rule_file_content = rule_file.read()
    # Delete rule line
    rule_file_content = rule_file_content.replace(previous_content, new_content)
    # Set the new custom rules file content
    with open(file_path, 'w') as rule_file:
        rule_file.write(rule_file_content)


def create_rule(rule_data: dict):
    """Function that takes a waf rule input in dict format and returns the waf rule in string format"""

    variables = ""
    operators = ""
    transformations_actions = ""
    if rule_data["variables"] != "":
        variables = f'''{rule_data["variables"]}'''
    if rule_data["operators"] != "":
        operators = f''' "{rule_data["operators"]}"'''
    if rule_data["transformations"] != "":
        transformations_actions = f''' "{rule_data["transformations"]}"'''
        if rule_data["actions"] != "":
            transformations_actions = f'''{transformations_actions[:len(transformations_actions)-1]}, {rule_data["actions"]}"'''
    elif rule_data["actions"] != "":
        transformations_actions = f''' "{rule_data["actions"]}"'''
    return f"SecRule {variables}{operators}{transformations_actions}"
