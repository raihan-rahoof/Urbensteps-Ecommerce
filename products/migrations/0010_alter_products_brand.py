# Generated by Django 4.2.6 on 2023-11-10 06:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adminside', '0015_custom_user_country_custom_user_mobile_number'),
        ('products', '0009_alter_products_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='brand',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='adminside.brand'),
        ),
    ]
