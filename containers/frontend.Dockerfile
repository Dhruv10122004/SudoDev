FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

# Run dev server with turbo 
CMD ["npm", "run", "dev", "--", "--turbo", "--hostname", "0.0.0.0"]
