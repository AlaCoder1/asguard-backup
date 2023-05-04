#!/bin/bash

# Installe python-pip et python-virtualenv avec pacman
yes | pacman -S python-pip python-virtualenv

# Installe django, encore, django-encore et whitenoise avec pip3
pip3 install django encore django-encore whitenoise

# Met à jour nodejs et npm avec pacman
yes | pacman -Syu nodejs npm

# Installe les versions les plus récentes de npm et n
npm i -g npm
npm i -g n

# Installe la version spécifique de Node.js (16.13.2) avec n
n 16.13.2

# Installe yarn avec npm
npm install yarn -g

# Installe yarn globalement
npm install --global yarn

# Installe les dépendances spécifiées dans le fichier requirements.txt avec pip3
pip3 install --no-cache-dir -r requirements.txt

# Installe les dépendances de yarn
yarn install

# Construit les fichiers statiques avec yarn
yarn build


