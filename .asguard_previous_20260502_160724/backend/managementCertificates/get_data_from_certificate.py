from datetime import datetime
from utils.commands_utils import execute_command_without_arguments


def read_certificate_value(certificate_path, decode=True):
    """This function take a certificate path and return the certificate value from system file"""
    command = ['sudo', 'cat', f'{certificate_path}']
    process = execute_command_without_arguments(command, decode)
    return process.stdout


def get_certificates_details(cert_path):
    """Get all the details of a certificates from its value in text form"""
    command = ['sudo', 'openssl', 'x509', '-in', f'{cert_path}', '-text']
    process = execute_command_without_arguments(command)
    cert_details = process.stdout
    return cert_details


def get_certifcate_serial_number(cert_path):
    """Get the serial number of certificate"""
    command = ['sudo', 'openssl', 'x509', '-in', f'{cert_path}', '-noout', '-serial']
    process = execute_command_without_arguments(command)
    serial = process.stdout
    serial = serial.replace('serial=', '')
    return serial


def get_certifcate_dates(cert_path):
    """Get the serial number of certificate"""
    command_start_date = ['openssl', 'x509', '-in', f'{cert_path}', '-noout', '-startdate']
    process_start_date = execute_command_without_arguments(command_start_date)
    start_date = process_start_date.stdout
    start_date = start_date.replace('notBefore=', '')
    start_date = start_date.replace('\n', '')
    start_date = datetime.strptime(start_date, '%b %d %H:%M:%S %Y %Z')

    command_end_date = ['openssl', 'x509', '-in', f'{cert_path}', '-noout', '-enddate']
    process_end_date = execute_command_without_arguments(command_end_date)
    end_date = process_end_date.stdout
    end_date = end_date.replace('notAfter=', '')
    end_date = end_date.replace('\n', '')
    end_date = datetime.strptime(end_date, '%b %d %H:%M:%S %Y %Z')

    lifetime = end_date - start_date
    lifetime = lifetime.days

    return start_date, end_date, lifetime


def extract_certificate_distingushed_name(cert_path):
    "Extract the distingushed name DN of a certificate like the common name and country code"
    process = execute_command_without_arguments(['sudo', 'openssl', 'x509', '-in', cert_path, '-noout',
                                                 '-subject', '-nameopt', 'sep_multiline'])
    dn = process.stdout
    dn_symbol = {"country_code": "C",
                 "state": "ST",
                 "city": "L",
                 "organization": "O",
                 "common_name": "CN",
                 "email": "E",
                 "email": "emailAddress",
                 "organization_unit":"OU"}
    dn_dict = {}
    for field, symbol in dn_symbol.items():
        if dn.find(f'{symbol}=') >-1:
            dn_line = dn[dn.find(f'{symbol}='):dn.find('\n', dn.find(f'{symbol}='))]
            dn_dict[field] = dn_line.replace(f'{symbol}=', '')

    return dn_dict


def extract_type_certificate(cert_path):
    cert_value = read_certificate_value(cert_path)
    if cert_value.find("TLS Web Server Authentication") > -1:
        return 'server'
    return 'client'