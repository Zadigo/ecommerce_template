#!/bin/bash/

# A script that initializes an SSH
# key on the server and facilitates
# for example pull and push without
# password

EMAIL="pendenquejohn@gmail.com"

ssh-keygen -t rsa -b 4096 -C $EMAIL

eval $(ssh-agent -s)

ssh-add ~/.ssh/id_rsa
