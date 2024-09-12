#!/bin/bash

# Prompt the user for the router name
echo "Please enter the router name:"
read router_name

source /root/.ziti/quickstart/Asguard/Asguard.env

sleep 2
# Define the base command path
command_path="${ZITI_BIN_DIR:-}/ziti"

files=("${router_name}.yaml" "${router_name}.jwt" "${router_name}_enrollment.log")

# Flag to track if we need to create and enroll the router
create_and_enroll=true
router_config_file="${router_name}.yaml"

# Check if at least one of the files exists
for file in "${files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "Router files exist. Skipping creation and enrollment."
        create_and_enroll=false
        break # Exit the loop once existence is confirmed
    fi
done

if [ "$create_and_enroll" = true ]; then
    echo "Please enter the JWT token:"
    read jwt_token

    # Create the JWT file with the token
    jwt_file="${router_name}.jwt"
    echo $jwt_token > $jwt_file

    # Set the JWT file permissions to read-only for the owner/user
    chmod 400 $jwt_file

    # Create the router configuration file
    $command_path create config router edge --routerName $router_name > $router_config_file
    sleep 2

    # Enroll the router and capture the enrollment log
    $command_path router enroll $router_config_file --jwt $jwt_file &> "${router_name}_enrollment.log"
    sleep 2
fi

# Run the router using nohup to keep it running after logout
nohup $command_path router run $router_config_file &
