from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.rules.models import Rule 
from backend.rules.views import * 
from backend.network.models import Interface

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-r', '--rule', type=str, help='Define a rule')
        parser.add_argument('-tp', '--type_rule', type=str, help='Define a type rule')
        parser.add_argument('-po', '--policy', type=str, help='Define a policy')
        parser.add_argument('-pr', '--protocol', type=str, help='Define a protocol')
        parser.add_argument('-saddr', '--source_address', type=str, help='Define a source address')
        parser.add_argument('-sport', '--source_port', type=str, help='Define a source_port')
        parser.add_argument('-daddr', '--destination_address', type=str, help='Define a destination address')
        parser.add_argument('-dport', '--destination_port', type=str, help='Define a destination port')
        parser.add_argument('-i', '--interface', type=str, help='Define a interface')
        parser.add_argument('-d', '--description', type=str, help='Define a description')
    def handle(self, *args, **options):
        try:
            rule = options.get('rule')
            type_rule = options.get('type_rule')
            policy = options.get('policy')
            protocol = options.get('protocol')
            if protocol == 'icmp-type-echo-reply':
                protocol = 'icmp type echo-reply'
            if protocol == 'icmp-type-echo-request':
                protocol = 'icmp type echo-request'
            source_address = options.get('source_address')
            source_port = options.get('source_port')
            destination_address = options.get('destination_address')
            destination_port = options.get('destination_port')
            interface = options.get('interface')
            description = options.get('description')
            description = description.replace("-"," ")
            rule = rule.replace("-"," ")
            rule = rule.replace(interface,'"'+interface+'"')
            if source_address.lower() == 'all':
                source_address = None
            if destination_address.lower() == 'all':
                destination_address = None
            if source_port.lower() == 'all' or protocol=="icmp":
                source_port = None
            if destination_port.lower() == 'all' or protocol=="icmp":
                destination_port = None
            # print({"rule":rule})
            # print({"type_rule":type_rule})
            # print({"policy":policy})
            # print({"protocol":protocol})
            # print({"source_address":source_address})
            # print({"source_port":source_port})
            # print({"destination_address":destination_address})
            # print({"destination_port":destination_port})
            # print({"interface":interface})
            # print({"description":description})
            interface_id = Interface.objects.get(ifname=interface)
            ruleupdate=return_rule(interface,policy,source_address,destination_address,source_port,destination_port,protocol,type_rule)
            handle=get_handle_rule(interface,type_rule,rule)
            if handle is not None:
                return_delete_rule_remote=delete_rule_remote(interface,type_rule,handle)
                if return_delete_rule_remote is True:
                    return_add_rule=add_rule_remote(ruleupdate,interface,type_rule)
                    if  return_add_rule is True:
                        saddr_db=calculate_subnet_address(source_address)
                        daddr_db=calculate_subnet_address(destination_address)
                        rule_db_update=return_rule(interface,policy,saddr_db,daddr_db,source_port,destination_port,protocol,type_rule)
                        try:
                            rule = Rule.objects.get(rule=rule)
                            rule.rule = rule_db_update
                            rule.rule_status=True 
                            rule.policy=policy 
                            rule.rule_description=description 
                            rule.protocol=protocol 
                            rule.saddr=source_address 
                            rule.sport=source_port 
                            rule.daddr=destination_address 
                            rule.dport=destination_port 
                            rule.save()
                            return "rule updated succesffuly"
                            
                        except IntegrityError as e:
                            print("Error occurred:", e)
                            
                    else:
                        return return_add_rule
                else:
                    return "This rule is already exist"
            else:
                return "Something Wrong"
        except IntegrityError as e:
            return "Error: " + str(e)