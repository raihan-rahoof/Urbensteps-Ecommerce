# Generated by Django 4.2.6 on 2023-11-26 09:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0017_alter_couponusage_discount_amount_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="coupons",
            name="image",
            field=models.ImageField(default="no images found", upload_to="coupons/"),
        ),
    ]