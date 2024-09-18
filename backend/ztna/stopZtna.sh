#!/bin/bash

# Search for the process of running the Ziti controller
process=$(ps aux | grep "controller run"  | grep -v grep)
echo "process id = $process"

# Check if the process was found
if [ -z "$process" ]; then
    echo "ZTNA is not running"
else
    # Extract the PID of the process
    pid=$(echo "$process" | awk '{print $2}')
    kill $pid && echo "ZTNA stopped successfully." || echo "Failed to stop ZTNA."
fi

