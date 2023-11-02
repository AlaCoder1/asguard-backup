from .functions import *
###################generic configuration

def generic_config(config,ifname,speed_duplex,addmac,mtuv,mssv,genericConfigObject):
    commandes=[]
    cmd_final=[]
    #traiter le speed_duplex
    match speed_duplex:
        case '100baseTx-FD':
            speedV=100
            duplexV='full'
        case '100baseTx-HD':
            speedV=100
            duplexV='half'
        case '10baseT-FD':
            speedV=10
            duplexV='full'
        case '10baseT-HD':
            speedV=10
            duplexV='half'
   #tester si addmac is not None
    if addmac is not None and (genericConfigObject is not None and genericConfigObject.addmac!=addmac or genericConfigObject is None):
            #lancer la fonction de "remove old config"
            config=clean_old_config(config,"addmac config {}".format(ifname))
             #la liste des commandes pour l'address mac
            commandes+=[
            "#Start addmac config {}".format(ifname),
            'ExecStart=/usr/bin/ip link set dev {} address {}'.format(ifname,addmac),
            "#End addmac config {}".format(ifname)
            ]
            cmd_final+=[
                'sudo ip link set dev {} address {}'.format(ifname,addmac),
            ]
    #tester si mtu is not None
    if mtuv is not None and (genericConfigObject is not None  and mtuv!=genericConfigObject.mtuv!=mtuv or genericConfigObject is None ):
        #lancer la fonction de "remove old config"
        config=clean_old_config(config,"mtu config {}".format(ifname))
        #la liste des commandes pour mtu
        commandes+=[
        "#Start mtu config {}".format(ifname),
        'ExecStart=/usr/bin/ip link set dev {} mtu {}'.format(ifname,mtuv),
        "#End mtu config {}".format(ifname)
            ]
        cmd_final+=[
        'sudo ip link set dev {} mtu {}'.format(ifname,mtuv),
         ]
    #tester si mtu is not None
    if mssv is not None and (genericConfigObject is not None  and mssv!=genericConfigObject.mssv or genericConfigObject is None ):
        #lancer la fonction de "remove old config"
        config=clean_old_config(config,"mss config {}".format(ifname))
         #la liste des commandes pour mss
        commandes+=[
        "#Start mss config {}".format(ifname),
        'ExecStart=/usr/bin/iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -o {} -j TCPMSS --set-mss {}'.format(ifname,mssv),
        "#End mss config {}".format(ifname),
            ]
        cmd_final+=[
        'sudo iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -o {} -j TCPMSS --set-mss {}'.format(ifname,mssv),
         ]
    #tester si speed_duplex is not None
    if speed_duplex is not None and (genericConfigObject is not None  and  speed_duplex!=genericConfigObject.speed_duplex or genericConfigObject is None ):
        #lancer la fonction de "remove old config"
        config=clean_old_config(config,"speed duplex config {}".format(ifname))
        #la liste des commandes pour speed duplex
        commandes+=[
        "#Start speed duplex config {}".format(ifname),
        'ExecStart=/usr/bin/ethtool -s {} speed {} duplex {}'.format(ifname,speedV,duplexV),
        "#End speed duplex config {}".format(ifname),
                    ]
        cmd_final+=[
        'sudo ethtool -s {} speed {} duplex {}'.format(ifname,speedV,duplexV),
         ]
    return commandes,config,cmd_final
