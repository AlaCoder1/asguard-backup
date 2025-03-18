###### Initialization for the generation of the ISO

pip install -r requirements.txt --break-system-packages

yarn install

yarn build

docker-compose up -d

python manage.py makemigrations

python manage.py migrate

//to collect static data of swagger UI in production

python manage.py collectstatic //with making DEBUG=False 

python manage.py create_wheel_group

python manage.py init_roles_db
python manage.py generate_user -u root -p root -r admin

python manage.py init_ASGUARD

python manage.py init_organisation -o Asguard

###### Init Firewall services

#### subscription
1/ ## init features
    python manage.py init_features_for_subscription
2/ ## init subscription
    python manage.py init_subscription
3/ ## add new features
    python manage.py add_feature_in_subscription -f `feature_name` -p `feature_price`

#### services
python manage.py init_services

#### commande to init squid 
python manage.py create_files_squid
python manage.py  init_conf_squid
python manage.py init_squid_conf_bd

iptables --flush

#### Nat
python manage.py init_rules_nat

#### IPsec start
python manage.py start_ipsec
    
#### suricata
python manage.py init_suricata_file
sudo suricata-update
sudo python manage.py init_config_suricata

#### Routing
python manage.py init_routing

#### timezone
python manage.py init_timezone_bd

#### settings
python manage.py init_generale_settings_bd

#### WAF
python manage.py init_waf_config

#### Logs
python manage.py init_logs


### Logs rotation 
python manage.py init_logrotate_script 
python manage.py init_logrotate 
python manage.py init_logrotate_timer

### init cron for logs firewall
python manage.py init_cron_log_firewall
