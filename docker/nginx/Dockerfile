FROM nginx

# HTTPS
# COPY ./nginx.conf /etc/nginx/nginx.conf

# HTTP
COPY ./http/nginx.conf /etc/nginx/nginx.conf

# Create error file at 
# etc/nginx/logs/error.log
RUN mkdir etc/nginx/logs/ && \
    touch etc/nginx/logs/error.log && \
    touch etc/nginx/logs/access.log

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
