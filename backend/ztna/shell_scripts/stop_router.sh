#!/bin/bash

# Prompt the user for the router name
echo "Please enter the router name:"
read router_name

# Search for the process using the router name
process=$(ps aux | grep "ziti router run .*/${router_name}\.yaml" | grep -v grep)

# Check if the process was found
if [ -z "$process" ]; then
    echo "No running router found with the name '$router_name'."
else
    # Extract the PID of the process
    pid=$(echo "$process" | awk '{print $2}')

    kill $pid && echo "Router '$router_name' stopped successfully." || echo "Failed to stop router '$router_name'."
fi
