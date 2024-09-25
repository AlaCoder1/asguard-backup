#!/bin/bash

# Search for the process of running the Ziti controller
process=$(ps aux | grep "controller run"  | grep -v grep)

# Check if the process was found
if [ -z "$process" ]; then
    echo "ZTNA is not running"
else
    # Extract the PID of the process
    pid=$(echo "$process" | awk '{print $2}')
    echo "$pid"
fi
