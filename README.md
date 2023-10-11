1- Connecter a l'aide du VS au machine virtuelle (SSH)

2- Lancer les containers

// avec détails d'exécution

docker-compose up

// sans détails

docker-compose up -d

3- Ouvrir deux autre terminal en //

dans le 1 er terminal lancer

python manage.py make migrations

python manage.py migrate

python manage.py generate_root -u root -p root

python manage.py initBD_subscription

python manage.py init_openVPN -u root -p root


python manage.py init_ASGUARD -u root -p root

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



