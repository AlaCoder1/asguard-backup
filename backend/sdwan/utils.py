import subprocess
import time
from datetime import datetime
from celery import shared_task

from utils.commands_utils import execute_command_without_arguments


@shared_task
def script_failover(primary_interface_address='192.168.71.28', backup_interface_address='10.1.12.1'):
    while True:
        if script_ping(primary_interface_address):
            switch_to_primary(primary_interface_address)
        else:
            switch_to_backup(backup_interface_address)
        time.sleep(0.5)


def script_ping(primary_interface_address):
    process = subprocess.run(['ping', '-c', '1', primary_interface_address], stdout=subprocess.PIPE, text=True, stderr=subprocess.PIPE)
    print(f'ping at {str(datetime.now())}: ', process.stdout)
    if process.stdout.find("1 packets transmitted, 1 received") >= 0:
        return True
    return False
            

def switch_to_primary(primary_interface_address):
    print(f"primary interface: {primary_interface_address}")


def switch_to_backup(backup_interface_address):
    print(f"backup interface: {backup_interface_address}")


def start_sdwan_rule_system():
    print('start background task')
    list_ping = script_failover.delay()
    print("list_ping: ", list_ping.id)
