# Generated by Django 4.2 on 2023-05-21 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0034_alter_pedigree_dam_alter_pedigree_sire"),
    ]

    operations = [
        migrations.AddField(
            model_name="class",
            name="viewable_traits",
            field=models.JSONField(default={"n": None}),
            preserve_default=False,
        ),
    ]