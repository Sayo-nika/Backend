# TODO: replace with Alpine image. Will require some more configuration to get stuff like uvloop working.
FROM python:3.7-stretch

# Make container root
USER root
RUN mkdir /app

# Install Python dependencies
COPY requirements.txt /app
RUN pip install daphne
RUN pip install -r /app/requirements.txt

COPY . /app
WORKDIR /app

# Setup user to run the server as
RUN useradd -m python

# Install dumb-init
RUN apt-get update && apt-get install \
    dumb-init

USER python
EXPOSE 8000

ENTRYPOINT ["dumb-init", "--"]
CMD ["sh", "dockerrun.sh"]
