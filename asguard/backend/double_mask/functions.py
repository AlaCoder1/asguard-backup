import subprocess
import re
import ipaddress

def run_command(command):
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error

def is_address_in_subnet(address: str, subnet: str) -> bool:
    """Check if an IP address is in a given subnet."""
    return ipaddress.ip_address(address) in ipaddress.ip_network(subnet, strict=False)

def get_nft_ip_addresses():
    try:
        result,error=run_command("sudo nft list ruleset | grep -E 'accept|drop|reject' | grep -vE 'policy (accept|reject|drop)'")
        rules_list=[]
        n=0
        if result !='':
            ruleset = result.splitlines()
            n=len(ruleset)
            ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?:/\d{1,2})?\b'
            for i in range(len(ruleset)):
                ip_addresses = re.findall(ip_pattern, ruleset[i])
                if ip_addresses!=[] and len(ip_addresses)==1:
                    address=ip_addresses[0].split("/")[0] if ip_addresses[0].find("/")!=-1 else ip_addresses[0]
                    rules_list.append(address) 
        return rules_list, n
    except Exception as e:
        print(f"Error: {e}")
        return [],0
    
def parse_subnet_address(config_text):
    """
    API to parse subnet addresses from a given configuration text.
    
    This function handles the parsing of subnet addresses from the given configuration text.
    The function returns a list of tuples, where each tuple contains the start and end subnet addresses.
    
    """
    result_pattern = re.compile(r"\d+\.\d+\.\d+\.\d+/\d+/\d+")

    lines = config_text.strip().split("\n")

    parsed_data = []
    for x in lines:
        if  result_pattern.match(x):
            x=x.strip().split('/')
            parsed_data.append(x[0].strip()+"/"+x[1].strip())
    
    return parsed_data

def get_compr_ratio():
    """
    API to get compression ratioo.
    
    This function handles the GET request to get the compression ratio of double mask.
    
    
    """
    output,error=run_command('sudo cat /etc/DoubleMask.conf')
    if output=="":
        ratio=0
        n_comp=0
        n=0
    else:
        ruleset_list,n=get_nft_ip_addresses()
        subnet_double=parse_subnet_address(output)
        ruleset_compr=[]
        if (len(subnet_double))!=0:
            for s in subnet_double:
                ruleset_compr+=[x for x in ruleset_list if is_address_in_subnet(x,s) and x not in ruleset_compr ]
            n_comp=n-len(ruleset_compr)+len(subnet_double)
            if n!=0:
                ratio=round(((n-n_comp)/n)*100,2)
            else:
                ratio=0
            
    return ratio,n_comp,n