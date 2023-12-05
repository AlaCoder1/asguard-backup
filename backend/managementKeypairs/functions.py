import re
import subprocess
from backend.openvpn.functions import execute_command_without_arguments


# def get_finger_print(public_key_name, public_key_length):
#     """Returns the finger print of a public key"""
#     # Writing the RSA key
#     process = execute_command_without_arguments(['sudo', 'ssh-keygen', '-f', f'/etc/ipsec.d/certs/{public_key_name}.key', '-i', '-m', 'PKCS8'])
#     rsa_key = process.stdout
#     with open(f'/etc/ipsec.d/finger_prints/{public_key_name}.pub', 'w') as rsa_file:
#         rsa_file.write(rsa_key)
    
#     # Read the finger print of a public key
#     process = execute_command_without_arguments(['sudo', 'ssh-keygen', '-l', '-f', f'/etc/ipsec.d/finger_prints/{public_key_name}.pub'])
#     finger_print = process.stdout
#     finger_print = finger_print.replace(f'{public_key_length} SHA256:', '')
#     finger_print = finger_print.replace(' no comment (RSA)', '')
#     return finger_print


def get_finger_print(private_key_name):
    """Returns the finger print of a public key"""
    # Command 1: Save the public key in DER format to a temporary file
    process = execute_command_without_arguments(["openssl", "rsa", "-in", f"/etc/ipsec.d/private/{private_key_name}.key", "-pubout", "-outform", "DER"])
    with open(f"/etc/ipsec.d/finger_prints/{private_key_name}.der", "w") as der_file:
        der_file.write(process.stdout)

    # Command 2: Calculate the SHA-1 hash using the temporary file
    command2 = ["openssl", "sha1", "-c"]
    with open(f"/etc/ipsec.d/finger_prints/{private_key_name}.der", "rb") as temp_file:
        result = subprocess.run(command2, stdin=temp_file, stdout=subprocess.PIPE, text=True, check=True)
        return result.stdout


def get_key_size(public_key_name):
    """Returns the key size of a public key"""
    process = execute_command_without_arguments(["sudo", "openssl", "rsa", "-in", f'/etc/ipsec.d/certs/{public_key_name}.pem', "-pubin", "-text", "-noout"])
    public_key = process.stdout
    key_size_line = public_key[public_key.find("Public-Key: "):public_key.find("\n", public_key.find("Public-Key: "))]
    key_size = re.findall(r'\d+', key_size_line)
    return key_size[0]
