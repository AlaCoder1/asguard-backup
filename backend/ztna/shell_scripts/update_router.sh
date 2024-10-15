#!/bin/bash

# Base directory where the folders are stored
base_directory="/asguard/newdms/backend/ztna/relays_folder"

# Read the current and new names from the command line arguments
read current_name
read new_name

# Define the full paths for the current and new folder names
current_folder="${base_directory}/${current_name}"
new_folder="${base_directory}/${new_name}"

# Check if the current folder exists
if [[ -d "$current_folder" ]]; then
    # Rename the .yaml file
    current_yaml_file="${current_folder}/${current_name}.yaml"
    new_yaml_file="${current_folder}/${new_name}.yaml"
    
    if [[ -f "$current_yaml_file" ]]; then
        echo "Renaming ${current_yaml_file} to ${new_yaml_file}"
        mv "$current_yaml_file" "$new_yaml_file"
    else
        echo "Error: YAML file ${current_yaml_file} does not exist."
    fi

    # Rename the .jwt file
    current_jwt_file="${current_folder}/${current_name}.jwt"
    new_jwt_file="${current_folder}/${new_name}.jwt"
    
    if [[ -f "$current_jwt_file" ]]; then
        echo "Renaming ${current_jwt_file} to ${new_jwt_file}"
        mv "$current_jwt_file" "$new_jwt_file"
    else
        echo "Error: JWT file ${current_jwt_file} does not exist."
    fi

    # Rename the enrollment log file
    current_log_file="${current_folder}/${current_name}_enrollment.log"
    new_log_file="${current_folder}/${new_name}_enrollment.log"
    
    if [[ -f "$current_log_file" ]]; then
        echo "Renaming ${current_log_file} to ${new_log_file}"
        mv "$current_log_file" "$new_log_file"
    else
        echo "Error: Enrollment log file ${current_log_file} does not exist."
    fi

    # Rename the folder
    echo "Renaming folder ${current_folder} to ${new_folder}"
    mv "$current_folder" "$new_folder"
    echo "Folder and all related files have been renamed."
else
    echo "Error: Folder ${current_folder} does not exist."
fi
