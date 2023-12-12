"""This file is for constants that are used many times in managementCertificates app"""

PATH_VARS_INITIALIZE = '/etc/easy-rsa/vars'

# Paths for Certificate authority
PATH_CA = '/etc/certificates_{}/'
PATH_CA_VARS = '/etc/certificates_{}/vars'
PATH_CA_CRT = '/etc/certificates_{}/ca.crt'
PATH_CA_KEY = '/etc/certificates_{}/ca.key'
PATH_CA_CRL_PEM = '/etc/certificates_{}/crl.pem'
PATH_CA_CRL = '/etc/certificates_{}/crl.crl'

# Paths for Certificates

## Server certificates
PATH_SERVER_CERT = '/etc/openvpn/certificates_{}/'
PATH_SERVER_CERT_VARS = '/etc/openvpn/certificates_{}/vars'
PATH_SERVER_CERT_CRT = '/etc/openvpn/certificates_{}/server.crt'
PATH_SERVER_CERT_KEY = '/etc/openvpn/certificates_{}/server.key'

## Client certificates
PATH_CLIENT_CERT = '/etc/openvpn/client/certificates_{}/'
PATH_CLIENT_CERT_VARS = '/etc/openvpn/client/certificates_{}/vars'
PATH_CLIENT_CERT_CRT = '/etc/openvpn/client/certificates_{}/{}.crt'
PATH_CLIENT_CERT_KEY = '/etc/openvpn/client/certificates_{}/{}.key'
