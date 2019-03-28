FROM dbogatov/docker-images:nginx-latest

LABEL maintainer="Dmytro Bogatov <dmytro@dbogatov.org>"

WORKDIR /srv

# Copy the source
COPY website .

# Copy the NGINX config
COPY nginx.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
