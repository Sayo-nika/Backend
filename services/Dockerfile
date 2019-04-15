FROM node:10-alpine

# Create container root
USER root
RUN mkdir /app

COPY package.json /app/
RUN cd /app; yarn

COPY . /app
WORKDIR /app

RUN apk add dumb-init

EXPOSE 9000

ENTRYPOINT ["dumb-init", "--"]
CMD ["yarn", "start"]
