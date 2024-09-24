#!/bin/bash

if ! printf "%s %s\n" "10.1.15.50" "Asguard" | sudo tee -a /etc/hosts > /dev/null; then
    echo "Failed to append entry to /etc/hosts"
    exit 1
fi
    
echo "Successfully appended entry to /etc/hosts"
    
