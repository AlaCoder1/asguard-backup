from backend.waf.models import ApplicationWaf, RulesWaf


def convert_waf_rule_payload(rule_data: dict):
    """Function to convert a WAF rule payload 
    from an object containing a list for each field 
    to a string to each one of them and set the rule_id for the rule_data"""
    rule_data["variables"] = ",".join(rule_data["variables"])
    rule_data["operators"] = convert_operators_list_to_str(rule_data["operators"])
    rule_data["transformations"] = convert_transformations_list_to_str(rule_data["transformations"])
    rule_data["actions"], rule_data["rule_id"] = convert_actions_list_to_str(rule_data["actions"])
    return rule_data


def convert_waf_rule_database(rule: dict):
    """Function to convert fields of a WAF rule from an object containing an str for each field to a list"""
    rule["variables"] = list(rule["variables"].split(","))
    rule["operators"] = convert_operators_str_to_list(rule["operators"])
    rule["transformations"] = convert_transformations_str_to_list(rule["transformations"])
    rule["actions"] = convert_actions_str_to_list(rule["actions"])
    return rule


def find_possible_id():
    """Function that return the possible id that can the new GEOIP rule can take it"""
    # Get list of all existed rule from created rules and GEOIP rules
    list_rule_waf = []
    if len(RulesWaf.objects.filter(created=True)) > 0:
        list_rule_waf = [rule.rule_id for rule in RulesWaf.objects.filter(created=True)]
    list_rule_geoip = []
    if len(ApplicationWaf.objects.all()) > 0:
        list_rule_geoip = [rule.rule_geoip_id for rule in ApplicationWaf.objects.all() if rule.rule_geoip_id]
    list_rule_id = list_rule_waf + list_rule_geoip
    if len(list_rule_id) > 0:
        # Sort the list in ascending order
        list_rule_id.sort(reverse=True)
        for rule_id in range(1, list_rule_id[0]):
            if rule_id not in list_rule_id:
                return rule_id
        return list_rule_id[0] + 1
    return 1


def convert_operators_list_to_str(list_operators: list):
    """Convert list of operators objects (each one contain type and value) to a string,
    add @ before each operator and seperate between two operators with comma"""
    print("list_operators= ", list_operators)
    operators = ""
    for operator_dict in list_operators:
        operators += f"""@{operator_dict["type"]}"""
        if operator_dict["value"] != "":
            operators += f""" {operator_dict["value"]}"""
        operators += ","
    # Remove the last comma
    return operators[:-1]


def convert_operators_str_to_list(operators: str):
    """Convert operators from str format to a list of objects contains type and value"""
    if operators != "":
        # Convert operators from str format to a list
        operators = list(operators.split(","))
        # Create an empty list
        list_operators = []
        for operator in operators:
            operator_list = list(operator.split(" "))
            # Remove the first character (@) from type
            if len(operator_list) > 1:
                list_operators.append({"type": operator_list[0][1:], "value": operator_list[1]})
            else:
                list_operators.append({"type": operator_list[0][1:], "value": ""})
        return list_operators
    return []


def convert_transformations_list_to_str(list_transformations: list):
    """Convert list of transformations objects to a string, 
    add t: before each transformation and seperate between two transformations with comma"""
    transformations = ""
    for transformation in list_transformations:
        transformations += f"""t:{transformation},"""
    # Remove the last comma
    return transformations[:-1]


def convert_transformations_str_to_list(transformations: str):
    """Convert transformations from str format to a list"""
    if transformations != "":
        # Convert transformations from str format to a list
        transformations = list(transformations.split(","))
        return [transf.replace("t:", "") for transf in transformations]
    return []


def convert_actions_list_to_str(list_actions:list):
    """Convert list of actions objects (each one contain type and value) to a string,
    add @ before each action and seperate between two actions with comma"""
    actions = ""
    rule_id = None
    for action_dict in list_actions:
        if action_dict["type"] == "id":
            rule_id = action_dict["value"]
        actions += action_dict["type"]
        if action_dict["value"] != "":
            actions += f""":{action_dict["value"]}"""
        actions += ","
    if rule_id:
        return actions[:-1], rule_id
    

def convert_actions_str_to_list(actions: str):
    """Convert actions from str format to a list of objects contains type and value"""
    if actions != "":
        actions = list(actions.split(","))
        list_actions = []
        for action in actions:
            action_list = list(action.split(":"))
            if len(action_list) > 1:
                list_actions.append({"type": action_list[0], "value": action_list[1]})
            else:
                list_actions.append({"type": action_list[0], "value": ""})
        return list_actions
    return []
