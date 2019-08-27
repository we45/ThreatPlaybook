FROM nginx:latest
COPY ./nginx.conf /etc/nginx/conf.d/app.conf
CMD ["nginx", "-g", "daemon off;"]
