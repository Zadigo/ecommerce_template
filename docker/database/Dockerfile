FROM postgres:latest

# Pg_cron extension
# RUN apt-get update
# RUN sudo apt-get -y install postgresql-10-cron

# ADD ./init/01-init.sh /docker-entrypoint-initdb.d/
# RUN chmod 0755 /docker-entrypoint-initdb.d/01-init.sh

RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/pg_hba.conf
RUN echo "listen_addresses='*'" >> /etc/postgresql/postgresql.conf

EXPOSE 5432
