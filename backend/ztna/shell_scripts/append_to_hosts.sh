#!/bin/bash

if ! printf "%s %s\n" "Unable to detect public IP address (/32 mask)." "Asguard" | sudo tee -a /etc/hosts > /dev/null; then
    echo "Failed to append entry to /etc/hosts"
    exit 1
fi
    
echo "Successfully appended entry to /etc/hosts"
    
