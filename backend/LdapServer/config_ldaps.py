import subprocess

def execute_cmd(command):
    """Function to execute system commands"""
    command = "sudo " + command
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error

def update_ldap_conf(ldap_conf_path, ssl_tls_activation):
    """Update the LDAP configuration file based on SSL/TLS activation"""

    try:
        # Read the current content of the ldap.conf file
        output, error = execute_cmd(f"cat {ldap_conf_path}")
        
        if output:
            config_content = output.strip().split('\n')

            # Modify the content based on SSL/TLS activation
            tls_reqcert_exists = any(line.strip().startswith('TLS_REQCERT allow') for line in config_content)
            
            if ssl_tls_activation and not tls_reqcert_exists:
                config_content.append("TLS_REQCERT allow")
            elif not ssl_tls_activation and tls_reqcert_exists:
                config_content = [line.replace('TLS_REQCERT allow', '#TLS_REQCERT allow') for line in config_content]

            # Write the modified content back to the ldap.conf file
            modified_content_str = "\n".join(config_content)
            execute_cmd(f"echo '{modified_content_str}' | sudo tee {ldap_conf_path} > /dev/null")

            return True
        else:
            print(f"Error reading LDAP configuration file: {error}")
            return False

    except Exception as e:
        print(f"Error updating LDAP configuration: {e}")
        return False