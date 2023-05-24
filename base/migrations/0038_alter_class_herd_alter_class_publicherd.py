# Generated by Django 4.2 on 2023-05-23 22:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0037_class_publicherd"),
    ]

    operations = [
        migrations.AlterField(
            model_name="class",
            name="herd",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="classherd",
                to="base.herd",
            ),
        ),
        migrations.AlterField(
            model_name="class",
            name="publicherd",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="classpublicherd",
                to="base.herd",
            ),
        ),
    ]