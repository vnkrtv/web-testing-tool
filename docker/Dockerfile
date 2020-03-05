FROM python:latest
WORKDIR /app
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt /
 && django-admin.py startproject quizer /
 && python quizer/manage.py startapp main /
 && echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', '', 'admin')" | python quizer/manage.py shell
COPY quizer /app/quizer
ENTRYPOINT ["python", "/app/quizer/manage.py", "runserver", "0.0.0.0:8000", "--noreload"]
