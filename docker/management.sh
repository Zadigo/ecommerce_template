#!/bin/bash

set -e

URL=https://mywebsite.fr/

function manager () {
    git pull
    docker-compose build $1
    docker-compose restart $1
    docker exec -it $1 python manage.py ping_google $URL/sitemap.xml
    docker ps
}

manager $1;
