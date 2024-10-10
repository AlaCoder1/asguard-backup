#!/bin/bash

source /root/.ziti/quickstart/Asguard/Asguard.env

command_path="${ZITI_BIN_DIR:-}/ziti"

# Read router name and JWT token from stdin
read router_name
read jwt_token

files=("${router_name}.yaml" "${router_name}.jwt" "${router_name}_enrollment.log")

create_and_enroll=true

# Function to generate the full path for the router folder inside relays_folder
get_router_folder_path() {
    local router_name="$1"
    local script_dir="$(dirname "${BASH_SOURCE[0]}")"
    echo "$script_dir/relays_folder/${router_name}"  # Always place inside relays_folder
}

# Check if at least one of the files exists
for file in "${files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "Router files exist. Skipping creation and enrollment."
        create_and_enroll=false
        break # Exit the loop once existence is confirmed
    fi
done

if [ "$create_and_enroll" = true ]; then
    # Create the directory inside relays_folder
    dir_path=$(get_router_folder_path "$router_name")
    mkdir -p "$dir_path"

    # Create the JWT file with the token
    jwt_file="$dir_path/${router_name}.jwt"
    echo $jwt_token > "$jwt_file"
    chmod 400 "$jwt_file"

    # Create the router configuration file
    router_config_file="$dir_path/${router_name}.yaml"
    $command_path create config router edge --routerName "$router_name" > "$router_config_file"
    sleep 2

    # Enroll the router and capture the enrollment log
    enrollment_log="$dir_path/${router_name}_enrollment.log"
    $command_path router enroll "$router_config_file" --jwt "$jwt_file" &> "$enrollment_log"
    sleep 2

    echo "Router creation and enrollment completed successfully."
else
    echo "Skipping router creation due to existing files."
fi
