# Generated by Django 4.2 on 2023-05-23 22:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0035_class_viewable_traits"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="herd",
            name="unrestricted",
        ),
    ]