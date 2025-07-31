from backend.nat.models import DNat, OneToOneNat, SNat
from backend.nat import utils_system


def save_rules_positions(rules_result: list, nat_type: SNat | OneToOneNat | DNat):
    """
    function to update rules positions in database
    """
    nat_type.objects.update(db_position=None)
    for rule in rules_result:
        nat_object = nat_type.objects.get(id=rule['id'])
        nat_object.db_position = rule["pos"]
        nat_object.save()


def change_position_rule(rule_id: int, new_position: int, nat_type: SNat | OneToOneNat | DNat) -> list:
    """Change the position of a NAT rule and reorder the list of the NAT rules by changing the db_position field"""
    list_nat_db = nat_type.objects.all().order_by("db_position")
    list_nat_dict = [{"id": rule.pk, "pos": rule.db_position} for rule in list_nat_db]
    new_list_nat_dict = move_rule(list_nat_dict, rule_id, new_position)
    save_rules_positions(new_list_nat_dict, nat_type)


def move_rule(list_rule: list, rule_id: int, new_pos: int):
    """Move a rule with a specific ID to a new position in a list of rules.
    Each rule is represented as a dictionary with "id" and "pos" keys.
    The function reorders the list so that the rule with the given ID
    is moved to the specified position, and updates the "pos" values
    of all rules to maintain a consistent sequence starting from 1."""
    # Ensure the list is sorted by position
    list_rule.sort(key=lambda r: r["pos"])

    # Find the rule to move
    rule_to_move = next((r for r in list_rule if r["id"] == rule_id), None)
    if not rule_to_move:
        raise ValueError(f"Rule with id={rule_id} not found.")

    # Remove the rule to move
    list_rule.remove(rule_to_move)

    # Adjust new position bounds
    new_pos = max(1, min(new_pos, len(list_rule) + 1))

    # Insert the rule at the new position
    list_rule.insert(new_pos - 1, rule_to_move)

    # Reassign positions
    for i, rule in enumerate(list_rule, start=1):
        rule["pos"] = i

    return list_rule


def get_rule_handle_position_with_content(rule_content: str, list_nat_rules: list[str]):
    """Get a rule content and extract its handle and position from list of nat rules.
    If the rule doesn't exist in table nat in system then the function return False"""
    for rule_index, rule in enumerate(list_nat_rules):
        if f"{rule} # handle ".find(rule_content) > -1:
            rule_handle = rule.split(" # handle ", 1)[1]
            return rule_handle, rule_index
    return False


def synchronize_rule_database(nat_rule=None, rule_handle=None, rule_position=None, 
                              rule_type="postrouting", is_activated=True):
    """Synchronize nat rule in database with system by updating the rule parameters"""
    nat_rule.rule_status = is_activated
    nat_rule.rule_number = rule_handle
    if rule_type == "postrouting":
        nat_rule.postrouting_position = rule_position
    else:
        nat_rule.prerouting_position = rule_position
    nat_rule.save()


def synchronize_nat_rules():
    """Synchronize nat rules between system and database
    1. Synchronize rules from database to system:
        1.1 Get all activated rules from database
        1.2 Find them in system
        1.3 Extract handle and position for each rules
        1.4 Save this parameters in database
    2. Synchronize rules from system to database"""
    # Delete postrouting and prerouting position saved in database before updating it
    SNat.objects.filter(rule_status=True).update(postrouting_position=None)
    OneToOneNat.objects.filter(rule_status=True).update(postrouting_position=None)
    DNat.objects.filter(rule_status=True).update(prerouting_position=None)
    # Get all activated rules from database
    list_snat = SNat.objects.filter(rule_status=True)
    list_one_to_one_nat = OneToOneNat.objects.filter(rule_status=True)
    list_dnat = DNat.objects.filter(rule_status=True)
    # Get all nat rules in system
    list_postrouting_from_system, list_prerouting_from_system = utils_system.get_list_nat_rules_from_system()
    # Extract handle and position for each rule and synchronize in database
    # SNAT
    for snat in list_snat:
        rule_params = get_rule_handle_position_with_content(snat.rule_content, 
                                                            list_postrouting_from_system)
        if rule_params:
            synchronize_rule_database(snat, rule_params[0], rule_params[1])
        else:
            synchronize_rule_database(snat, is_activated=False)
    
    # One To One NAT
    for one_to_one_nat in list_one_to_one_nat:
        rule_params = get_rule_handle_position_with_content(one_to_one_nat.rule_content, 
                                                            list_postrouting_from_system)
        if rule_params:
            synchronize_rule_database(one_to_one_nat, rule_params[0], rule_params[1])
        else:
            synchronize_rule_database(one_to_one_nat, is_activated=False)
    
    # DNAT
    for dnat in list_dnat:
        rule_params = get_rule_handle_position_with_content(dnat.rule_content, 
                                                            list_prerouting_from_system)
        if rule_params:
            synchronize_rule_database(dnat, rule_params[0], rule_params[1], "prerouting")
        else:
            synchronize_rule_database(dnat, is_activated=False)


def deactivate_all_rules():
    """Deactivating all nat rules:
    1. Deleting them from system
    2. Making rule_status filed False
    3. Making postrouting_position and prerouting_position fields None"""
    utils_system.delete_all_nat_rule_from_system()
    SNat.objects.filter(rule_status=True).update(rule_status=False, 
                                                 postrouting_position=None, 
                                                 rule_number=None)
    OneToOneNat.objects.filter(rule_status=True).update(rule_status=False, 
                                                        postrouting_position=None, 
                                                 rule_number=None)
    DNat.objects.filter(rule_status=True).update(rule_status=False, 
                                                 prerouting_position=None, 
                                                 rule_number=None)


def get_next_nat_handle(rule_nat, chain="postrouting"):
    """Get the next rule handle in system. If the chain is postrouting it must take the minimum between SNAT and OneToOneNat"""
    if chain == "postrouting":
        try:
            list_next_snat = SNat.objects.filter(rule_status=True, postrouting_position__gt=rule_nat.postrouting_position)
        except ValueError:
            list_next_snat = []
        try:
            list_next_one_to_one_nat = OneToOneNat.objects.filter(rule_status=True, postrouting_position__gt=rule_nat.postrouting_position)
        except ValueError:
            list_next_one_to_one_nat = []

        if len(list_next_snat) > 0:
            next_snat_handle = list_next_snat.order_by('postrouting_position')[0].rule_number
            if len(list_next_one_to_one_nat) > 0:
                next_one_to_one_handle = list_next_one_to_one_nat.order_by('postrouting_position')[0].rule_number
                return min(next_snat_handle, next_one_to_one_handle)
            return next_snat_handle
        elif len(list_next_one_to_one_nat) > 0:
            return list_next_one_to_one_nat.order_by('postrouting_position')[0].rule_number
    else:
        list_next_dnat = DNat.objects.filter(rule_status=True, prerouting_position__gt=rule_nat.prerouting_position)
        if len(list_next_dnat) > 0:
            return list_next_dnat.order_by('prerouting_position')[0].rule_number
    return -1
