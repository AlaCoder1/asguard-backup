1- Connecter a l'aide du VS au machine virtuelle (SSH)

2- Lancer les containers

// avec détails d'exécution

docker-compose up

// sans détails

docker-compose up -d

3- Ouvrir deux autre terminal en //

dans le 1 er terminal lancer

python manage.py makemigrations

python manage.py migrate

python manage.py generate_root -u root -p root

python manage.py initBD_subscription

python manage.py init_openVPN -u root -p root


python manage.py init_ASGUARD 


python manage.py create_wheel_group

python manage.py conf_nftable_dhclient -u root -p root

// a ne pas exécuter python manage.py confInterfaces -u root -p root 

python manage.py init_bd_interfaces -u root -p root

python manage.py init_network

//need to pull and migrate 

pip install -r requirements.txt --break-system-packages

dans l'autre terminal pour la build des assets lors la modification de n'importe quel fichier JS

yarn install

yarn build / yarn watch

//initialiser les services 

python manage.py init_services

//to collect static data of swagger UI in production

python manage.py collectstatic //avec debug=False 

#### suricata

//commande to correct config file to generate rules 

sudo python manage.py init_suricata_file

//commande to generate file suricata.rules

sudo suricata-update

//commande to init Suricata config  (all config general config , default rules and alerts)

sudo python manage.py init_config_suricata 

#### suricata

// commande to init default values clamav

python manage.py init_clamav

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
