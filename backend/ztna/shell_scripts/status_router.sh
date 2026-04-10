#!/bin/bash

read router_name

process=$(ps aux | grep "router run .*${router_name}"  | grep -v grep)

if [ -z "$process" ]; then
    echo "Router is not running"
else
    # Extract the PID of the process
    pid=$(echo "$process" | awk '{print $2}')
    echo "$pid"
fi
