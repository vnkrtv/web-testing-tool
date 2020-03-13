FROM       ubuntu:latest
MAINTAINER quizer

# Installation:
RUN apt-get update && apt-get install -y build-essential python3 \
 && apt-get install -y python-setuptools \
 && apt-get install -y python-pip
# RUN apt-get install -y nano
# RUN apt-get install -y telnet
# RUN apt-get install -y vim

# Import MongoDB public GPG key AND create a MongoDB list file
# RUN apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv 7F0CEB10
# RUN echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | tee /etc/apt/sources.list.d/10gen.list

# Update apt-get sources AND install MongoDB
RUN apt-get update && apt-get install -y mongodb

# Create the MongoDB data directory
RUN mkdir -p /data/db

# Create the MongoDB data directory
RUN mkdir -p /data/code

# Expose port #27017 from the container to the host
# EXPOSE 27017

# Set /usr/bin/mongod as the dockerized entry-point application

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt \
 && django-admin.py startproject quizer \
 && python3 quizer/manage.py startapp main \
 && python3 quizer/manage.py migrate \
 && python3 quizer/manage.py makemigrations \
 && echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', '', 'admin')" | python3 quizer/manage.py shell

COPY quizer /app/quizer

ENTRYPOINT ["python3", "/app/quizer/manage.py", "runserver", "0.0.0.0:8000", "--noreload"]
