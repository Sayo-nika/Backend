FROM python:3.7-stretch
RUN mkdir -p /app
WORKDIR /app

RUN apt-get update && \
    apt-get install -y sudo gettext && \
    apt-get clean;

RUN pip install -r requirements.txt && \
    chmod g+rw /app;

RUN adduser --disabled-password --gecos '' sayonika && \
    mkdir -p /etc/sudoers.d && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    echo "sayonika ALL=(root) NOPASSWD:ALL" >> /etc/sudoers.d/user && \
    chmod 0440 /etc/sudoers.d/user;

COPY . .
COPY entrypoint /home/sayonika

RUN chgrp -R 0 /home/sayonika && \
    chmod a+x /home/sayonika/entrypoint && \
    chmod -R g=u /home/sayonika && \
    chmod g=u /etc/passwd && \
    find /home/sayonika -type d -exec chmod g+x {} +

EXPOSE 4444
ENV PYTHONPATH="$PYTHONPATH:/app"

USER 10001

ENTRYPOINT [ "/home/sayonika/entrypoint" ]
CMD ["hypercorn", "main:sayonika_instance", "-k uvloop"]
