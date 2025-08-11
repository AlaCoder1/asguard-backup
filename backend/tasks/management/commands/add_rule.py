from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.rules.functions import get_position
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
            if source_address.lower() == 'all':
                source_address = None
            if destination_address.lower() == 'all':
                destination_address = None
            if source_port.lower() == 'all' or protocol=="icmp":
                source_port = None
            if destination_port.lower() == 'all' or protocol=="icmp":
                destination_port = None
            interface_id = Interface.objects.get(ifname=interface)
            return_init_file_nftables = init_file_nftables(interface)
            if return_init_file_nftables:
                saddr_db=calculate_subnet_address(source_address)
                daddr_db=calculate_subnet_address(destination_address)
                rule=return_rule(interface,policy,saddr_db,daddr_db,source_port,destination_port,protocol,type_rule)
                prefix="___nftables_logs_rule___"+"_".join(rule.split(" "))+"___"
                prefix=prefix.replace('"', '')
                prefix=prefix.replace('-', '')
                if rule.find("reject with icmp port-unreachable")==-1:
                    rule_mod=" ".join(rule.split(" ")[:-1])
                    policy=rule.split(" ")[-1]
                    rule=f'{rule_mod} log prefix "{prefix}" {policy}'
                else:
                    rule_mod=rule.split("reject with icmp port-unreachable")[0].strip()
                    rule=f'{rule_mod} log prefix "{prefix}" reject with icmp port-unreachable'
                rule=rule.strip()
                if not Rule.objects.filter(
                    Q(rule=rule) & (
                        (Q(interface_id=interface_id.id) ) &
                        (Q(type_rule=type_rule))
                    )
                ).exists():
                    return_add_rule=add_rule_remote(rule,interface,type_rule)
                    if return_add_rule is True:
                        try:
                            position=get_position(type_rule)
                            rule = Rule.objects.create(rule=rule, rule_status=True, type_rule=type_rule, policy=policy, rule_description=description, protocol=protocol, saddr=source_address, sport=source_port, daddr=destination_address, dport=destination_port, interface=interface_id,position=position)
                            return "rule added succesffuly"
                        except IntegrityError as e:
                            print("Error occurred:", e)
                    else:
                        return return_add_rule
                else:
                    return "This rule is already exist"
        except IntegrityError as e:
            return "Error: " + str(e)