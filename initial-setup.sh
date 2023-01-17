#!/bin/sh

cd ~

sudo yum -y update

sudo yum install -y epel-release

sudo yum install -y python3 gcc nginx git nano java-1.8.0-openjdk-devel wget

sudo systemctl daemon-reload

sudo systemctl start nginx

sudo systemctl enable nginx

