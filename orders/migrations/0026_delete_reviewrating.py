# Generated by Django 4.2.6 on 2023-12-06 11:42

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0025_reviewrating"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ReviewRating",
        ),
    ]