# Generated by Django 4.2.6 on 2023-12-01 05:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("offers", "0003_alter_offer_discount"),
    ]

    operations = [
        migrations.AlterField(
            model_name="offer",
            name="discount",
            field=models.PositiveIntegerField(),
        ),
    ]
