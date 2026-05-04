FROM node:18

WORKDIR /app

# Copy only package files first (better caching)
COPY package.json package-lock.json ./

RUN npm install

# Now copy rest of code
COPY . .

EXPOSE 3000

CMD ["npm", "start"]