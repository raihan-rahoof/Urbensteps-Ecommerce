# Generated by Django 4.2.6 on 2023-10-21 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User_auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
    ]