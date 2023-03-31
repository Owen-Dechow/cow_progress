# Generated by Django 4.1.3 on 2023-03-30 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0015_staticdataclass"),
    ]

    operations = [
        migrations.RenameField(
            model_name="staticdataclass",
            old_name="title",
            new_name="name",
        ),
        migrations.AlterField(
            model_name="staticdataclass",
            name="data",
            field=models.TextField(blank=True, max_length=1000),
        ),
    ]
