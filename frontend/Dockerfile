FROM node:10-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY threatplaybook/package.json /usr/src/app/package.json
RUN npm install && npm install -g serve dotenv
COPY threatplaybook/ /usr/src/app/
#CMD serve -s dist
ADD docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD npm run serve
