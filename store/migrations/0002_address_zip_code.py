# Generated by Django 5.0.3 on 2024-04-08 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="address",
            name="zip_code",
            field=models.CharField(default="00000", max_length=10),
        ),
    ]