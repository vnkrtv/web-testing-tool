FROM       ubuntu:latest
MAINTAINER quizer

RUN apt-get update && apt-get install -y build-essential python3 \
 && apt-get install -y python3-setuptools \
 && apt-get install -y python3-pip \
 && apt-get install -y python3-venv

RUN apt-get update && apt-get install -y mongodb \
 && mkdir -p /data/db \
 && mkdir -p /data/code

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN python3 -m venv venv \
 && . venv/bin/activate \
 && pip3 install --no-cache-dir -r requirements.txt \
 && django-admin.py startproject quizer \
 && python3 quizer/manage.py startapp main

COPY quizer /app/quizer
#RUN . venv/bin/activate \
# && python3 quizer/manage.py makemigrations \
# && python3 quizer/manage.py migrate

#RUN . venv/bin/activate \
# && python3 quizer/manage.py makemigrations \
# && python3 quizer/manage.py migrate \
# && echo 'from django.contrib.auth.models import Group; l = Group(id=1, name="lecturer"); l.save()' | python3 quizer/manage.py shell \
# && echo 'from django.contrib.auth.models import Group; s = Group(id=2, name="student"); s.save()' | python3 quizer/manage.py shell \
# && echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', '', 'admin')" | python3 quizer/manage.py shell \
# && echo 'from django.contrib.auth.models import User; a = User.objects.get(username="admin"); a.groups.add(1); a.save()'  | python3 quizer/manage.py shell
# && echo 'from django.contrib.auth.models import User; s = User(id=2); s.username = "user"; s.set_password("password"); s.groups.add(2); s.save()' | python3 quizer/manage.py shell

COPY entry_commands /entry_commands.sh
EXPOSE 8000
ENTRYPOINT ["/entry_commands"]