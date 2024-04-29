"""This file is for changes on system"""


from backend.waf.constant_variables import PATH_RULES_WAF
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
