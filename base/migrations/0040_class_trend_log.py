# Generated by Django 4.2 on 2023-05-28 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0039_class_breeding_limit"),
    ]

    operations = [
        migrations.AddField(
            model_name="class",
            name="trend_log",
            field=models.JSONField(default={}),
        ),
    ]
