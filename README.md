###### Initialization for the generation of the ISO

pip install -r requirements.txt --break-system-packages

yarn install

yarn build

docker-compose up -d

python manage.py makemigrations

python manage.py migrate

python manage.py create_wheel_group

python manage.py generate_user -u root -p root

python manage.py init_ASGUARD

###### Init Firewall services

python manage.py init_services

//to collect static data of swagger UI in production

python manage.py collectstatic //with making DEBUG=False 

#### subscription
1/ ## init features
    python manage.py init_features_for_subscription
2/ ## init subscription
    python manage.py init_subscription
3/ ## add new features
    python manage.py add_feature_in_subscription -f `feature_name` -p `feature_price`
    
#### suricata

//commande to correct config file to generate rules 

sudo python manage.py init_suricata_file

//commande to generate file suricata.rules

sudo suricata-update

//commande to init Suricata config  (all config general config , default rules and alerts)

sudo python manage.py init_config_suricata 

#### suricata

// commande to init squid 

python manage.py create_files_squid
python manage.py  init_conf_squid
python manage.py init_squid_conf_bd

#### Nat
python manage.py init_rules_nat

#### IPsec start
python manage.py start_ipsec

#### Routing
python manage.py init_routing

#### WAF
python manage.py init_waf_config

#### Logs
python manage.py init_logs


### Logs rotation 
## example
python manage.py init_logrotate_script 
python manage.py init_logrotate 
python manage.py init_logrotate_timer