# Generated by Django 3.2.4 on 2021-06-27 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20210626_1538'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_image',
            field=models.ImageField(default='files/profile_images/default.png', upload_to='files/profile_images/'),
        ),
    ]