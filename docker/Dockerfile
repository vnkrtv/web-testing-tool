FROM       ubuntu:latest
MAINTAINER quizer

RUN apt-get update && apt-get install -y build-essential python3 \
 && apt-get install -y python-setuptools \
 && apt-get install -y python-pip

RUN apt-get update && apt-get install -y mongodb \
 && mkdir -p /data/db \
 && mkdir -p /data/code

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN apt-get install -y python3-pip \
 && pip3 install --no-cache-dir -r requirements.txt \
 && django-admin.py startproject quizer \
 && python3 quizer/manage.py startapp main \
 && python3 quizer/manage.py migrate \
 && python3 quizer/manage.py makemigrations \
 && echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', '', 'admin')" | python3 quizer/manage.py shell

COPY quizer /app/quizer
COPY entry_commands.sh /entry_commands.sh

EXPOSE 8000
ENTRYPOINT ["/entry_commands.sh"]
