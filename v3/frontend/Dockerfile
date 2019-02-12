FROM node:10-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY threatplaybook/package.json /usr/src/app/package.json
RUN npm install && npm install -g serve
COPY threatplaybook/ /usr/src/app/
RUN npm run build
#CMD serve -s dist
CMD echo "{\"API_URL\": \"$API_URL\"}" > configure.json && serve -s dist