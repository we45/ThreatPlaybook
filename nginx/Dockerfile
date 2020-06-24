FROM ubuntu:16.04

RUN apt-get update && apt-get install -y nginx && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN rm /etc/nginx/sites-enabled/default

ADD sites-enabled/ /etc/nginx/sites-enabled/

EXPOSE 5000
EXPOSE 80

CMD ["/usr/sbin/nginx"]
