#!/bin/bash

# Function to get public IP address
get_public_ip() {
    # Extract IPv4 addresses with /32 mask as apublic address 
    #in testing context i will use /24
    ip_addrs=$(ip addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}/32')
    
    # Check if we got an IP address
    if [ -z "$ip_addrs" ]; then
        echo "Unable to detect public IP address (/32 mask)."
        exit 1
    fi

    ip_addr=$(echo $ip_addrs | sed 's/\//\n/g' | head -n 1)

    # Return the first IP address found
    echo "$ip_addr"
}

# Get public IP address of controller
controller_ip=$(get_public_ip)

echo $controller_ip