# Generated by Django 4.2.6 on 2023-11-16 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_rename_city_order_district_order_hometown'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='zipcode',
            field=models.CharField(default=0, max_length=100),
            preserve_default=False,
        ),
    ]
