# Generated by Django 4.2.6 on 2023-11-16 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0004_remove_cart_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='size',
            field=models.CharField(max_length=25, null=True),
        ),
    ]
