FROM node:20-alpine
WORKDIR /app
COPY __AGENT_ID__/frontend/package*.json ./
RUN npm install
COPY __AGENT_ID__/frontend .
EXPOSE 3001
CMD ["npm","run","dev","--","--host","--port","3001"]
