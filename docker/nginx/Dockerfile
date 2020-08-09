FROM nginx

COPY ./nginx.conf /etc/nginx/nginx.conf

# Create error file at 
# etc/nginx/logs/error.log
RUN mkdir etc/nginx/logs/ && \
        touch etc/nginx/logs/error.log && \
        touch etc/nginx/logs/access.log

# Includes additional certificates
# such as Apple pay etc.
# RUN mkdir var/www/certificates

# COPY ./certificates/ var/www/certificates/

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
