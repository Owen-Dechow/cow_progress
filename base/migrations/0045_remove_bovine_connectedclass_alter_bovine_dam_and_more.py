# Generated by Django 4.2 on 2023-06-26 21:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0044_bovine_connectedclass_alter_bovine_herd"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="bovine",
            name="connectedclass",
        ),
        migrations.AlterField(
            model_name="bovine",
            name="dam",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="_dam",
                to="base.bovine",
            ),
        ),
        migrations.AlterField(
            model_name="bovine",
            name="herd",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to="base.herd"
            ),
        ),
        migrations.AlterField(
            model_name="bovine",
            name="sire",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="_sire",
                to="base.bovine",
            ),
        ),
        migrations.CreateModel(
            name="Pedigree",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("animal_id", models.CharField(max_length=255)),
                ("male", models.BooleanField()),
                ("inbreeding", models.FloatField()),
                (
                    "dam",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="_dam",
                        to="base.pedigree",
                    ),
                ),
                (
                    "sire",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="_sire",
                        to="base.pedigree",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="bovine",
            name="pedigree",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="base.pedigree",
            ),
        ),
    ]
