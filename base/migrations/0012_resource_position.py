# Generated by Django 4.1.3 on 2023-03-30 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0011_alter_resource_info"),
    ]

    operations = [
        migrations.AddField(
            model_name="resource",
            name="position",
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]
