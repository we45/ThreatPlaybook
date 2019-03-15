FROM node:10-alpine

RUN npm install -g http-server
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY threatplaybook/package.json /usr/src/app/package.json
RUN npm install
COPY threatplaybook/ /usr/src/app/
RUN npm run build
#CMD serve -s dist
RUN echo "{\"API_URL\": \"$API_URL\"}" > configure.json
EXPOSE 8080
CMD [ "http-server", "dist" ]