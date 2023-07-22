# Generated by Django 4.2 on 2023-06-26 18:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0041_alter_bovine_pedigree_alter_class_trend_log"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="bovine",
            name="pedigree",
        ),
        migrations.AddField(
            model_name="bovine",
            name="dam",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="_dam",
                to="base.bovine",
            ),
        ),
        migrations.AddField(
            model_name="bovine",
            name="inbreeding",
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="bovine",
            name="sire",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="_sire",
                to="base.bovine",
            ),
        ),
        migrations.DeleteModel(
            name="Pedigree",
        ),
    ]