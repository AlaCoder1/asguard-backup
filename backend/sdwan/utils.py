from backend.gateway.models import Gateway, GatewayInterface
from backend.network.models import IP4Config, Interface
from backend.sdwan.models import AreaInterface, SdwanRules


def search_routing_table_id():
    """Return the first possible id that system can create a routing table with it"""
    sdwan_rule_list = SdwanRules.objects.order_by("table_id").values("table_id")
    sdwan_rule_list = [id['table_id'] for id in sdwan_rule_list]
    first_unused_id = 1
    while first_unused_id in sdwan_rule_list:
        first_unused_id += 1
    return first_unused_id


def rule_failover_requirements(rule_id):
    """Take the id of the rule and return its requirements to start it: primary and backup gateway and ifname"""

    # Get the list of interfaces 
    sdwan_rule = SdwanRules.objects.get(id=rule_id)
    area_interfaces = AreaInterface.objects.filter(area=sdwan_rule.area)
    area_interfaces = [area_interface.interface for area_interface in area_interfaces]

    # Remove the primary to get the backup interface
    area_interfaces.remove(sdwan_rule.primary_interface)
    backup_interface = area_interfaces[0]

    # Get primary and backup gateway and ifname
    list_interfaces = get_interfaces_details(sdwan_rule.primary_interface.name_interface, backup_interface.name_interface)
    return (list_interfaces[0]["gateway"], list_interfaces[0]["ifname"], 
            list_interfaces[1]["gateway"], list_interfaces[1]["ifname"])


def rule_round_robin_requirements(rule_id):
    """Take the id of the rule and return the its requirements to start it: 
    gateway and ifname of each interface of the area"""

    sdwan_rule = SdwanRules.objects.get(id=rule_id)
    area_interfaces = AreaInterface.objects.filter(area=sdwan_rule.area)
    list_interfaces = [area_interface.interface.name_interface for area_interface in area_interfaces]

    # Get primary and backup gateway and ifname
    list_interfaces = get_interfaces_details(*list_interfaces)

    return list_interfaces


def get_interfaces_details(*args):
    """Take a list of name of interfaces and returns informations related to this interface"""
    list_interfaces = []
    for interface_name in args:
        interface = Interface.objects.get(name_interface=interface_name)
        ipv4 = IP4Config.objects.get(interface=interface)
        gateway_interface = GatewayInterface.objects.get(interface=interface)
        gateway = Gateway.objects.get(id=gateway_interface.gateway.pk)
        list_interfaces.append({"ifname": interface.ifname,
                                "address": ipv4.ip_address,
                                "mask": ipv4.netmask,
                                "gateway": gateway.gwaddress})
    return list_interfaces
