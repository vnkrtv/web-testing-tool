# Generated by Django 3.1.13 on 2021-10-26 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0003_auto_20211026_1409"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile",
            name="name",
        ),
        migrations.AlterField(
            model_name="profile",
            name="group",
            field=models.TextField(default=""),
        ),
    ]
