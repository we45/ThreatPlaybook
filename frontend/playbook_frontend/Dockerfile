FROM node:10
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ADD package.json /usr/src/app/package.json
RUN npm install && npm install -g serve
ADD . /usr/src/app
RUN npm run build
ENV PORT=8080
CMD echo "{\"API_URL\": \"$API_URL\"}" > configure.json && serve -s dist
