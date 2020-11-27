#!/bin/bash

sudo apt-get update
sudo apt-get upgrade

# Installs docker
sudo apt-get install docker.io
# Installs docker compose
curl -L https://github.com/docker/compose/releases/download/1.25.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Updates docker engine
# apt-get upgrade docker-engine

# Prints Docker version
# echo docker version | grep "Version"

read -p "Install nginx-proxy [yes|no]? " install_nginx_proxy

if [ $install_nginx_proxy = "yes" ]; then
    # Create a network for nginx-proxy
    docker network create nginx-proxy
    # Install nginx-proxy: this is a container that allows to process
    # multiple incoming requests and redirect them to the correct container.
    # Useful in cases where we want to host multiple websites using the same
    # VPS and IP adress
    docker run -d -p 80:80 --name nginx-proxy --net nginx-proxy -v /var/run/docker.sock:/tmp/docker.sock jwilder/nginx-proxy
fi

# Pulls the cadvisor container for monitoring purposes
read -p "Install Cadvisor [yes|no]?" install_cadvisor

if [ $cadvisor = "yes" ]; then
    docker pull cadvisor
fi

# Pulls the PGAdmin container
read -p "Install PG Admin [yes|no]?" pg_admin

if [ $pg_admin = "yes" ]; then
    docker pull dpage/pgadmin4
fi

# General update
sudo apt-get update
sudo apt-get upgrade

# Tools for creating credential files
# for Nginx
sudo apt-get install apache2-utils
mkdir -p etc/apache2 && touch etc/apache2/.htpasswd
echo sudo htpasswd -c /etc/apache2/.htpasswd admin1
echo "Do not forget to change the default password for admin1 in the credentials file for restrictions"

# Others

snap install tree

ufw enable
ufw allow 443
ufw allow 80
ufw allow ssh

bash ~/../home/init-ssh.sh

if ![ $1 eq "" ]; then
    cd ~/../home && git clone $1
fi
