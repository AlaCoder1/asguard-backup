"""This file is for working on SDWAN in system"""

from datetime import datetime
import subprocess
import time

from celery import shared_task
from backend.sdwan.models import SdwanRules
from backend.sdwan.utils import rule_failover_requirements, rule_round_robin_requirements
from utils.commands_utils import execute_command_without_arguments


def create_sdwan_rule_in_system(source_address, table_id):
    """Function to create an sdwan rule in system by adding a routing table in system"""
    execute_command_without_arguments(['sudo', 'ip', 'rule', 'add', 'from', source_address, 'table', table_id])


def delete_sdwan_rule_in_system(table_id):
    """Function to delete an sdwan rule in system by removing the routing table in system"""
    execute_command_without_arguments(['sudo', 'ip', 'rule', 'del', 'table', table_id])


def update_sdwan_rule_in_system(source_address, table_id):
    """Function to update an sdwan rule in system by removing the routing table and adding it again"""
    delete_sdwan_rule_in_system(table_id)
    create_sdwan_rule_in_system(source_address, table_id)


def script_ping(interface, health_check_target):
    """Function to check the availability of the interface by testing the ping to a gateway associated with this interface"""
    process = subprocess.run(["sudo", "ping", "-c", "1", "-w", "1", "-I", interface, health_check_target], stdout=subprocess.PIPE, text=True, stderr=subprocess.PIPE)
    if process.stdout.find("1 packets transmitted, 1 received") >= 0:
        return True
    return False


def switch_gateway(previous_gateway, previous_ifname, new_gateway, new_ifname, table_id):
    """Function to switch between two gateways by defining a command that modifies the routing table (table 200) 
    to set the default gateway to the new gateway via the new interface"""
    subprocess.run(["sudo", "ip", "r", "d", "default", "via", 
                    previous_gateway, "dev", previous_ifname, "table", table_id])
    subprocess.run(["sudo", "ip", "r", "a", "default", "via", 
                    new_gateway, "dev", new_ifname,"table", table_id])


@shared_task
def script_failover(rule_id):
    """Function to execute the failover algorithm. When connectivity of the primary interface is lost, 
    the default gateway switches to the backup until the primary returns."""

    # Get the requirements of the interfaces primary and backup
    primary_gateway, primary_ifname, backup_gateway, backup_ifname = rule_failover_requirements(rule_id)
    sdwan_rule = SdwanRules.objects.get(id=rule_id)
    rule_status = sdwan_rule.rule_status
    
    # The while loop still running until the rule_status field of the sdwan rule table change to False
    while rule_status:
        # Test the availablility of the primary interface
        if script_ping(primary_ifname, sdwan_rule.health_check_target):
            print(f"primary interface: {primary_gateway}")
            switch_gateway(backup_gateway, backup_ifname, primary_gateway, primary_ifname, str(sdwan_rule.table_id))
        else:
            # Switch to the backup interface
            print(f"backup interface: {backup_gateway}")
            switch_gateway(primary_gateway, primary_ifname, backup_gateway, backup_ifname, str(sdwan_rule.table_id))
        time.sleep(sdwan_rule.health_check)
        rule_status = SdwanRules.objects.get(id=rule_id).rule_status


@shared_task
def script_round_robin(rule_id):
    """Function to execute the Round-Robin algorithm. Allocate time slots for the use of each connection. 
    For the time slots, all traffic will be directed through one of the ISP connection 
    after checking the availability of the interface and then the traffic will be redirected to the next ISP connection,
    and so on."""

    # Get the requirements of all interfaces
    list_interfaces = rule_round_robin_requirements(rule_id)
    sdwan_rule = SdwanRules.objects.get(id=rule_id)
    rule_status = sdwan_rule.rule_status
    interface_index = 0
    
    # The while loop still running until the rule_status field of the sdwan rule table change to False
    while rule_status:
        
        # Reset the interface_index to 0 after completing the list of interfaces
        if interface_index == len(list_interfaces):
            interface_index = 0
        print(f'''interface {interface_index}: {sdwan_rule.area.members.split(',')[interface_index]}''')
        print(list_interfaces[interface_index])

        # Calculate traffic duration for each interface
        start_trafic = datetime.now()
        trafic_duration = datetime.now() - start_trafic
        # The while loop for each interface still running if:
        # 1. Rule is still running (rule_status is True)
        # 2. Traffic duration is less the 10 seconds
        # 3. The interface is available
        while rule_status and (trafic_duration.seconds < 10) and script_ping(
            list_interfaces[interface_index]["ifname"], sdwan_rule.health_check_target):
            print(f'''duration of interface {interface_index}: {sdwan_rule.area.members.split(',')[interface_index]} : {trafic_duration.seconds}''')
            print("ping", script_ping(list_interfaces[interface_index]["ifname"], sdwan_rule.health_check_target))
            switch_gateway(
                list_interfaces[interface_index-1]["gateway"], list_interfaces[interface_index-1]["ifname"],
                list_interfaces[interface_index]["gateway"], list_interfaces[interface_index]["ifname"],
                str(sdwan_rule.table_id))
            time.sleep(sdwan_rule.health_check)
            trafic_duration = datetime.now() - start_trafic
            
            rule_status = SdwanRules.objects.get(id=rule_id).rule_status

        # Going to the next interface
        interface_index += 1


def start_sdwan_rule_in_system(rule_id):
    print('start background task')
    if len(SdwanRules.objects.filter(rule_status=True)) == 1:
        process = subprocess.Popen("sudo celery -A asguard worker -l info 2>/dev/null &", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        time.sleep(5)
        process.terminate()
        process.wait()
    sdwan_rule = SdwanRules.objects.get(id=rule_id)

    if sdwan_rule.algorythme_type == 'failover':
        script_failover.delay(rule_id)
    else:
        script_round_robin.delay(rule_id)


def kill_celery_process_in_system():

    if len(SdwanRules.objects.filter(rule_status=True)) == 0:
    # display information about the currently running processes
        process = execute_command_without_arguments(["sudo", "ps", "aux"])
        process = process.stdout.splitlines()

        # display information about the celery running processe
        celery_list = [line.split() for line in process if "celery" in line.split()[10]]
        execute_command_without_arguments(["sudo", "kill", "-9", celery_list[0][1]])


def synchronize_routing_table():
    list_sdwan_rule = SdwanRules.objects.order_by("table_id")
    print("list_sdwan_rule= ", list_sdwan_rule)
    list_routing_table_system = execute_command_without_arguments(["ip", "rule", "show"])
    list_routing_table_system = list_routing_table_system.stdout.splitlines()
    list_routing_table_system.remove('0:\tfrom all lookup local')
    list_routing_table_system.remove('32766:\tfrom all lookup main')
    list_routing_table_system.remove('32767:\tfrom all lookup default')
    for sdwan_rule in list_sdwan_rule:
        if not find_routing_table(sdwan_rule, list_routing_table_system):
            create_sdwan_rule_in_system(sdwan_rule.source_address, str(sdwan_rule.table_id))


def find_routing_table(sdwan_rule:SdwanRules, list_routing_table_system):
    """Find routing table in list of rules"""
    line_table_rule = f"from {sdwan_rule.source_address} lookup {sdwan_rule.table_id}"
    for table in list_routing_table_system:
        if table.find(line_table_rule) > -1:
            return True
    return False
