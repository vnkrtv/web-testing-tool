#!/bin/bash

service mongodb start
. /app/venv/bin/activate
python3 /app/quizer/manage.py makemigrations
python3 /app/quizer/manage.py migrate
echo 'from django.contrib.auth.models import Group; l = Group(id=1, name="lecturer"); l.save()' | python3 /app/quizer/manage.py shell
echo 'from django.contrib.auth.models import Group; s = Group(id=2, name="student"); s.save()' | python3 /app/quizer/manage.py shell
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', '', 'admin')" | python3 /app/quizer/manage.py shell
echo 'from django.contrib.auth.models import User; a = User.objects.get(id=1); a.groups.add(1); a.save(); print("Added user %s to group %s" % (a.username, "lecturer"))'  | python3 /app/quizer/manage.py shell
echo 'from django.contrib.auth.models import User; s = User(id=4, username="user"); s.set_password("password"); s.groups.add(2); s.save()' | python3 /app/quizer/manage.py shell
echo 'from main.models import Subject; s = Subject(id=1, lecturer_id=1, name="Python", description="PL Python"); s.save()' | python3 /app/quizer/manage.py shell
echo 'from main.models import Test; t = Test(id=1, author_id=1, name="PZ1", duration=300, subject_id=1, tasks_num=5, description="Test based on lecture 1"); t.save()' | python3 /app/quizer/manage.py shell
python3 /app/quizer/manage.py runserver 0.0.0.0:8000 --noreload
