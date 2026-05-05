"""This file is for changes on system"""


from backend.waf.constant_variables import PATH_RULES_WAF
from utils.commands_utils import append_file_from_system, execute_command_without_arguments, read_file_from_system, write_file_from_system


def create_rule_waf_in_system(rule_waf):
    """Function to add a WAF Rule in system"""
    # Add the rule in custom_rules file
    append_file_from_system(PATH_RULES_WAF.format("custom_rules"), f"\n{rule_waf}")
    execute_command_without_arguments(["sudo", "nginx", "-s", "reload"])


def delete_rule_waf_in_system(rule_content:str):
    """Function to delete a WAF Rule in system"""
    # Remove the rule from custom rule file by replacing the rule content with an empty string
    update_content_in_rules_file(PATH_RULES_WAF.format("custom_rules"), rule_content, "")
    execute_command_without_arguments(["sudo", "nginx", "-s", "reload"])


def update_rule_waf_in_system(previous_rule_content, rule_waf):
    """Function to update a WAF Rule in system"""
    # Update the rule in custom_rules file
    update_content_in_rules_file(PATH_RULES_WAF.format("custom_rules"), previous_rule_content, f"\n{rule_waf}")
    execute_command_without_arguments(["sudo", "nginx", "-s", "reload"])


def update_content_in_rules_file(file_path, previous_content, new_content):
    """Function to update a content in rules file"""
    # Get the custom rules file content
    rule_file_content = read_file_from_system(file_path)
    # Delete rule line
    rule_file_content = rule_file_content.replace(previous_content, new_content)
    # Set the new custom rules file content
    write_file_from_system(file_path, rule_file_content)


def create_rule_waf_str(rule_data: dict):
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
