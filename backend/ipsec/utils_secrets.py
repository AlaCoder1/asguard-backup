"""This file is for utils functions of the IPsec secrets file"""


from backend.ipsec.constant_variables import CONSTANT_METHOD_PSK, CONSTANT_METHOD_RSA, PATH_IPSEC_SECRETS
from backend.ipsec.models import ServerIPsec
from backend.ipsec.utils import reorganize_file
from backend.managementCertificates.constant_variables import PATH_SERVER_CERT_KEY
from backend.managementKeypairs.models import PublicKey


def create_line_secrets(secret_config:str, server:ServerIPsec):
    """Return a line secrets of a server IPsec"""
    if server.authentication_method == CONSTANT_METHOD_PSK:
        list_secret_lines = secret_config.splitlines()
        for line_secret in list_secret_lines:
            if line_secret.find(server.pre_shared_key) > 0:
                return line_secret
        return ""
    elif server.authentication_method == CONSTANT_METHOD_RSA:
        return f""" : RSA {PATH_SERVER_CERT_KEY.format(server.cert)}"""
    else:
        private_key = PublicKey.objects.get(name=server.local_key_pair).private_key
        return f""" : RSA {private_key.name}.pem """


def find_line_in_secrets_file(config:str, server:ServerIPsec):
    """Find a line secrets in ipsec.secrets file"""
    line_secrets = create_line_secrets(config, server)
    if config[config.find(line_secrets)-1] == "#":
        return f'#{line_secrets}'
    return line_secrets


def comment_line_in_secrets_file(server):
    """Comment a line in secrets file ipsec.secrets by adding a # in a line"""
    with open(PATH_IPSEC_SECRETS) as secrets_file:
        secrets_content = secrets_file.read()

    previous_line_secrets = find_line_in_secrets_file(secrets_content, server)
    new_line_secrets = "#" + previous_line_secrets

    secrets_content = secrets_content.replace(previous_line_secrets, new_line_secrets)

    with open(PATH_IPSEC_SECRETS, 'w') as secrets_file:
        secrets_file.write(secrets_content)

    return secrets_content


def uncomment_line_in_secrets_file(server):
    """Unomment a line in secrets file ipsec.secrets by removing a # in the line"""
    with open(PATH_IPSEC_SECRETS) as secrets_file:
        secrets_content = secrets_file.read()

    previous_line_secrets = find_line_in_secrets_file(secrets_content, server)
    new_line_secrets = previous_line_secrets[1:]

    secrets_content = secrets_content.replace(previous_line_secrets, new_line_secrets)

    with open(PATH_IPSEC_SECRETS, 'w') as secrets_file:
        secrets_file.write(secrets_content)

    return secrets_content


def edit_line_in_secrets_file(previous_server:ServerIPsec, new_line_secrets):
    """Edit a line in secrets file (/etc/ipsec.secrets)"""
    with open(PATH_IPSEC_SECRETS, 'r') as secrets_file:
        secrets_content = secrets_file.read()
    
    previous_line_in_secrets_file = create_line_secrets(secrets_content, previous_server)

    secrets_content = secrets_content.replace(previous_line_in_secrets_file, new_line_secrets)
    secrets_content = reorganize_file(secrets_content)

    with open(PATH_IPSEC_SECRETS, 'w') as secrets_file:
        secrets_file.write(secrets_content)

    return secrets_content
