# pylint: skip-file
from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Subject


admin.site.register(Subject)

admin.site.site_header = 'Quizer'

