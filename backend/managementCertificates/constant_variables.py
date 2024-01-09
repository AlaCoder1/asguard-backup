"""This file is for constants that are used many times in managementCertificates app"""

PATH_VARS_INITIALIZE = '/etc/easy-rsa/vars'

# Paths PKI
PATH_PKI = '{}/pki/'
PATH_PKI_VARS = PATH_PKI + 'vars'
PATH_PKI_CA = PATH_PKI + 'ca.crt'
PATH_PKI_CA_KEY = PATH_PKI + 'private/ca.key'
PATH_PKI_CA_CRL = PATH_PKI + 'crl.pem'
PATH_PKI_CERT = PATH_PKI + 'issued/{}.crt'
PATH_PKI_CERT_KEY = PATH_PKI + 'private/{}.key'
PATH_PKI_CERT_REQ = PATH_PKI + 'reqs/{}.req'
PATH_PKI_CERT_INLINE = PATH_PKI + 'inline/{}.inline'
PATH_PKI_CERT_REVOKED = PATH_PKI + 'revoked/certs_by_serial/{}.crt'

PATH_CERT = '/etc/ssl/certs/'
PATH_KEY = '/etc/ssl/private/'
PATH_VARS = PATH_CERT + 'vars_{}'

# Paths for Certificate authority
PATH_CA_CRT = PATH_CERT + 'ca_{}.crt'
PATH_CA_KEY = PATH_KEY + 'ca_{}.key'
PATH_CA_CRL_PEM = PATH_CERT + 'crl_{}.pem'
PATH_CA_CRL = PATH_CERT + 'crl_{}.crl'

# Paths for Certificates

## Server certificates
PATH_SERVER_CERT_CRT = PATH_CERT + 'server_{}.crt'
PATH_SERVER_CERT_KEY = PATH_KEY + 'server_{}.key'

## Client certificates
PATH_CLIENT_CERT_CRT = PATH_CERT + 'client_{}.crt'
PATH_CLIENT_CERT_KEY = PATH_KEY + 'client_{}.key'

## Revoked certififcates
PATH_REVOKED = PATH_CERT + 'revoked/'
PATH_REVOKED_CERT = PATH_REVOKED + '{}.crt'

# Constants
CONSTANT_EASYRSA_VARIABLE = 'set_var EASYRSA_'
