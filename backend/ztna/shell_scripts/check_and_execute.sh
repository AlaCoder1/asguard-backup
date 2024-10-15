#!/bin/bash

# Directory where the append_to_host files are located
file_directory="/asguard/newdms/backend/ztna/shell_scripts/"

# Source the get_public_ip function from get_public_ip.sh
source $file_directory/get_public_ip.sh

# Function to extract the IP from the .bat or .sh files (assuming the IP is stored inside)
extract_ip_from_file() {
    grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' "$1"
}

# Get the current public IP
current_ip=$(get_public_ip)

# Check if the files exist
bat_exists=false
sh_exists=false

if [[ -f "$file_directory/append_to_hosts.bat" ]]; then
    bat_exists=true
fi

if [[ -f "$file_directory/append_to_hosts.sh" ]]; then
    sh_exists=true
fi

if $bat_exists && $sh_exists; then
    # You can choose to extract the IP from either the .bat or .sh file (I'll use .bat here)
    stored_ip=$(extract_ip_from_file "$file_directory/append_to_hosts.bat")

    if [[ "$stored_ip" == "$current_ip" ]]; then
        echo "IP address has not changed. Exiting."
        exit 0
    else
        echo "IP address has changed. Deleting append_to_hosts files and regenerating..."
        rm -f "$file_directory/append_to_hosts.bat" "$file_directory/append_to_hosts.sh"
        bat_exists=false
        sh_exists=false
    fi
fi

# Generate missing files
if ! $bat_exists; then
    echo "Generating append_to_hosts.bat..."
    bash $file_directory/get_public_ip.sh | bash $file_directory/windows_host.sh
fi

if ! $sh_exists; then
    echo "Generating append_to_hosts.sh..."
    bash $file_directory/get_public_ip.sh | bash $file_directory/linux_host.sh
fi
