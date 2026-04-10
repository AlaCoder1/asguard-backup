#!/bin/bash

# Read IP address from user input
read -p "Enter IP address: " ipadd

file_directory="/asguard/asguard/backend/ztna/shell_scripts/"

# Write IP address to a temporary file
temp_file=$(mktemp)
echo "$ipadd" > "$temp_file"

current_hostname=$(hostname)
# Create the final script
cat << EOF > $file_directory/append_to_hosts.sh
#!/bin/bash

if ! printf "%s %s\n" "$(cat "$temp_file")" "$current_hostname" | sudo tee -a /etc/hosts > /dev/null; then
    echo "Failed to append entry to /etc/hosts"
    exit 1
fi
    
echo "Successfully appended entry to /etc/hosts"
    
EOF

echo "Script created: append_to_hosts.sh"
