# Generated by Django 4.2.6 on 2023-11-14 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0007_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='phone',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
