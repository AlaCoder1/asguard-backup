all_rules=[
    {"id":1,"rule_number":1,"snat_position":1,"rule_status":True},
    {"id":2,"rule_number":2,"snat_position":2,"rule_status":False},
    {"id":3,"rule_number":3,"snat_position":3 ,"rule_status":False},
    {"id":4,"rule_number":4,"snat_position":4,"rule_status":False},
    {"id":5,"rule_number":5,"snat_position":5,"rule_status":False},
    {"id":6,"rule_number":6,"snat_position":6,"rule_status":False},
   
]
new_rule= {"id":1,"rule_number":1,"new_snat_position":3,"rule_status":True}

def continue_until_true(all_rules:list,rule:str)-> str:
    """ 
    Continue until find a rule with rule_status=True.
    Return the command to be executed and the handle number of the rule.
    If no rule with rule_status=True is found, return an empty string and -1 as handle number.
    """
    i=all_rules.index(rule)
    while i < len(all_rules)-1 and all_rules[i]["rule_status"] is False:
        i+=1
        aux=False
        if all_rules[i]["rule_status"] is True :
            print("rule status active ..")
            print(all_rules[i])
            print("inserting rule in handle ...")
            print(handle)
            handle=all_rules[i]['rule_number']
           
            cmd ="nft insert rule"
            aux=True
            break 
    if aux==False:
        print("No next rule in system")
        print("adding rule ...")
        cmd="nft add rule "
    return cmd
        
        
def permut_rule_sys(new_rule:dict,all_rules:list[dict]):
    """ 
    This function takes a new rule and returns a command to be executed and the handle number of the rule.
    If no rule with rule_status=True is found, return an empty string and -1 as handle number.
    """
    cmd=""
    if new_rule["rule_status"] is True:
        rule_ind=next((rule for rule in all_rules if rule["snat_position"] == new_rule['new_snat_position']), None)
        if all_rules.index(rule_ind) == len(all_rules)-1:
            print("No next rule in system")
            print("adding rule ...")
            cmd="nft add rule "
        else:
            rule=all_rules[all_rules.index(rule_ind)+1]
            if rule["rule_status"] is True :
                handle=rule['rule_number']
                print("inserting rule in handle ...")
                print(handle)
                cmd ="nft insert rule"
            else:
                print("hello")
                cmd=continue_until_true(continue_until_true,rule)
    return cmd 
