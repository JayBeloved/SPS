# Generated by Django 5.1.5 on 2025-02-03 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="phone_number",
            field=models.CharField(default=90233345986, max_length=15),
            preserve_default=False,
        ),
    ]
