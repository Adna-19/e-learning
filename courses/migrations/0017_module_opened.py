# Generated by Django 3.2.4 on 2021-08-01 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0016_auto_20210729_0955'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='opened',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]