# Generated by Django 4.2 on 2023-05-23 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0038_alter_class_herd_alter_class_publicherd"),
    ]

    operations = [
        migrations.AddField(
            model_name="class",
            name="breeding_limit",
            field=models.IntegerField(default=0),
        ),
    ]
