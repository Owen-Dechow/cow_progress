# Generated by Django 4.2 on 2023-06-27 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0047_bovine_connectedclass_alter_bovine_herd"),
    ]

    operations = [
        migrations.AddField(
            model_name="bovine",
            name="pedigree",
            field=models.JSONField(default=dict),
        ),
    ]