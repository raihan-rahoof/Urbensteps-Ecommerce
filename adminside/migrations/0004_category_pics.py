# Generated by Django 4.2.6 on 2023-10-23 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminside', '0003_custom_user_delete_customuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='pics',
            field=models.ImageField(default=None, upload_to='categories/'),
        ),
    ]