# Generated by Django 4.1.3 on 2023-03-26 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0008_herd_enrollment"),
    ]

    operations = [
        migrations.AddField(
            model_name="class",
            name="info",
            field=models.TextField(blank=True, max_length=1024, null=True),
        ),
    ]
