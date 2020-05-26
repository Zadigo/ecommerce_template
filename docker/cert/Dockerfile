FROM certbot/certbot

LABEL "com.cerbot.letsencrypt"="certbot"

# docker-compose run certbot certonly --manual --force-renew -d nawoka.fr --preferred-challenges dns-01 --server https://acme-v02.api.letsencrypt.org/directory
CMD [ "certonly", "--manual", "-d nawoka.fr", "-d *.nawoka.fr", "--preferred-challenges", "dns-01", "--server", "https://acme-v02.api.letsencrypt.org/directory" ]

ENTRYPOINT [ "certbot" ]
