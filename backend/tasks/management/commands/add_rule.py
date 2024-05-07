from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.rules.models import Rule 
from backend.rules.views import * 
from backend.network.models import Interface

class Command(BaseCommand):
    def add_arguments(self, parser):
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
            print({"source_address":source_address})
            print({"source_port":source_port})
            print({"destination_address":destination_address})
            print({"destination_port":destination_port})
            print({"interface":interface})
            print({"description":description})
            if source_address.lower() == 'all':
                source_address = None
            if destination_address.lower() == 'all':
                destination_address = None
            if source_port.lower() == 'all':
                source_port = None
            if destination_port.lower() == 'all':
                destination_port = None
            interface_id = Interface.objects.get(ifname=interface)
            print({"interface_id":interface_id.id})
            return_init_file_nftables = init_file_nftables(interface)
            print({"return_init_file_nftables":return_init_file_nftables})
            if return_init_file_nftables:
                rule=return_rule(policy,source_address,destination_address,source_port,destination_port,protocol,type_rule)
                saddr_db=calculate_subnet_address(source_address)
                daddr_db=calculate_subnet_address(destination_address)
                rule_db=return_rule(policy,saddr_db,daddr_db,source_port,destination_port,protocol,type_rule)
                print({"rule":rule})
                if not Rule.objects.filter(
                    Q(rule=rule_db) & (
                        (Q(interface_id=interface_id.id) ) &
                        (Q(type_rule=type_rule))
                    )
                ).exists():
                    return_add_rule=add_rule_remote(rule,interface,type_rule)
                    print({"return_add_rule":return_add_rule})
                    if return_add_rule is True:
                        
                        print({"rule_db":rule_db})
                        try:
                            rule = Rule.objects.create(rule=rule_db, rule_status=True, type_rule=type_rule, policy=policy, rule_description=description, protocol=protocol, saddr=source_address, sport=source_port, daddr=destination_address, dport=destination_port, interface=interface_id)
                            return "rule added succesffuly"
                            
                            # If you reach this point, creation was successful
                        except IntegrityError as e:
                            # Handle the integrity error, maybe log it or perform some other action
                            print("Error occurred:", e)
                        # rule=Rule.objects.create(rule=rule_db, rule_status=True, type_rule = type_rule, policy = policy, rule_description = description, protocol = protocol, saddr = saddr_db, sport = source_port, daddr = daddr_db, dport = destination_port, interface = interface_id)
                    else:
                        return return_add_rule
                else:
                    return "exist"
        except IntegrityError as e:
            return "Error: " + str(e)