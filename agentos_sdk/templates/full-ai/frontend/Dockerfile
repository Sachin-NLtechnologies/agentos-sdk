FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3001
CMD ["sh","-c","if [ ! -f /certs/key.pem ] || [ ! -f /certs/cert.pem ]; then echo 'ERROR: mkcert cert missing. Expected /certs/key.pem and /certs/cert.pem. Generate it once at CERT_DIR, default C:/agentos-certs, before docker compose up.'; exit 1; fi; npm run dev -- --host --port 3001"]
