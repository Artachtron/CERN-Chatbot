FROM node:20.4

WORKDIR /usr/src/frontend

COPY package.json ./

RUN npm install

COPY . .

CMD ["npm", "start"]