# Generated by Django 4.1.3 on 2023-03-30 00:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0012_resource_position"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="resource",
            name="info",
        ),
    ]
