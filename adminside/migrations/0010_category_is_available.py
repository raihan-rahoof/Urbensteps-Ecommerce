# Generated by Django 4.2.6 on 2023-10-23 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminside', '0009_remove_category_pics'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
    ]
