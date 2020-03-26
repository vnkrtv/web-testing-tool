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
RUN source ./venv/bin/activate \
RUN pip install --no-cache-dir -r requirements.txt \
RUN django-admin.py startproject quizer \
RUN python quizer/manage.py startapp main \
RUN python quizer/manage.py makemigrations \
RUN python quizer/manage.py migrate \
RUN echo 'from django.contrib.auth.models import Group; l = Group(id=1, name="lecturer"); l.save()' | python quizer/manage.py shell \
RUN echo 'from django.contrib.auth.models import Group; s = Group(id=2, name="student"); s.save()' | python quizer/manage.py shell \
RUN echo 'from django.contrib.auth.models import User; a = User.objects.get(id=1); s.groups.add(id=1); s.save(); print("Added user %s to group %s" % (a.username, "lecturer"))'  | python quizer/manage.py shell \
RUN echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', '', 'admin')" | python quizer/manage.py shell \
RUN echo 'from django.contrib.auth.models import User; s = User(id=4, username="user"); s.set_password("password"); s.groups.add(2); s.save()' | python quizer/manage.py shell

COPY quizer /app/quizer
COPY entry_commands.sh /entry_commands.sh

EXPOSE 8000
ENTRYPOINT ["/entry_commands.sh"]