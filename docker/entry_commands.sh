#!/bin/bash

python3 /app/quizer/manage.py runserver 0.0.0.0:8000 --noreload
service mongodb start