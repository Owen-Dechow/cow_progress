# Generated by Django 4.1.3 on 2023-03-27 23:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0010_resource"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resource",
            name="info",
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
    ]
