FROM node:20.4.0

WORKDIR /usr/frontend

COPY package.json ./

RUN npm install

COPY . .

RUN npm run build

CMD ["npm", "start"]