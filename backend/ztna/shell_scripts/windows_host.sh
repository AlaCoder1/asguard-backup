#!/bin/bash

# Read IP address from user input
read -p "Enter IP address: " ipadd

# Write IP address to a temporary file
temp_file=$(mktemp)
echo "$ipadd" > "$temp_file"
file_directory="/asguard/asguard/backend/ztna/shell_scripts/"
current_hostname=$(hostname)

# Create the final batch script
cat << EOF > $file_directory/append_to_hosts.bat
@echo off

:: Append to hosts file
echo $(cat "$temp_file") $current_hostname >> "%windir%\system32\drivers\etc\hosts"

:: Check if successful
if %errorlevel% equ 0 (
    echo Successfully appended entry to hosts file
) else (
    echo Failed to append entry to hosts file
)
EOF

echo "Batch script created: append_to_hosts.bat"
