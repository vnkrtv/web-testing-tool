FROM snakepacker/python:all as builder
MAINTAINER LeadNess

RUN python3.7 -m venv /usr/share/python3/venv
RUN /usr/share/python3/venv/bin/pip install -U pip

ARG MONGO_HOST=localhost
COPY requirements.txt /mnt/
RUN /usr/share/python3/venv/bin/pip install -Ur /mnt/requirements.txt \
 && file="$(echo "$(cat /usr/share/python3/venv/lib/python3.7/site-packages/pymongo/mongo_client.py)")" \
 && echo "${file}" | sed "s/localhost/$MONGO_HOST/" > /usr/share/python3/venv/lib/python3.7/site-packages/pymongo/mongo_client.py

FROM snakepacker/python:3.7 as api

COPY --from=builder /usr/share/python3/venv /usr/share/python3/venv
COPY quizer /usr/share/python3/quizer
COPY deploy/settings /usr/share/python3/quizer/quizer/settings.py

ENV MONGO_HOST=$MONGO_HOST
COPY deploy/entrypoint /entrypoint
ENTRYPOINT ["/entrypoint"]