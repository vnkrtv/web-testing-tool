# Generated by Django 3.1.13 on 2021-10-26 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0002_auto_20211024_1813"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile",
            name="web_url",
        ),
        migrations.AlterField(
            model_name="profile",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]