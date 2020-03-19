#!/bin/bash

service mongodb start
python3 /app/quizer/manage.py runserver 0.0.0.0:8000 --noreload
