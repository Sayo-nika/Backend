FROM node:10
RUN mkdir -p /app && \
    chown -R node:node /app
WORKDIR /app
COPY . .
RUN npm i -S -P
EXPOSE 9000
CMD ["node", "server"]