FROM nginx:latest

ARG env=prod

# Create ssl directory and set permissions
RUN mkdir -p /etc/nginx/ssl && chmod 700 /etc/nginx/ssl

COPY config.${env}.conf /etc/nginx/conf.d/default.conf