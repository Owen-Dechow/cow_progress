# Generated by Django 4.2 on 2023-05-14 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0031_alter_bovine_pedigree"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bovine",
            name="male",
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name="bovine",
            name="name",
            field=models.CharField(max_length=255, null=True),
        ),
    ]
