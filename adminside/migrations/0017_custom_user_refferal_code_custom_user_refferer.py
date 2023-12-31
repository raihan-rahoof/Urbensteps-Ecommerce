# Generated by Django 4.2.6 on 2023-12-01 14:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("adminside", "0016_category_offer"),
    ]

    operations = [
        migrations.AddField(
            model_name="custom_user",
            name="refferal_code",
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="custom_user",
            name="refferer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="adminside.custom_user",
            ),
        ),
    ]
