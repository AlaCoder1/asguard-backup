#!/bin/bash

# Define the base directory where the relays folders are stored
base_directory="/asguard/newdms/backend/ztna/relays_folder"

# Define the directory containing the router-specific files to be deleted
ziti_directory="/root/.ziti/quickstart/Asguard"

# Read the router name (UTS name) from the command line argument
read router_name

# Construct the full path to the router's folder
router_folder="${base_directory}/${router_name}"

# Define the router-specific files to delete based on the router_name
files_to_delete=(
    "$ziti_directory/${router_name}.cas"
    "$ziti_directory/${router_name}.cert"
    "$ziti_directory/${router_name}.key"
    "$ziti_directory/${router_name}.server.chain.cert"
)

# Check if the router folder exists and delete it
if [[ -d "$router_folder" ]]; then
    echo "Deleting folder for router: $router_name"
    rm -rf "$router_folder"
    echo "Folder and contents for router '$router_name' have been deleted."
else
    echo "Error: Folder for router '$router_name' does not exist."
fi

# Check and delete the specific files based on the router name
for file in "${files_to_delete[@]}"; do
    if [[ -f "$file" ]]; then
        echo "Deleting file: $file"
        rm -f "$file"
        echo "File '$file' has been deleted."
    else
        echo "File '$file' does not exist."
    fi
done
