from backend.waf.models import ApplicationWaf, RulesWaf


def convert_waf_rule_payload(rule_data):
    """Function to convert a WAF rule payload 
    from an object containing a list for each field 
    to a string to each one of them and set the rule_id for the rule_data"""
    rule_data["variables"] = ",".join(rule_data["variables"])
    rule_data["operators"] = ",".join(rule_data["operators"])
    rule_data["transformations"] = ",".join(rule_data["transformations"])
    actions = ""
    for action_dict in rule_data["actions"]:
        if action_dict["type"] == "id":
            rule_data["rule_id"] = action_dict["value"]
        actions += action_dict["type"]
        if action_dict["value"] != "":
            actions += f""":{action_dict["value"]}"""
        actions += ","
    rule_data["actions"] = actions[:-1]
    return rule_data


def convert_waf_rule_database(rule: dict):
    """Function to convert fields of a WAF rule from an object containing an str for each field to a list"""
    rule["variables"] = list(rule["variables"].split(","))
    rule["operators"] = list(rule["operators"].split(","))
    rule["transformations"] = list(rule["transformations"].split(","))
    actions = list(rule["actions"].split(","))
    rule["actions"] = []
    for action in actions:
        action_list = list(action.split(":"))
        if len(action_list) > 1:
            rule["actions"].append({"type": action_list[0], "value": action_list[1]})
        else:
            rule["actions"].append({"type": action_list[0], "value": ""})
    return rule


def find_possible_id():
    """Function that return the possible id that can the new GEOIP rule can take it"""
    # Get list of all existed rule from created rules and GEOIP rules
    list_rule_waf = []
    if len(RulesWaf.objects.filter(created=True)) > 0:
        list_rule_waf = [rule.rule_id for rule in RulesWaf.objects.filter(created=True)]
    list_rule_geoip = []
    if len(ApplicationWaf.objects.all()) > 0:
        list_rule_geoip = [rule.rule_geoip_id for rule in ApplicationWaf.objects.all()]
    list_rule_id = list_rule_waf + list_rule_geoip
    # Sort the list in ascending order
    list_rule_id.sort(reverse=True)
    for rule_id in range(1, list_rule_id[0]):
        if rule_id not in list_rule_id:
            return rule_id
    return list_rule_id[0] + 1
