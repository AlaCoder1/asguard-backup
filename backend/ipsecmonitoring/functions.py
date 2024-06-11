import json
import subprocess
import time
from backend.ipsecmonitoring.models import IpsecMonitoring
from django.core import serializers


def run_command(command):
    completed_process = subprocess.run("sudo "+command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error
def get_uptime():
    """function to get uptime from logs"""
    uptime=None
    command='ipsec statusall | grep "uptime" | cut -d \',\' -f 1'
    output, error=run_command(command)
    if output!='' and error=='':
        list_uptime=output.split(':')[1].strip().split(' ')
        if len(list_uptime)>1:
            if list_uptime[1].lower()=='minutes':
                uptime=int(list_uptime[0])*60
            elif list_uptime[1].lower()=='hours':
                uptime=int(list_uptime[0])*3600
            else:
                uptime=int(list_uptime[0])
    return uptime 
def get_establishetd_date():
    """function to get tunnel establishetd date from logs"""
    establishetd_date=None
    command='ipsec statusall | grep "uptime" | cut -d "," -f2'
    output, error=run_command(command)
    if output!='' and error=='':
        establishetd_date=output.strip('since')
    return establishetd_date         
def get_time_established():
    """function to get all time from established connections"""
    time_established=None
    command='ipsec statusall | grep "ESTABLISHED" | cut -d \',\' -f 1'
    output, error=run_command(command)
    if output!='' and error=='':
        list_estab=output.split(':')[1].strip().split(' ')[1:-1] 
        if len(list_estab)>1:
            if list_estab[1].lower()=='minutes':
                time_established=int(list_estab[0])*60
            elif list_estab[1].lower()=='hours':
                time_established=int(list_estab[0])*3600
            else:
                time_established=int(list_estab[0])
    return time_established
        
    
def get_availability(time_established,uptime):
    """function to calculate availability %"""
    availability=0
    if uptime is not  None and time_established is not None:
        availability=round((time_established/uptime)*100,2)
    return availability
 
 
def get_active_session():
    """function to get nomber of active sessions"""
    active_session=0
    command='ipsec statusall | grep "Security Associations" | cut -d \'(\' -f 2 | cut -d \',\' -f 1'
    output, error=run_command(command)
    if output!='' and error=='':
        active_session=output.split(' ')[0]
    return active_session

       
def get_bytes_in():
    """function to get bytes received (in)"""
    bytes_in=0
    command='ipsec statusall | grep "bytes_i" | cut -d ":" -f 2 | cut -d "," -f2'
    output, error=run_command(command)
    if output!='' and error=='':
        bytes_in=output.strip().split(' ')[0]
        bytes_in=int(bytes_in) if bytes_in!='' else 0
    return bytes_in

def get_bytes_out():
    """function to get bytes sent (out)"""
    bytes_out=0
    command='ipsec statusall | grep "bytes_i" | cut -d ":" -f 2 | cut -d "," -f3'
    output, error=run_command(command)
    if output!='' and error=='':
        bytes_out=output.strip().split(' ')[0]
        bytes_out=int(bytes_out) if bytes_out!='' else 0
    return bytes_out  

def get_tunnel_ip(tunnel_name):
    """function to get tunnel ip from tunnel name"""
    tunnel_endpoint_ip = f"ipsec status | grep -i {tunnel_name} | grep -o '===.*' | awk '{{print $2}}' | cut -d'/' -f1"
    output, _=run_command(tunnel_endpoint_ip)
    return output.split('\n')[0]
def get_packet_loss(address):
    """function to get packet loss % """
    packet_loss=0
    command=f"ping {address} -c 20 -i 0.2 -W1 | grep loss | cut -d ',' -f3"
    output, error=run_command(command)
    if output!='' and error=='':
        packet_loss=output.split(' ')[0].strip('%')
        packet_loss=int(packet_loss) if packet_loss!='' else 0
    return packet_loss

def get_availabile_bytes(bytes_in,bytes_out):
    """function to calculate availability bytes """
    availability_bytes=0
    if bytes_in !=0 and bytes_out!=0:
        availability_bytes=round(bytes_out/bytes_in,2)
    return availability_bytes

def convert_to_seconds(time_value, time_unit):
    """
    Convert a given time value in minutes, hours, days, or weeks into seconds.

    :param time_value: The numerical value of the time to be converted.
    :param time_unit: The unit of time for the time_value ('minutes', 'hours', 'days', 'weeks').
    :return: The equivalent time in seconds.
    """
    # Define conversion factors for each time unit to seconds
    conversion_factors = {
        'minutes': 60,
        'hours': 3600,
        'days': 86400,
        'weeks': 604800
    }
    
    # Convert the given time value to seconds
    if time_unit in conversion_factors:
        seconds = time_value * conversion_factors[time_unit]
        return seconds
    else:
        return None
    
def get_differnce_time(timestamp,current_time):
    """function to get differnce time"""
    differnce_time=0
    if timestamp is not None and current_time is not None:
        differnce_time=current_time-timestamp
    return differnce_time
    
def get_data_time(time_value):
    """function to last time _value from database that  """
    all_data=[]
    all_data_object=IpsecMonitoring.objects.all()
    data = serializers.serialize("json", all_data_object)
    res = json.loads(data)
    for i in range(len(res)):
        res[i]['fields']['id']=res[i]["pk"]
        diffrence_time=(time.time()-time_value)-res[i]['fields']["timestamp"]
        if diffrence_time>=0:
            all_data.append(res[i]['fields'])
    return all_data
            

