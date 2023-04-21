FROM node:lts-alpine

WORKDIR /app

COPY package.json ./
RUN npm instal
ENV PATH /app/node_modules/.bin:$PATH

WORKDIR /app/frontend
COPY . .

#ENTRYPOINT ["tail", "-f", "/dev/null"]
ENTRYPOINT ["npm" , "run", "serve"]
