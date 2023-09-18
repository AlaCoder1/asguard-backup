import json
import requests
import time

url = "http://127.0.0.1:8000/network/conf/WAN1"
CSRFToken = "jsHCrsc11AUYIBr0hW7gbCEsc9Hy9DK3"
sessionid = "dxe3lck99i6nas2donr75q1duq8fz572"
payloadStaticWithGenericConf = json.dumps({
  "nameInterface": "LAN",
  "device": "eth2",
  "description": "test description ",
  "bogon_aux": True,
  "private_aux": False,
  "mtuV": 4001,
  "mssV": 1005,
  "speed_duplex": "10baseT-FD",
  "setuptypeIP4": "static",
  "value_setup_Ipv4": {
    "ip_address4": "10.1.12.7",
    "netmask4": 32,
    "gateway4": {"value":"10.1.12.1"}
  }
})
payloaStaticdWithOutGenericConf = json.dumps({
  "nameInterface": "LAN",
  "device": "eth2",
  "description": "test description ",
  "bogon_aux": True,
  "private_aux": False,
  "setuptypeIP4": "static",
  "value_setup_Ipv4": {
    "ip_address4": "10.1.12.7",
    "netmask4": 32,
    "gateway4": {"value":"10.1.12.1"}
  }
})
payloadDhcpBaseWithGenericConf = json.dumps({
  "nameInterface": "WAN",
  "device": "eth2",
  "description": "test description ",
  "bogon_aux": True,
  "private_aux": False,
  "mtuV": 1800,
  "mssV": 1005,
  "speed_duplex": "100baseTx-FD",
  "setuptypeIP4": "dhcp",
  "value_setup_Ipv4": {
    "typeDHCP4": "Base",
    "alias_add": "192.5.5.210",
    "alias_mask": 32,
    "reject": "192.33.137.209",
    "hostname": "andare.fugue.com"
  }
})
payloadDhcpBaseWithOutGenericConf = json.dumps({
  "nameInterface": "WAN",
  "device": "eth2",
  "description": "test description ",
  "bogon_aux": True,
  "private_aux": False,
  "setuptypeIP4": "dhcp",
  "value_setup_Ipv4": {
    "typeDHCP4": "Base",
    "alias_add": "192.5.5.210",
    "alias_mask": 32,
    "reject": "192.33.137.209",
    "hostname": "andare.fugue.com"
  }
})
payloadDhcpAdvancedWithGenericConf = json.dumps({
  "nameInterface": "LAN",
  "device": "eth1",
  "description": "test description ",
  "bogon_aux": True,
  "private_aux": False,
  "setuptypeIP4": "dhcp",
  "mtuV":4000,
  "mssV":1005,
  "speed_duplex":"10baseT-FD",
  "value_setup_Ipv4": {
    "typeDHCP4": "Advanced",
    "alias_add": "192.5.5.215",
    "alias_mask": 32,
    "reject": "192.33.137.209",
    "hostname": "andare.fugue.com",
    "timeout": 60,
    "retry": 60,
    "select_timeout": 5,
    "reboot": 10,
    "backoff": 10,
    "initial_interval": 2,
    "send_options_dhcp_client": "1:0:a0:24:ab:fb:9c",
    "send_options_lease_time": 3600,
    "request": "subnet-mask, broadcast-address, time-offset, routers,domain-name, domain-name-servers, host-name",
    "require": "subnet-mask , domain-name-servers",
    "supersede_domaine_name": "fugue.comrc.vix.comhome.vix.com",
    "prepend_domain_server": "127.0.0.1"
  }
})
payloadDhcpAdvancedWithOutGenericConf = json.dumps({
  "nameInterface": "LAN",
  "device": "eth1",
  "description": "test description ",
  "bogon_aux": True,
  "private_aux": False,
  "setuptypeIP4": "dhcp",
  "value_setup_Ipv4": {
    "typeDHCP4": "Advanced",
    "alias_add": "192.5.5.215",
    "alias_mask": 32,
    "reject": "192.33.137.209",
    "hostname": "andare.fugue.com",
    "timeout": 60,
    "retry": 60,
    "select_timeout": 5,
    "reboot": 10,
    "backoff": 10,
    "initial_interval": 2,
    "send_options_dhcp_client": "1:0:a0:24:ab:fb:9c",
    "send_options_lease_time": 3600,
    "request": "subnet-mask, broadcast-address, time-offset, routers,domain-name, domain-name-servers, host-name",
    "require": "subnet-mask , domain-name-servers",
    "supersede_domaine_name": "fugue.comrc.vix.comhome.vix.com",
    "prepend_domain_server": "127.0.0.1"
  }
})
headers = {
  'X-CSRFToken': CSRFToken,
  'Content-Type': 'application/json',
  'Cookie': 'csrftoken='+CSRFToken+'; sessionid='+sessionid
}


# for i in range(0,11):
#     # Record start time
#     start_time = time.time()
    
#     response = requests.request("PUT", url, headers=headers, data=payloadStaticWithGenericConf)
#     response = requests.request("PUT", url, headers=headers, data=payloaStaticdWithOutGenericConf)
#     response = requests.request("PUT", url, headers=headers, data=payloadDhcpBaseWithGenericConf)
#     response = requests.request("PUT", url, headers=headers, data=payloadDhcpBaseWithOutGenericConf)
#     response = requests.request("PUT", url, headers=headers, data=payloadDhcpAdvancedWithGenericConf)
#     response = requests.request("PUT", url, headers=headers, data=payloadDhcpAdvancedWithOutGenericConf)

#     # Record end time
#     end_time = time.time()

#     # Calculate and print the elapsed time
#     elapsed_time = end_time - start_time
#     print("Elapsed Time:", elapsed_time, "seconds")
tasks = [
    ("payloadStaticWithGenericConf", payloadStaticWithGenericConf),
    ("payloadStaticdWithOutGenericConf", payloaStaticdWithOutGenericConf),
    ("payloadDhcpBaseWithGenericConf", payloadDhcpBaseWithGenericConf),
    ("payloadDhcpBaseWithOutGenericConf", payloadDhcpBaseWithOutGenericConf),
    ("payloadDhcpAdvancedWithGenericConf", payloadDhcpAdvancedWithGenericConf),
    ("payloadDhcpAdvancedWithOutGenericConf", payloadDhcpAdvancedWithOutGenericConf)
]
for i in range(0, 11):
  for task_name, payload in tasks:
  
        start_time = time.time()
        
        response = requests.request("PUT", url, headers=headers, data=payload)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed Time: {task_name}", elapsed_time, "seconds")
        if response.status_code !=200: 
          print("error in API!")
        else:
          print("successfully executed API!")
        print("\\\\\\\\\\\\\\\\\\\\\\\\",task_name)
  print("\\\\\\\\\\\\\\\\\\\\\\\\",i)