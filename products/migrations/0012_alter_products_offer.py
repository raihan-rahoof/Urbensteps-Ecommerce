# Generated by Django 4.2.6 on 2023-12-01 05:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("offers", "0003_alter_offer_discount"),
        ("products", "0011_products_offer"),
    ]

    operations = [
        migrations.AlterField(
            model_name="products",
            name="offer",
            field=models.ForeignKey(
                blank=True,
                default="nothing",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="offers.offer",
            ),
        ),
    ]
