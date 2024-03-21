CONSTANT_SNAT_RULE = 'SNAT rule'
CONSTANT_ONE_TO_ONE_NAT_RULE = 'OneToOneNat rule'
CONSTANT_DNAT_RULE = 'DNAT rule'

INIT_NAT_FILE_CONTENT = """table ip nat {
        chain postrouting {
                type nat hook postrouting priority srcnat; policy accept;
        }
 
        chain prerouting {
                type nat hook prerouting priority 100; policy accept;
        }
}"""

PATH_NFTABLES_CONF = '/etc/nftables.conf'
PATH_RULESET_NAT_DIRECTORY = '/etc/rules/nat/'
PATH_RULESET_NFT = PATH_RULESET_NAT_DIRECTORY + 'nat.nft'
