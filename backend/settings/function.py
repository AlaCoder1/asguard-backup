import subprocess

def get_time_zone():
    command_output = subprocess.check_output(['timedatectl']).decode('utf-8')
    for line in command_output.split('\n'):
        if 'Time zone:' in line:
            return line.split(':')[-1].strip()
        
def set_time_zone(time_zone):
    try:
        subprocess.run(['timedatectl', 'set-timezone', time_zone], check=True)
        return True
    except subprocess.CalledProcessError:
        return False
   
def get_hostname():
    try:
        # Open the /etc/hostname file and read the hostname
        with open("/etc/hostname", "r") as file:
            hostname = file.readline().strip()
        return hostname
    except Exception as e:
        print("Error:", e)
        return None     

def change_hostname(new_hostname):
    try:
        subprocess.run(['sudo', 'hostnamectl', 'set-hostname', new_hostname], check=True)
        return True
    except subprocess.CalledProcessError as e:
        return False

    
def change_domain(new_domain):
    # Read the contents of /etc/resolv.conf
    with open('/etc/resolv.conf', 'r') as file:
        resolv_conf_content = file.readlines()

    # Modify the search parameter line if it exists
    for i, line in enumerate(resolv_conf_content):
        if line.startswith("search"):
            resolv_conf_content[i] = f"search {new_domain}\n"
            break
    else:
        # If the search parameter line doesn't exist, add a new line
        resolv_conf_content.append(f"search {new_domain}\n")

    # Write the modified content back to /etc/resolv.conf
    with open('/etc/resolv.conf', 'w') as file:
        file.writelines(resolv_conf_content)
        
def get_dns_servers():
    nameservers = []
    with open('/etc/resolv.conf', 'r') as file:
        for line in file:
            if line.startswith('nameserver'):
                nameservers.append(line.split()[1])
    return nameservers


def add_dns_servers(nameserver):
    # Read the current content of /etc/resolv.conf
    with open('/etc/resolv.conf', 'r') as file:
        existing_content = file.readlines()
    if nameserver not in get_dns_servers():
        existing_content.append(f"nameserver {nameserver}\n")

        # Write the updated content back to /etc/resolv.conf
        with open('/etc/resolv.conf', 'w') as file:
            file.writelines(existing_content)
        

def add_gateway_to_dns_servers(nameserver,gateways_address,ifname,metric):
    cmd = f'ip route add {nameserver} via {gateways_address} dev {ifname} metric {metric}'
    completed_process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output,error