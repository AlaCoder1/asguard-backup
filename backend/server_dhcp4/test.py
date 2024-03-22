# config=['192.168.10.1','192.168.20.1']

# result_string = ' , '.join(filter(None, config))
# print(result_string)import ipaddress

import ipaddress

def is_ip_in_range(ip_address, start_range, end_range):
    ip_address = ipaddress.ip_address(ip_address)
    start_ip = ipaddress.ip_address(start_range)
    end_ip = ipaddress.ip_address(end_range)

    return start_ip <= ip_address <= end_ip

# Example usage:
start_ip = "192.168.1.1"
end_ip = "192.168.1.10"

test_ip = "192.168.1.25"

if is_ip_in_range(test_ip, start_ip, end_ip):
    print(f"{test_ip} is within the IP range.")
else:
    print(f"{test_ip} is outside the IP range.")

