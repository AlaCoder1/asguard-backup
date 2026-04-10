#!/bin/bash

read router_name

source /root/.ziti/quickstart/Asguard/Asguard.env

command_path="${ZITI_BIN_DIR:-}/ziti"

router_config_file="/asguard/asguard/backend/ztna/relays_folder/${router_name}/${router_name}.yaml"

log_file="/asguard/asguard/backend/ztna/relays_folder/${router_name}/${router_name}.log"

nohup $command_path router run "$router_config_file" >"$log_file" 2>&1 &

echo "Ziti router is running in the background. Logs can be found in $log_file"
