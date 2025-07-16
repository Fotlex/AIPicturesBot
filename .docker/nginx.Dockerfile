FROM nginx:1.27.5-alpine

ARG NGINX_CONF_PATH

COPY ${NGINX_CONF_PATH} /etc/nginx/templates/default.conf.template

RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log
