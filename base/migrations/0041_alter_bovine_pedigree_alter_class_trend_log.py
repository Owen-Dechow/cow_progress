# Generated by Django 4.2 on 2023-06-23 13:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0040_class_trend_log"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bovine",
            name="pedigree",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="base.pedigree",
            ),
        ),
        migrations.AlterField(
            model_name="class",
            name="trend_log",
            field=models.JSONField(default=dict),
        ),
    ]
