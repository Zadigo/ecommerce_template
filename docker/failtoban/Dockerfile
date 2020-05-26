FROM superitman/fail2ban

LABEL "com.failtoban.vendor"="fail2ban"

COPY jail.local .

COPY ./jails/nginx-x00.conf /etc/fail2ban/filter.d/nginx-x00.conf
COPY ./jails/dana-exploit.conf /etc/fail2ban/filter.d/dana-exploit.conf
COPY ./jails/php-scripts.conf /etc/fail2ban/filter.d/php-scripts.conf
COPY ./jails/suspect-ips.conf /etc/fail2ban/filter.d/suspect-ips.conf

RUN touch /etc/fail2ban/auth.log
