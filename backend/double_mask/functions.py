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
    
def get_compr_ratio():
    """
    API to get compression ratioo.
    
    This function handles the GET request to get the compression ratio of double mask.
    
    
    """
    output,error=run_command('sudo dmesg | grep "The Double mask for"')
    if output=="":
        ratio=0
        n_comp=0
        n=0
    else:
        ruleset_list,n=get_nft_ip_addresses()
        subnet_double=output.split("is")[1].split("/")[0:2]
        print(subnet_double)
        subnet=subnet_double[0].strip()+"/"+subnet_double[1].strip()
        ruleset_compr=[x for x in ruleset_list if is_address_in_subnet(x,subnet) ]
        ratio=(len(ruleset_compr)/n)*100
        n_comp=n-len(ruleset_compr)+1
    return ratio,n_comp,n