from backend.waf.constant_variables import CONSTANT_JSON_REQUEST, CONSTANT_JSON_REQUEST_COMMENTED, CONSTANT_XML_REQUEST, CONSTANT_XML_REQUEST_COMMENTED, PATH_WAF_CONFIG
from utils.commands_utils import execute_command_without_arguments, read_file_from_system, write_file_from_system


def create_waf_config(config_path, config_data):
    """Create a specific WAF config for an application"""
    # Copy the config of the modsecurity to the application
    execute_command_without_arguments(["sudo", "cp", PATH_WAF_CONFIG, config_path])
    # Change the config of the application with data input
    change_waf_config_file(config_data, config_path)


def change_waf_config_file(data_config, path_config=PATH_WAF_CONFIG):
    """Change WAF config file with inputs"""
    waf_config_content = read_file_from_system(path_config)
    config = change_content_config(waf_config_content, data_config)
    write_file_from_system(path_config, config)
    execute_command_without_arguments(["sudo", "systemctl", "restart", "nginx"])


def change_content_config(config: str, data_config: dict):
    """Get content of WAF config file and return a new content with input data"""
    config_keys = {"rule_engine_initialization": "SecRuleEngine",
                   "access_request_bodies": "SecRequestBodyAccess",
                   "xml_request_body_parser": "SecRule",
                   "json_request_body_parser": "SecRule",
                   "maximum_request_body_size": "SecRequestBodyLimit",
                   "request_body_size_files_excluded": "SecRequestBodyNoFilesLimit",
                   "request_body_limit_action": "SecRequestBodyLimitAction",
                   "maximum_parsing_depth_json": "SecRequestBodyJsonDepthLimit",
                   "maximum_number_args_request": "SecArgumentsLimit",
                   "pcre_match_limit": "SecPcreMatchLimit",
                   "pcre_match_limit_recursion": "SecPcreMatchLimitRecursion",
                   "response_body_access": "SecResponseBodyAccess",
                   "response_body_mimetype": "SecResponseBodyMimeType",
                   "response_body_limit": "SecResponseBodyLimit",
                   "response_body_limit_action": "SecResponseBodyLimitAction"
                   }
    for key in config_keys:

        if key == 'access_request_bodies':
            config = convert_bool_to_on_off(data_config[key], 'SecRequestBodyAccess', config)

        elif key == 'response_body_access':
            config = convert_bool_to_on_off(data_config[key], 'SecResponseBodyAccess', config)

        elif key == "xml_request_body_parser":
            config = comment_uncomment_field(data_config[key], CONSTANT_XML_REQUEST_COMMENTED, CONSTANT_XML_REQUEST, config)
                
        elif key == "json_request_body_parser":
            config = comment_uncomment_field(data_config[key], CONSTANT_JSON_REQUEST_COMMENTED, CONSTANT_JSON_REQUEST, config)

        else:
            index_key = config.find(f'{config_keys[key]} ')
            line = config[index_key:config.find("\n", index_key)]
            if key == 'response_body_mimetype':
                response_body_mimetype = data_config[key]
                if data_config[key] == 'text/*':
                    response_body_mimetype = 'text/plain text/html text/xml'
                config = config.replace(line, f'SecResponseBodyMimeType {response_body_mimetype}')
            else:
                config = config.replace(line, f'{config_keys[key]} {data_config[key]}')
                
    return config


def convert_bool_to_on_off(bool_test, field_config, config: str):
    """Convert a boolean input (True or False) to On/Off on a config file content"""
    if bool_test:
        config = config.replace(f'\n{field_config} Off', f'\n{field_config} On')
    else:
        config = config.replace(f'\n{field_config} On', f'\n{field_config} Off')
    return config


def comment_uncomment_field(bool_test, field_commented, field_uncommented, config: str):
    """Comment or uncomment a field on a config file content"""
    if bool_test:
        config = config.replace(f'\n{field_commented}', f'\n{field_uncommented}')
    else:
        config = config.replace(f'\n{field_uncommented}', f'\n{field_commented}')
    return config
