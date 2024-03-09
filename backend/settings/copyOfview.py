def get_dns_servers():
    nameservers = []
    with open('/etc/resolv.conf', 'r') as file:
        for line in file:
            if line.startswith('nameserver'):
                nameservers.append(line.split()[1])
    return nameservers


print(get_dns_servers())