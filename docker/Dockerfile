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
 && python3 quizer/manage.py makemigrations \
 && python3 quizer/manage.py migrate \
 &&
 && echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', '', 'admin')" | python3 quizer/manage.py shell

COPY quizer /app/quizer
COPY entry_commands.sh /entry_commands.sh

EXPOSE 8000
ENTRYPOINT ["/entry_commands.sh"]


echo 'from django.contrib.auth.models import Group; l = Group(id=1, name="lecturer"); l.save()' | python quizer/manage.py shell
echo 'from django.contrib.auth.models import Group; s = Group(id=2, name="student"); s.save()' | python quizer/manage.py shell
echo "Created 'student' group"
echo "===========================================Enter superuser info==============================================="
python quizer/manage.py createsuperuser
echo 'from django.contrib.auth.models import User; a = User.objects.get(id=1); s.groups.add(id=1); s.save(); print("Added user %s to group %s" % (a.username, "lecturer"))'  | python quizer/manage.py shell
echo 'from django.contrib.auth.models import User; s = User(id=4, username="user"); s.set_password("password"); s.groups.add(2); s.save()' | python quizer/manage.py shell
echo "Added user 'user' with password 'password' to group 'student'"