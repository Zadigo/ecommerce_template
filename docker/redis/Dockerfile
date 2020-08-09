FROM redis

COPY redis.conf /usr/local/etc/redis/redis.conf

# ENTRYPOINT [ "redis-server", "/usr/local/etc/redis/redis.conf" ]

ENTRYPOINT [ "redis-server", "--bind", "redis", "--port", "6379" ]
