# Generated by Django 2.2.10 on 2020-03-03 19:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20200303_1917'),
    ]

    operations = [
        migrations.RenameField(
            model_name='test',
            old_name='test_theme',
            new_name='name',
        ),
    ]
