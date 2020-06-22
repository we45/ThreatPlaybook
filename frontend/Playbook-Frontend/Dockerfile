FROM node:12

COPY . ./

RUN yarn install
RUN yarn build

CMD ["yarn", "dev"]
