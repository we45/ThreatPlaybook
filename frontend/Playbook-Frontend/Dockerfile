FROM node:12

COPY dist ./dist

RUN npm install -g serve
ENV PORT=80
CMD serve -s dist -p 80
