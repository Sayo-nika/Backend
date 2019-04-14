FROM python:3.7-stretch
RUN mkdir -p /app
WORKDIR /app

RUN apt-get update && \
    apt-get install -y sudo gettext dumb-init && \
    apt-get clean;

RUN adduser --disabled-password --gecos '' sayonika && \
    mkdir -p /etc/sudoers.d && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    echo "sayonika ALL=(root) NOPASSWD:ALL" >> /etc/sudoers.d/user && \
    chmod 0440 /etc/sudoers.d/user;

COPY . .
COPY entrypoint /home/sayonika
COPY passwd_template /tmp
COPY run.sh /tmp

RUN pip install requests uvloop psycopg2 && pip install -r requirements.txt && \
    chmod g+rw /app;

RUN chgrp -R 0 /home/sayonika && \
    chmod a+x /home/sayonika/entrypoint && \
    chmod a+x /tmp/run.sh && \
    chmod -R g=u /home/sayonika && \
    chmod g=u /etc/passwd && \
    find /home/sayonika -type d -exec chmod g+x {} +

EXPOSE 4444
ENV PYTHONPATH="$PYTHONPATH:/app"

USER 10001

ENTRYPOINT [ "/home/sayonika/entrypoint" ]
CMD ["dumb-init", "bash", "/tmp/run.sh"]
