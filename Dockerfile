FROM       ubuntu:latest
MAINTAINER LeadNess

RUN apt-get update && apt-get install -y build-essential python3 \
 && apt-get install -y python3-setuptools \
 && apt-get install -y python3-pip

RUN apt-get update && apt-get install -y mongodb \
 && mkdir -p /data/db \
 && mkdir -p /data/code

COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

COPY quizer /app/quizer

# MongoDB port
EXPOSE 27017

# App port
EXPOSE 80

COPY deploy/entrypoint /entrypoint
ENTRYPOINT ["/entrypoint"]
