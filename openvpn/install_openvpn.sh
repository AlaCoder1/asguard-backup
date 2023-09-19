if [[ ! -e /etc/openvpn/server.conf ]]; then
    # Install required dependencies and upgrade the system
	pacman --needed --noconfirm -Syu openvpn iptables openssl wget ca-certificates curl
fi

# An old version of easy-rsa was available by default in some openvpn packages
if [[ -d /etc/openvpn/easy-rsa/ ]]; then
    rm -rf /etc/openvpn/easy-rsa/
fi

# Find out if the machine uses nogroup or nobody for the permissionless group
if grep -qs "^nogroup:" /etc/group; then
    NOGROUP=nogroup
else
    NOGROUP=nobody
fi

if [[ ! -d /etc/openvpn/easy-rsa/ ]]; then
    local version="3.1.2"
    wget -O ~/easy-rsa.tgz https://github.com/OpenVPN/easy-rsa/releases/download/v${version}/EasyRSA-${version}.tgz
    mkdir -p /etc/openvpn/easy-rsa
    tar xzf ~/easy-rsa.tgz --strip-components=1 --no-same-owner --directory /etc/openvpn/easy-rsa
    rm -f ~/easy-rsa.tgz

    cd /etc/openvpn/easy-rsa/ || return
    case $CERT_TYPE in
    1)
        echo "set_var EASYRSA_ALGO ec" >vars
        echo "set_var EASYRSA_CURVE $CERT_CURVE" >>vars
        ;;
    2)
        echo "set_var EASYRSA_KEY_SIZE $RSA_KEY_SIZE" >vars
        ;;
    esac

    # Generate a random, alphanumeric identifier of 16 characters for CN and one for server name
    SERVER_CN="cn_$(head /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1)"
    echo "$SERVER_CN" >SERVER_CN_GENERATED
    SERVER_NAME="server_$(head /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1)"
    echo "$SERVER_NAME" >SERVER_NAME_GENERATED

    # Create the PKI, set up the CA, the DH params and the server certificate
    ./easyrsa init-pki
    ./easyrsa --batch --req-cn="$SERVER_CN" build-ca nopass

    ################ A verifier #####################
    if [[ $DH_TYPE == "2" ]]; then
        # ECDH keys are generated on-the-fly so we don't need to generate them beforehand
        openssl dhparam -out dh.pem $DH_KEY_SIZE
    fi

    ./easyrsa --batch build-server-full "$SERVER_NAME" nopass
    EASYRSA_CRL_DAYS=3650 ./easyrsa gen-crl

    case $TLS_SIG in
    1)
        # Generate tls-crypt key
        openvpn --genkey --secret /etc/openvpn/tls-crypt.key
        ;;
    2)
        # Generate tls-auth key
        openvpn --genkey --secret /etc/openvpn/tls-auth.key
        ;;
    esac
else
    # If easy-rsa is already installed, grab the generated SERVER_NAME
    # for client configs
    cd /etc/openvpn/easy-rsa/ || return
    SERVER_NAME=$(cat SERVER_NAME_GENERATED)
fi

# Move all the generated files
cp pki/ca.crt pki/private/ca.key "pki/issued/$SERVER_NAME.crt" "pki/private/$SERVER_NAME.key" /etc/openvpn/easy-rsa/pki/crl.pem /etc/openvpn
################ A verifier #####################
if [[ $DH_TYPE == "2" ]]; then
    cp dh.pem /etc/openvpn
fi

# Make cert revocation list readable for non-root
chmod 644 /etc/openvpn/crl.pem

# Generate server.conf
echo "port 1194
proto udp
dev tun
user nobody
group nogroup
persist-key
persist-tun
keepalive 10 120
topology subnet
server 10.8.0.0 255.255.255.0
ifconfig-pool-persist ipp.txt
push "dhcp-option DNS 8.8.8.8"
push "dhcp-option DNS 8.8.4.4"
push "redirect-gateway def1 bypass-dhcp"
dh none
ecdh-curve prime256v1
tls-crypt tls-crypt.key
crl-verify crl.pem
ca ca.crt
cert server_TzOIvgMDkySTSkvC.crt
key server_TzOIvgMDkySTSkvC.key
auth SHA256
cipher AES-128-GCM
ncp-ciphers AES-128-GCM
tls-server
tls-version-min 1.2 " >>/etc/openvpn/server.conf

# Create client-config-dir dir
mkdir -p /etc/openvpn/ccd
# Create log dir
mkdir -p /var/log/openvpn

# Enable routing
echo 'net.ipv4.ip_forward=1' >/etc/sysctl.d/99-openvpn.conf

# Apply sysctl rules
sysctl --system

# If SELinux is enabled and a custom port was selected, we need this
if hash sestatus 2>/dev/null; then
    if sestatus | grep "Current mode" | grep -qs "enforcing"; then
        if [[ $PORT != '1194' ]]; then
            semanage port -a -t openvpn_port_t -p "$PROTOCOL" "$PORT"
        fi
    fi
fi

# Finally, restart and enable OpenVPN
# Don't modify package-provided service
cp /usr/lib/systemd/system/openvpn-server@.service /etc/systemd/system/openvpn-server@.service

# Workaround to fix OpenVPN service on OpenVZ
sed -i 's|LimitNPROC|#LimitNPROC|' /etc/systemd/system/openvpn-server@.service
# Another workaround to keep using /etc/openvpn/
sed -i 's|/etc/openvpn/server|/etc/openvpn|' /etc/systemd/system/openvpn-server@.service

systemctl daemon-reload
systemctl enable openvpn-server@server
systemctl restart openvpn-server@server

# if [[ $DNS == 2 ]]; then
#     installUnbound
# fi

# Add iptables rules in two scripts
mkdir -p /etc/iptables

# Script to add rules
echo "#!/bin/sh
iptables -t nat -I POSTROUTING 1 -s 10.8.0.0/24 -o $NIC -j MASQUERADE
iptables -I INPUT 1 -i tun0 -j ACCEPT
iptables -I FORWARD 1 -i $NIC -o tun0 -j ACCEPT
iptables -I FORWARD 1 -i tun0 -o $NIC -j ACCEPT
iptables -I INPUT 1 -i $NIC -p $PROTOCOL --dport $PORT -j ACCEPT" >/etc/iptables/add-openvpn-rules.sh

	# Script to remove rules
	echo "#!/bin/sh
iptables -t nat -D POSTROUTING -s 10.8.0.0/24 -o $NIC -j MASQUERADE
iptables -D INPUT -i tun0 -j ACCEPT
iptables -D FORWARD -i $NIC -o tun0 -j ACCEPT
iptables -D FORWARD -i tun0 -o $NIC -j ACCEPT
iptables -D INPUT -i $NIC -p $PROTOCOL --dport $PORT -j ACCEPT" >/etc/iptables/rm-openvpn-rules.sh

chmod +x /etc/iptables/add-openvpn-rules.sh
chmod +x /etc/iptables/rm-openvpn-rules.sh
