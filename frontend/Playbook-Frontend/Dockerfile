FROM node:12

COPY dist ./dist
RUN npm install -g serve 
ENV PORT=3000
CMD serve -s dist -p 3000