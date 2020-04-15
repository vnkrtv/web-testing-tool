FROM       ubuntu:latest
MAINTAINER quizer

RUN apt-get update && apt-get install -y build-essential python3 \
 && apt-get install -y python3-setuptools \
 && apt-get install -y python3-pip

RUN apt-get update && apt-get install -y mongodb \
 && mkdir -p /data/db \
 && mkdir -p /data/code

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install --no-cache-dir -r requirements.txt \
 && django-admin.py startproject quizer \
 && python3 quizer/manage.py startapp main

COPY quizer /app/quizer

COPY entry_commands /entry_commands
EXPOSE 80
ENTRYPOINT ["/entry_commands"]
