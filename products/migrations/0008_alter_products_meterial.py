# Generated by Django 4.2.6 on 2023-11-04 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_alter_products_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='meterial',
            field=models.CharField(default='NA', max_length=200),
        ),
    ]
