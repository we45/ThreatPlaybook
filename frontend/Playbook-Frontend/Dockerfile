FROM node:12

COPY dist/ ./
RUN npm install -g serve 
# RUN yarn install
# RUN yarn build
WORKDIR /dist/
ENV PORT=3000
CMD serve -s dist
# CMD ["yarn", "dev"]
