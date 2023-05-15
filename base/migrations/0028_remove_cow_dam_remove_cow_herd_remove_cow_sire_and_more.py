# Generated by Django 4.2 on 2023-05-14 17:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0027_delete_resource"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cow",
            name="dam",
        ),
        migrations.RemoveField(
            model_name="cow",
            name="herd",
        ),
        migrations.RemoveField(
            model_name="cow",
            name="sire",
        ),
        migrations.RemoveField(
            model_name="cow",
            name="traits",
        ),
        migrations.RemoveField(
            model_name="bovine",
            name="connected_bull",
        ),
        migrations.RemoveField(
            model_name="bovine",
            name="connected_cow",
        ),
        migrations.AddField(
            model_name="bovine",
            name="generation",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="bovine",
            name="herd",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to="base.herd"
            ),
        ),
        migrations.AddField(
            model_name="bovine",
            name="male",
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="bovine",
            name="name",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name="Bull",
        ),
        migrations.DeleteModel(
            name="Cow",
        ),
    ]