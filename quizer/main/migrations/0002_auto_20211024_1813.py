# Generated by Django 3.1.13 on 2021-10-24 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="options",
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name="runningtestsanswers",
            name="right_answers",
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name="userresult",
            name="questions",
            field=models.JSONField(),
        ),
    ]
